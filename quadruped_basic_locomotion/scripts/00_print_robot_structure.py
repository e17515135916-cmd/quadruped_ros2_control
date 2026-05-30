#!/usr/bin/env python3
"""Print and report robot joint/link structure before any gait work.

This diagnostic intentionally stops at structure inspection.  It validates that
leg joints are exactly three revolute joints per leg and that prismatic rails are
excluded from the leg maps.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import xml.etree.ElementTree as ET

import yaml

try:
    import xacro
except Exception:  # pragma: no cover - reported at runtime
    xacro = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.rail_lock_controller import RailLockController


REVOLUTE_TYPES = {"revolute", "continuous"}
RAIL_NAME_RE = re.compile(r"(rail|slider|slide|linear|prismatic)", re.IGNORECASE)


def resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        candidate = (base_dir / path).resolve()
        if candidate.exists():
            return candidate
        candidate = (WORKSPACE_ROOT / path).resolve()
        if candidate.exists():
            return candidate
    return path.resolve()


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def local_package_map(workspace_root: Path) -> Dict[str, Path]:
    package_map: Dict[str, Path] = {}
    for package_xml in workspace_root.glob("src/*/package.xml"):
        package_dir = package_xml.parent
        try:
            root = ET.parse(package_xml).getroot()
            name = (root.findtext("name") or package_dir.name).strip()
        except ET.ParseError:
            name = package_dir.name
        package_map[name] = package_dir.resolve()
    return package_map


def expand_model_to_urdf(model_path: Path, robot_config: Mapping[str, Any], config_dir: Path) -> str:
    suffix = model_path.suffix.lower()
    if suffix == ".xacro":
        if xacro is None:
            raise RuntimeError("xacro is required to expand .xacro files.")
        raw_args = robot_config.get("robot", {}).get("xacro_args", {}) or {}
        mappings = {
            key: str(resolve_path(str(value), config_dir))
            for key, value in raw_args.items()
        }
        doc = xacro.process_file(str(model_path), mappings=mappings)
        return doc.toprettyxml(indent="  ")

    with model_path.open("r", encoding="utf-8") as f:
        return f.read()


def replace_package_urls(urdf_text: str, package_map: Mapping[str, Path]) -> str:
    result = urdf_text
    for package_name, package_dir in package_map.items():
        result = result.replace(f"package://{package_name}", str(package_dir))
    return result


def parse_float_list(text: Optional[str], default: Sequence[float]) -> List[float]:
    if not text:
        return list(default)
    try:
        return [float(part) for part in text.split()]
    except ValueError:
        return list(default)


def parse_limit(joint_el: ET.Element) -> Dict[str, Optional[float]]:
    limit_el = joint_el.find("limit")
    out = {"lower": None, "upper": None, "effort": None, "velocity": None}
    if limit_el is None:
        return out
    for key in out:
        value = limit_el.attrib.get(key)
        out[key] = float(value) if value is not None else None
    return out


def parse_joints(urdf_text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    root = ET.fromstring(urdf_text)
    links = [link.attrib["name"] for link in root.findall("link") if "name" in link.attrib]
    joints = []
    motion_index = 0
    for joint_index, joint_el in enumerate(root.findall("joint")):
        name = joint_el.attrib.get("name", "")
        joint_type = joint_el.attrib.get("type", "unknown")
        parent_el = joint_el.find("parent")
        child_el = joint_el.find("child")
        axis_el = joint_el.find("axis")
        origin_el = joint_el.find("origin")
        limits = parse_limit(joint_el)
        joints.append(
            {
                "joint_index": joint_index,
                "motion_index": None if joint_type == "fixed" else motion_index,
                "name": name,
                "type": joint_type,
                "parent": parent_el.attrib.get("link", "") if parent_el is not None else "",
                "child": child_el.attrib.get("link", "") if child_el is not None else "",
                "axis": parse_float_list(axis_el.attrib.get("xyz") if axis_el is not None else None, [0, 0, 0]),
                "origin_xyz": parse_float_list(origin_el.attrib.get("xyz") if origin_el is not None else None, [0, 0, 0]),
                "origin_rpy": parse_float_list(origin_el.attrib.get("rpy") if origin_el is not None else None, [0, 0, 0]),
                **limits,
            }
        )
        if joint_type != "fixed":
            motion_index += 1
    return links, joints


def configured_rail_names(robot_config: Mapping[str, Any]) -> List[str]:
    rail = robot_config.get("rail", {}) or {}
    names: List[str] = []
    raw_names = rail.get("joint_names", []) or []
    if isinstance(raw_names, str):
        raw_names = [raw_names]
    names.extend(str(name) for name in raw_names if str(name).strip())
    single = str(rail.get("joint_name", "") or "").strip()
    if single and single not in names:
        names.append(single)
    return names


def detect_rail_joints(joints: Sequence[Mapping[str, Any]], robot_config: Mapping[str, Any]) -> List[str]:
    configured = configured_rail_names(robot_config)
    existing = {joint["name"] for joint in joints}
    if configured and all(name in existing for name in configured):
        return configured

    name_matches = [
        joint["name"]
        for joint in joints
        if joint["type"] == "prismatic" and RAIL_NAME_RE.search(joint["name"])
    ]
    if name_matches:
        return name_matches
    return [joint["name"] for joint in joints if joint["type"] == "prismatic"]


def leg_config_joint_names(robot_config: Mapping[str, Any]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for leg in ("FL", "FR", "RL", "RR"):
        raw = (((robot_config.get("legs") or {}).get(leg) or {}).get("joint_names") or [])
        out[leg] = [str(name) for name in raw]
    return out


def leg_config_foot_links(robot_config: Mapping[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for leg in ("FL", "FR", "RL", "RR"):
        out[leg] = str((((robot_config.get("legs") or {}).get(leg) or {}).get("foot_link") or ""))
    return out


def sorted_leg_candidates(names: Iterable[str]) -> List[str]:
    role_order = [
        ("coxa", "hip_roll", "haa", "joint_0"),
        ("femur", "hip_pitch", "hfe", "joint_1"),
        ("tibia", "knee", "kfe", "joint_2"),
    ]

    def score(name: str) -> Tuple[int, str]:
        lowered = name.lower()
        for index, aliases in enumerate(role_order):
            if any(alias in lowered for alias in aliases):
                return index, lowered
        return 99, lowered

    return sorted(names, key=score)


def auto_detect_leg_mapping(
    joints: Sequence[Mapping[str, Any]], links: Sequence[str], rail_names: Sequence[str]
) -> Tuple[Dict[str, List[str]], Dict[str, str], List[str]]:
    patterns = {
        "FL": ("fl", "front_left", "left_front", "lf"),
        "FR": ("fr", "front_right", "right_front", "rf"),
        "RL": ("rl", "rear_left", "left_rear", "lh"),
        "RR": ("rr", "rear_right", "right_rear", "rh"),
    }
    warnings: List[str] = []
    rail_set = set(rail_names)
    revolute_names = [
        joint["name"]
        for joint in joints
        if joint["type"] in REVOLUTE_TYPES and joint["name"] not in rail_set
    ]
    mapping: Dict[str, List[str]] = {}
    foot_links: Dict[str, str] = {}
    for leg, prefixes in patterns.items():
        candidates = []
        for joint_name in revolute_names:
            lowered = joint_name.lower()
            if any(lowered.startswith(prefix + "_") or lowered.startswith(prefix) for prefix in prefixes):
                candidates.append(joint_name)
        mapping[leg] = sorted_leg_candidates(candidates)

        foot_candidates = []
        for link in links:
            lowered = link.lower()
            if "foot" in lowered and any(lowered.startswith(prefix + "_") or lowered.startswith(prefix) for prefix in prefixes):
                foot_candidates.append(link)
        foot_links[leg] = sorted(foot_candidates)[0] if len(foot_candidates) == 1 else ""
        if len(foot_candidates) != 1:
            warnings.append(f"{leg}: foot_link is ambiguous; configure it manually.")
    return mapping, foot_links, warnings


def validate_mapping(
    leg_map: Mapping[str, Sequence[str]],
    foot_links: Mapping[str, str],
    joints_by_name: Mapping[str, Mapping[str, Any]],
    links: Sequence[str],
    rail_names: Sequence[str],
) -> Tuple[bool, List[str]]:
    ok = True
    messages: List[str] = []
    rail_set = set(rail_names)
    used: List[str] = []

    for leg in ("FL", "FR", "RL", "RR"):
        names = list(leg_map.get(leg, []))
        if len(names) != 3:
            ok = False
            messages.append(f"{leg}: expected exactly 3 revolute joints, got {len(names)}: {names}")
            continue
        for name in names:
            used.append(name)
            if name in rail_set:
                ok = False
                messages.append(f"{leg}: rail joint {name} is incorrectly listed as a leg joint.")
            joint = joints_by_name.get(name)
            if joint is None:
                ok = False
                messages.append(f"{leg}: joint {name} is not present in the model.")
            elif joint["type"] not in REVOLUTE_TYPES:
                ok = False
                messages.append(f"{leg}: joint {name} type is {joint['type']}, expected revolute/continuous.")
        foot_link = foot_links.get(leg, "")
        if not foot_link:
            ok = False
            messages.append(f"{leg}: missing foot_link.")
        elif foot_link not in links:
            ok = False
            messages.append(f"{leg}: foot_link {foot_link} is not present in the model.")

    duplicates = sorted({name for name in used if used.count(name) > 1})
    if duplicates:
        ok = False
        messages.append(f"Leg joint names are duplicated across legs: {duplicates}")

    return ok, messages


def initial_states(robot_config: Mapping[str, Any], rail_names: Sequence[str]) -> Dict[str, Tuple[float, float]]:
    states: Dict[str, Tuple[float, float]] = {}
    rail_cfg = robot_config.get("rail", {}) or {}
    rail_lock_source = str(rail_cfg.get("lock_position_source", "initial"))
    rail_lock_position = float(rail_cfg.get("lock_position", 0.0) or 0.0)
    for rail_name in rail_names:
        states[rail_name] = (rail_lock_position if rail_lock_source == "configured" else 0.0, 0.0)
    for leg_cfg in (robot_config.get("legs") or {}).values():
        joint_names = leg_cfg.get("joint_names", []) or []
        default_q = leg_cfg.get("default_stand_q", []) or []
        for index, joint_name in enumerate(joint_names):
            q = float(default_q[index]) if index < len(default_q) else 0.0
            states[str(joint_name)] = (q, 0.0)
    return states


def classify_joints(
    joints: Sequence[Mapping[str, Any]], leg_map: Mapping[str, Sequence[str]], rail_names: Sequence[str]
) -> Dict[str, List[str]]:
    rail_set = set(rail_names)
    leg_set = {name for names in leg_map.values() for name in names}
    fixed = [joint["name"] for joint in joints if joint["type"] == "fixed"]
    leg = [joint["name"] for joint in joints if joint["name"] in leg_set]
    rail = [joint["name"] for joint in joints if joint["name"] in rail_set]
    passive = [
        joint["name"]
        for joint in joints
        if joint["type"] != "fixed" and joint["name"] not in leg_set and joint["name"] not in rail_set
    ]
    return {"leg_revolute_joints": leg, "rail_prismatic_joints": rail, "passive_joints": passive, "fixed_joints": fixed}


def root_links(links: Sequence[str], joints: Sequence[Mapping[str, Any]]) -> List[str]:
    child_links = {joint["child"] for joint in joints if joint["child"]}
    return [link for link in links if link not in child_links]


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, list):
        return "[" + ", ".join(f"{x:.6g}" if isinstance(x, float) else str(x) for x in value) + "]"
    return str(value)


def print_joint_table(joints: Sequence[Mapping[str, Any]], init: Mapping[str, Tuple[float, float]]) -> None:
    headers = [
        "idx", "name", "type", "parent", "child", "axis", "lower", "upper", "effort", "velocity", "initial_q", "initial_dq",
    ]
    print("\t".join(headers))
    for joint in joints:
        q, dq = init.get(joint["name"], (0.0, 0.0))
        row = [
            joint["joint_index"],
            joint["name"],
            joint["type"],
            joint["parent"],
            joint["child"],
            fmt(joint["axis"]),
            fmt(joint["lower"]),
            fmt(joint["upper"]),
            fmt(joint["effort"]),
            fmt(joint["velocity"]),
            fmt(q),
            fmt(dq),
        ]
        print("\t".join(str(item) for item in row))


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(fmt(cell) for cell in row) + " |")
    return "\n".join(out)


def write_report(
    report_path: Path,
    model_path: Path,
    links: Sequence[str],
    joints: Sequence[Mapping[str, Any]],
    init: Mapping[str, Tuple[float, float]],
    base_link: str,
    roots: Sequence[str],
    classes: Mapping[str, Sequence[str]],
    leg_map: Mapping[str, Sequence[str]],
    foot_links: Mapping[str, str],
    rail_names: Sequence[str],
    validation_ok: bool,
    validation_messages: Sequence[str],
) -> None:
    rows = []
    for joint in joints:
        q, dq = init.get(joint["name"], (0.0, 0.0))
        rows.append(
            [
                joint["joint_index"],
                joint["motion_index"],
                joint["name"],
                joint["type"],
                joint["parent"],
                joint["child"],
                joint["axis"],
                joint["lower"],
                joint["upper"],
                joint["effort"],
                joint["velocity"],
                q,
                dq,
            ]
        )

    lines = [
        "# Robot Structure Report",
        "",
        f"- model_path: `{model_path}`",
        f"- base_link: `{base_link}`",
        f"- root_links / floating base candidates: `{', '.join(roots)}`",
        f"- total_links: {len(links)}",
        f"- total_joints: {len(joints)}",
        f"- mapping_valid: `{validation_ok}`",
        "",
        "## Joint Table",
        "",
        markdown_table(
            [
                "joint_index",
                "motion_index",
                "joint_name",
                "joint_type",
                "parent_link",
                "child_link",
                "joint_axis",
                "lower",
                "upper",
                "effort",
                "velocity",
                "initial_q",
                "initial_dq",
            ],
            rows,
        ),
        "",
        "## Classification",
        "",
    ]
    for key, values in classes.items():
        lines.append(f"- {key}: {', '.join(values) if values else '(none)'}")

    lines.extend(["", "## Rail Lock Inputs", ""])
    for rail_name in rail_names:
        q, dq = init.get(rail_name, (0.0, 0.0))
        lines.append(f"- {rail_name}: initial_q={q:.6g}, initial_dq={dq:.6g}")

    lines.extend(["", "## Leg Joint Mapping", ""])
    for leg in ("FL", "FR", "RL", "RR"):
        names = list(leg_map.get(leg, []))
        lines.extend(
            [
                f"### {leg}",
                "",
                f"- joint_0: `{names[0] if len(names) > 0 else ''}`",
                f"- joint_1: `{names[1] if len(names) > 1 else ''}`",
                f"- joint_2: `{names[2] if len(names) > 2 else ''}`",
                f"- foot_link: `{foot_links.get(leg, '')}`",
                "",
            ]
        )

    lines.extend(["## Validation", ""])
    if validation_messages:
        lines.extend(f"- {message}" for message in validation_messages)
    else:
        lines.append("- No validation errors.")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def draw_pybullet_gui(
    urdf_text: str,
    base_link: str,
    rail_names: Sequence[str],
    leg_map: Mapping[str, Sequence[str]],
    foot_links: Mapping[str, str],
    package_map: Mapping[str, Path],
    robot_config: Mapping[str, Any],
    rail_controller: Optional[RailLockController] = None,
    apply_rail_lock: bool = False,
    dynamic_gui: bool = False,
) -> None:
    try:
        import pybullet as p
        import pybullet_data
    except Exception as exc:
        print(f"[WARN] PyBullet GUI requested but pybullet is unavailable: {exc}")
        return

    resolved_urdf = replace_package_urls(urdf_text, package_map)
    with tempfile.NamedTemporaryFile("w", suffix=".urdf", delete=False, encoding="utf-8") as f:
        f.write(resolved_urdf)
        temp_urdf = f.name

    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0.0, 0.0, 0.0)
    p.loadURDF("plane.urdf")
    body_id = p.loadURDF(temp_urdf, useFixedBase=not dynamic_gui)
    joint_name_to_index = {}
    link_name_to_index = {}
    for joint_index in range(p.getNumJoints(body_id)):
        info = p.getJointInfo(body_id, joint_index)
        joint_name = info[1].decode("utf-8")
        link_name = info[12].decode("utf-8")
        joint_name_to_index[joint_name] = joint_index
        link_name_to_index[link_name] = joint_index

    pybullet_cfg = ((robot_config.get("simulation") or {}).get("pybullet") or {})
    base_rpy = pybullet_cfg.get("base_orientation_rpy", [0.0, 0.0, 0.0])
    base_quat = p.getQuaternionFromEuler([float(v) for v in base_rpy])
    p.resetBasePositionAndOrientation(body_id, [0.0, 0.0, 0.42], base_quat)
    rail_cfg = robot_config.get("rail") or {}
    rail_source = str(rail_cfg.get("lock_position_source", "initial"))
    rail_default = float(rail_cfg.get("lock_position", 0.0))
    rail_map = {
        str(name): float(value)
        for name, value in (rail_cfg.get("lock_position_map", {}) or {}).items()
    }
    for rail_name in rail_names:
        if rail_name in joint_name_to_index:
            rail_q = rail_map.get(rail_name, rail_default) if rail_source == "configured" else 0.0
            p.resetJointState(body_id, joint_name_to_index[rail_name], rail_q, 0.0)
    for leg_cfg in (robot_config.get("legs") or {}).values():
        joint_names = leg_cfg.get("joint_names", []) or []
        default_q = leg_cfg.get("default_stand_q", []) or []
        for index, joint_name in enumerate(joint_names):
            if joint_name in joint_name_to_index and index < len(default_q):
                p.resetJointState(body_id, joint_name_to_index[joint_name], float(default_q[index]), 0.0)
    foot_z = []
    for foot_link in foot_links.values():
        if foot_link in link_name_to_index:
            foot_z.append(p.getLinkState(body_id, link_name_to_index[foot_link])[0][2])
    if foot_z:
        base_pos, base_quat_current = p.getBasePositionAndOrientation(body_id)
        p.resetBasePositionAndOrientation(
            body_id,
            [base_pos[0], base_pos[1], base_pos[2] + (0.014 - min(foot_z))],
            base_quat_current,
        )

    if apply_rail_lock:
        if rail_controller is None:
            raise RuntimeError("apply_rail_lock requires a RailLockController.")
        rail_state = {
            name: p.getJointState(body_id, joint_name_to_index[name])[:2]
            for name in rail_controller.rail_joint_names
            if name in joint_name_to_index
        }
        rail_controller.initialize(rail_state)
        rail_controller.apply_pybullet_position_lock(p, body_id, joint_name_to_index)

    p.addUserDebugText(f"base frame: {base_link}", [0, 0, 0.25], textColorRGB=[1, 1, 1], textSize=1.3)
    p.addUserDebugLine([0, 0, 0], [0.15, 0, 0], [1, 0, 0], lineWidth=3)
    p.addUserDebugLine([0, 0, 0], [0, 0.15, 0], [0, 1, 0], lineWidth=3)
    p.addUserDebugLine([0, 0, 0], [0, 0, 0.15], [0, 0.4, 1], lineWidth=3)
    mode_text = (
        "rail lock ACTIVE; dynamic stand pose display"
        if apply_rail_lock
        else f"static structure display; base rpy={[round(math.degrees(float(v)), 1) for v in base_rpy]} deg"
    )
    p.addUserDebugText(mode_text, [0, 0, 0.35], textColorRGB=[0, 1, 1], textSize=1.1)

    for rail_name in rail_names:
        joint_index = joint_name_to_index.get(rail_name)
        if joint_index is None:
            continue
        link_state = p.getLinkState(body_id, joint_index)
        pos = link_state[0]
        label = "active lock" if apply_rail_lock else "rail joint"
        p.addUserDebugText(f"{rail_name}: {label}", pos, textColorRGB=[0, 1, 1], textSize=1.0)

    for leg, names in leg_map.items():
        color = [1, 0.6, 0] if leg in {"FL", "RR"} else [0.2, 0.6, 1]
        foot_link = foot_links.get(leg, "")
        foot_index = link_name_to_index.get(foot_link)
        if foot_index is not None:
            foot_pos = p.getLinkState(body_id, foot_index)[0]
            p.addUserDebugText(f"{leg} foot: {foot_link}", foot_pos, textColorRGB=color, textSize=1.0)
        for joint_name in names:
            joint_index = joint_name_to_index.get(joint_name)
            if joint_index is None:
                continue
            joint_pos = p.getLinkState(body_id, joint_index)[0]
            p.addUserDebugText(joint_name, joint_pos, textColorRGB=color, textSize=0.8)

    if apply_rail_lock:
        print("[INFO] PyBullet GUI is open with active rail position lock.")
        if dynamic_gui:
            print("[INFO] Dynamic GUI enabled; watch terminal rail_error warnings.")
        else:
            print("[INFO] Static/fixed-base GUI enabled; use 02_stand_test.py --gui for dynamics.")
    else:
        print("[INFO] PyBullet GUI is static structure-only: fixed base, zero gravity, no dynamics stepping.")
        print("[INFO] Use 02_stand_test.py --gui for the dynamic stand test.")
    print("[INFO] Press Ctrl+C in this terminal to exit.")
    sim_step = 0
    try:
        while True:
            if apply_rail_lock and rail_controller is not None:
                rail_state = {
                    name: p.getJointState(body_id, joint_name_to_index[name])[:2]
                    for name in rail_controller.rail_joint_names
                    if name in joint_name_to_index
                }
                commands = rail_controller.compute(rail_state)
                rail_controller.apply_pybullet_position_lock(p, body_id, joint_name_to_index)
                if sim_step % 240 == 0:
                    for command in commands.values():
                        status = "SAFETY" if command.safety_stop else "WARN" if command.warning else "OK"
                        print(
                            f"[{status}] {command.joint_name}: "
                            f"q={command.q:.6f} q0={command.q0:.6f} "
                            f"error={command.error:.6f} force={command.force:.3f}"
                        )
            if dynamic_gui:
                p.stepSimulation()
            else:
                time.sleep(0.05)
            sim_step += 1
    except KeyboardInterrupt:
        pass
    finally:
        p.disconnect()
        try:
            os.unlink(temp_urdf)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(PROJECT_ROOT / "config" / "robot_config.yaml"))
    parser.add_argument("--rail-config", default=str(PROJECT_ROOT / "config" / "rail_config.yaml"))
    parser.add_argument("--report", default=str(PROJECT_ROOT / "robot_structure_report.md"))
    parser.add_argument("--gui", action="store_true", help="Open optional PyBullet GUI annotations.")
    parser.add_argument(
        "--apply-rail-lock",
        action="store_true",
        help="In PyBullet GUI, actively lock rail joints at their initial q using RailLockController.",
    )
    parser.add_argument(
        "--dynamic-gui",
        action="store_true",
        help="Let 00_print_robot_structure.py step PyBullet dynamics. Off by default to avoid contact explosions.",
    )
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    rail_config_path = Path(args.rail_config).resolve()
    robot_config = load_yaml(config_path)
    rail_config = load_yaml(rail_config_path)
    config_dir = config_path.parent
    model_path = resolve_path(robot_config["robot"]["model_path"], config_dir)
    base_link = str(robot_config.get("robot", {}).get("base_link", "base"))

    urdf_text = expand_model_to_urdf(model_path, robot_config, config_dir)
    package_map = local_package_map(WORKSPACE_ROOT)
    links, joints = parse_joints(urdf_text)
    joints_by_name = {joint["name"]: joint for joint in joints}
    rail_names = detect_rail_joints(joints, robot_config)

    configured_leg_map = leg_config_joint_names(robot_config)
    configured_foot_links = leg_config_foot_links(robot_config)
    config_mapping_ok, _ = validate_mapping(
        configured_leg_map, configured_foot_links, joints_by_name, links, rail_names
    )
    if config_mapping_ok:
        leg_map = configured_leg_map
        foot_links = configured_foot_links
        auto_warnings: List[str] = []
    else:
        leg_map, foot_links, auto_warnings = auto_detect_leg_mapping(joints, links, rail_names)

    init = initial_states(robot_config, rail_names)
    classes = classify_joints(joints, leg_map, rail_names)
    roots = root_links(links, joints)

    validation_ok, validation_messages = validate_mapping(
        leg_map, foot_links, joints_by_name, links, rail_names
    )
    validation_messages = list(auto_warnings) + validation_messages

    rail_controller = RailLockController.from_config_dicts(
        robot_config, rail_config, detected_rail_joints=rail_names
    )
    try:
        rail_controller.validate_leg_joint_exclusion(leg_map)
    except ValueError as exc:
        validation_ok = False
        validation_messages.append(str(exc))

    if base_link not in links:
        validation_ok = False
        validation_messages.append(f"Configured base_link {base_link} is not present in the model.")
    if set(rail_names) - set(joints_by_name):
        validation_ok = False
        validation_messages.append(f"Rail joints missing from model: {sorted(set(rail_names) - set(joints_by_name))}")

    print("\n=== Robot Joint Structure ===")
    print_joint_table(joints, init)

    print("\n=== Classification ===")
    print(f"floating base/root candidates: {roots}")
    for key, values in classes.items():
        print(f"{key}: {values}")

    print("\n=== Leg Joint Mapping ===")
    for leg in ("FL", "FR", "RL", "RR"):
        names = leg_map.get(leg, [])
        print(f"{leg}:")
        print(f"  joint_0: {names[0] if len(names) > 0 else ''}")
        print(f"  joint_1: {names[1] if len(names) > 1 else ''}")
        print(f"  joint_2: {names[2] if len(names) > 2 else ''}")
        print(f"  foot_link: {foot_links.get(leg, '')}")

    report_path = Path(args.report).resolve()
    write_report(
        report_path,
        model_path,
        links,
        joints,
        init,
        base_link,
        roots,
        classes,
        leg_map,
        foot_links,
        rail_names,
        validation_ok,
        validation_messages,
    )
    print(f"\n[INFO] Wrote report: {report_path}")

    if validation_messages:
        print("\n=== Validation Messages ===")
        for message in validation_messages:
            print(f"- {message}")

    if args.gui:
        draw_pybullet_gui(
            urdf_text,
            base_link,
            rail_names,
            leg_map,
            foot_links,
            package_map,
            robot_config,
            rail_controller=rail_controller,
            apply_rail_lock=args.apply_rail_lock,
            dynamic_gui=args.dynamic_gui,
        )

    if not validation_ok:
        print("\n[ERROR] Joint mapping is not clear. Fill robot_config.yaml manually before gait work.")
        return 2

    print("\n[OK] Structure mapping is valid. Gait code is still intentionally not generated in step 1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
