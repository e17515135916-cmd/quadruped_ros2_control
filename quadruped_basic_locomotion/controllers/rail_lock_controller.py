#!/usr/bin/env python3
"""Rail locking controller for walking-mode diagnostics and locomotion.

The rail is deliberately not part of any leg IK or leg PD interface.  This
controller owns rail targets and returns independent rail force commands.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Tuple

import yaml


Number = float
JointStateValue = Tuple[Number, Number]


@dataclass(frozen=True)
class RailLockConfig:
    joint_names: Tuple[str, ...]
    enabled: bool = True
    lock_in_walking: bool = True
    lock_position_source: str = "initial"
    lock_position: float = 0.0
    lock_position_map: Mapping[str, float] | None = None
    kp: float = 3000.0
    kd: float = 80.0
    max_force: float = 500.0
    warning_error_threshold_m: float = 0.002
    safety_error_threshold_m: float = 0.010


@dataclass(frozen=True)
class RailLockCommand:
    joint_name: str
    q: float
    dq: float
    q0: float
    error: float
    force: float
    locked: bool
    warning: bool
    safety_stop: bool


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clip(value: float, limit: float) -> float:
    if limit <= 0.0:
        return value
    return max(-limit, min(limit, value))


def _normalize_joint_names(rail_section: Mapping[str, Any]) -> Tuple[str, ...]:
    names = []
    raw_names = rail_section.get("joint_names", [])
    if isinstance(raw_names, str):
        raw_names = [raw_names]
    for name in raw_names or []:
        if name and str(name).strip():
            names.append(str(name).strip())

    single = str(rail_section.get("joint_name", "") or "").strip()
    if single and single not in {"AUTO", "AUTO_DETECT", "AUTO_DETECT_PRISMATIC_RAILS"}:
        names.append(single)

    deduped = []
    for name in names:
        if name not in deduped:
            deduped.append(name)
    return tuple(deduped)


def _extract_q_dq(value: Any) -> JointStateValue:
    if isinstance(value, Mapping):
        return _as_float(value.get("q")), _as_float(value.get("dq"))
    if isinstance(value, (tuple, list)):
        if len(value) >= 2:
            return _as_float(value[0]), _as_float(value[1])
        if len(value) == 1:
            return _as_float(value[0]), 0.0
    return _as_float(value), 0.0


class RailLockController:
    """Locks one or more prismatic rail joints at their initial/configured q."""

    def __init__(self, config: RailLockConfig):
        if not config.joint_names and config.enabled:
            raise ValueError("RailLockController requires at least one rail joint name.")
        self.config = config
        self._lock_positions: Dict[str, float] = {}
        self._initialized = False
        self._last_commands: Dict[str, RailLockCommand] = {}

    @classmethod
    def from_yaml_files(
        cls,
        robot_config_path: str | Path,
        rail_config_path: str | Path,
        detected_rail_joints: Optional[Iterable[str]] = None,
    ) -> "RailLockController":
        with Path(robot_config_path).open("r", encoding="utf-8") as f:
            robot_config = yaml.safe_load(f) or {}
        with Path(rail_config_path).open("r", encoding="utf-8") as f:
            rail_config = yaml.safe_load(f) or {}
        return cls.from_config_dicts(robot_config, rail_config, detected_rail_joints)

    @classmethod
    def from_config_dicts(
        cls,
        robot_config: Mapping[str, Any],
        rail_config: Mapping[str, Any],
        detected_rail_joints: Optional[Iterable[str]] = None,
    ) -> "RailLockController":
        robot_rail = robot_config.get("rail", {}) or {}
        rail_lock = rail_config.get("rail_lock", rail_config.get("rail", {})) or {}
        rail_pd = rail_config.get("rail_pd", {}) or {}

        merged: Dict[str, Any] = {}
        merged.update(robot_rail)
        merged.update(rail_lock)
        joint_names = _normalize_joint_names(merged)
        if not joint_names and detected_rail_joints:
            joint_names = tuple(str(name) for name in detected_rail_joints)

        config = RailLockConfig(
            joint_names=joint_names,
            enabled=bool(merged.get("enabled", True)),
            lock_in_walking=bool(merged.get("lock_in_walking", True)),
            lock_position_source=str(merged.get("lock_position_source", "initial")),
            lock_position=_as_float(merged.get("lock_position", 0.0)),
            lock_position_map={
                str(name): _as_float(value)
                for name, value in (merged.get("lock_position_map", {}) or {}).items()
            },
            kp=_as_float(rail_pd.get("kp", merged.get("kp", 3000.0)), 3000.0),
            kd=_as_float(rail_pd.get("kd", merged.get("kd", 80.0)), 80.0),
            max_force=_as_float(rail_pd.get("max_force", merged.get("max_force", 500.0)), 500.0),
            warning_error_threshold_m=_as_float(
                merged.get("warning_error_threshold_m", 0.002), 0.002
            ),
            safety_error_threshold_m=_as_float(
                merged.get("safety_error_threshold_m", 0.010), 0.010
            ),
        )
        return cls(config)

    @property
    def rail_joint_names(self) -> Tuple[str, ...]:
        return self.config.joint_names

    @property
    def lock_positions(self) -> Dict[str, float]:
        return dict(self._lock_positions)

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def last_commands(self) -> Dict[str, RailLockCommand]:
        return dict(self._last_commands)

    def is_rail_joint(self, joint_name: str) -> bool:
        return joint_name in self.config.joint_names

    def validate_leg_joint_exclusion(self, leg_joint_map: Mapping[str, Iterable[str]]) -> None:
        rail_set = set(self.config.joint_names)
        for leg_name, joint_names in leg_joint_map.items():
            overlap = rail_set.intersection(str(name) for name in joint_names)
            if overlap:
                overlap_text = ", ".join(sorted(overlap))
                raise ValueError(
                    f"Leg {leg_name} includes rail joint(s): {overlap_text}. "
                    "Rail joints must not enter leg IK or leg PD."
                )

    def initialize(self, joint_state: Mapping[str, Any]) -> None:
        """Capture q0.  Walking code must not mutate q0 after this point."""
        if not self.config.enabled:
            self._initialized = True
            return

        lock_positions: Dict[str, float] = {}
        for joint_name in self.config.joint_names:
            if self.config.lock_position_source == "configured":
                if self.config.lock_position_map and joint_name in self.config.lock_position_map:
                    q0 = self.config.lock_position_map[joint_name]
                else:
                    q0 = self.config.lock_position
            else:
                if joint_name not in joint_state:
                    raise KeyError(f"Missing initial rail joint state for {joint_name}")
                q0, _ = _extract_q_dq(joint_state[joint_name])
            lock_positions[joint_name] = float(q0)

        self._lock_positions = lock_positions
        self._initialized = True

    def compute(self, joint_state: Mapping[str, Any]) -> Dict[str, RailLockCommand]:
        """Return independent rail force commands.

        Force formula:
            force = kp * (q0 - q) + kd * (0 - dq)
        """
        if not self._initialized:
            self.initialize(joint_state)

        commands: Dict[str, RailLockCommand] = {}
        if not self.config.enabled:
            self._last_commands = commands
            return commands

        for joint_name in self.config.joint_names:
            if joint_name not in joint_state:
                raise KeyError(f"Missing rail joint state for {joint_name}")

            q, dq = _extract_q_dq(joint_state[joint_name])
            q0 = self._lock_positions[joint_name]
            error = q0 - q
            raw_force = self.config.kp * error + self.config.kd * (0.0 - dq)
            force = _clip(raw_force, self.config.max_force)
            abs_error = abs(error)
            commands[joint_name] = RailLockCommand(
                joint_name=joint_name,
                q=q,
                dq=dq,
                q0=q0,
                error=error,
                force=force,
                locked=self.config.lock_in_walking,
                warning=abs_error > self.config.warning_error_threshold_m,
                safety_stop=abs_error > self.config.safety_error_threshold_m,
            )

        self._last_commands = commands
        return commands

    def safety_stop_requested(self) -> bool:
        return any(command.safety_stop for command in self._last_commands.values())

    def status_rows(self) -> Tuple[Dict[str, Any], ...]:
        rows = []
        for command in self._last_commands.values():
            rows.append(
                {
                    "rail_joint_name": command.joint_name,
                    "rail_q": command.q,
                    "rail_q0": command.q0,
                    "rail_error": command.error,
                    "rail_force": command.force,
                    "rail_locked": command.locked,
                    "warning": command.warning,
                    "safety_stop": command.safety_stop,
                }
            )
        return tuple(rows)

    def assert_finite(self) -> None:
        for command in self._last_commands.values():
            values = (command.q, command.dq, command.q0, command.error, command.force)
            if not all(math.isfinite(value) for value in values):
                raise FloatingPointError(f"Non-finite rail command for {command.joint_name}")

    def apply_pybullet_position_lock(
        self,
        pybullet_client: Any,
        body_id: int,
        joint_name_to_index: Mapping[str, int],
    ) -> None:
        """Fallback lock for PyBullet POSITION_CONTROL backends.

        This is not used by leg PD.  It is a simulator-specific convenience when
        true fixed-joint constraints are unavailable.
        """
        if not self._initialized:
            raise RuntimeError("RailLockController must be initialized before applying locks.")
        for joint_name, q0 in self._lock_positions.items():
            if joint_name not in joint_name_to_index:
                raise KeyError(f"Missing PyBullet index for rail joint {joint_name}")
            pybullet_client.setJointMotorControl2(
                bodyUniqueId=body_id,
                jointIndex=joint_name_to_index[joint_name],
                controlMode=pybullet_client.POSITION_CONTROL,
                targetPosition=q0,
                targetVelocity=0.0,
                force=self.config.max_force,
            )


__all__ = [
    "RailLockCommand",
    "RailLockConfig",
    "RailLockController",
]
