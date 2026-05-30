#!/usr/bin/env python3
"""Swing-leg trajectory generation.

This module only generates swing foot position/velocity targets in world frame.
It does not know about rails, gait scheduling, or IK.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, List, Mapping, Optional, Sequence, Tuple

import numpy as np


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class SwingTrajectoryConfig:
    trajectory_type: str = "cycloid"
    step_height: float = 0.03
    max_step_height: float = 0.06
    max_step_length: float = 0.08
    max_position_delta_per_cycle: float = 0.02


@dataclass(frozen=True)
class SwingTrajectorySample:
    position_world: Tuple[float, float, float]
    velocity_world: Optional[Tuple[float, float, float]]
    target_world_limited: Tuple[float, float, float]


class SwingTrajectory:
    """Cycloid-like swing trajectory with conservative target limiting."""

    def __init__(self, config: SwingTrajectoryConfig):
        self.config = config

    @classmethod
    def from_config_dict(cls, gait_config: Mapping[str, Any]) -> "SwingTrajectory":
        swing = gait_config.get("swing_trajectory", {}) or {}
        return cls(
            SwingTrajectoryConfig(
                trajectory_type=str(swing.get("type", "cycloid")),
                step_height=max(_float(swing.get("step_height"), 0.03), 0.0),
                max_step_height=max(_float(swing.get("max_step_height"), 0.06), 1e-6),
                max_step_length=max(_float(swing.get("max_step_length"), 0.08), 1e-6),
                max_position_delta_per_cycle=max(_float(swing.get("max_position_delta_per_cycle"), 0.02), 1e-6),
            )
        )

    def _clip_target_xy(self, start_world: np.ndarray, target_world: np.ndarray) -> np.ndarray:
        delta_xy = target_world[:2] - start_world[:2]
        length_xy = float(np.linalg.norm(delta_xy))
        if length_xy <= self.config.max_step_length:
            return target_world.copy()
        scale = self.config.max_step_length / max(length_xy, 1e-9)
        clipped = target_world.copy()
        clipped[:2] = start_world[:2] + scale * delta_xy
        return clipped

    def limit_target_change(
        self,
        previous_target_world: Optional[Sequence[float]],
        proposed_target_world: Sequence[float],
    ) -> Tuple[float, float, float]:
        proposed = np.asarray(proposed_target_world, dtype=float)
        if previous_target_world is None:
            return tuple(float(v) for v in proposed)
        previous = np.asarray(previous_target_world, dtype=float)
        delta = proposed - previous
        length = float(np.linalg.norm(delta))
        if length <= self.config.max_position_delta_per_cycle:
            return tuple(float(v) for v in proposed)
        limited = previous + delta / max(length, 1e-9) * self.config.max_position_delta_per_cycle
        return tuple(float(v) for v in limited)

    def evaluate(
        self,
        start_foot_pos_world: Sequence[float],
        target_foot_pos_world: Sequence[float],
        swing_phase: float,
        step_height: Optional[float] = None,
        swing_duration: Optional[float] = None,
        previous_desired_foot_pos_world: Optional[Sequence[float]] = None,
    ) -> SwingTrajectorySample:
        phase = min(max(float(swing_phase), 0.0), 1.0)
        start = np.asarray(start_foot_pos_world, dtype=float)
        target = np.asarray(target_foot_pos_world, dtype=float)
        target_limited = self._clip_target_xy(start, target)

        height = self.config.step_height if step_height is None else float(step_height)
        height = min(max(height, 0.0), self.config.max_step_height)

        delta = target_limited - start
        pos = start + phase * delta
        pos[2] = start[2] + phase * delta[2] + height * math.sin(math.pi * phase)

        vel_tuple: Optional[Tuple[float, float, float]] = None
        if swing_duration is not None and swing_duration > 0.0:
            vel = delta / float(swing_duration)
            vel[2] = delta[2] / float(swing_duration) + height * math.pi * math.cos(math.pi * phase) / float(
                swing_duration
            )
            vel_tuple = tuple(float(v) for v in vel)

        if previous_desired_foot_pos_world is not None:
            pos = np.asarray(self.limit_target_change(previous_desired_foot_pos_world, pos), dtype=float)

        return SwingTrajectorySample(
            position_world=tuple(float(v) for v in pos),
            velocity_world=vel_tuple,
            target_world_limited=tuple(float(v) for v in target_limited),
        )

    def sample_curve(
        self,
        start_foot_pos_world: Sequence[float],
        target_foot_pos_world: Sequence[float],
        step_height: Optional[float] = None,
        num_points: int = 21,
    ) -> List[Tuple[float, float, float]]:
        num_points = max(int(num_points), 2)
        return [
            self.evaluate(start_foot_pos_world, target_foot_pos_world, i / (num_points - 1), step_height).position_world
            for i in range(num_points)
        ]


__all__ = ["SwingTrajectory", "SwingTrajectoryConfig", "SwingTrajectorySample"]
