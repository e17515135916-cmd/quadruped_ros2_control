#!/usr/bin/env python3
"""Automated PASS/FAIL check for Dog2 window-frame crossing."""

from __future__ import annotations

import os
import math
import sys
import time
from typing import Dict, Optional, Set

import rclpy
from dog2_interfaces.msg import ContactPhase, RobotState
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float64MultiArray, String


class CrossingCheckNode(Node):
    def __init__(self) -> None:
        super().__init__("dog2_crossing_check")

        self.declare_parameter("timeout_sec", 150.0)
        self.declare_parameter("freshness_timeout_sec", 2.0)
        self.declare_parameter("poll_period_sec", 0.1)
        self.declare_parameter("window_x_position", 1.55)
        self.declare_parameter("body_pass_margin", 0.10)
        self.declare_parameter("rail_motion_threshold_m", 0.025)
        self.declare_parameter("mode", "stage_smoke")
        self.declare_parameter("full_required_stage", "CROSSING:RECOVERY")
        self.declare_parameter("body_z_min", 0.08)
        self.declare_parameter("body_z_max", 0.35)
        self.declare_parameter("max_abs_roll", 0.55)
        self.declare_parameter("max_abs_pitch", 0.55)
        self.declare_parameter("possible_flip_warning_roll", 2.8)
        self.declare_parameter("result_file", "")
        self.declare_parameter("trigger_topic", "/enable_crossing")
        self.declare_parameter("crossing_state_topic", "/dog2/mpc/crossing_state")
        self.declare_parameter("joint_state_topic", "/joint_states")
        self.declare_parameter("odom_topic", "/dog2/state_estimation/odom")
        self.declare_parameter("robot_state_topic", "/dog2/state_estimation/robot_state")
        self.declare_parameter("contact_phase_topic", "/dog2/gait/contact_phase")
        self.declare_parameter("foot_force_topic", "/dog2/mpc/foot_forces")
        self.declare_parameter("joint_effort_topic", "/dog2/wbc/joint_effort_command")
        self.declare_parameter("rail_effort_topic", "/dog2/wbc/rail_effort_command")
        self.declare_parameter("effort_command_topic", "/effort_controller/commands")

        self._timeout_sec = float(self.get_parameter("timeout_sec").value)
        self._freshness_timeout_sec = float(self.get_parameter("freshness_timeout_sec").value)
        self._poll_period_sec = float(self.get_parameter("poll_period_sec").value)
        self._window_x_position = float(self.get_parameter("window_x_position").value)
        self._body_pass_margin = float(self.get_parameter("body_pass_margin").value)
        self._rail_motion_threshold_m = float(
            self.get_parameter("rail_motion_threshold_m").value
        )
        self._mode = str(self.get_parameter("mode").value).strip().lower()
        self._full_required_stage = str(self.get_parameter("full_required_stage").value)
        self._body_z_min_limit = float(self.get_parameter("body_z_min").value)
        self._body_z_max_limit = float(self.get_parameter("body_z_max").value)
        self._max_abs_roll_limit = float(self.get_parameter("max_abs_roll").value)
        self._max_abs_pitch_limit = float(self.get_parameter("max_abs_pitch").value)
        self._possible_flip_warning_roll = float(
            self.get_parameter("possible_flip_warning_roll").value
        )
        self._result_file = str(self.get_parameter("result_file").value)
        self._deadline = time.monotonic() + self._timeout_sec

        self._last_odom_sec: Optional[float] = None
        self._last_robot_state_sec: Optional[float] = None
        self._last_contact_phase_sec: Optional[float] = None
        self._last_foot_force_sec: Optional[float] = None
        self._last_joint_effort_sec: Optional[float] = None
        self._last_rail_effort_sec: Optional[float] = None
        self._last_effort_command_sec: Optional[float] = None
        self._last_joint_state_sec: Optional[float] = None
        self._trigger_seen = False
        self._current_crossing_state = "UNKNOWN"
        self._crossing_states_seen: Set[str] = set()
        self._latest_x = float("-inf")
        self._max_x = float("-inf")
        self._latest_z = float("nan")
        self._min_z = float("inf")
        self._max_z = float("-inf")
        self._latest_roll = float("nan")
        self._latest_pitch = float("nan")
        self._max_abs_roll = 0.0
        self._max_abs_pitch = 0.0
        self._latest_level_roll = float("nan")
        self._latest_level_pitch = float("nan")
        self._latest_level_tilt = float("nan")
        self._latest_body_up_z = float("nan")
        self._max_abs_level_roll = 0.0
        self._max_abs_level_pitch = 0.0
        self._max_level_tilt = 0.0
        self._min_body_up_z = 1.0
        self._possible_flip_warning = False
        self._rail_names = (
            "lf_rail_joint",
            "lh_rail_joint",
            "rh_rail_joint",
            "rf_rail_joint",
        )
        self._initial_rail_positions: Dict[str, float] = {}
        self._max_rail_delta = 0.0
        self._last_status_log_sec = 0.0
        self._stage_first_seen_sec: Dict[str, float] = {}
        self.exit_code = 1
        self._done = False

        self.create_subscription(
            Bool,
            str(self.get_parameter("trigger_topic").value),
            self._on_trigger,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("crossing_state_topic").value),
            self._on_crossing_state,
            20,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("joint_state_topic").value),
            self._on_joint_state,
            20,
        )
        self.create_subscription(
            Odometry,
            str(self.get_parameter("odom_topic").value),
            self._on_odom,
            20,
        )
        self.create_subscription(
            RobotState,
            str(self.get_parameter("robot_state_topic").value),
            self._on_robot_state,
            20,
        )
        self.create_subscription(
            ContactPhase,
            str(self.get_parameter("contact_phase_topic").value),
            self._on_contact_phase,
            20,
        )
        self.create_subscription(
            Float64MultiArray,
            str(self.get_parameter("foot_force_topic").value),
            self._on_foot_force,
            20,
        )
        self.create_subscription(
            Float64MultiArray,
            str(self.get_parameter("joint_effort_topic").value),
            self._on_joint_effort,
            20,
        )
        self.create_subscription(
            Float64MultiArray,
            str(self.get_parameter("rail_effort_topic").value),
            self._on_rail_effort,
            20,
        )
        self.create_subscription(
            Float64MultiArray,
            str(self.get_parameter("effort_command_topic").value),
            self._on_effort_command,
            20,
        )

        self.create_timer(self._poll_period_sec, self._poll)

    @staticmethod
    def _now_sec() -> float:
        return time.monotonic()

    def _age_sec(self, stamp_sec: Optional[float]) -> float:
        if stamp_sec is None:
            return float("inf")
        return max(0.0, self._now_sec() - stamp_sec)

    def _is_fresh(self, stamp_sec: Optional[float]) -> bool:
        return self._age_sec(stamp_sec) <= self._freshness_timeout_sec

    def _write_result(self, status: str, message: str) -> None:
        if not self._result_file:
            return
        try:
            directory = os.path.dirname(self._result_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self._result_file, "a", encoding="utf-8") as handle:
                handle.write(f"{status}: {message}\n")
        except Exception as exc:
            self.get_logger().warn(f"Failed to write crossing result file: {exc}")

    @staticmethod
    def _quat_to_rpy(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1.0:
            pitch = math.copysign(math.pi / 2.0, sinp)
        else:
            pitch = math.asin(sinp)

        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    @staticmethod
    def _level_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float, float]:
        norm = math.sqrt(x * x + y * y + z * z + w * w)
        if norm < 1e-9:
            return float("nan"), float("nan"), float("nan"), float("nan")
        x /= norm
        y /= norm
        z /= norm
        w /= norm

        # Third column of body-to-world rotation matrix, i.e. body +Z in world.
        body_z_x = 2.0 * (x * z + w * y)
        body_z_y = 2.0 * (y * z - w * x)
        body_z_z = 1.0 - 2.0 * (x * x + y * y)
        up_z = max(-1.0, min(1.0, body_z_z))
        lateral_norm = math.sqrt(body_z_x * body_z_x + body_z_y * body_z_y)
        tilt = math.atan2(lateral_norm, up_z)
        denom = max(0.15, abs(up_z))
        roll_like = math.atan2(-body_z_y, denom)
        pitch_like = math.atan2(body_z_x, denom)
        return roll_like, pitch_like, tilt, up_z

    def _stage_timeline_str(self) -> str:
        if not self._stage_first_seen_sec:
            return "none"
        start_sec = min(self._stage_first_seen_sec.values())
        parts = []
        for stage, stamp in sorted(self._stage_first_seen_sec.items(), key=lambda item: item[1]):
            parts.append(f"{stage}@{stamp - start_sec:.2f}s")
        return ",".join(parts)

    def _finish(self, success: bool, message: str) -> None:
        if self._done:
            return
        self._done = True
        self.exit_code = 0 if success else 1
        if success:
            if self._mode == "full":
                status = "PASS_FULL"
            elif self._mode == "body_shift":
                status = "PASS_BODY_SHIFT"
            else:
                status = "PASS_STAGE_SMOKE"
        else:
            status = "FAIL"
        flip_note = "; warning=POSSIBLE_EULER_WRAP_OR_FLIP" if self._possible_flip_warning else ""
        self._write_result(
            status,
            (
                f"{message}; stage={self._current_crossing_state}; "
                f"max_x={self._max_x:.3f}; min_z={self._min_z:.3f}; "
                f"max_z={self._max_z:.3f}; max_rail_delta={self._max_rail_delta:.3f}; "
                f"max_abs_roll={self._max_abs_roll:.3f}; max_abs_pitch={self._max_abs_pitch:.3f}; "
                f"max_abs_level_roll={self._max_abs_level_roll:.3f}; "
                f"max_abs_level_pitch={self._max_abs_level_pitch:.3f}; "
                f"max_level_tilt={self._max_level_tilt:.3f}; min_body_up_z={self._min_body_up_z:.3f}; "
                f"timeline={self._stage_timeline_str()}{flip_note}"
            ),
        )
        log = self.get_logger().info if success else self.get_logger().error
        log(
            f"{status}: {message}; stage={self._current_crossing_state}; "
            f"max_x={self._max_x:.3f}; min_z={self._min_z:.3f}; "
            f"max_z={self._max_z:.3f}; max_rail_delta={self._max_rail_delta:.3f}; "
            f"max_abs_roll={self._max_abs_roll:.3f}; max_abs_pitch={self._max_abs_pitch:.3f}; "
            f"max_abs_level_roll={self._max_abs_level_roll:.3f}; "
            f"max_abs_level_pitch={self._max_abs_level_pitch:.3f}; "
            f"max_level_tilt={self._max_level_tilt:.3f}; min_body_up_z={self._min_body_up_z:.3f}; "
            f"timeline={self._stage_timeline_str()}{flip_note}"
        )
        # Raising SystemExit from an rclpy timer callback can be swallowed by
        # the executor, leaving the launch test running after the result file
        # has already been written. This node is a test sentinel, so exit the
        # process directly to let launch cleanup run deterministically.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(self.exit_code)

    def _on_trigger(self, msg: Bool) -> None:
        if msg.data:
            self._trigger_seen = True

    def _on_crossing_state(self, msg: String) -> None:
        self._current_crossing_state = msg.data
        if msg.data.startswith("CROSSING:"):
            self._crossing_states_seen.add(msg.data)
            self._stage_first_seen_sec.setdefault(msg.data, self._now_sec())

    def _on_joint_state(self, msg: JointState) -> None:
        self._last_joint_state_sec = self._now_sec()
        rail_positions = {
            name: float(position)
            for name, position in zip(msg.name, msg.position)
            if name in self._rail_names
        }
        if len(rail_positions) != len(self._rail_names):
            return

        if not self._initial_rail_positions:
            self._initial_rail_positions = dict(rail_positions)
            return

        for name in self._rail_names:
            delta = abs(rail_positions[name] - self._initial_rail_positions[name])
            self._max_rail_delta = max(self._max_rail_delta, delta)

    def _on_odom(self, msg: Odometry) -> None:
        self._last_odom_sec = self._now_sec()
        self._latest_x = float(msg.pose.pose.position.x)
        self._latest_z = float(msg.pose.pose.position.z)
        self._max_x = max(self._max_x, self._latest_x)
        self._min_z = min(self._min_z, self._latest_z)
        self._max_z = max(self._max_z, self._latest_z)
        qx = float(msg.pose.pose.orientation.x)
        qy = float(msg.pose.pose.orientation.y)
        qz = float(msg.pose.pose.orientation.z)
        qw = float(msg.pose.pose.orientation.w)
        roll, pitch, _ = self._quat_to_rpy(qx, qy, qz, qw)
        self._latest_roll = roll
        self._latest_pitch = pitch
        self._max_abs_roll = max(self._max_abs_roll, abs(roll))
        self._max_abs_pitch = max(self._max_abs_pitch, abs(pitch))
        level_roll, level_pitch, level_tilt, body_up_z = self._level_from_quat(qx, qy, qz, qw)
        if math.isfinite(level_tilt):
            self._latest_level_roll = level_roll
            self._latest_level_pitch = level_pitch
            self._latest_level_tilt = level_tilt
            self._latest_body_up_z = body_up_z
            self._max_abs_level_roll = max(self._max_abs_level_roll, abs(level_roll))
            self._max_abs_level_pitch = max(self._max_abs_level_pitch, abs(level_pitch))
            self._max_level_tilt = max(self._max_level_tilt, level_tilt)
            self._min_body_up_z = min(self._min_body_up_z, body_up_z)
        if abs(roll) >= self._possible_flip_warning_roll:
            self._possible_flip_warning = True

    def _on_robot_state(self, _msg: RobotState) -> None:
        self._last_robot_state_sec = self._now_sec()

    def _on_contact_phase(self, _msg: ContactPhase) -> None:
        self._last_contact_phase_sec = self._now_sec()

    def _on_foot_force(self, _msg: Float64MultiArray) -> None:
        self._last_foot_force_sec = self._now_sec()

    def _on_joint_effort(self, _msg: Float64MultiArray) -> None:
        self._last_joint_effort_sec = self._now_sec()

    def _on_rail_effort(self, _msg: Float64MultiArray) -> None:
        self._last_rail_effort_sec = self._now_sec()

    def _on_effort_command(self, _msg: Float64MultiArray) -> None:
        self._last_effort_command_sec = self._now_sec()

    def _missing_streams(self) -> list[str]:
        missing = []
        if not self._is_fresh(self._last_odom_sec):
            missing.append("/dog2/state_estimation/odom")
        if not self._is_fresh(self._last_robot_state_sec):
            missing.append("/dog2/state_estimation/robot_state")
        if not self._is_fresh(self._last_contact_phase_sec):
            missing.append("/dog2/gait/contact_phase")
        if not self._is_fresh(self._last_joint_state_sec):
            missing.append("/joint_states")
        if not self._is_fresh(self._last_foot_force_sec):
            missing.append("/dog2/mpc/foot_forces")
        if not self._is_fresh(self._last_joint_effort_sec):
            missing.append("/dog2/wbc/joint_effort_command")
        if not self._is_fresh(self._last_rail_effort_sec):
            missing.append("/dog2/wbc/rail_effort_command")
        if not self._is_fresh(self._last_effort_command_sec):
            missing.append("/effort_controller/commands")
        return missing

    def _stage_smoke_ready(self) -> tuple[bool, str]:
        if not self._trigger_seen:
            return False, "waiting for crossing trigger"
        if not self._crossing_states_seen:
            return False, "waiting for CROSSING stage"
        if self._max_rail_delta < self._rail_motion_threshold_m:
            return False, "rail motion below threshold"
        if self._max_x < (self._window_x_position + self._body_pass_margin):
            return False, "body has not cleared window x region"
        missing = self._missing_streams()
        if missing:
            return False, "stale streams: " + ", ".join(missing)
        return True, "crossing stage smoke validated"

    def _full_ready(self) -> tuple[bool, str]:
        ready, message = self._stage_smoke_ready()
        if not ready:
            return ready, message
        required_stages = (
            "CROSSING:FRONT_LEGS_TRANSIT",
            "CROSSING:REAR_LEGS_TRANSIT",
            self._full_required_stage,
        )
        for stage in required_stages:
            if stage not in self._crossing_states_seen:
                return False, f"never reached required stage {stage}"
        if self._min_z < self._body_z_min_limit:
            return False, f"body_z below limit {self._body_z_min_limit:.3f}"
        if self._max_z > self._body_z_max_limit:
            return False, f"body_z above limit {self._body_z_max_limit:.3f}"
        if self._max_abs_roll > self._max_abs_roll_limit:
            return False, f"roll above limit {self._max_abs_roll_limit:.3f}"
        if self._max_abs_pitch > self._max_abs_pitch_limit:
            return False, f"pitch above limit {self._max_abs_pitch_limit:.3f}"
        return True, "full crossing validated"

    def _body_shift_ready(self) -> tuple[bool, str]:
        ready, message = self._stage_smoke_ready()
        if not ready:
            return ready, message
        required_stages = (
            "CROSSING:BODY_FORWARD_SHIFT",
            "CROSSING:FRONT_LEGS_TRANSIT",
        )
        for stage in required_stages:
            if stage not in self._crossing_states_seen:
                return False, f"never reached required stage {stage}"
        return True, "body shift crossing validated"

    def _poll(self) -> None:
        if self._done:
            return

        if self._mode == "full":
            ready, message = self._full_ready()
        elif self._mode == "body_shift":
            ready, message = self._body_shift_ready()
        else:
            ready, message = self._stage_smoke_ready()
        if ready:
            self._finish(True, message)
            return

        now = self._now_sec()
        if now >= self._deadline:
            missing = self._missing_streams()
            suffix = f"; missing={','.join(missing)}" if missing else ""
            self._finish(False, f"{message}{suffix}")
            return

        if now - self._last_status_log_sec >= 5.0:
            self._last_status_log_sec = now
            self.get_logger().info(
                "crossing_check: mode=%s trigger=%s stage=%s max_x=%.3f latest_z=%.3f min_z=%.3f max_z=%.3f roll=%.3f pitch=%.3f level=[%.3f,%.3f] tilt=%.3f up_z=%.3f max_roll=%.3f max_pitch=%.3f max_level_tilt=%.3f min_up_z=%.3f max_rail_delta=%.3f timeline=%s"
                % (
                    self._mode,
                    self._trigger_seen,
                    self._current_crossing_state,
                    self._max_x,
                    self._latest_z,
                    self._min_z,
                    self._max_z,
                    self._latest_roll,
                    self._latest_pitch,
                    self._latest_level_roll,
                    self._latest_level_pitch,
                    self._latest_level_tilt,
                    self._latest_body_up_z,
                    self._max_abs_roll,
                    self._max_abs_pitch,
                    self._max_level_tilt,
                    self._min_body_up_z,
                    self._max_rail_delta,
                    self._stage_timeline_str(),
                )
            )


def main() -> None:
    rclpy.init()
    node = CrossingCheckNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        exit_code = node.exit_code
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(exit_code)
