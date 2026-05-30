#!/usr/bin/env python3
"""Numerical IK for non-standard 3R quadruped legs.

The solver does not assume Unitree/MIT-Cheetah joint axes or mirror symmetry.
It only needs a forward-kinematics callback for one leg's configured three
revolute joints.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np


ForwardKinematicsFn = Callable[[str, Sequence[float]], Sequence[float]]


@dataclass(frozen=True)
class LegIKConfig:
    joint_names: Tuple[str, str, str]
    joint_sign: Tuple[float, float, float]
    joint_offset: Tuple[float, float, float]
    lower: Tuple[float, float, float]
    upper: Tuple[float, float, float]


@dataclass(frozen=True)
class IKResult:
    leg_name: str
    q: Tuple[float, float, float]
    success: bool
    error_norm: float
    iterations: int
    message: str = ""


class NumericalIK:
    """Damped least-squares IK over the configured three revolute joints."""

    def __init__(
        self,
        leg_configs: Mapping[str, LegIKConfig],
        forward_kinematics: ForwardKinematicsFn,
        tolerance: float = 0.005,
        finite_difference_step: float = 1e-4,
    ):
        self.leg_configs = dict(leg_configs)
        self.forward_kinematics = forward_kinematics
        self.tolerance = float(tolerance)
        self.finite_difference_step = float(finite_difference_step)

    @classmethod
    def from_robot_config(
        cls,
        robot_config: Mapping[str, object],
        forward_kinematics: ForwardKinematicsFn,
        tolerance: float = 0.005,
        finite_difference_step: float = 1e-4,
    ) -> "NumericalIK":
        leg_configs: Dict[str, LegIKConfig] = {}
        for leg_name, raw_cfg in (robot_config.get("legs") or {}).items():  # type: ignore[union-attr]
            cfg = raw_cfg or {}
            joint_names = tuple(str(name) for name in (cfg.get("joint_names") or []))
            if len(joint_names) != 3:
                raise ValueError(f"{leg_name} must have exactly three IK joints.")
            signs = tuple(float(v) for v in (cfg.get("joint_sign") or [1.0, 1.0, 1.0]))
            offsets = tuple(float(v) for v in (cfg.get("joint_offset") or [0.0, 0.0, 0.0]))
            limits = cfg.get("joint_limit") or {}
            lower = tuple(float(v) for v in (limits.get("lower") or [-math.inf] * 3))
            upper = tuple(float(v) for v in (limits.get("upper") or [math.inf] * 3))
            if len(signs) != 3 or len(offsets) != 3 or len(lower) != 3 or len(upper) != 3:
                raise ValueError(f"{leg_name} joint_sign/joint_offset/joint_limit must all have length 3.")
            leg_configs[str(leg_name)] = LegIKConfig(
                joint_names=joint_names,  # type: ignore[arg-type]
                joint_sign=signs,  # type: ignore[arg-type]
                joint_offset=offsets,  # type: ignore[arg-type]
                lower=lower,  # type: ignore[arg-type]
                upper=upper,  # type: ignore[arg-type]
            )
        return cls(leg_configs, forward_kinematics, tolerance, finite_difference_step)

    def _model_to_internal(self, leg_name: str, q_model: np.ndarray) -> np.ndarray:
        cfg = self.leg_configs[leg_name]
        sign = np.asarray(cfg.joint_sign, dtype=float)
        offset = np.asarray(cfg.joint_offset, dtype=float)
        return (q_model - offset) / sign

    def _internal_to_model(self, leg_name: str, q_internal: np.ndarray) -> np.ndarray:
        cfg = self.leg_configs[leg_name]
        sign = np.asarray(cfg.joint_sign, dtype=float)
        offset = np.asarray(cfg.joint_offset, dtype=float)
        return sign * q_internal + offset

    def _clamp_model(self, leg_name: str, q_model: np.ndarray) -> np.ndarray:
        cfg = self.leg_configs[leg_name]
        lower = np.asarray(cfg.lower, dtype=float)
        upper = np.asarray(cfg.upper, dtype=float)
        return np.minimum(np.maximum(q_model, lower), upper)

    def _fk(self, leg_name: str, q_model: np.ndarray) -> np.ndarray:
        return np.asarray(self.forward_kinematics(leg_name, q_model.tolist()), dtype=float)

    def solve(
        self,
        leg_name,
        target_foot_pos,
        q_init,
        max_iters=30,
        damping=1e-3,
        step_limit=0.05,
    ) -> IKResult:
        """Solve for three model-space joint targets.

        Args:
            leg_name: One of FL/FR/RL/RR.
            target_foot_pos: Desired foot position in the configured FK frame.
            q_init: Current/previous three joint angles in model joint space.
            max_iters: Maximum DLS iterations.
            damping: DLS damping coefficient.
            step_limit: Per-iteration joint update limit in internal joint space.

        Returns:
            IKResult.q contains exactly three model-space joint angles.  Rail
            joints are never part of the input or output.
        """
        if leg_name not in self.leg_configs:
            raise KeyError(f"Unknown leg_name {leg_name}")

        target = np.asarray(target_foot_pos, dtype=float)
        q_model = self._clamp_model(leg_name, np.asarray(q_init, dtype=float))
        if q_model.shape != (3,):
            raise ValueError("q_init must have exactly three joint angles.")

        q_internal = self._model_to_internal(leg_name, q_model)
        best_q = q_model.copy()
        best_error = math.inf
        message = "max iterations reached"

        for iteration in range(1, int(max_iters) + 1):
            q_model = self._clamp_model(leg_name, self._internal_to_model(leg_name, q_internal))
            q_internal = self._model_to_internal(leg_name, q_model)
            pos = self._fk(leg_name, q_model)
            error = target - pos
            error_norm = float(np.linalg.norm(error))
            if error_norm < best_error:
                best_q = q_model.copy()
                best_error = error_norm
            if error_norm <= self.tolerance:
                return IKResult(
                    leg_name=str(leg_name),
                    q=tuple(float(v) for v in q_model),
                    success=True,
                    error_norm=error_norm,
                    iterations=iteration,
                    message="converged",
                )

            jacobian = np.zeros((3, 3), dtype=float)
            eps = self.finite_difference_step
            for joint_i in range(3):
                q_step_internal = q_internal.copy()
                q_step_internal[joint_i] += eps
                q_step_model = self._clamp_model(
                    leg_name,
                    self._internal_to_model(leg_name, q_step_internal),
                )
                pos_step = self._fk(leg_name, q_step_model)
                jacobian[:, joint_i] = (pos_step - pos) / eps

            lhs = jacobian @ jacobian.T + float(damping) ** 2 * np.eye(3)
            try:
                delta = jacobian.T @ np.linalg.solve(lhs, error)
            except np.linalg.LinAlgError:
                message = "singular damped system"
                break
            delta = np.clip(delta, -float(step_limit), float(step_limit))
            if not np.all(np.isfinite(delta)):
                message = "non-finite update"
                break
            q_internal = q_internal + delta

        return IKResult(
            leg_name=str(leg_name),
            q=tuple(float(v) for v in best_q),
            success=False,
            error_norm=float(best_error),
            iterations=int(max_iters),
            message=message,
        )


__all__ = ["IKResult", "LegIKConfig", "NumericalIK"]
