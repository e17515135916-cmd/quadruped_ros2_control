#!/usr/bin/env python3
"""Stage 3 single-leg numerical IK test.

One leg moves slowly in semantic base-frame vertical z.  The other three legs
hold default_stand_q.  Rail joints remain locked by RailLockController.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Dict, Mapping, Sequence, Tuple
import xml.etree.ElementTree as ET

import yaml

try:
    import xacro
except Exception:  # pragma: no cover
    xacro = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.joint_pd_controller import JointPDController
from controllers.rail_lock_controller import RailLockController
from controllers.safety_checker import SafetyChecker
from kinematics.numerical_ik import NumericalIK


LEG_ORDER = ("FL", "FR", "RL", "RR")


def resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        for root in (base_dir, WORKSPACE_ROOT):
            candidate = (root / path).resolve()
            if candidate.exists():
                return candidate
    return path.resolve()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def local_package_map(workspace_root: Path) -> Dict[str, Path]:
    package_map: Dict[str, Path] = {}
    for package_xml in workspace_root.glob("src/*/package.xml"):
        try:
            package_name = (ET.parse(package_xml).getroot().findtext("name") or package_xml.parent.name).strip()
        except ET.ParseError:
            package_name = package_xml.parent.name
        package_map[package_name] = package_xml.parent.resolve()
    return package_map


def expand_model_to_urdf(model_path: Path, robot_config: Mapping[str, Any], config_dir: Path) -> str:
    if model_path.suffix.lower() == ".xacro":
        if xacro is None:
            raise RuntimeError("xacro is required to expand .xacro robot models.")
        raw_args = robot_config.get("robot", {}).get("xacro_args", {}) or {}
        mappings = {key: str(resolve_path(str(value), config_dir)) for key, value in raw_args.items()}
        return xacro.process_file(str(model_path), mappings=mappings).toprettyxml(indent="  ")
    return model_path.read_text(encoding="utf-8")


def replace_package_urls(urdf_text: str, package_map: Mapping[str, Path]) -> str:
    out = urdf_text
    for package_name, package_dir in package_map.items():
        out = out.replace(f"package://{package_name}", str(package_dir))
    return out


def pybullet_base_alignment_quat(p: Any, robot_config: Mapping[str, Any]) -> Tuple[float, float, float, float]:
    pybullet_cfg = ((robot_config.get("simulation") or {}).get("pybullet") or {})
    base_rpy = pybullet_cfg.get("base_orientation_rpy", [0.0, 0.0, 0.0])
    return tuple(p.getQuaternionFromEuler([float(v) for v in base_rpy]))


def semantic_base_pose(
    p: Any,
    robot_config: Mapping[str, Any],
    body_id: int,
) -> Tuple[Sequence[float], Sequence[float]]:
    base_pos, base_urdf_quat = p.getBasePositionAndOrientation(body_id)
    align_quat = pybullet_base_alignment_quat(p, robot_config)
    _, inv_align = p.invertTransform([0.0, 0.0, 0.0], align_quat)
    _, base_sem_quat = p.multiplyTransforms(
        [0.0, 0.0, 0.0],
        base_urdf_quat,
        [0.0, 0.0, 0.0],
        inv_align,
    )
    return base_pos, base_sem_quat


def world_to_semantic_base(
    p: Any,
    robot_config: Mapping[str, Any],
    body_id: int,
    point_world: Sequence[float],
) -> Tuple[float, float, float]:
    base_pos, base_sem_quat = semantic_base_pose(p, robot_config, body_id)
    inv_pos, inv_quat = p.invertTransform(base_pos, base_sem_quat)
    pos, _ = p.multiplyTransforms(inv_pos, inv_quat, point_world, [0.0, 0.0, 0.0, 1.0])
    return tuple(float(v) for v in pos)


def semantic_base_to_world(
    p: Any,
    robot_config: Mapping[str, Any],
    body_id: int,
    point_base: Sequence[float],
) -> Tuple[float, float, float]:
    base_pos, base_sem_quat = semantic_base_pose(p, robot_config, body_id)
    pos, _ = p.multiplyTransforms(base_pos, base_sem_quat, point_base, [0.0, 0.0, 0.0, 1.0])
    return tuple(float(v) for v in pos)


def semantic_base_rpy(p: Any, robot_config: Mapping[str, Any], body_id: int) -> Tuple[float, float, float]:
    _, base_sem_quat = semantic_base_pose(p, robot_config, body_id)
    return tuple(p.getEulerFromQuaternion(base_sem_quat))


def leg_joint_names(robot_config: Mapping[str, Any]) -> Dict[str, Sequence[str]]:
    return {
        leg: [str(name) for name in ((robot_config.get("legs") or {}).get(leg, {}) or {}).get("joint_names", [])]
        for leg in LEG_ORDER
    }


def default_stand_targets(robot_config: Mapping[str, Any]) -> Dict[str, float]:
    targets: Dict[str, float] = {}
    for leg in LEG_ORDER:
        leg_cfg = ((robot_config.get("legs") or {}).get(leg, {}) or {})
        for index, joint_name in enumerate(leg_cfg.get("joint_names", []) or []):
            default_q = leg_cfg.get("default_stand_q", []) or []
            targets[str(joint_name)] = float(default_q[index]) if index < len(default_q) else 0.0
    return targets


def configured_rail_positions(robot_config: Mapping[str, Any]) -> Dict[str, float]:
    rail_cfg = robot_config.get("rail") or {}
    joint_names = [str(name) for name in (rail_cfg.get("joint_names") or [])]
    single = str(rail_cfg.get("joint_name", "") or "").strip()
    if single and single not in joint_names:
        joint_names.append(single)
    source = str(rail_cfg.get("lock_position_source", "initial"))
    position_default = float(rail_cfg.get("lock_position", 0.0))
    position_map = {
        str(name): float(value)
        for name, value in (rail_cfg.get("lock_position_map", {}) or {}).items()
    }
    positions: Dict[str, float] = {}
    for joint_name in joint_names:
        positions[joint_name] = position_map.get(joint_name, position_default) if source == "configured" else 0.0
    return positions


def joint_dict_from_pybullet(p: Any, body_id: int, joint_name_to_index: Mapping[str, int]) -> Dict[str, Tuple[float, float]]:
    return {
        joint_name: tuple(float(v) for v in p.getJointState(body_id, joint_index)[:2])
        for joint_name, joint_index in joint_name_to_index.items()
    }


def pybullet_maps(p: Any, body_id: int) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, Tuple[float, float]], Dict[str, float]]:
    joint_name_to_index: Dict[str, int] = {}
    link_name_to_index: Dict[str, int] = {}
    joint_limits: Dict[str, Tuple[float, float]] = {}
    torque_limits: Dict[str, float] = {}
    for joint_index in range(p.getNumJoints(body_id)):
        info = p.getJointInfo(body_id, joint_index)
        joint_name = info[1].decode("utf-8")
        link_name = info[12].decode("utf-8")
        joint_name_to_index[joint_name] = joint_index
        link_name_to_index[link_name] = joint_index
        if info[2] != p.JOINT_FIXED:
            lower = float(info[8])
            upper = float(info[9])
            joint_limits[joint_name] = (lower, upper) if lower <= upper else (None, None)
            torque_limits[joint_name] = float(info[10]) if info[10] > 0 else math.inf
    return joint_name_to_index, link_name_to_index, joint_limits, torque_limits


def reset_initial_pose(
    p: Any,
    body_id: int,
    joint_name_to_index: Mapping[str, int],
    link_name_to_index: Mapping[str, int],
    robot_config: Mapping[str, Any],
    base_height: float,
) -> None:
    base_quat = pybullet_base_alignment_quat(p, robot_config)
    p.resetBasePositionAndOrientation(body_id, [0.0, 0.0, base_height], base_quat)
    p.resetBaseVelocity(body_id, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    for rail_name, rail_q in configured_rail_positions(robot_config).items():
        if rail_name in joint_name_to_index:
            p.resetJointState(body_id, joint_name_to_index[rail_name], rail_q, 0.0)
    for joint_name, q in default_stand_targets(robot_config).items():
        if joint_name in joint_name_to_index:
            p.resetJointState(body_id, joint_name_to_index[joint_name], q, 0.0)

    foot_z = []
    for leg in LEG_ORDER:
        foot_link = ((robot_config.get("legs") or {}).get(leg, {}) or {}).get("foot_link", "")
        if foot_link in link_name_to_index:
            foot_z.append(p.getLinkState(body_id, link_name_to_index[str(foot_link)])[0][2])
    if foot_z:
        shift = 0.014 - min(foot_z)
        base_pos, base_quat = p.getBasePositionAndOrientation(body_id)
        p.resetBasePositionAndOrientation(body_id, [base_pos[0], base_pos[1], base_pos[2] + shift], base_quat)
        p.resetBaseVelocity(body_id, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])


def apply_zero_default_motors(p: Any, body_id: int) -> None:
    for joint_index in range(p.getNumJoints(body_id)):
        info = p.getJointInfo(body_id, joint_index)
        if info[2] != p.JOINT_FIXED:
            p.setJointMotorControl2(body_id, joint_index, p.VELOCITY_CONTROL, targetVelocity=0.0, force=0.0)


def disable_body_collision_and_visual(p: Any, body_id: int) -> None:
    for link_index in range(-1, p.getNumJoints(body_id)):
        p.setCollisionFilterGroupMask(body_id, link_index, 0, 0)
        try:
            p.changeVisualShape(body_id, link_index, rgbaColor=[1.0, 1.0, 1.0, 0.0])
        except Exception:
            pass


class PyBulletLegKinematics:
    """Fixed-base FK backend that returns foot position in semantic base frame."""

    def __init__(
        self,
        p: Any,
        body_id: int,
        robot_config: Mapping[str, Any],
        joint_name_to_index: Mapping[str, int],
        link_name_to_index: Mapping[str, int],
    ):
        self.p = p
        self.body_id = body_id
        self.robot_config = robot_config
        self.joint_name_to_index = dict(joint_name_to_index)
        self.link_name_to_index = dict(link_name_to_index)

    def set_nominal_pose(self) -> None:
        self.p.resetBasePositionAndOrientation(
            self.body_id,
            [0.0, 0.0, 0.0],
            pybullet_base_alignment_quat(self.p, self.robot_config),
        )
        for rail_name, rail_q in configured_rail_positions(self.robot_config).items():
            if rail_name in self.joint_name_to_index:
                self.p.resetJointState(self.body_id, self.joint_name_to_index[rail_name], rail_q, 0.0)
        for joint_name, q in default_stand_targets(self.robot_config).items():
            if joint_name in self.joint_name_to_index:
                self.p.resetJointState(self.body_id, self.joint_name_to_index[joint_name], q, 0.0)

    def foot_position(self, leg_name: str, q_model: Sequence[float]) -> Tuple[float, float, float]:
        leg_cfg = ((self.robot_config.get("legs") or {}).get(leg_name, {}) or {})
        joint_names = [str(name) for name in leg_cfg.get("joint_names", [])]
        if len(joint_names) != 3:
            raise ValueError(f"{leg_name} must have three configured joints.")
        for joint_name, q in zip(joint_names, q_model):
            self.p.resetJointState(self.body_id, self.joint_name_to_index[joint_name], float(q), 0.0)
        foot_link = str(leg_cfg.get("foot_link", ""))
        pos = self.p.getLinkState(self.body_id, self.link_name_to_index[foot_link])[0]
        return tuple(float(v) for v in pos)


def row_json(values: Mapping[str, Any]) -> str:
    return json.dumps(values, sort_keys=True, separators=(",", ":"))


def add_marker(
    p: Any,
    pos: Sequence[float],
    color: Sequence[float],
    label: str = "",
    size: float = 0.045,
    life_time: float = 0.8,
) -> None:
    x, y, z = pos
    p.addUserDebugLine([x - size, y, z], [x + size, y, z], color, lineWidth=6, lifeTime=life_time)
    p.addUserDebugLine([x, y - size, z], [x, y + size, z], color, lineWidth=6, lifeTime=life_time)
    p.addUserDebugLine([x, y, z - size], [x, y, z + size], color, lineWidth=6, lifeTime=life_time)
    if label:
        p.addUserDebugText(label, [x, y, z + 0.05], textColorRGB=color[:3], textSize=1.4, lifeTime=life_time)


def apply_leg_visuals(
    p: Any,
    body_id: int,
    link_name_to_index: Mapping[str, int],
    active_leg: str,
) -> None:
    prefix_map = {"FL": "lf", "FR": "rf", "RL": "lh", "RR": "rh"}
    active_prefix = prefix_map[active_leg]
    for link_name, link_index in link_name_to_index.items():
        if link_name == "base_link":
            continue
        is_active = link_name.startswith(active_prefix + "_")
        rgba = [1.0, 0.78, 0.08, 1.0] if is_active else [0.80, 0.80, 0.80, 0.92]
        try:
            p.changeVisualShape(body_id, link_index, rgbaColor=rgba)
        except Exception:
            continue


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(PROJECT_ROOT / "config" / "robot_config.yaml"))
    parser.add_argument("--rail-config", default=str(PROJECT_ROOT / "config" / "rail_config.yaml"))
    parser.add_argument("--controller-config", default=str(PROJECT_ROOT / "config" / "controller_config.yaml"))
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--leg", choices=LEG_ORDER, default=None)
    parser.add_argument("--duration-per-leg", type=float, default=5.0)
    parser.add_argument("--lift-height", type=float, default=0.04)
    parser.add_argument(
        "--dynamic",
        action="store_true",
        help="Run with free-base dynamics. Default is fixed-base kinematic IK validation.",
    )
    args = parser.parse_args()

    try:
        import pybullet as p
        import pybullet_data
    except Exception as exc:
        print(f"[ERROR] pybullet is required for single_leg_ik_test: {exc}")
        return 2

    robot_config_path = Path(args.config).resolve()
    rail_config_path = Path(args.rail_config).resolve()
    controller_config_path = Path(args.controller_config).resolve()
    robot_config = load_yaml(robot_config_path)
    rail_config = load_yaml(rail_config_path)
    controller_config = load_yaml(controller_config_path)
    config_dir = robot_config_path.parent

    dt = float((controller_config.get("controller") or {}).get("control_dt", 0.002))
    base_height = float((controller_config.get("controller") or {}).get("initial_base_height", 0.42))
    step_height = min(max(float(args.lift_height), 0.03), 0.05)
    tested_legs = (args.leg,) if args.leg else LEG_ORDER

    model_path = resolve_path(robot_config["robot"]["model_path"], config_dir)
    urdf_text = expand_model_to_urdf(model_path, robot_config, config_dir)
    urdf_text = replace_package_urls(urdf_text, local_package_map(WORKSPACE_ROOT))
    with tempfile.NamedTemporaryFile("w", suffix=".urdf", delete=False, encoding="utf-8") as f:
        f.write(urdf_text)
        temp_urdf = f.name

    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "ik_test_log.csv"

    physics_client = p.connect(p.GUI if args.gui else p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0.0, 0.0, -9.81)
        p.setTimeStep(dt)
        p.loadURDF("plane.urdf")
        body_id = p.loadURDF(temp_urdf, useFixedBase=not args.dynamic, flags=p.URDF_USE_INERTIA_FROM_FILE)
        kin_body_id = p.loadURDF(temp_urdf, useFixedBase=True, flags=p.URDF_USE_INERTIA_FROM_FILE)
        disable_body_collision_and_visual(p, kin_body_id)

        joint_name_to_index, link_name_to_index, joint_limits, _ = pybullet_maps(p, body_id)
        kin_joint_name_to_index, kin_link_name_to_index, _, _ = pybullet_maps(p, kin_body_id)
        reset_initial_pose(p, body_id, joint_name_to_index, link_name_to_index, robot_config, base_height)
        apply_zero_default_motors(p, body_id)

        rail_controller = RailLockController.from_config_dicts(robot_config, rail_config)
        joint_pd = JointPDController.from_config_dicts(
            robot_config,
            controller_config,
            excluded_joints=rail_controller.rail_joint_names,
        )
        rail_controller.validate_leg_joint_exclusion(leg_joint_names(robot_config))

        kin = PyBulletLegKinematics(
            p,
            kin_body_id,
            robot_config,
            kin_joint_name_to_index,
            kin_link_name_to_index,
        )
        kin.set_nominal_pose()
        ik = NumericalIK.from_robot_config(robot_config, kin.foot_position, tolerance=0.005)
        safety_checker = SafetyChecker.from_config_dict(controller_config)

        joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
        rail_controller.initialize({name: joint_state[name] for name in rail_controller.rail_joint_names})
        joint_pd.reset_targets(joint_state)
        q_des_all = default_stand_targets(robot_config)
        last_good_q = {
            leg: tuple(q_des_all[joint_name] for joint_name in leg_joint_names(robot_config)[leg])
            for leg in LEG_ORDER
        }
        pd_torque_limits = {name: cfg.torque_limit for name, cfg in joint_pd.joint_configs.items()}

        headers = [
            "time",
            "leg",
            "target_foot_pos_base",
            "actual_foot_pos_base",
            "target_foot_pos_world",
            "actual_foot_pos_world",
            "ik_error",
            "ik_success",
            "ik_iterations",
            "q_des_leg",
            "rail_error",
            "safety_status",
        ]

        max_error_by_leg = {leg: 0.0 for leg in tested_legs}
        success = True
        global_step = 0
        with log_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for leg_name in tested_legs:
                print(f"[INFO] Testing {leg_name} IK for {args.duration_per_leg:.1f}s")
                foot_link = str(((robot_config.get("legs") or {}).get(leg_name, {}) or {}).get("foot_link"))
                start_world = p.getLinkState(body_id, link_name_to_index[foot_link])[0]
                start_base = world_to_semantic_base(p, robot_config, body_id, start_world)
                if args.gui:
                    apply_leg_visuals(p, body_id, link_name_to_index, leg_name)
                    p.removeAllUserDebugItems()
                    top_world = semantic_base_to_world(
                        p,
                        robot_config,
                        body_id,
                        (start_base[0], start_base[1], start_base[2] + step_height),
                    )
                    p.addUserDebugLine(start_world, top_world, [1.0, 1.0, 0.0], lineWidth=4, lifeTime=0.0)
                    p.addUserDebugText(
                        f"Testing {leg_name} | slow vertical lift {step_height * 100.0:.1f} cm",
                        [0.18, -0.18, 0.32],
                        textColorRGB=[1.0, 0.9, 0.1],
                        textSize=1.6,
                        lifeTime=0.0,
                    )
                    p.addUserDebugText(
                        "Red = target foot, Green = actual foot, Yellow line = lift range",
                        [0.18, -0.18, 0.28],
                        textColorRGB=[1.0, 1.0, 1.0],
                        textSize=1.35,
                        lifeTime=0.0,
                    )
                    camera_yaw = 30.0 if leg_name in ("FL", "RL") else 145.0
                    camera_pitch = -28.0
                    p.resetDebugVisualizerCamera(
                        cameraDistance=0.95,
                        cameraYaw=camera_yaw,
                        cameraPitch=camera_pitch,
                        cameraTargetPosition=start_world,
                    )
                    add_marker(p, start_world, [0.2, 0.8, 1.0], f"{leg_name} start", size=0.055, life_time=0.0)
                    add_marker(p, top_world, [1.0, 0.85, 0.0], f"{leg_name} top", size=0.055, life_time=0.0)

                steps = int(float(args.duration_per_leg) / dt)
                previous_target_world = start_world
                for step in range(steps):
                    t = global_step * dt
                    local_t = step * dt
                    joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
                    phase = min(1.0, local_t / float(args.duration_per_leg))
                    lift = step_height * math.sin(math.pi * phase) ** 2
                    target_base = (start_base[0], start_base[1], start_base[2] + lift)
                    q_current_leg = tuple(joint_state[joint_name][0] for joint_name in leg_joint_names(robot_config)[leg_name])
                    result = ik.solve(
                        leg_name,
                        target_base,
                        last_good_q[leg_name],
                        max_iters=30,
                        damping=1e-3,
                        step_limit=0.05,
                    )
                    if result.success or result.error_norm <= 0.02:
                        last_good_q[leg_name] = result.q
                    else:
                        print(
                            f"[WARN] {leg_name} IK not converged at t={local_t:.3f}s: "
                            f"error={result.error_norm:.4f}, keeping previous q_des"
                        )
                    for joint_name, q in zip(leg_joint_names(robot_config)[leg_name], last_good_q[leg_name]):
                        q_des_all[joint_name] = q
                    for other_leg in LEG_ORDER:
                        if other_leg == leg_name:
                            continue
                        for joint_name in leg_joint_names(robot_config)[other_leg]:
                            q_des_all[joint_name] = default_stand_targets(robot_config)[joint_name]

                    if args.dynamic:
                        pd_commands = joint_pd.compute(joint_state, q_des_all)
                        torques = {name: command.tau for name, command in pd_commands.items()}
                        for command in pd_commands.values():
                            p.setJointMotorControl2(
                                body_id,
                                joint_name_to_index[command.joint_name],
                                p.TORQUE_CONTROL,
                                force=command.tau,
                            )

                        rail_commands = rail_controller.compute(
                            {name: joint_state[name] for name in rail_controller.rail_joint_names}
                        )
                        for command in rail_commands.values():
                            p.setJointMotorControl2(
                                body_id,
                                joint_name_to_index[command.joint_name],
                                p.TORQUE_CONTROL,
                                force=command.force,
                            )
                        p.stepSimulation()
                    else:
                        for joint_name, q in q_des_all.items():
                            p.resetJointState(body_id, joint_name_to_index[joint_name], float(q), 0.0)
                        for rail_name in rail_controller.rail_joint_names:
                            p.resetJointState(body_id, joint_name_to_index[rail_name], 0.0, 0.0)
                        joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
                        rail_commands = rail_controller.compute(
                            {name: joint_state[name] for name in rail_controller.rail_joint_names}
                        )
                        torques = {name: 0.0 for name in joint_pd.joint_names}
                        p.stepSimulation()

                    if args.gui and bool((controller_config.get("controller") or {}).get("gui_sleep", True)):
                        time.sleep(dt)

                    joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
                    actual_world = p.getLinkState(body_id, link_name_to_index[foot_link])[0]
                    actual_base = world_to_semantic_base(p, robot_config, body_id, actual_world)
                    target_world = semantic_base_to_world(p, robot_config, body_id, target_base)
                    track_error = math.dist(actual_base, target_base)
                    max_error_by_leg[leg_name] = max(max_error_by_leg[leg_name], track_error, result.error_norm)
                    last_target_world = previous_target_world
                    target_jump = math.dist(target_world, last_target_world)
                    previous_target_world = target_world

                    base_pos, _ = p.getBasePositionAndOrientation(body_id)
                    base_rpy = semantic_base_rpy(p, robot_config, body_id)
                    safety = safety_checker.check(
                        base_position=base_pos,
                        base_rpy=base_rpy,
                        joint_state={
                            name: joint_state[name]
                            for name in set(joint_pd.joint_names) | set(rail_controller.rail_joint_names)
                        },
                        joint_limits=joint_limits,
                        torques=torques,
                        torque_limits=pd_torque_limits,
                        rail_errors={name: command.error for name, command in rail_commands.items()},
                        ik_success={leg_name: result.success or result.error_norm <= 0.02},
                        foot_target_jumps={leg_name: target_jump},
                    )
                    safety_status = "OK" if safety.ok else "STOP"
                    if not safety.ok:
                        print(f"[SAFETY STOP] {leg_name} t={local_t:.3f}: {'; '.join(safety.reasons)}")
                        success = False

                    if args.gui and step % 5 == 0:
                        add_marker(p, target_world, [1, 0, 0], f"{leg_name} target", size=0.05, life_time=0.9)
                        add_marker(p, actual_world, [0, 1, 0], f"{leg_name} actual", size=0.05, life_time=0.9)
                        p.addUserDebugLine(last_target_world, target_world, [1, 0.4, 0], lineWidth=4, lifeTime=4.0)
                        p.addUserDebugLine(actual_world, target_world, [1.0, 0.0, 1.0], lineWidth=2, lifeTime=0.9)
                        p.addUserDebugText(
                            f"{leg_name} phase={phase:.2f} lift={lift * 100.0:.1f} cm err={track_error * 100.0:.1f} cm",
                            [0.18, -0.18, 0.24],
                            textColorRGB=[0.9, 1.0, 0.9],
                            textSize=1.25,
                            lifeTime=0.25,
                        )

                    if global_step % 10 == 0:
                        writer.writerow(
                            {
                                "time": f"{t:.6f}",
                                "leg": leg_name,
                                "target_foot_pos_base": row_json({"x": target_base[0], "y": target_base[1], "z": target_base[2]}),
                                "actual_foot_pos_base": row_json({"x": actual_base[0], "y": actual_base[1], "z": actual_base[2]}),
                                "target_foot_pos_world": row_json({"x": target_world[0], "y": target_world[1], "z": target_world[2]}),
                                "actual_foot_pos_world": row_json({"x": actual_world[0], "y": actual_world[1], "z": actual_world[2]}),
                                "ik_error": f"{result.error_norm:.6f}",
                                "ik_success": str(result.success),
                                "ik_iterations": str(result.iterations),
                                "q_des_leg": row_json({name: q for name, q in zip(leg_joint_names(robot_config)[leg_name], last_good_q[leg_name])}),
                                "rail_error": row_json({name: command.error for name, command in rail_commands.items()}),
                                "safety_status": safety_status,
                            }
                        )
                    global_step += 1
                    if not safety.ok:
                        break
                if not success:
                    break

        print(f"[INFO] IK log: {log_path}")
        for leg_name, error in max_error_by_leg.items():
            print(f"[INFO] {leg_name} max IK/track error: {error:.4f} m")
            if error > 0.02:
                success = False
        print("[PASS] Single-leg IK test passed." if success else "[FAIL] Single-leg IK test did not meet criteria.")
        return 0 if success else 1
    finally:
        p.disconnect(physics_client)
        try:
            os.unlink(temp_urdf)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
