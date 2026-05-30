#!/usr/bin/env python3
"""Conservative Raibert foot-placement planner.

The planner operates entirely in the body frame.  It does not know about rail
joints and cannot use rail motion to compensate body velocity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class RaibertConfig:
    enabled: bool = True
    k_velocity_x: float = 0.03
    k_velocity_y: float = 0.02
    velocity_error_sign: float = 1.0
    max_step_length_x: float = 0.05
    max_step_length_y: float = 0.03
    max_foot_target_change_per_cycle: float = 0.01
    use_yaw_correction: bool = False
    k_yaw: float = 0.02


@dataclass(frozen=True)
class RaibertResult:
    leg_name: str
    foot_target_body: Tuple[float, float, float]
    nominal_foot_pos_body: Tuple[float, float, float]
    velocity_error_body: Tuple[float, float, float]
    coordinate_frame: str = "body"


class RaibertPlanner:
    """Low-speed Raibert heuristic with explicit coordinate-frame output."""

    def __init__(self, config: RaibertConfig):
        self.config = config
        self._last_targets_body: Dict[str, Tuple[float, float, float]] = {}

    @classmethod
    def from_config_dict(cls, gait_config: Mapping[str, Any]) -> "RaibertPlanner":
        cfg = gait_config.get("raibert", {}) or {}
        return cls(
            RaibertConfig(
                enabled=bool(cfg.get("enabled", True)),
                k_velocity_x=_float(cfg.get("k_velocity_x"), 0.03),
                k_velocity_y=_float(cfg.get("k_velocity_y"), 0.02),
                velocity_error_sign=_float(cfg.get("velocity_error_sign"), 1.0),
                max_step_length_x=max(_float(cfg.get("max_step_length_x"), 0.05), 0.0),
                max_step_length_y=max(_float(cfg.get("max_step_length_y"), 0.03), 0.0),
                max_foot_target_change_per_cycle=max(
                    _float(cfg.get("max_foot_target_change_per_cycle"), 0.01), 0.0
                ),
                use_yaw_correction=bool(cfg.get("use_yaw_correction", False)),
                k_yaw=_float(cfg.get("k_yaw"), 0.02),
            )
        )

    def reset(self) -> None:
        self._last_targets_body.clear()

    def plan(
        self,
        leg_name: str,
        nominal_foot_pos_body: Sequence[float],
        desired_base_velocity_body: Sequence[float],
        current_base_velocity_body: Sequence[float],
        stance_time: float,
        swing_time: float,
        yaw_rate_desired: float = 0.0,
        current_yaw_rate: float = 0.0,
        previous_target_body: Optional[Sequence[float]] = None,
    ) -> RaibertResult:
        nominal = np.asarray(nominal_foot_pos_body, dtype=float)
        desired_vel = np.asarray(desired_base_velocity_body, dtype=float)
        current_vel = np.asarray(current_base_velocity_body, dtype=float)
        if nominal.shape != (3,) or desired_vel.shape != (3,) or current_vel.shape != (3,):
            raise ValueError("nominal_foot_pos_body and velocities must be 3D body-frame vectors.")

        if not self.config.enabled:
            target = nominal.copy()
            velocity_error = desired_vel - current_vel
        else:
            velocity_error = desired_vel - current_vel
            target = nominal.copy()
            target[:2] += 0.5 * float(stance_time) * current_vel[:2]
            target[0] += self.config.k_velocity_x * self.config.velocity_error_sign * velocity_error[0]
            target[1] += self.config.k_velocity_y * self.config.velocity_error_sign * velocity_error[1]

            if self.config.use_yaw_correction:
                yaw_error = float(yaw_rate_desired) - float(current_yaw_rate)
                lateral_sign = 1.0 if nominal[1] >= 0.0 else -1.0
                target[0] += self.config.k_yaw * yaw_error * lateral_sign

            delta = target - nominal
            delta[0] = float(np.clip(delta[0], -self.config.max_step_length_x, self.config.max_step_length_x))
            delta[1] = float(np.clip(delta[1], -self.config.max_step_length_y, self.config.max_step_length_y))
            delta[2] = 0.0
            target = nominal + delta

        previous_raw = previous_target_body
        if previous_raw is None:
            previous_raw = self._last_targets_body.get(str(leg_name))
        if previous_raw is not None and self.config.max_foot_target_change_per_cycle > 0.0:
            previous = np.asarray(previous_raw, dtype=float)
            change = target - previous
            change_norm = float(np.linalg.norm(change))
            if change_norm > self.config.max_foot_target_change_per_cycle:
                target = previous + change / max(change_norm, 1e-9) * self.config.max_foot_target_change_per_cycle

        target[2] = nominal[2]
        target_tuple = tuple(float(v) for v in target)
        self._last_targets_body[str(leg_name)] = target_tuple
        return RaibertResult(
            leg_name=str(leg_name),
            foot_target_body=target_tuple,
            nominal_foot_pos_body=tuple(float(v) for v in nominal),
            velocity_error_body=tuple(float(v) for v in velocity_error),
        )


__all__ = ["RaibertConfig", "RaibertPlanner", "RaibertResult"]
