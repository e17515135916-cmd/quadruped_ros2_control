#!/usr/bin/env python3

"""
Validate URDF shift boundary invariants for dog2.

This script enforces the rule that CAD-origin compensation is applied only at
`base_offset_joint`, while `base_link` and leg-root anchors remain expressed in
base_link-local coordinates.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

EPS = 1e-4
STRICT_EPS = 1e-6

EXPECTED_BASE_LINK_VISUAL = (-0.9780, 0.87203, -0.2649)
EXPECTED_BASE_LINK_INERTIAL = (0.2492, 0.12503, 0.0)
EXPECTED_RAIL_JOINTS = {
    "lf_rail_joint": (0.1246, 0.0625, 0.0),
    "lh_rail_joint": (0.3711, 0.0625, 0.0),
    "rh_rail_joint": (0.3711, 0.1825, 0.0),
    "rf_rail_joint": (0.1291, 0.1825, 0.0),
}


def parse_xyz(xyz: str) -> tuple[float, float, float]:
    parts = xyz.split()
    if len(parts) != 3:
        raise ValueError(f"Invalid xyz format: {xyz!r}")
    return (float(parts[0]), float(parts[1]), float(parts[2]))


def is_close_vec(a: tuple[float, float, float], b: tuple[float, float, float], tol: float) -> bool:
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b))


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def run_xacro_to_urdf(xacro_path: Path) -> Path:
    with tempfile.NamedTemporaryFile(suffix=".urdf", delete=False) as tmp:
        urdf_path = Path(tmp.name)

    cmd = ["xacro", str(xacro_path), "-o", str(urdf_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(
            "xacro expansion failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return urdf_path


def get_joint_origin(robot: ET.Element, joint_name: str) -> tuple[float, float, float]:
    joint = robot.find(f"./joint[@name='{joint_name}']")
    if joint is None:
        fail(f"Missing joint: {joint_name}")

    origin = joint.find("origin")
    if origin is None:
        fail(f"Joint {joint_name} has no origin")

    xyz = origin.attrib.get("xyz")
    if xyz is None:
        fail(f"Joint {joint_name} origin missing xyz")

    return parse_xyz(xyz)


def get_link_visual_origin(robot: ET.Element, link_name: str) -> tuple[float, float, float]:
    link = robot.find(f"./link[@name='{link_name}']")
    if link is None:
        fail(f"Missing link: {link_name}")

    visual = link.find("visual")
    if visual is None:
        fail(f"Link {link_name} missing visual")

    origin = visual.find("origin")
    if origin is None:
        fail(f"Link {link_name} visual missing origin")

    xyz = origin.attrib.get("xyz")
    if xyz is None:
        fail(f"Link {link_name} visual origin missing xyz")

    return parse_xyz(xyz)


def get_link_inertial_origin(robot: ET.Element, link_name: str) -> tuple[float, float, float]:
    link = robot.find(f"./link[@name='{link_name}']")
    if link is None:
        fail(f"Missing link: {link_name}")

    inertial = link.find("inertial")
    if inertial is None:
        fail(f"Link {link_name} missing inertial")

    origin = inertial.find("origin")
    if origin is None:
        fail(f"Link {link_name} inertial missing origin")

    xyz = origin.attrib.get("xyz")
    if xyz is None:
        fail(f"Link {link_name} inertial origin missing xyz")

    return parse_xyz(xyz)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate dog2 URDF shift boundary invariants")
    parser.add_argument(
        "xacro_file",
        nargs="?",
        default="src/dog2_description/urdf/dog2.urdf.xacro",
        help="Path to dog2 xacro file",
    )
    parser.add_argument("--tolerance", "--tol", dest="tolerance", type=float, default=EPS,
                        help="Absolute tolerance (default: 1e-4)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict tolerance mode (overrides tolerance to 1e-6)",
    )
    args = parser.parse_args()

    tol = STRICT_EPS if args.strict else args.tolerance

    xacro_path = Path(args.xacro_file).resolve()
    if not xacro_path.exists():
        fail(f"xacro file not found: {xacro_path}")

    urdf_path = run_xacro_to_urdf(xacro_path)

    try:
        root = ET.parse(urdf_path).getroot()

        base_visual = get_link_visual_origin(root, "base_link")
        if not is_close_vec(base_visual, EXPECTED_BASE_LINK_VISUAL, tol):
            fail(
                "base_link visual origin changed unexpectedly. "
                f"expected={EXPECTED_BASE_LINK_VISUAL}, got={base_visual}, tol={tol}"
            )

        base_inertial = get_link_inertial_origin(root, "base_link")
        if not is_close_vec(base_inertial, EXPECTED_BASE_LINK_INERTIAL, tol):
            fail(
                "base_link inertial origin changed unexpectedly. "
                f"expected={EXPECTED_BASE_LINK_INERTIAL}, got={base_inertial}, tol={tol}"
            )

        for joint, expected_xyz in EXPECTED_RAIL_JOINTS.items():
            xyz = get_joint_origin(root, joint)
            if not is_close_vec(xyz, expected_xyz, tol):
                fail(f"{joint} origin mismatch: expected={expected_xyz}, got={xyz}, tol={tol}")

        mode = "strict" if args.strict else "normal"
        print(f"[PASS] URDF shift boundary checks passed (mode={mode}, tol={tol:g}).")
        return 0
    finally:
        try:
            urdf_path.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
