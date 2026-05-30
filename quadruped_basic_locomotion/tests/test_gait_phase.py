from pathlib import Path
import sys

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.gait_scheduler import GaitScheduler


def load_gait_scheduler() -> GaitScheduler:
    config_path = PROJECT_ROOT / "config" / "gait_config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        gait_config = yaml.safe_load(f) or {}
    return GaitScheduler.from_config_dict(gait_config)


def test_diagonal_phase_pairing():
    scheduler = load_gait_scheduler()
    state = scheduler.update(2.35)
    assert abs(state["FL"]["phase"] - state["RR"]["phase"]) < 1e-9
    assert abs(state["FR"]["phase"] - state["RL"]["phase"]) < 1e-9


def test_half_cycle_offset_between_groups():
    scheduler = load_gait_scheduler()
    state = scheduler.update(2.35)
    diff = (state["FR"]["phase"] - state["FL"]["phase"]) % 1.0
    assert abs(diff - 0.5) < 1e-9


def test_at_least_two_stance_legs():
    scheduler = load_gait_scheduler()
    for i in range(200):
        t = 2.0 + i * 0.01
        state = scheduler.update(t)
        stance_count = sum(1 for leg in state.values() if leg["state"] == "stance")
        assert stance_count >= 2
