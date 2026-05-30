#!/usr/bin/env python3
"""Leg joint position PD controller.

Rail joints are intentionally excluded.  Rail locking is owned by
RailLockController.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple


@dataclass(frozen=True)
class JointPDConfig:
    kp: float
    kd: float
    torque_limit: float
    lower: Optional[float] = None
    upper: Optional[float] = None


@dataclass(frozen=True)
class JointPDCommand:
    joint_name: str
    q: float
    dq: float
    q_des: float
    dq_des: float
    tau: float
    saturated: bool
    limit_warning: bool


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clip(value: float, low: Optional[float], high: Optional[float]) -> Tuple[float, bool]:
    clipped = value
    if low is not None:
        clipped = max(low, clipped)
    if high is not None:
        clipped = min(high, clipped)
    return clipped, clipped != value


def _extract_q_dq(value: Any) -> Tuple[float, float]:
    if isinstance(value, Mapping):
        return _float(value.get("q"), 0.0), _float(value.get("dq"), 0.0)
    if isinstance(value, (tuple, list)):
        if len(value) >= 2:
            return _float(value[0], 0.0), _float(value[1], 0.0)
        if len(value) == 1:
            return _float(value[0], 0.0), 0.0
    return _float(value, 0.0), 0.0


class JointPDController:
    def __init__(
        self,
        joint_configs: Mapping[str, JointPDConfig],
        max_q_des_change_per_step: float = 0.03,
        excluded_joints: Optional[Iterable[str]] = None,
    ):
        self.joint_configs = dict(joint_configs)
        self.max_q_des_change_per_step = float(max_q_des_change_per_step)
        self.excluded_joints = set(excluded_joints or [])
        self._prev_q_des: Dict[str, float] = {}
        overlap = self.excluded_joints.intersection(self.joint_configs)
        if overlap:
            raise ValueError(f"JointPDController config includes excluded rail joints: {sorted(overlap)}")

    @classmethod
    def from_config_dicts(
        cls,
        robot_config: Mapping[str, Any],
        controller_config: Mapping[str, Any],
        excluded_joints: Optional[Iterable[str]] = None,
    ) -> "JointPDController":
        joint_pd = controller_config.get("joint_pd", {}) or {}
        default_kp = _float(joint_pd.get("default_kp", joint_pd.get("kp")), 20.0)
        default_kd = _float(joint_pd.get("default_kd", joint_pd.get("kd")), 0.8)
        default_torque = _float(joint_pd.get("torque_limit_default"), 18.0)
        max_change = _float(joint_pd.get("max_q_des_change_per_step"), 0.03)

        configs: Dict[str, JointPDConfig] = {}
        for leg_cfg in (robot_config.get("legs") or {}).values():
            joint_names = [str(name) for name in (leg_cfg.get("joint_names") or [])]
            limits = leg_cfg.get("joint_limit", {}) or {}
            lowers = limits.get("lower", []) or []
            uppers = limits.get("upper", []) or []
            torque_limits = leg_cfg.get("torque_limit", []) or []
            gains = leg_cfg.get("pd_gain", {}) or {}
            kps = gains.get("kp", []) or []
            kds = gains.get("kd", []) or []
            for index, joint_name in enumerate(joint_names):
                configs[joint_name] = JointPDConfig(
                    kp=_float(kps[index] if index < len(kps) else None, default_kp),
                    kd=_float(kds[index] if index < len(kds) else None, default_kd),
                    torque_limit=_float(
                        torque_limits[index] if index < len(torque_limits) else None,
                        default_torque,
                    ),
                    lower=_float(lowers[index], -math.inf) if index < len(lowers) else None,
                    upper=_float(uppers[index], math.inf) if index < len(uppers) else None,
                )
        return cls(configs, max_q_des_change_per_step=max_change, excluded_joints=excluded_joints)

    @property
    def joint_names(self) -> Tuple[str, ...]:
        return tuple(self.joint_configs)

    def reset_targets(self, joint_state: Mapping[str, Any]) -> None:
        self._prev_q_des = {
            joint_name: _extract_q_dq(joint_state[joint_name])[0]
            for joint_name in self.joint_configs
            if joint_name in joint_state
        }

    def compute(
        self,
        joint_state: Mapping[str, Any],
        q_des: Mapping[str, float],
        dq_des: Optional[Mapping[str, float]] = None,
    ) -> Dict[str, JointPDCommand]:
        commands: Dict[str, JointPDCommand] = {}
        dq_des = dq_des or {}

        for joint_name, cfg in self.joint_configs.items():
            if joint_name in self.excluded_joints:
                raise ValueError(f"Refusing to control excluded rail joint {joint_name}")
            if joint_name not in joint_state:
                raise KeyError(f"Missing joint state for {joint_name}")
            if joint_name not in q_des:
                raise KeyError(f"Missing q_des for {joint_name}")

            q, dq = _extract_q_dq(joint_state[joint_name])
            desired = float(q_des[joint_name])
            desired, limit_warning = _clip(desired, cfg.lower, cfg.upper)

            previous = self._prev_q_des.get(joint_name, q)
            delta = desired - previous
            if abs(delta) > self.max_q_des_change_per_step:
                desired = previous + math.copysign(self.max_q_des_change_per_step, delta)
            self._prev_q_des[joint_name] = desired

            desired_dq = float(dq_des.get(joint_name, 0.0))
            tau_raw = cfg.kp * (desired - q) + cfg.kd * (desired_dq - dq)
            tau = max(-cfg.torque_limit, min(cfg.torque_limit, tau_raw))
            saturated = tau != tau_raw
            commands[joint_name] = JointPDCommand(
                joint_name=joint_name,
                q=q,
                dq=dq,
                q_des=desired,
                dq_des=desired_dq,
                tau=tau,
                saturated=saturated,
                limit_warning=limit_warning,
            )

        return commands


__all__ = ["JointPDCommand", "JointPDConfig", "JointPDController"]
