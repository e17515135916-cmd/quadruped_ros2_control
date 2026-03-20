"""
Spider Robot Controller - 主控制器

协调所有子系统，实现50Hz实时主控制循环
将 GaitGenerator(步态大脑), TrajectoryPlanner(轨迹平滑), 
KinematicsSolver(运动学求解) 和 JointController(硬件驱动) 完美串联。
"""

import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json

from .gait_generator import GaitGenerator, GaitConfig
from .kinematics_solver import create_kinematics_solver
from .trajectory_planner import TrajectoryPlanner
from .joint_controller import JointController
from .joint_names import PREFIX_TO_LEG_MAP, get_leg_joint_names
from .config_loader import ConfigLoader


class SpiderRobotController(Node):
    """蜘蛛机器人主控制器"""

    # FK 标定的站立角度（与 kinematics_solver.py 中保持一致）
    # Requirements: 2.1, 2.2
    _STANDING_ANGLES = {
        "lf": (0.0, 0.0, 0.3000, -0.5000),
        "lh": (0.0, 0.0, 0.3000, -0.5000),
        "rh": (0.0, 0.0, 0.3000, -0.5000),
        "rf": (0.0, 0.0, 0.3000, -0.5000),
    }

    def __init__(self, config_path=None):
        super().__init__("spider_robot_controller")
        self.get_logger().info("Initializing Spider Robot Controller...")

        self.config_loader = ConfigLoader(config_path)
        self.config_loader.load()
        gait_config = self.config_loader.get_gait_config()

        self.ik_solver = create_kinematics_solver()
        self.trajectory_planner = TrajectoryPlanner()
        self.joint_controller = JointController(self)

        # 用 FK 标定结果初始化 GaitGenerator 的名义落脚点
        # Requirements: 3.1, 3.4
        nominal_positions = {
            leg_id: self.ik_solver.solve_fk(leg_id, angles)
            for leg_id, angles in self._STANDING_ANGLES.items()
        }
        self.gait_generator = GaitGenerator(gait_config, nominal_positions)

        self.current_velocity = (0.0, 0.0, 0.0)
        self.target_velocity = (0.0, 0.0, 0.0)
        self.is_running = False
        self.is_stopping = False
        self.stop_start_time = 0.0
        self.last_time = time.time()

        # Minimum Jerk ramp 状态
        self.is_ramping = False
        self.ramp_start_time = 0.0
        self.ramp_duration = 2.0
        self.standing_joint_angles = {}
        self.ramp_last_valid_commands = {}

        self.is_emergency_mode = False
        self.emergency_start_time = 0.0
        self.EMERGENCY_DESCENT_DURATION = 3.0

        self.last_valid_joint_positions = {"lf": None, "rf": None, "lh": None, "rh": None}
        self.ik_failure_count = {"lf": 0, "rf": 0, "lh": 0, "rh": 0}

        self.pending_config_update = None
        self.last_cycle_phase = 0.0

        self.debug_mode = False
        self.debug_publisher = self.create_publisher(String, "/spider_debug_info", 10)
        self.debug_publish_counter = 0

        self.cmd_vel_sub = self.create_subscription(
            Twist, "/cmd_vel", self._cmd_vel_callback, 10
        )
        self.timer_period = 0.02
        self.timer = None

        self.get_logger().info("Spider Robot Controller is READY.")

    def _cmd_vel_callback(self, msg):
        if abs(msg.linear.x) < 0.001 and abs(msg.linear.y) < 0.001 and abs(msg.angular.z) < 0.001:
            if not self.is_stopping and self.is_running:
                self.initiate_smooth_stop()
        else:
            self.is_stopping = False
            v = (msg.linear.x, msg.linear.y, msg.angular.z)
            self.target_velocity = v

    def start(self):
        """启动控制器：先执行 Minimum Jerk 站立插值，再进入步态循环"""
        self.get_logger().info("Starting 50Hz control loop...")
        self.is_running = True
        self.is_stopping = False
        self.last_time = time.time()

        # Requirements: 4.1
        self._compute_standing_joint_angles()

        self.is_ramping = True
        self.ramp_start_time = time.time()
        self.ramp_last_valid_commands = {}

        self.timer = self.create_timer(self.timer_period, self._timer_callback)

    def _compute_standing_joint_angles(self):
        """将 FK 标定站立角映射到 URDF 关节名称字典。Requirements: 4.1"""
        self.standing_joint_angles = {}
        for leg_id, (s_m, haa_rad, hfe_rad, kfe_rad) in self._STANDING_ANGLES.items():
            leg_num = PREFIX_TO_LEG_MAP[leg_id]
            jn = get_leg_joint_names(leg_num)
            self.standing_joint_angles[jn["rail"]] = s_m
            self.standing_joint_angles[jn["coxa"]] = haa_rad
            self.standing_joint_angles[jn["femur"]] = hfe_rad
            self.standing_joint_angles[jn["tibia"]] = kfe_rad
        self.get_logger().info(
            f"Standing joint angles computed for {len(self.standing_joint_angles)} joints."
        )

    def _execute_standup_trajectory(self):
        """Minimum Jerk 站立插值，使用 TrajectoryPlanner.smooth_phase()。Requirements: 4.2, 4.3"""
        elapsed = time.time() - self.ramp_start_time
        t = min(elapsed / self.ramp_duration, 1.0)
        phi = self.trajectory_planner.smooth_phase(t)

        # Requirements: 4.5
        if not self.standing_joint_angles:
            self.get_logger().warn("Ramp: standing_joint_angles empty. Holding last valid commands.")
            if self.ramp_last_valid_commands:
                self.joint_controller.send_joint_commands(self.ramp_last_valid_commands)
            return

        commands = {jn: phi * angle for jn, angle in self.standing_joint_angles.items()}
        self.ramp_last_valid_commands = commands.copy()
        self.joint_controller.send_joint_commands(commands)

        if t >= 1.0:
            # Requirements: 4.4
            self.is_ramping = False
            self.get_logger().info("Standup trajectory complete. Entering normal gait loop.")

    def initiate_smooth_stop(self):
        self.get_logger().info("Initiating smooth stop...")
        self.is_stopping = True
        self.stop_start_time = self.gait_generator.current_time
        self.target_velocity = self.current_velocity

    def stop(self):
        self.get_logger().info("Stopping control loop, engaging safety lock...")
        self.is_running = False
        if self.timer is not None:
            self.timer.cancel()
        self.joint_controller.lock_rails_with_max_effort()

    def engage_emergency_safety_posture(self):
        self.get_logger().error("EMERGENCY: Engaging safety posture!")
        self.is_emergency_mode = True
        self.emergency_start_time = time.time()
        self.current_velocity = (0.0, 0.0, 0.0)
        self.target_velocity = (0.0, 0.0, 0.0)
        self.is_stopping = False
        self.joint_controller.lock_rails_with_max_effort()

    def _execute_emergency_descent(self):
        elapsed = time.time() - self.emergency_start_time
        if elapsed >= self.EMERGENCY_DESCENT_DURATION:
            self.get_logger().info("Emergency descent completed.")
            return True

        progress = elapsed / self.EMERGENCY_DESCENT_DURATION
        initial_h = self.gait_generator.config.body_height
        current_h = initial_h - (initial_h - 0.10) * progress

        target_joint_positions = {}
        for leg_id in ["lf", "rf", "lh", "rh"]:
            if self.last_valid_joint_positions[leg_id] is not None:
                fp = self.ik_solver.solve_fk(leg_id, self.last_valid_joint_positions[leg_id])
                fp_adj = (fp[0], fp[1], fp[2] + (initial_h - current_h))
                ik = self.ik_solver.solve_ik(leg_id, fp_adj)
                s_m, haa, hfe, kfe = ik if ik else self.last_valid_joint_positions[leg_id]
            else:
                s_m, haa, hfe, kfe = 0.0, 0.0, 0.0, 0.0
            jn = get_leg_joint_names(PREFIX_TO_LEG_MAP[leg_id])
            target_joint_positions[jn["rail"]] = s_m
            target_joint_positions[jn["coxa"]] = haa
            target_joint_positions[jn["femur"]] = hfe
            target_joint_positions[jn["tibia"]] = kfe

        self.joint_controller.send_joint_commands(target_joint_positions)
        if not self.joint_controller.monitor_rail_positions():
            self.get_logger().error("CRITICAL: Rail slip during emergency descent!")
        return False

    def _timer_callback(self):
        if not self.is_running:
            return
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.update(dt)

    def update(self, dt):
        if not self.joint_controller.check_connection():
            self.get_logger().warn("Joint controller connection lost. Attempting reconnect...")
            if not self.joint_controller.attempt_reconnect():
                self.get_logger().error("Reconnection failed. Engaging emergency safety posture.")
                self.engage_emergency_safety_posture()
            return

        if self.is_emergency_mode:
            if self._execute_emergency_descent():
                self.stop()
            return

        # Requirements: 4.2, 4.3, 4.4, 4.5
        if self.is_ramping:
            self._execute_standup_trajectory()
            return

        self._check_and_apply_config_update()

        if not self.joint_controller.monitor_rail_positions():
            self.get_logger().error("CRITICAL: Rail slip detected!")
            self.engage_emergency_safety_posture()
            return

        stuck_joints = self.joint_controller.detect_stuck_joints()
        stuck_count = sum(1 for v in stuck_joints.values() if v)
        for jn, stuck in stuck_joints.items():
            if stuck:
                self.joint_controller.handle_stuck_joint(jn)
        if stuck_count >= 3:
            self.get_logger().error(f"CRITICAL: {stuck_count} joints stuck!")
            self.engage_emergency_safety_posture()
            return

        if self.is_stopping:
            self._handle_smooth_stop()
        else:
            # 低通平滑速度，避免从静止到运动时足端目标位置突跳
            alpha = min(1.0, dt / 0.25) if dt > 0.0 else 1.0
            cvx, cvy, comega = self.current_velocity
            tvx, tvy, tomega = self.target_velocity
            self.current_velocity = (
                cvx + alpha * (tvx - cvx),
                cvy + alpha * (tvy - cvy),
                comega + alpha * (tomega - comega),
            )

        self.gait_generator.update(dt, self.current_velocity)

        target_joint_positions = {}
        for leg_id in ["lf", "rf", "lh", "rh"]:
            foot_pos = self.gait_generator.get_foot_target(leg_id)
            ik_result = self.ik_solver.solve_ik(leg_id, foot_pos)

            if ik_result is None:
                self._handle_ik_failure(leg_id, foot_pos)
                if self.last_valid_joint_positions[leg_id] is not None:
                    s_m, haa, hfe, kfe = self.last_valid_joint_positions[leg_id]
                else:
                    self.get_logger().error(f"No last valid config for {leg_id}, using zero.")
                    s_m, haa, hfe, kfe = 0.0, 0.0, 0.0, 0.0
            else:
                s_m, haa, hfe, kfe = ik_result
                self.last_valid_joint_positions[leg_id] = ik_result
                self.ik_failure_count[leg_id] = 0

            jn = get_leg_joint_names(PREFIX_TO_LEG_MAP[leg_id])
            target_joint_positions[jn["rail"]] = s_m
            target_joint_positions[jn["coxa"]] = haa
            target_joint_positions[jn["femur"]] = hfe
            target_joint_positions[jn["tibia"]] = kfe

        self.joint_controller.send_joint_commands(target_joint_positions)
        if self.debug_mode:
            self._publish_debug_info(target_joint_positions)

    def _handle_smooth_stop(self):
        elapsed = self.gait_generator.current_time - self.stop_start_time
        stop_dur = self.gait_generator.config.cycle_time
        if elapsed >= stop_dur:
            self.current_velocity = (0.0, 0.0, 0.0)
            self.is_stopping = False
            self.get_logger().info("Smooth stop completed.")
        else:
            f = 1.0 - elapsed / stop_dur
            vx, vy, om = self.target_velocity
            self.current_velocity = (vx * f, vy * f, om * f)

    def update_gait_config(self, new_config):
        self.pending_config_update = new_config
        self.get_logger().info(
            f"Config update requested: stride_length={new_config.stride_length}, "
            f"stride_height={new_config.stride_height}, cycle_time={new_config.cycle_time}"
        )

    def reload_config_from_file(self, config_path=None):
        if config_path is not None:
            self.config_loader = ConfigLoader(config_path)
        self.config_loader.load()
        self.update_gait_config(self.config_loader.get_gait_config())
        self.get_logger().info(f"Config reloaded from {self.config_loader.config_path}")

    def _check_and_apply_config_update(self):
        if self.pending_config_update is None or self.is_stopping:
            return
        phase = self.gait_generator.get_phase("lf")
        if self.last_cycle_phase > 0.9 and phase < 0.1:
            self.gait_generator.config = self.pending_config_update
            self.pending_config_update = None
            self.get_logger().info("Config update applied at cycle boundary.")
        self.last_cycle_phase = phase

    def enable_debug_mode(self, enable=True):
        self.debug_mode = enable
        self.get_logger().info(f"Debug mode {'ENABLED' if enable else 'DISABLED'}.")

    def _publish_debug_info(self, joint_positions):
        if not self.debug_mode:
            return
        self.debug_publish_counter += 1
        if self.debug_publish_counter < 10:
            return
        self.debug_publish_counter = 0

        debug_data = {
            "timestamp": self.gait_generator.current_time,
            "gait_config": {
                "stride_length": self.gait_generator.config.stride_length,
                "stride_height": self.gait_generator.config.stride_height,
                "cycle_time": self.gait_generator.config.cycle_time,
                "duty_factor": self.gait_generator.config.duty_factor,
                "body_height": self.gait_generator.config.body_height,
                "gait_type": self.gait_generator.config.gait_type,
            },
            "velocity": {
                "vx": self.current_velocity[0],
                "vy": self.current_velocity[1],
                "omega": self.current_velocity[2],
            },
            "legs": {},
        }
        for leg_id in ["lf", "rf", "lh", "rh"]:
            jn = get_leg_joint_names(PREFIX_TO_LEG_MAP[leg_id])
            fp = self.gait_generator.get_foot_target(leg_id)
            debug_data["legs"][leg_id] = {
                "phase": round(self.gait_generator.get_phase(leg_id), 3),
                "is_stance": self.gait_generator.is_stance_phase(leg_id),
                "foot_position": {"x": round(fp[0], 4), "y": round(fp[1], 4), "z": round(fp[2], 4)},
                "joint_positions": {
                    "rail_m": round(joint_positions.get(jn["rail"], 0.0), 4),
                    "haa_rad": round(joint_positions.get(jn["coxa"], 0.0), 4),
                    "hfe_rad": round(joint_positions.get(jn["femur"], 0.0), 4),
                    "kfe_rad": round(joint_positions.get(jn["tibia"], 0.0), 4),
                },
            }
        support_legs = self.gait_generator.get_support_triangle()
        debug_data["support_legs"] = support_legs
        debug_data["num_support_legs"] = len(support_legs)
        debug_data["is_stable"] = self.gait_generator.verify_stability()

        msg = String()
        msg.data = json.dumps(debug_data, indent=2)
        self.debug_publisher.publish(msg)

    def _handle_ik_failure(self, leg_id, target_pos):
        self.ik_failure_count[leg_id] += 1
        self.get_logger().error(
            f"IK Failure on {leg_id} at {target_pos}. "
            f"Using last valid config. (count: {self.ik_failure_count[leg_id]})"
        )
        if self.ik_failure_count[leg_id] > 10:
            self.get_logger().warn(
                f"Leg {leg_id} has {self.ik_failure_count[leg_id]} consecutive IK failures."
            )


def main(args=None):
    rclpy.init(args=args)
    controller = SpiderRobotController()
    try:
        controller.start()
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info("Keyboard Interrupt detected.")
    finally:
        controller.stop()
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
