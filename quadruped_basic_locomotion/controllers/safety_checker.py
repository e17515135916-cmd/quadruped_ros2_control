#!/usr/bin/env python3
"""Runtime safety checks for staged locomotion tests."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class SafetyConfig:
    max_roll_deg: float = 20.0
    max_pitch_deg: float = 20.0
    min_base_height: float = 0.12
    joint_limit_tolerance: float = 0.0005
    max_joint_velocity: float = 25.0
    max_torque_ratio: float = 1.05
    rail_error_safety_m: float = 0.010
    min_stance_legs: int = 2
    max_ik_failures: int = 5
    max_foot_target_jump_m: float = 0.05


@dataclass(frozen=True)
class SafetyResult:
    ok: bool
    severe: bool
    reasons: Tuple[str, ...]
    warnings: Tuple[str, ...]


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _finite_values(values: Iterable[Any]) -> bool:
    for value in values:
        if isinstance(value, Mapping):
            if not _finite_values(value.values()):
                return False
        elif isinstance(value, (list, tuple)):
            if not _finite_values(value):
                return False
        elif isinstance(value, (int, float)) and not math.isfinite(float(value)):
            return False
    return True


class SafetyChecker:
    def __init__(self, config: SafetyConfig):
        self.config = config
        self._ik_failures: Dict[str, int] = {}

    @classmethod
    def from_config_dict(cls, controller_config: Mapping[str, Any]) -> "SafetyChecker":
        safety = controller_config.get("safety", {}) or {}
        return cls(
            SafetyConfig(
                max_roll_deg=_float(safety.get("max_roll_deg"), 20.0),
                max_pitch_deg=_float(safety.get("max_pitch_deg"), 20.0),
                min_base_height=_float(safety.get("min_base_height"), 0.12),
                joint_limit_tolerance=_float(safety.get("joint_limit_tolerance"), 0.0005),
                max_joint_velocity=_float(safety.get("max_joint_velocity"), 25.0),
                max_torque_ratio=_float(safety.get("max_torque_ratio"), 1.05),
                rail_error_safety_m=_float(safety.get("rail_error_safety_m"), 0.010),
                min_stance_legs=int(_float(safety.get("min_stance_legs"), 2)),
                max_ik_failures=int(_float(safety.get("max_ik_failures"), 5)),
                max_foot_target_jump_m=_float(safety.get("max_foot_target_jump_m"), 0.05),
            )
        )

    def check(
        self,
        *,
        base_position: Sequence[float],
        base_rpy: Sequence[float],
        joint_state: Mapping[str, Tuple[float, float]],
        joint_limits: Mapping[str, Tuple[Optional[float], Optional[float]]],
        torques: Mapping[str, float],
        torque_limits: Mapping[str, float],
        rail_errors: Mapping[str, float],
        gait_states: Optional[Mapping[str, str]] = None,
        ik_success: Optional[Mapping[str, bool]] = None,
        foot_target_jumps: Optional[Mapping[str, float]] = None,
    ) -> SafetyResult:
        reasons = []
        warnings = []

        if not _finite_values(
            [base_position, base_rpy, joint_state, joint_limits, torques, torque_limits, rail_errors]
        ):
            reasons.append("NaN/Inf detected in robot state or command.")

        roll_deg = abs(math.degrees(float(base_rpy[0])))
        pitch_deg = abs(math.degrees(float(base_rpy[1])))
        if roll_deg > self.config.max_roll_deg:
            reasons.append(f"base roll too large: {roll_deg:.2f} deg")
        if pitch_deg > self.config.max_pitch_deg:
            reasons.append(f"base pitch too large: {pitch_deg:.2f} deg")
        if float(base_position[2]) < self.config.min_base_height:
            reasons.append(f"base height too low: {float(base_position[2]):.3f} m")

        for joint_name, (q, dq) in joint_state.items():
            lower, upper = joint_limits.get(joint_name, (None, None))
            tol = self.config.joint_limit_tolerance
            if lower is not None and q < lower - tol:
                reasons.append(f"{joint_name} below lower limit: q={q:.4f}, lower={lower:.4f}")
            if upper is not None and q > upper + tol:
                reasons.append(f"{joint_name} above upper limit: q={q:.4f}, upper={upper:.4f}")
            if abs(dq) > self.config.max_joint_velocity:
                warnings.append(f"{joint_name} velocity high: dq={dq:.3f}")

        for joint_name, tau in torques.items():
            limit = abs(float(torque_limits.get(joint_name, math.inf)))
            if math.isfinite(limit) and abs(tau) > self.config.max_torque_ratio * limit:
                reasons.append(f"{joint_name} torque exceeds limit: tau={tau:.3f}, limit={limit:.3f}")

        for rail_name, error in rail_errors.items():
            if abs(error) > self.config.rail_error_safety_m:
                reasons.append(f"{rail_name} rail error too large: {error:.6f} m")

        if gait_states:
            stance_count = sum(1 for state in gait_states.values() if state == "stance")
            swing_count = sum(1 for state in gait_states.values() if state == "swing")
            if stance_count < self.config.min_stance_legs:
                reasons.append(f"too few stance legs: {stance_count}")
            if swing_count == len(gait_states):
                reasons.append("all legs are swing")

        if ik_success:
            for leg_name, success in ik_success.items():
                self._ik_failures[leg_name] = 0 if success else self._ik_failures.get(leg_name, 0) + 1
                if self._ik_failures[leg_name] > self.config.max_ik_failures:
                    reasons.append(f"{leg_name} IK failed consecutively: {self._ik_failures[leg_name]}")

        if foot_target_jumps:
            for leg_name, jump in foot_target_jumps.items():
                if jump > self.config.max_foot_target_jump_m:
                    reasons.append(f"{leg_name} foot target jump too large: {jump:.4f} m")

        return SafetyResult(ok=not reasons, severe=bool(reasons), reasons=tuple(reasons), warnings=tuple(warnings))


__all__ = ["SafetyChecker", "SafetyConfig", "SafetyResult"]
