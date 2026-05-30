#!/usr/bin/env python3
"""Stage 2 stand test: rail locked, legs hold default_stand_q.

No gait scheduling, no foot trajectory, no Raibert planner, no WBC, no MPC.
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
from utils.contact_filter import enable_foot_only_ground_contact, ground_contact_link_names


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
            root = ET.parse(package_xml).getroot()
            package_name = (root.findtext("name") or package_xml.parent.name).strip()
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


def semantic_base_rpy(
    p: Any,
    robot_config: Mapping[str, Any],
    world_base_quat: Sequence[float],
) -> Tuple[float, float, float]:
    """Return base roll/pitch/yaw relative to the configured PyBullet alignment."""
    align_quat = pybullet_base_alignment_quat(p, robot_config)
    _, inv_align = p.invertTransform([0.0, 0.0, 0.0], align_quat)
    _, relative_quat = p.multiplyTransforms(
        [0.0, 0.0, 0.0],
        inv_align,
        [0.0, 0.0, 0.0],
        world_base_quat,
    )
    return tuple(p.getEulerFromQuaternion(relative_quat))


def leg_joint_names(robot_config: Mapping[str, Any]) -> Dict[str, Sequence[str]]:
    return {
        leg: [str(name) for name in ((robot_config.get("legs") or {}).get(leg, {}) or {}).get("joint_names", [])]
        for leg in LEG_ORDER
    }


def default_stand_targets(
    robot_config: Mapping[str, Any],
    pose_key: str = "default_stand_q",
) -> Dict[str, float]:
    targets: Dict[str, float] = {}
    for leg in LEG_ORDER:
        leg_cfg = ((robot_config.get("legs") or {}).get(leg, {}) or {})
        names = [str(name) for name in leg_cfg.get("joint_names", [])]
        q = leg_cfg.get(pose_key, leg_cfg.get("default_stand_q", [])) or []
        for index, joint_name in enumerate(names):
            targets[joint_name] = float(q[index]) if index < len(q) else 0.0
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
    state = {}
    for joint_name, joint_index in joint_name_to_index.items():
        q, dq, *_ = p.getJointState(body_id, joint_index)
        state[joint_name] = (float(q), float(dq))
    return state


def pybullet_maps(p: Any, body_id: int) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, Tuple[float, float]], Dict[str, float]]:
    joint_name_to_index: Dict[str, int] = {}
    link_name_to_index: Dict[str, int] = {}
    joint_limits: Dict[str, Tuple[float, float]] = {}
    torque_limits: Dict[str, float] = {}
    for joint_index in range(p.getNumJoints(body_id)):
        info = p.getJointInfo(body_id, joint_index)
        joint_name = info[1].decode("utf-8")
        link_name = info[12].decode("utf-8")
        joint_type = info[2]
        joint_name_to_index[joint_name] = joint_index
        link_name_to_index[link_name] = joint_index
        if joint_type != p.JOINT_FIXED:
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
    pose_key: str = "default_stand_q",
) -> None:
    base_quat = pybullet_base_alignment_quat(p, robot_config)
    p.resetBasePositionAndOrientation(body_id, [0.0, 0.0, base_height], base_quat)
    p.resetBaseVelocity(body_id, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    for rail_name, rail_q in configured_rail_positions(robot_config).items():
        if rail_name in joint_name_to_index:
            p.resetJointState(body_id, joint_name_to_index[rail_name], rail_q, 0.0)

    for joint_name, q in default_stand_targets(robot_config, pose_key=pose_key).items():
        if joint_name in joint_name_to_index:
            p.resetJointState(body_id, joint_name_to_index[joint_name], q, 0.0)

    foot_links = [
        str(((robot_config.get("legs") or {}).get(leg, {}) or {}).get("foot_link", ""))
        for leg in LEG_ORDER
    ]
    foot_z = []
    p.performCollisionDetection()
    for foot_link in foot_links:
        if foot_link in link_name_to_index:
            foot_z.append(p.getLinkState(body_id, link_name_to_index[foot_link])[0][2])
    if foot_z:
        target_foot_center_z = 0.014
        shift = target_foot_center_z - min(foot_z)
        base_pos, base_quat = p.getBasePositionAndOrientation(body_id)
        p.resetBasePositionAndOrientation(
            body_id,
            [base_pos[0], base_pos[1], base_pos[2] + shift],
            base_quat,
        )
        p.resetBaseVelocity(body_id, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])


def apply_zero_default_motors(p: Any, body_id: int) -> None:
    for joint_index in range(p.getNumJoints(body_id)):
        info = p.getJointInfo(body_id, joint_index)
        if info[2] != p.JOINT_FIXED:
            p.setJointMotorControl2(body_id, joint_index, p.VELOCITY_CONTROL, targetVelocity=0.0, force=0.0)


def actuator_mode(controller_config: Mapping[str, Any]) -> str:
    return str((controller_config.get("controller") or {}).get("actuator_mode", "torque_pd"))


def apply_leg_actuators(
    p: Any,
    body_id: int,
    joint_name_to_index: Mapping[str, int],
    pd_commands: Mapping[str, Any],
    joint_pd: JointPDController,
    controller_config: Mapping[str, Any],
) -> None:
    controller = controller_config.get("controller") or {}
    if actuator_mode(controller_config) == "pybullet_position":
        position_gain = float(controller.get("pybullet_position_gain", 0.35))
        velocity_gain = float(controller.get("pybullet_velocity_gain", 0.08))
        for command in pd_commands.values():
            p.setJointMotorControl2(
                body_id,
                joint_name_to_index[command.joint_name],
                p.POSITION_CONTROL,
                targetPosition=command.q_des,
                targetVelocity=command.dq_des,
                positionGain=position_gain,
                velocityGain=velocity_gain,
                force=joint_pd.joint_configs[command.joint_name].torque_limit,
            )
        return

    for command in pd_commands.values():
        p.setJointMotorControl2(
            body_id,
            joint_name_to_index[command.joint_name],
            p.TORQUE_CONTROL,
            force=command.tau,
        )


def apply_rail_actuators(
    p: Any,
    body_id: int,
    joint_name_to_index: Mapping[str, int],
    rail_commands: Mapping[str, Any],
    rail_controller: RailLockController,
    controller_config: Mapping[str, Any],
) -> None:
    controller = controller_config.get("controller") or {}
    if actuator_mode(controller_config) == "pybullet_position":
        position_gain = float(controller.get("rail_position_gain", 0.8))
        velocity_gain = float(controller.get("rail_velocity_gain", 0.2))
        for command in rail_commands.values():
            p.setJointMotorControl2(
                body_id,
                joint_name_to_index[command.joint_name],
                p.POSITION_CONTROL,
                targetPosition=command.q0,
                targetVelocity=0.0,
                positionGain=position_gain,
                velocityGain=velocity_gain,
                force=rail_controller.config.max_force,
            )
        return

    for command in rail_commands.values():
        p.setJointMotorControl2(
            body_id,
            joint_name_to_index[command.joint_name],
            p.TORQUE_CONTROL,
            force=command.force,
        )


def row_json(values: Mapping[str, Any]) -> str:
    return json.dumps(values, sort_keys=True, separators=(",", ":"))


def hold_gui_after_safety_stop(p: Any, physics_client: int, body_id: int, plane_id: int) -> None:
    print("[INFO] GUI hold after safety stop. Press Ctrl+C in this terminal to close.")
    try:
        while p.isConnected(physics_client):
            contact_names = sorted(ground_contact_link_names(p, body_id, plane_id))
            p.addUserDebugText(
                "SAFETY STOP - inspect pose, then press Ctrl+C",
                [0.15, -0.16, 0.38],
                textColorRGB=[1.0, 0.1, 0.1],
                textSize=1.25,
                lifeTime=0.3,
            )
            p.addUserDebugText(
                "Ground contacts: " + (", ".join(contact_names) if contact_names else "none"),
                [0.15, -0.16, 0.34],
                textColorRGB=[0.65, 1.0, 1.0],
                textSize=1.0,
                lifeTime=0.3,
            )
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass


def recover_to_default_stand_posture(
    p: Any,
    body_id: int,
    joint_name_to_index: Mapping[str, int],
    link_name_to_index: Mapping[str, int],
    robot_config: Mapping[str, Any],
    controller_config: Mapping[str, Any],
    rail_controller: RailLockController,
) -> None:
    default_q = default_stand_targets(robot_config)
    base_height = float((controller_config.get("controller") or {}).get("initial_base_height", 0.42))
    reset_initial_pose(p, body_id, joint_name_to_index, link_name_to_index, robot_config, base_height)
    p.resetBaseVelocity(body_id, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    for _ in range(300):
        for joint_name, q_des in default_q.items():
            p.setJointMotorControl2(
                body_id,
                joint_name_to_index[joint_name],
                p.POSITION_CONTROL,
                targetPosition=q_des,
                targetVelocity=0.0,
                positionGain=0.35,
                velocityGain=0.08,
                force=80.0,
            )
        for rail_name, rail_q in rail_controller.lock_positions.items():
            p.setJointMotorControl2(
                body_id,
                joint_name_to_index[rail_name],
                p.POSITION_CONTROL,
                targetPosition=rail_q,
                targetVelocity=0.0,
                positionGain=0.8,
                velocityGain=0.2,
                force=rail_controller.config.max_force,
            )
        p.stepSimulation()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(PROJECT_ROOT / "config" / "robot_config.yaml"))
    parser.add_argument("--rail-config", default=str(PROJECT_ROOT / "config" / "rail_config.yaml"))
    parser.add_argument("--controller-config", default=str(PROJECT_ROOT / "config" / "controller_config.yaml"))
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument(
        "--no-hold-on-stop",
        action="store_true",
        help="Do not keep the PyBullet GUI open after a safety stop.",
    )
    args = parser.parse_args()

    try:
        import pybullet as p
        import pybullet_data
    except Exception as exc:
        print(f"[ERROR] pybullet is required for stand_test: {exc}")
        return 2

    robot_config_path = Path(args.config).resolve()
    rail_config_path = Path(args.rail_config).resolve()
    controller_config_path = Path(args.controller_config).resolve()
    robot_config = load_yaml(robot_config_path)
    rail_config = load_yaml(rail_config_path)
    controller_config = load_yaml(controller_config_path)
    config_dir = robot_config_path.parent

    dt = float((controller_config.get("controller") or {}).get("control_dt", 0.002))
    duration = float(args.duration or (controller_config.get("controller") or {}).get("duration", 10.0))
    transition_time = float((controller_config.get("controller") or {}).get("transition_time", 1.5))
    base_height = float((controller_config.get("controller") or {}).get("initial_base_height", 0.42))

    model_path = resolve_path(robot_config["robot"]["model_path"], config_dir)
    urdf_text = expand_model_to_urdf(model_path, robot_config, config_dir)
    urdf_text = replace_package_urls(urdf_text, local_package_map(WORKSPACE_ROOT))

    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "stand_test_log.csv"
    safety_path = logs_dir / "safety_events.log"

    with tempfile.NamedTemporaryFile("w", suffix=".urdf", delete=False, encoding="utf-8") as f:
        f.write(urdf_text)
        temp_urdf = f.name

    physics_client = p.connect(p.GUI if args.gui else p.DIRECT)
    try:
        if args.gui:
            p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0.0, 0.0, -9.81)
        p.setTimeStep(dt)
        p.setPhysicsEngineParameter(numSolverIterations=120, numSubSteps=2)
        plane_id = p.loadURDF("plane.urdf")
        body_id = p.loadURDF(temp_urdf, useFixedBase=False, flags=p.URDF_USE_INERTIA_FROM_FILE)

        joint_name_to_index, link_name_to_index, joint_limits, pybullet_torque_limits = pybullet_maps(p, body_id)
        enable_foot_only_ground_contact(
            p,
            body_id,
            plane_id,
            link_name_to_index,
            robot_config,
            keep_base_collision=True,
        )
        reset_initial_pose(p, body_id, joint_name_to_index, link_name_to_index, robot_config, base_height)
        apply_zero_default_motors(p, body_id)

        rail_controller = RailLockController.from_config_dicts(robot_config, rail_config)
        joint_pd = JointPDController.from_config_dicts(
            robot_config,
            controller_config,
            excluded_joints=rail_controller.rail_joint_names,
        )
        rail_controller.validate_leg_joint_exclusion(leg_joint_names(robot_config))

        joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
        rail_state = {name: joint_state[name] for name in rail_controller.rail_joint_names}
        rail_controller.initialize(rail_state)
        joint_pd.reset_targets(joint_state)

        safety_checker = SafetyChecker.from_config_dict(controller_config)
        desired_q_final = default_stand_targets(robot_config)
        desired_q_start = {name: joint_state[name][0] for name in joint_pd.joint_names}
        pd_torque_limits = {
            name: cfg.torque_limit
            for name, cfg in joint_pd.joint_configs.items()
        }

        headers = [
            "time",
            "base_position",
            "base_orientation_rpy",
            "base_linear_velocity",
            "base_angular_velocity",
            "each_joint_q",
            "each_joint_q_des",
            "each_joint_tau",
            "rail_q",
            "rail_error",
            "rail_force",
            "safety_status",
        ]

        max_abs_roll = 0.0
        max_abs_pitch = 0.0
        min_base_z = math.inf
        safety_status = "OK"

        with log_path.open("w", newline="", encoding="utf-8") as csv_file, safety_path.open(
            "w", encoding="utf-8"
        ) as safety_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            steps = int(duration / dt)
            for step in range(steps):
                t = step * dt
                joint_state = joint_dict_from_pybullet(p, body_id, joint_name_to_index)
                alpha = 1.0 if transition_time <= 0.0 else min(1.0, t / transition_time)
                q_des = {
                    name: desired_q_start[name] + alpha * (desired_q_final[name] - desired_q_start[name])
                    for name in joint_pd.joint_names
                }

                pd_commands = joint_pd.compute(joint_state, q_des)

                rail_state = {name: joint_state[name] for name in rail_controller.rail_joint_names}
                rail_commands = rail_controller.compute(rail_state)
                apply_leg_actuators(p, body_id, joint_name_to_index, pd_commands, joint_pd, controller_config)
                apply_rail_actuators(p, body_id, joint_name_to_index, rail_commands, rail_controller, controller_config)

                base_pos, base_quat = p.getBasePositionAndOrientation(body_id)
                base_rpy = semantic_base_rpy(p, robot_config, base_quat)
                base_lin_vel, base_ang_vel = p.getBaseVelocity(body_id)
                max_abs_roll = max(max_abs_roll, abs(base_rpy[0]))
                max_abs_pitch = max(max_abs_pitch, abs(base_rpy[1]))
                min_base_z = min(min_base_z, base_pos[2])

                torques = {name: command.tau for name, command in pd_commands.items()}
                rail_errors = {name: command.error for name, command in rail_commands.items()}
                result = safety_checker.check(
                    base_position=base_pos,
                    base_rpy=base_rpy,
                    joint_state={name: joint_state[name] for name in set(joint_pd.joint_names) | set(rail_controller.rail_joint_names)},
                    joint_limits=joint_limits,
                    torques=torques,
                    torque_limits=pd_torque_limits,
                    rail_errors=rail_errors,
                )
                safety_status = "OK" if result.ok else "STOP"
                if result.warnings and step % max(1, int(0.5 / dt)) == 0:
                    print("[WARN] " + "; ".join(result.warnings))
                if not result.ok:
                    reason_text = "; ".join(result.reasons)
                    print(f"[SAFETY STOP] t={t:.3f}: {reason_text}")
                    safety_file.write(f"t={t:.6f}: {reason_text}\n")

                writer.writerow(
                    {
                        "time": f"{t:.6f}",
                        "base_position": row_json({"x": base_pos[0], "y": base_pos[1], "z": base_pos[2]}),
                        "base_orientation_rpy": row_json({"roll": base_rpy[0], "pitch": base_rpy[1], "yaw": base_rpy[2]}),
                        "base_linear_velocity": row_json({"x": base_lin_vel[0], "y": base_lin_vel[1], "z": base_lin_vel[2]}),
                        "base_angular_velocity": row_json({"x": base_ang_vel[0], "y": base_ang_vel[1], "z": base_ang_vel[2]}),
                        "each_joint_q": row_json({name: joint_state[name][0] for name in joint_pd.joint_names}),
                        "each_joint_q_des": row_json({name: command.q_des for name, command in pd_commands.items()}),
                        "each_joint_tau": row_json(torques),
                        "rail_q": row_json({name: command.q for name, command in rail_commands.items()}),
                        "rail_error": row_json(rail_errors),
                        "rail_force": row_json({name: command.force for name, command in rail_commands.items()}),
                        "safety_status": safety_status,
                    }
                )

                if not result.ok:
                    break

                p.stepSimulation()
                if args.gui and bool((controller_config.get("controller") or {}).get("gui_sleep", True)):
                    time.sleep(dt)

        stand_accept = controller_config.get("safety", {}) or {}
        roll_limit = math.radians(float(stand_accept.get("stand_accept_roll_deg", 10.0)))
        pitch_limit = math.radians(float(stand_accept.get("stand_accept_pitch_deg", 10.0)))
        rail_error_max = max(
            abs(command.error)
            for command in rail_controller.last_commands.values()
        ) if rail_controller.last_commands else 0.0
        passed = (
            safety_status == "OK"
            and max_abs_roll < roll_limit
            and max_abs_pitch < pitch_limit
            and min_base_z >= float((controller_config.get("safety") or {}).get("min_base_height", 0.12))
            and rail_error_max <= float((rail_config.get("rail_lock") or {}).get("warning_error_threshold_m", 0.002))
        )

        print(f"[INFO] Stand log: {log_path}")
        print(f"[INFO] Max roll: {math.degrees(max_abs_roll):.2f} deg")
        print(f"[INFO] Max pitch: {math.degrees(max_abs_pitch):.2f} deg")
        print(f"[INFO] Min base height: {min_base_z:.3f} m")
        print(f"[INFO] Max rail error: {rail_error_max:.6f} m")
        print("[PASS] Stand test passed." if passed else "[FAIL] Stand test did not meet acceptance criteria.")
        if args.gui and not passed and not args.no_hold_on_stop:
            recover_to_default_stand_posture(
                p,
                body_id,
                joint_name_to_index,
                link_name_to_index,
                robot_config,
                controller_config,
                rail_controller,
            )
            hold_gui_after_safety_stop(p, physics_client, body_id, plane_id)
        return 0 if passed else 1
    finally:
        p.disconnect(physics_client)
        try:
            os.unlink(temp_urdf)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
