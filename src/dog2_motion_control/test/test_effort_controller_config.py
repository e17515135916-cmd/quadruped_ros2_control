from pathlib import Path

from dog2_motion_control.joint_names import ALL_JOINT_NAMES


def _extract_effort_controller_joints(config_text: str) -> list[str]:
    marker = "effort_controller:\n  ros__parameters:\n    joints:\n"
    start = config_text.index(marker) + len(marker)
    joint_lines = []
    for line in config_text[start:].splitlines():
        if not line.strip():
            continue
        if not line.startswith("      - "):
            break
        joint_lines.append(line.removeprefix("      - ").strip())
    return joint_lines


def test_effort_controller_joint_order_matches_canonical_joint_names():
    config_path = Path(__file__).resolve().parent.parent / "config" / "effort_controllers.yaml"
    joints = _extract_effort_controller_joints(config_path.read_text(encoding="utf-8"))
    assert joints == ALL_JOINT_NAMES
