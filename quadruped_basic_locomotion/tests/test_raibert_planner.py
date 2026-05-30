from pathlib import Path
import sys

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.raibert_planner import RaibertPlanner


def make_planner() -> RaibertPlanner:
    cfg = yaml.safe_load((PROJECT_ROOT / "config" / "gait_config.yaml").read_text(encoding="utf-8")) or {}
    return RaibertPlanner.from_config_dict(cfg)


def test_foot_target_limited_by_max_step_length():
    planner = make_planner()
    result = planner.plan(
        "FL",
        nominal_foot_pos_body=[0.2, 0.1, -0.18],
        desired_base_velocity_body=[1.0, 1.0, 0.0],
        current_base_velocity_body=[-1.0, -1.0, 0.0],
        stance_time=0.7,
        swing_time=0.3,
    )
    dx = result.foot_target_body[0] - result.nominal_foot_pos_body[0]
    dy = result.foot_target_body[1] - result.nominal_foot_pos_body[1]
    assert abs(dx) <= 0.05
    assert abs(dy) <= 0.03


def test_z_is_not_modified():
    planner = make_planner()
    result = planner.plan(
        "FR",
        nominal_foot_pos_body=[0.2, -0.1, -0.21],
        desired_base_velocity_body=[0.05, 0.0, 0.0],
        current_base_velocity_body=[0.0, 0.0, 0.0],
        stance_time=0.7,
        swing_time=0.3,
    )
    assert result.foot_target_body[2] == result.nominal_foot_pos_body[2]


def test_output_coordinate_frame_is_explicit():
    planner = make_planner()
    result = planner.plan(
        "RL",
        nominal_foot_pos_body=[-0.2, 0.1, -0.2],
        desired_base_velocity_body=[0.03, 0.0, 0.0],
        current_base_velocity_body=[0.0, 0.0, 0.0],
        stance_time=0.7,
        swing_time=0.3,
    )
    assert result.coordinate_frame == "body"
