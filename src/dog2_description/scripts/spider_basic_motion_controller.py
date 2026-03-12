#!/usr/bin/env python3
"""Basic crawl-gait motion controller for the spider robot.

Design alignment:
- 50 Hz control loop
- 16-channel output via two trajectory controllers
- Rails are continuously locked to 0.0 m
- Crawl gait with one swing leg and three stance legs
"""

from __future__ import annotations

import math
import rclpy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


LEG_IDS = ("leg1", "leg2", "leg3", "leg4")
LEG_ORDER = ("leg1", "leg3", "leg2", "leg4")
LEG_TO_PREFIX = {
    "leg1": "lf",
    "leg2": "rf",
    "leg3": "lh",
    "leg4": "rh",
}
LEG_TO_RAIL = {
    "leg1": "j1",
    "leg2": "j2",
    "leg3": "j3",
    "leg4": "j4",
}


@dataclass
class GaitConfig:
    stride_length: float = 0.08
    stride_height: float = 0.03
    cycle_time: float = 2.0
    duty_factor: float = 0.75
    body_height: float = 0.27


@dataclass
class LegParameters:
    leg_id: str
    base_position: np.ndarray
    l1_hip_offset: float
    l2_thigh: float
    l3_shin: float
    joint_limits: Dict[str, Tuple[float, float]]


class TrajectoryPlanner:
    def plan_swing_trajectory(
        self,
        start_pos: np.ndarray,
        end_pos: np.ndarray,
        duration: float,
        height: float,
    ) -> Callable[[float], np.ndarray]:
        _ = duration

        def _traj(alpha: float) -> np.ndarray:
            alpha_clamped = float(np.clip(alpha, 0.0, 1.0))
            pos = start_pos + alpha_clamped * (end_pos - start_pos)
            pos[2] = start_pos[2] + 4.0 * height * alpha_clamped * (1.0 - alpha_clamped)
            return pos

        return _traj

    def plan_stance_trajectory(
        self,
        start_pos: np.ndarray,
        end_pos: np.ndarray,
        duration: float,
    ) -> Callable[[float], np.ndarray]:
        _ = duration

        def _traj(alpha: float) -> np.ndarray:
            alpha_clamped = float(np.clip(alpha, 0.0, 1.0))
            return start_pos + alpha_clamped * (end_pos - start_pos)

        return _traj


class GaitGenerator:
    def __init__(self, config: GaitConfig, planner: TrajectoryPlanner):
        self.config = config
        self.planner = planner
        self.phase = 0.0
        self.phase_offsets = {
            "leg1": 0.0,
            "leg3": 0.25,
            "leg2": 0.50,
            "leg4": 0.75,
        }
        self.nominal_feet = {
            "leg1": np.array([0.18, -0.12, -self.config.body_height]),
            "leg2": np.array([0.18, 0.12, -self.config.body_height]),
            "leg3": np.array([-0.18, -0.12, -self.config.body_height]),
            "leg4": np.array([-0.18, 0.12, -self.config.body_height]),
        }
        self.current_velocity = (0.0, 0.0, 0.0)

    def update(self, dt: float, velocity: Tuple[float, float, float]) -> None:
        self.current_velocity = velocity
        vx, vy, _ = velocity
        speed = float(np.hypot(vx, vy))
        speed_scale = float(np.clip(speed / 0.15, 0.15, 1.0))
        phase_rate = speed_scale / max(self.config.cycle_time, 1e-4)
        self.phase = (self.phase + dt * phase_rate) % 1.0

    def _step_vector(self, leg_id: str) -> np.ndarray:
        vx, vy, omega = self.current_velocity
        cycle = self.config.cycle_time
        translational = np.array([vx * cycle * 0.5, vy * cycle * 0.5, 0.0])
        nominal = self.nominal_feet[leg_id]
        rotational = omega * cycle * 0.20 * np.array([-nominal[1], nominal[0], 0.0])
        step_vec = translational + rotational
        max_len = max(self.config.stride_length, 1e-4)
        norm = float(np.linalg.norm(step_vec[:2]))
        if norm > max_len:
            step_vec *= max_len / norm
        return step_vec

    def _leg_phase(self, leg_id: str) -> float:
        return (self.phase + self.phase_offsets[leg_id]) % 1.0

    def is_stance_phase(self, leg_id: str) -> bool:
        swing_ratio = 1.0 - self.config.duty_factor
        return self._leg_phase(leg_id) >= swing_ratio

    def get_support_triangle(self) -> List[str]:
        return [leg for leg in LEG_IDS if self.is_stance_phase(leg)]

    def get_foot_target(self, leg_id: str) -> Tuple[float, float, float]:
        leg_phase = self._leg_phase(leg_id)
        swing_ratio = 1.0 - self.config.duty_factor
        nominal = self.nominal_feet[leg_id]
        step_vec = self._step_vector(leg_id)
        start = nominal - 0.5 * step_vec
        end = nominal + 0.5 * step_vec

        if leg_phase < swing_ratio:
            alpha = leg_phase / max(swing_ratio, 1e-6)
            traj = self.planner.plan_swing_trajectory(
                start_pos=start,
                end_pos=end,
                duration=swing_ratio * self.config.cycle_time,
                height=self.config.stride_height,
            )
            pos = traj(alpha)
        else:
            alpha = (leg_phase - swing_ratio) / max(self.config.duty_factor, 1e-6)
            traj = self.planner.plan_stance_trajectory(
                start_pos=end,
                end_pos=start,
                duration=self.config.duty_factor * self.config.cycle_time,
            )
            pos = traj(alpha)

        return float(pos[0]), float(pos[1]), float(pos[2])


class KinematicsSolver:
    def __init__(self, leg_params: Dict[str, LegParameters]):
        self.leg_params = leg_params

    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, v))

    def solve_ik(
        self,
        leg_id: str,
        foot_pos: Tuple[float, float, float],
        rail_offset: float = 0.0,
    ) -> Optional[Tuple[float, float, float, float]]:
        params = self.leg_params[leg_id]
        target = np.asarray(foot_pos, dtype=float) - params.base_position
        px, py, pz = float(target[0]), float(target[1]), float(target[2])

        s_m = float(rail_offset)
        # Foot directly below hip should map to ~0 rad instead of +/-pi.
        theta_haa = math.atan2(py, -pz if abs(pz) > 1e-8 else -1e-8)

        radial = math.sqrt(py * py + pz * pz) - params.l1_hip_offset
        d = math.sqrt(px * px + radial * radial)
        if d < 1e-8:
            return None

        min_reach = abs(params.l2_thigh - params.l3_shin) + 1e-4
        max_reach = (params.l2_thigh + params.l3_shin) - 1e-4
        d_clamped = self._clamp(d, min_reach, max_reach)
        if abs(d_clamped - d) > 1e-8:
            scale = d_clamped / d
            px *= scale
            radial *= scale
            d = d_clamped

        cos_k = (
            d * d
            - params.l2_thigh * params.l2_thigh
            - params.l3_shin * params.l3_shin
        ) / (2.0 * params.l2_thigh * params.l3_shin)
        cos_k = self._clamp(cos_k, -1.0, 1.0)
        theta_kfe = math.acos(cos_k)

        alpha = math.atan2(px, radial)
        beta = math.atan2(
            params.l3_shin * math.sin(theta_kfe),
            params.l2_thigh + params.l3_shin * math.cos(theta_kfe),
        )
        theta_hfe = alpha - beta

        limits = params.joint_limits
        if not (limits["haa"][0] <= theta_haa <= limits["haa"][1]):
            return None
        if not (limits["hfe"][0] <= theta_hfe <= limits["hfe"][1]):
            return None
        if not (limits["kfe"][0] <= theta_kfe <= limits["kfe"][1]):
            return None

        return s_m, theta_haa, theta_hfe, theta_kfe

    def solve_fk(
        self,
        leg_id: str,
        joint_positions: Tuple[float, float, float, float],
    ) -> Tuple[float, float, float]:
        params = self.leg_params[leg_id]
        _, theta_haa, theta_hfe, theta_kfe = joint_positions

        radial = params.l1_hip_offset
        radial += params.l2_thigh * math.cos(theta_hfe)
        radial += params.l3_shin * math.cos(theta_hfe + theta_kfe)

        px = params.l2_thigh * math.sin(theta_hfe) + params.l3_shin * math.sin(theta_hfe + theta_kfe)
        py = radial * math.sin(theta_haa)
        pz = radial * math.cos(theta_haa)

        pos = params.base_position + np.array([px, py, pz])
        return float(pos[0]), float(pos[1]), float(pos[2])


class JointController:
    def __init__(self, node: Node):
        self.node = node
        self.revolute_pub = node.create_publisher(
            JointTrajectory,
            "/joint_trajectory_controller/joint_trajectory",
            10,
        )
        self.rail_pub = node.create_publisher(
            JointTrajectory,
            "/rail_position_controller/joint_trajectory",
            10,
        )
        self._joint_state_map: Dict[str, float] = {}
        self._last_rail_check_time = 0.0

        node.create_subscription(JointState, "/joint_states", self._joint_state_cb, 20)

        self.joint_limits = {
            "haa": (-2.618, 2.618),
            "hfe": (-2.8, 2.8),
            "kfe": (-2.8, 2.8),
        }

    def _joint_state_cb(self, msg: JointState) -> None:
        for name, pos in zip(msg.name, msg.position):
            self._joint_state_map[name] = float(pos)

    def check_joint_limits(self, joint_name: str, position: float) -> float:
        if joint_name.endswith("_haa_joint"):
            lo, hi = self.joint_limits["haa"]
        elif joint_name.endswith("_hfe_joint"):
            lo, hi = self.joint_limits["hfe"]
        elif joint_name.endswith("_kfe_joint"):
            lo, hi = self.joint_limits["kfe"]
        else:
            return position

        clipped = max(lo, min(hi, position))
        if clipped != position:
            self.node.get_logger().warn(
                f"Joint limit clipped: {joint_name} {position:.3f} -> {clipped:.3f}",
                throttle_duration_sec=1.0,
            )
        return clipped

    def send_joint_commands(self, joint_positions: Dict[str, float]) -> None:
        revolute_names: List[str] = []
        revolute_positions: List[float] = []
        for leg_id in LEG_IDS:
            prefix = LEG_TO_PREFIX[leg_id]
            for suffix in ("haa_joint", "hfe_joint", "kfe_joint"):
                name = f"{prefix}_{suffix}"
                if name not in joint_positions:
                    continue
                revolute_names.append(name)
                revolute_positions.append(self.check_joint_limits(name, joint_positions[name]))

        rev_msg = JointTrajectory()
        rev_msg.joint_names = revolute_names
        rev_pt = JointTrajectoryPoint()
        rev_pt.positions = revolute_positions
        rev_pt.time_from_start = Duration(sec=0, nanosec=40_000_000)
        rev_msg.points = [rev_pt]
        self.revolute_pub.publish(rev_msg)

        rail_msg = JointTrajectory()
        rail_msg.joint_names = [LEG_TO_RAIL[leg] for leg in LEG_IDS]
        rail_pt = JointTrajectoryPoint()
        rail_pt.positions = [0.0, 0.0, 0.0, 0.0]
        rail_pt.time_from_start = Duration(sec=0, nanosec=40_000_000)
        rail_msg.points = [rail_pt]
        self.rail_pub.publish(rail_msg)

    def monitor_rail_positions(self) -> bool:
        # 使用节点的 ROS 时钟来计算节流与时间戳，支持模拟时间
        now = self.node.get_clock().now().nanoseconds * 1e-9
        if now - self._last_rail_check_time < 0.2:
            return True
        self._last_rail_check_time = now

        threshold_m = 0.0005
        for joint_name in ("j1", "j2", "j3", "j4"):
            value = self._joint_state_map.get(joint_name)
            if value is None:
                continue
            if abs(value) > threshold_m:
                self.node.get_logger().error(
                    f"Rail slip detected on {joint_name}: {value * 1000.0:.2f} mm",
                    throttle_duration_sec=1.0,
                )
                return False
        return True

    def get_joint_states(self) -> Dict[str, float]:
        return dict(self._joint_state_map)


class SpiderRobotController:
    def __init__(self, node: Node):
        self.node = node
        self.config = GaitConfig()
        self.trajectory_planner = TrajectoryPlanner()
        self.gait_generator = GaitGenerator(self.config, self.trajectory_planner)

        joint_limits = {
            "rail": (-0.111, 0.111),
            "haa": (-2.618, 2.618),
            "hfe": (-2.8, 2.8),
            "kfe": (-2.8, 2.8),
        }
        self.kinematics_solver = KinematicsSolver(
            {
                "leg1": LegParameters("leg1", np.array([0.10, -0.08, 0.0]), 0.055, 0.152, 0.299, joint_limits),
                "leg2": LegParameters("leg2", np.array([0.10, 0.08, 0.0]), 0.055, 0.152, 0.299, joint_limits),
                "leg3": LegParameters("leg3", np.array([-0.10, -0.08, 0.0]), 0.055, 0.152, 0.299, joint_limits),
                "leg4": LegParameters("leg4", np.array([-0.10, 0.08, 0.0]), 0.055, 0.152, 0.299, joint_limits),
            }
        )

        self.joint_controller = JointController(node)
        self.current_velocity = (0.0, 0.0, 0.0)
        self.filtered_velocity = np.zeros(3, dtype=float)

        self.last_valid_leg_joints: Dict[str, Tuple[float, float, float, float]] = {
            leg: (0.0, 0.0, 0.6, 1.2) for leg in LEG_IDS
        }

    def set_velocity_command(self, vx: float, vy: float, omega: float) -> None:
        vx = float(np.clip(vx, -0.25, 0.25))
        vy = float(np.clip(vy, -0.20, 0.20))
        omega = float(np.clip(omega, -0.8, 0.8))
        self.current_velocity = (vx, vy, omega)

    def _smooth_velocity(self, dt: float) -> Tuple[float, float, float]:
        tau = 0.25
        alpha = float(np.clip(dt / max(tau, 1e-4), 0.0, 1.0))
        target = np.array(self.current_velocity)
        self.filtered_velocity = (1.0 - alpha) * self.filtered_velocity + alpha * target
        return float(self.filtered_velocity[0]), float(self.filtered_velocity[1]), float(self.filtered_velocity[2])

    def update(self, dt: float) -> None:
        vel = self._smooth_velocity(dt)
        self.gait_generator.update(dt, vel)

        joint_targets: Dict[str, float] = {}
        for leg_id in LEG_ORDER:
            foot_target = self.gait_generator.get_foot_target(leg_id)
            ik = self.kinematics_solver.solve_ik(leg_id, foot_target, rail_offset=0.0)
            if ik is None:
                ik = self.last_valid_leg_joints[leg_id]
                self.node.get_logger().warn(
                    f"IK failed on {leg_id}, fallback to last valid joints",
                    throttle_duration_sec=1.0,
                )
            else:
                self.last_valid_leg_joints[leg_id] = ik

            _, haa, hfe, kfe = ik
            prefix = LEG_TO_PREFIX[leg_id]
            joint_targets[f"{prefix}_haa_joint"] = haa
            joint_targets[f"{prefix}_hfe_joint"] = hfe
            joint_targets[f"{prefix}_kfe_joint"] = kfe

        self.joint_controller.send_joint_commands(joint_targets)
        self.joint_controller.monitor_rail_positions()


class SpiderBasicMotionNode(Node):
    def __init__(self):
        super().__init__("spider_basic_motion_controller")

        self.controller = SpiderRobotController(self)
        # 记录上次更新时间（ROS 时钟）
        self.last_update_time = self.get_clock().now()

        self.create_subscription(Twist, "/cmd_vel", self._cmd_vel_cb, 20)
        self.timer = self.create_timer(0.02, self._on_timer)

        self.get_logger().info("Spider basic motion controller started at 50 Hz")

    def _cmd_vel_cb(self, msg: Twist) -> None:
        self.controller.set_velocity_command(
            vx=msg.linear.x,
            vy=msg.linear.y,
            omega=msg.angular.z,
        )

    def _on_timer(self) -> None:
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds * 1e-9
        self.last_update_time = now
        if dt <= 0.0:
            dt = 0.02
        self.controller.update(dt)


def main(args: Optional[List[str]] = None) -> None:
    rclpy.init(args=args)
    node = SpiderBasicMotionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
