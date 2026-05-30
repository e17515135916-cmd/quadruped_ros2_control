#!/usr/bin/env python3
"""World-frame stance anchor management for quadruped feet."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


LEG_ORDER = ("FL", "FR", "RL", "RR")


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _quat_conjugate(quat_xyzw: Sequence[float]) -> Tuple[float, float, float, float]:
    x, y, z, w = (float(v) for v in quat_xyzw)
    return (-x, -y, -z, w)


def _quat_multiply(a_xyzw: Sequence[float], b_xyzw: Sequence[float]) -> Tuple[float, float, float, float]:
    ax, ay, az, aw = (float(v) for v in a_xyzw)
    bx, by, bz, bw = (float(v) for v in b_xyzw)
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _rotate_vector(quat_xyzw: Sequence[float], vec_xyz: Sequence[float]) -> Tuple[float, float, float]:
    vec_quat = (float(vec_xyz[0]), float(vec_xyz[1]), float(vec_xyz[2]), 0.0)
    rotated = _quat_multiply(_quat_multiply(quat_xyzw, vec_quat), _quat_conjugate(quat_xyzw))
    return (rotated[0], rotated[1], rotated[2])


@dataclass(frozen=True)
class StanceControllerConfig:
    foot_slip_warning_m: float = 0.01


@dataclass(frozen=True)
class StanceTarget:
    target_world: Tuple[float, float, float]
    slip_error: float
    warning: bool
    just_touchdown: bool


class StanceController:
    """Keeps each stance foot anchored in world coordinates."""

    def __init__(self, config: StanceControllerConfig, leg_names: Sequence[str] = LEG_ORDER):
        self.config = config
        self.leg_names = tuple(str(name) for name in leg_names)
        self._anchors_world: Dict[str, Optional[Tuple[float, float, float]]] = {name: None for name in self.leg_names}
        self._last_state: Dict[str, Optional[str]] = {name: None for name in self.leg_names}

    @classmethod
    def from_config_dict(cls, gait_config: Mapping[str, Any]) -> "StanceController":
        stance = gait_config.get("stance", {}) or {}
        return cls(StanceControllerConfig(foot_slip_warning_m=max(_float(stance.get("foot_slip_warning_m"), 0.01), 0.0)))

    def reset(self) -> None:
        for leg_name in self.leg_names:
            self._anchors_world[leg_name] = None
            self._last_state[leg_name] = None

    def update_leg(
        self,
        leg_name: str,
        leg_state: str,
        actual_foot_pos_world: Sequence[float],
    ) -> StanceTarget:
        if leg_name not in self._anchors_world:
            raise KeyError(f"Unknown leg {leg_name}")
        actual = tuple(float(v) for v in actual_foot_pos_world)
        last_state = self._last_state[leg_name]
        just_touchdown = leg_state == "stance" and last_state != "stance"

        if leg_state == "stance" and (just_touchdown or self._anchors_world[leg_name] is None):
            self._anchors_world[leg_name] = actual
        elif leg_state != "stance":
            self._anchors_world[leg_name] = None

        anchor = self._anchors_world[leg_name] if self._anchors_world[leg_name] is not None else actual
        slip_error = math.dist(anchor, actual) if leg_state == "stance" else 0.0
        warning = leg_state == "stance" and slip_error > self.config.foot_slip_warning_m
        self._last_state[leg_name] = leg_state
        return StanceTarget(target_world=anchor, slip_error=slip_error, warning=warning, just_touchdown=just_touchdown)

    def get_anchor_world(self, leg_name: str) -> Optional[Tuple[float, float, float]]:
        if leg_name not in self._anchors_world:
            raise KeyError(f"Unknown leg {leg_name}")
        return self._anchors_world[leg_name]

    @staticmethod
    def world_to_base_frame(
        point_world: Sequence[float],
        base_position_world: Sequence[float],
        base_orientation_world_xyzw: Sequence[float],
    ) -> Tuple[float, float, float]:
        delta = (
            float(point_world[0]) - float(base_position_world[0]),
            float(point_world[1]) - float(base_position_world[1]),
            float(point_world[2]) - float(base_position_world[2]),
        )
        return _rotate_vector(_quat_conjugate(base_orientation_world_xyzw), delta)

    @staticmethod
    def base_to_world_frame(
        point_base: Sequence[float],
        base_position_world: Sequence[float],
        base_orientation_world_xyzw: Sequence[float],
    ) -> Tuple[float, float, float]:
        rotated = _rotate_vector(base_orientation_world_xyzw, point_base)
        return (
            rotated[0] + float(base_position_world[0]),
            rotated[1] + float(base_position_world[1]),
            rotated[2] + float(base_position_world[2]),
        )

    @classmethod
    def world_to_hip_frame(
        cls,
        point_world: Sequence[float],
        base_position_world: Sequence[float],
        base_orientation_world_xyzw: Sequence[float],
        hip_position_base: Sequence[float],
        hip_orientation_base_xyzw: Sequence[float] = (0.0, 0.0, 0.0, 1.0),
    ) -> Tuple[float, float, float]:
        point_base = cls.world_to_base_frame(point_world, base_position_world, base_orientation_world_xyzw)
        relative_base = (
            point_base[0] - float(hip_position_base[0]),
            point_base[1] - float(hip_position_base[1]),
            point_base[2] - float(hip_position_base[2]),
        )
        return _rotate_vector(_quat_conjugate(hip_orientation_base_xyzw), relative_base)


__all__ = ["StanceController", "StanceControllerConfig", "StanceTarget", "LEG_ORDER"]
