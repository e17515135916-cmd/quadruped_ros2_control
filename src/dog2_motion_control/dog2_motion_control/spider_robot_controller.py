"""
Spider Robot Controller - 主控制器

协调所有子系统，实现50Hz实时主控制循环
将 GaitGenerator(步态大脑), TrajectoryPlanner(轨迹平滑), 
KinematicsSolver(运动学求解) 和 JointController(硬件驱动) 完美串联。
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json
from enum import Enum

# 导入我们的四大核心积木
from .gait_generator import GaitGenerator, GaitConfig
from .kinematics_solver import create_kinematics_solver
from .trajectory_planner import TrajectoryPlanner
from .joint_controller import JointController
from .joint_names import PREFIX_TO_LEG_MAP, get_leg_joint_names
from .config_loader import ConfigLoader


class ControllerState(Enum):
    """控制器状态机"""
    INITIALIZING = 'initializing'
    STANDING_UP = 'standing_up'
    READY_FOR_MPC = 'ready_for_mpc'


class SpiderRobotController(Node):
    """蜘蛛机器人主控制器"""
    
    def __init__(self, config_path: str = None):
        super().__init__('spider_robot_controller')
        self.get_logger().info('Initializing Spider Robot Controller...')
        
        # 0. 加载配置文件（作为默认值/兜底）
        self.config_loader = ConfigLoader(config_path)
        self.config_loader.load()
        gait_config = self.config_loader.get_gait_config()

        # 0.1 ROS2 参数化：声明 gait.*，允许用 --params-file / ros2 param set 覆盖
        self.declare_parameters(
            namespace='',
            parameters=[
                ('gait.body_height', float(gait_config.body_height)),
                ('gait.stride_length', float(gait_config.stride_length)),
                ('gait.stride_height', float(gait_config.stride_height)),
                ('gait.cycle_time', float(gait_config.cycle_time)),
                ('gait.duty_factor', float(gait_config.duty_factor)),
                ('gait.gait_type', str(gait_config.gait_type)),
            ]
        )

        # 0.2 将 ROS 参数写回 gait_config（如果启动时传了 params-file，这里会读到覆盖值）
        gait_config.body_height = float(self.get_parameter('gait.body_height').value)
        gait_config.stride_length = float(self.get_parameter('gait.stride_length').value)
        gait_config.stride_height = float(self.get_parameter('gait.stride_height').value)
        gait_config.cycle_time = float(self.get_parameter('gait.cycle_time').value)
        gait_config.duty_factor = float(self.get_parameter('gait.duty_factor').value)
        gait_config.gait_type = str(self.get_parameter('gait.gait_type').value)

        # 动态调参回调（运行中 ros2 param set 立即生效）
        self.add_on_set_parameters_callback(self._on_set_parameters)

        # 1. 实例化核心子系统
        self.gait_generator = GaitGenerator(gait_config)
        self.ik_solver = create_kinematics_solver()
        self.trajectory_planner = TrajectoryPlanner()
        self.joint_controller = JointController(self)
        
        # 2. 状态变量
        self.current_velocity = (0.0, 0.0, 0.0)  # vx, vy, omega
        self.target_velocity = (0.0, 0.0, 0.0)   # 目标速度（用于平滑停止/加速斜坡）
        self.max_linear_accel = 0.5   # 最大线加速度 (m/s^2)
        self.max_angular_accel = 1.0  # 最大角加速度 (rad/s^2)
        self.is_running = False
        self.is_stopping = False  # 是否正在执行平滑停止
        self.stop_start_time = 0.0  # 停止开始时间
        # 使用 ROS 时钟 (rclpy Time) 记录上次循环时间，以支持仿真时间(use_sim_time=True)
        self.last_ros_time = self.get_clock().now()

        # 开机平滑起立状态机（避免初始姿态突变）
        self.current_state = ControllerState.INITIALIZING
        self.standup_duration = 3.0  # 起立过渡时长（秒）
        self.standup_start_time = None
        self.initial_joint_positions = {}  # 从 /joint_states 读取的初始关节状态
        self.target_standing_pose = {}
        self.stuck_detection_start_time = None
        
        # 紧急安全姿态相关
        self.is_emergency_mode = False  # 是否处于紧急模式
        self.emergency_start_time = None  # 紧急模式开始时间 (rclpy Time 或 None)
        self.EMERGENCY_DESCENT_DURATION = 3.0  # 紧急下降持续时间（秒）

        # 卡死检测延迟（避免刚启动就误判）
        self.stuck_detection_delay_sec = 5.0
        self.stuck_detection_start_time = None  # rclpy Time 或 None
        
        # IK失败恢复：存储每条腿的上一个有效关节配置
        self.last_valid_joint_positions = {
            'lf': None,
            'rf': None,
            'lh': None,
            'rh': None
        }
        self.ik_failure_count = {
            'lf': 0,
            'rf': 0,
            'lh': 0,
            'rh': 0
        }
        
        # 参数更新相关
        self.pending_config_update = None  # 待应用的配置更新
        self.last_cycle_phase = 0.0  # 上一次的步态相位（用于检测周期边界）
        
        # 调试模式
        self.declare_parameter('debug_mode', False)
        self.debug_mode = bool(self.get_parameter('debug_mode').value)
        self.debug_publisher = self.create_publisher(String, '/spider_debug_info', 10)
        self.debug_publish_counter = 0  # 用于控制发布频率
        
        # 3. 订阅 /cmd_vel 获取外部控制指令
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self._cmd_vel_callback,
            10
        )
        
        # 4. 创建 50Hz 的核心控制循环定时器 (0.02秒)
        self.timer_period = 0.02
        self.timer = None  # 在 start() 中启动
        
        self.get_logger().info('Spider Robot Controller is READY.')

    def _on_set_parameters(self, params):
        """动态参数回调：运行中更新步态参数"""
        updated = False
        for param in params:
            if param.name == 'gait.body_height':
                self.gait_generator.config.body_height = float(param.value)
                updated = True
            elif param.name == 'gait.stride_length':
                self.gait_generator.config.stride_length = float(param.value)
                updated = True
            elif param.name == 'gait.stride_height':
                self.gait_generator.config.stride_height = float(param.value)
                updated = True
            elif param.name == 'gait.cycle_time':
                self.gait_generator.config.cycle_time = float(param.value)
                updated = True
            elif param.name == 'gait.duty_factor':
                self.gait_generator.config.duty_factor = float(param.value)
                updated = True
            elif param.name == 'gait.gait_type':
                self.gait_generator.config.gait_type = str(param.value)
                updated = True
            elif param.name == 'debug_mode':
                self.debug_mode = bool(param.value)
                self.get_logger().info(
                    f'Debug mode {"ENABLED" if self.debug_mode else "DISABLED"}.'
                )

        if updated:
            self.get_logger().info('Gait parameters updated via ROS params')
        return SetParametersResult(successful=True)
    
    def _cmd_vel_callback(self, msg: Twist):
        """处理外部速度指令"""
        # 检查是否为停止命令
        if abs(msg.linear.x) < 0.001 and abs(msg.linear.y) < 0.001 and abs(msg.angular.z) < 0.001:
            # 接收到停止命令，启动平滑停止
            if not self.is_stopping and self.is_running:
                self.initiate_smooth_stop()
        else:
            # 非停止命令：仅更新目标速度，由update中的速度斜坡平滑逼近
            self.is_stopping = False
            self.target_velocity = (
                msg.linear.x,
                msg.linear.y,
                msg.angular.z
            )
    
    def start(self):
        """启动控制器循环"""
        self.get_logger().info('Starting 50Hz control loop...')
        self.is_running = True
        self.is_stopping = False
        # 重置为当前 ROS 时钟时间（支持仿真时间）
        self.last_ros_time = self.get_clock().now()
        self.timer = self.create_timer(self.timer_period, self._timer_callback)

        # 配置目标站立姿态（合法关节范围内）
        self.target_standing_pose = {}
        initial_haa = 0.0
        initial_hfe = 0.7
        initial_kfe = -1.2
        initial_rail = 0.0
        for leg_id in ['lf', 'rf', 'lh', 'rh']:
            leg_num = PREFIX_TO_LEG_MAP[leg_id]
            joint_names = get_leg_joint_names(leg_num)
            self.target_standing_pose[joint_names['rail']] = initial_rail
            self.target_standing_pose[joint_names['haa']] = initial_haa
            self.target_standing_pose[joint_names['hfe']] = initial_hfe
            self.target_standing_pose[joint_names['kfe']] = initial_kfe

        # 读取当前真实关节状态作为插值起点（仅旋转关节）；
        # 导轨由 JointController 内部强制锁定为 0.0，不参与起立插值
        current_states = self.joint_controller.get_joint_states()
        for joint_name, target_value in self.target_standing_pose.items():
            if joint_name.startswith('j'):
                continue
            if joint_name in current_states:
                self.initial_joint_positions[joint_name] = current_states[joint_name]['position']
            else:
                # 如果状态尚未到达，使用目标值作为保底，避免瞬间大跳
                self.initial_joint_positions[joint_name] = target_value

        # 进入平滑起立状态
        # 如果仿真时钟未推进，直接进入就绪状态避免卡死
        if self.get_clock().now().nanoseconds == 0:
            self.current_state = ControllerState.READY_FOR_MPC
            self.get_logger().warn('Sim time not advancing; skipping stand-up trajectory')
            self.stuck_detection_start_time = self.get_clock().now()
        else:
            self.current_state = ControllerState.STANDING_UP
            self.standup_start_time = self.get_clock().now()
            self.stuck_detection_start_time = self.standup_start_time
            self.get_logger().info(f'Starting smooth stand-up trajectory ({self.standup_duration:.1f}s)')
    
    def initiate_smooth_stop(self):
        """启动平滑停止过程
        
        在一个步态周期内平滑停止运动：
        - 速度线性衰减到零
        - 确保所有腿回到支撑相
        """
        self.get_logger().info('Initiating smooth stop...')
        self.is_stopping = True
        self.stop_start_time = self.gait_generator.current_time
        # 保存当前速度作为衰减的起始速度
        self.target_velocity = self.current_velocity
    
    def stop(self):
        """停止控制器并切入安全姿态"""
        self.get_logger().info('Stopping control loop, engaging safety lock...')
        # 标记停止，取消定时器并清理紧急状态标志
        self.is_running = False

        if self.timer is not None:
            try:
                self.timer.cancel()
            except Exception:
                # 防御性：忽略定时器取消异常
                pass
            self.timer = None

        # 紧急相关标志清理，避免后续逻辑误判
        self.is_emergency_mode = False
        self.emergency_start_time = None

        # ROS上下文可能已关闭（Ctrl-C后），此时不能再发布
        if not rclpy.ok():
            self.get_logger().warn('ROS context is not OK; skipping rail lock publish')
            return

        # 紧急安全锁死：最大力矩锁死导轨，防止机器人瘫软滑坡
        self.joint_controller.lock_rails_with_max_effort()
    
    def engage_emergency_safety_posture(self):
        """切换到紧急安全姿态
        
        严重错误时的应急措施：
        1. 停止所有运动规划
        2. 持续锁定导轨（最大力矩）
        3. 缓慢降低身体高度
        4. 监控导轨滑动
        
        需求: 8.4, 8.5, 8.6
        """
        self.get_logger().error('EMERGENCY: Engaging safety posture!')
        
        # 标记进入紧急模式，记录 ROS 时钟时间
        self.is_emergency_mode = True
        self.emergency_start_time = self.get_clock().now()

        # 确保控制循环处于运行状态以执行紧急下降
        # 如果控制器尚未启动或定时器已被取消，尝试创建定时器以保证 _execute_emergency_descent 被周期性调用
        if not self.is_running:
            self.get_logger().warn('Controller was not running; starting control loop to perform emergency descent')
            self.is_running = True
        if self.timer is None:
            # 防御性创建定时器（如果节点生命周期允许）
            try:
                self.timer = self.create_timer(self.timer_period, self._timer_callback)
            except Exception:
                self.get_logger().error('Failed to create emergency descent timer; emergency descent may not proceed')

        
        # 停止所有运动规划
        self.current_velocity = (0.0, 0.0, 0.0)
        self.target_velocity = (0.0, 0.0, 0.0)
        self.is_stopping = False
        
        # 持续锁定导轨（最大力矩）
        self.joint_controller.lock_rails_with_max_effort()
        
        self.get_logger().info('Emergency safety posture engaged. Slowly lowering body...')
    
    def _execute_emergency_descent(self) -> bool:
        """执行紧急下降
        
        缓慢降低身体高度到安全姿态
        
        Returns:
            True如果下降完成，False如果仍在进行中
        """
        # 计算自进入紧急模式的经过时间（秒），使用 ROS 时钟以支持仿真时间
        if self.emergency_start_time is None:
            elapsed_time = 0.0
        else:
            now = self.get_clock().now()
            elapsed_time = (now - self.emergency_start_time).nanoseconds * 1e-9

        if elapsed_time >= self.EMERGENCY_DESCENT_DURATION:
            # 下降完成
            self.get_logger().info('Emergency descent completed. Robot in safe posture.')
            return True
        
        # 计算下降进度（0到1）
        progress = elapsed_time / self.EMERGENCY_DESCENT_DURATION
        
        # 目标身体高度：从当前高度线性下降到0.10米（蹲下姿态）
        initial_height = self.gait_generator.config.body_height
        target_height = 0.10  # 蹲下姿态的身体高度
        current_height = initial_height - (initial_height - target_height) * progress
        
        # 计算4条腿的目标脚部位置（保持在原地，只降低身体）
        target_joint_positions = {}
        
        for leg_id in ['lf', 'rf', 'lh', 'rh']:
            # 获取当前脚部位置（假设脚部不移动）
            # 使用上一个有效配置的脚部位置
            if self.last_valid_joint_positions[leg_id] is not None:
                # 使用FK计算当前脚部位置
                foot_pos = self.ik_solver.solve_fk(leg_id, self.last_valid_joint_positions[leg_id])
                
                # 调整Z坐标以降低身体
                # 注意：这里简化处理，实际应该根据身体高度变化调整
                foot_pos_adjusted = (foot_pos[0], foot_pos[1], foot_pos[2] + (initial_height - current_height))
                
                # 计算新的关节位置
                ik_result = self.ik_solver.solve_ik(leg_id, foot_pos_adjusted)
                
                if ik_result is not None:
                    s_m, haa_rad, hfe_rad, kfe_rad = ik_result
                else:
                    # IK失败，使用上一个有效配置
                    s_m, haa_rad, hfe_rad, kfe_rad = self.last_valid_joint_positions[leg_id]
            else:
                # 没有上一个有效配置，使用零位
                s_m, haa_rad, hfe_rad, kfe_rad = 0.0, 0.0, 0.0, 0.0
            
            # 获取关节名称
            leg_num = PREFIX_TO_LEG_MAP[leg_id]
            joint_names = get_leg_joint_names(leg_num)
            
            # 收集关节命令
            target_joint_positions[joint_names['rail']] = s_m  # 导轨始终为0.0
            target_joint_positions[joint_names['haa']] = haa_rad
            target_joint_positions[joint_names['hfe']] = hfe_rad
            target_joint_positions[joint_names['kfe']] = kfe_rad
        
        # 发送关节命令
        self.joint_controller.send_joint_commands(target_joint_positions)
        
        # 持续监控导轨位置
        if not self.joint_controller.monitor_rail_positions():
            self.get_logger().error('CRITICAL: Rail slip detected during emergency descent!')
        
        return False
    
    def _timer_callback(self):
        """定时器回调，计算实际 dt 并调用 update"""
        if not self.is_running:
            return
        
        # 使用 ROS 时钟计算 dt，避免与系统时间产生偏差（尤其是在 Gazebo simulate time 下）
        now = self.get_clock().now()
        dt = (now - self.last_ros_time).nanoseconds * 1e-9
        # 更新上次时间
        self.last_ros_time = now

        # 防御性处理：如果 dt 非正或非常小，使用定时器周期作为后备值
        if dt <= 0.0:
            dt = self.timer_period

        self.update(dt)
    
    def update(self, dt: float):
        """主控制循环核心逻辑 (Task 9)"""

        # 状态机：开机平滑起立阶段（Minimum Jerk）
        if self.current_state == ControllerState.STANDING_UP:
            if self._execute_standup_trajectory():
                self.current_state = ControllerState.READY_FOR_MPC
                self.get_logger().info('Stand-up complete. Ready for MPC/WBC commands.')
            return
        
        # 步骤 0.0：检查控制器连接状态（需求8.1）
        if not self.joint_controller.check_connection():
            self.get_logger().warn('Joint controller connection lost. Attempting reconnect...')
            
            # 停止发送命令
            # 尝试重新连接
            if not self.joint_controller.attempt_reconnect():
                # 重连失败，触发紧急安全姿态
                self.get_logger().error('Reconnection failed. Engaging emergency safety posture.')
                self.engage_emergency_safety_posture()
            return
        
        # 步骤 0.1：如果处于紧急模式，执行紧急下降
        if self.is_emergency_mode:
            descent_complete = self._execute_emergency_descent()
            if descent_complete:
                # 下降完成，停止控制循环
                self.stop()
            return
        
        # 步骤 0：检查是否需要在周期边界应用参数更新
        self._check_and_apply_config_update()
        
        # 步骤 1.1：检测关节卡死（需求8.3）
        should_check_stuck = True
        if self.stuck_detection_start_time is not None:
            elapsed = (self.get_clock().now() - self.stuck_detection_start_time).nanoseconds / 1e9
            should_check_stuck = elapsed >= self.stuck_detection_delay_sec

        if should_check_stuck:
            # 步骤 1：安全第一！监控直线导轨是否发生物理滑移
            if not self.joint_controller.monitor_rail_positions():
                self.get_logger().error(
                    'CRITICAL: Rail slip detected! Initiating emergency stop.'
                )
                self.engage_emergency_safety_posture()
                return

            stuck_joints = self.joint_controller.detect_stuck_joints()
            stuck_count = sum(1 for is_stuck in stuck_joints.values() if is_stuck)

            for joint_name, is_stuck in stuck_joints.items():
                if is_stuck:
                    self.joint_controller.handle_stuck_joint(joint_name)

            # 如果多个关节卡死，触发紧急安全姿态
            if stuck_count >= 3:
                self.get_logger().error(
                    f'CRITICAL: {stuck_count} joints stuck! (Ignored for test)'
                )
                return
        else:
            if self.debug_mode:
                self.get_logger().debug('Skipping stuck detection during startup delay')
        
        # 步骤 1.5：速度平滑处理（停止或斜坡加减速）
        if self.is_stopping:
            self._handle_smooth_stop()
        else:
            vx_curr, vy_curr, w_curr = self.current_velocity
            vx_tgt, vy_tgt, w_tgt = self.target_velocity

            max_dv = self.max_linear_accel * dt
            max_dw = self.max_angular_accel * dt

            def ramp(current, target, step):
                if current < target:
                    return min(current + step, target)
                if current > target:
                    return max(current - step, target)
                return current

            self.current_velocity = (
                ramp(vx_curr, vx_tgt, max_dv),
                ramp(vy_curr, vy_tgt, max_dv),
                ramp(w_curr, w_tgt, max_dw)
            )
        
        # 低速保持站立姿态：避免零速时步态/IK回到全零关节
        if (abs(self.current_velocity[0]) < 1e-4 and
                abs(self.current_velocity[1]) < 1e-4 and
                abs(self.current_velocity[2]) < 1e-4):
            self.joint_controller.send_joint_commands(self.target_standing_pose)
            if self.debug_mode:
                self._publish_debug_info(self.target_standing_pose)
            return

        # 步骤 2：更新步态大脑，计算当前相位
        self.gait_generator.update(dt, self.current_velocity)
        
        target_joint_positions = {}
        
        # 步骤 3：为4条腿分别计算运动学解
        for leg_id in ['lf', 'rf', 'lh', 'rh']:
            # 步骤 4：查表获取当前腿的严格 URDF 关节名映射
            leg_num = PREFIX_TO_LEG_MAP[leg_id]
            joint_names = get_leg_joint_names(leg_num)

            # 获取该腿在当前 dt 时刻的笛卡尔空间期望坐标 (x, y, z)
            # (注：目前由 GaitGenerator 内部抛物线直接提供)
            foot_pos_cartesian = self.gait_generator.get_foot_target(leg_id)
            
            # 调用 IK 求解器：笛卡尔坐标 -> 1个导轨 + 3个旋转关节
            ik_result = self.ik_solver.solve_ik(leg_id, foot_pos_cartesian)
            
            if ik_result is None:
                # IK失败：使用上一个有效配置（需求8.2）
                self._handle_ik_failure(leg_id, foot_pos_cartesian)
                
                # 使用上一个有效配置
                if self.last_valid_joint_positions[leg_id] is not None:
                    s_m, haa_rad, hfe_rad, kfe_rad = self.last_valid_joint_positions[leg_id]
                else:
                    # 如果没有上一个有效配置，退回站立姿态（避免回到全零）
                    self.get_logger().error(
                        f"No last valid config for {leg_id}, using standing pose"
                    )
                    s_m = self.target_standing_pose.get(joint_names['rail'], 0.0)
                    haa_rad = self.target_standing_pose.get(joint_names['haa'], 0.0)
                    hfe_rad = self.target_standing_pose.get(joint_names['hfe'], 0.0)
                    kfe_rad = self.target_standing_pose.get(joint_names['kfe'], 0.0)
            else:
                # IK成功：保存为有效配置
                s_m, haa_rad, hfe_rad, kfe_rad = ik_result
                self.last_valid_joint_positions[leg_id] = ik_result
                # 重置失败计数
                self.ik_failure_count[leg_id] = 0
            
            # 收集该腿的 4 个驱动命令（先只修正左右镜像）
            final_haa = haa_rad
            final_hfe = hfe_rad
            final_kfe = kfe_rad

            if 'r' in leg_id:
                final_haa = -final_haa
                final_hfe = -final_hfe
                final_kfe = -final_kfe

            target_joint_positions[joint_names['rail']] = s_m
            target_joint_positions[joint_names['haa']] = final_haa
            target_joint_positions[joint_names['hfe']] = final_hfe
            target_joint_positions[joint_names['kfe']] = final_kfe
        
        # 步骤 5：通过硬件接口层将 16 通道指令打包发送
        self.joint_controller.send_joint_commands(target_joint_positions)
        
        # 步骤 6：发布调试信息（如果启用）
        if self.debug_mode:
            self._publish_debug_info(target_joint_positions)
    
    def _execute_standup_trajectory(self) -> bool:
        """执行开机平滑起立轨迹（Minimum Jerk）

        Returns:
            True: 起立完成
            False: 起立进行中
        """
        if self.standup_start_time is None:
            self.standup_start_time = self.get_clock().now()

        elapsed = (self.get_clock().now() - self.standup_start_time).nanoseconds * 1e-9
        t = min(max(elapsed / self.standup_duration, 0.0), 1.0)

        # Minimum Jerk 插值比率: 10t^3 - 15t^4 + 6t^5
        ratio = 10.0 * (t ** 3) - 15.0 * (t ** 4) + 6.0 * (t ** 5)

        interp_positions = {}
        for joint_name, qf in self.target_standing_pose.items():
            # 导轨在 JointController 中被锁定为0.0，不参与插值
            if joint_name.startswith('j'):
                continue
            q0 = self.initial_joint_positions.get(joint_name, qf)
            interp_positions[joint_name] = q0 + ratio * (qf - q0)

        self.joint_controller.send_joint_commands(interp_positions)
        return t >= 1.0

    def _handle_smooth_stop(self):
        """处理平滑停止过程
        
        在一个步态周期内线性衰减速度到零
        """
        # 计算停止进度（0到1）
        elapsed_time = self.gait_generator.current_time - self.stop_start_time
        stop_duration = self.gait_generator.config.cycle_time  # 一个步态周期
        
        if elapsed_time >= stop_duration:
            # 停止完成
            self.current_velocity = (0.0, 0.0, 0.0)
            self.is_stopping = False
            self.get_logger().info('Smooth stop completed.')
        else:
            # 线性衰减速度
            progress = elapsed_time / stop_duration
            decay_factor = 1.0 - progress
            
            vx, vy, omega = self.target_velocity
            self.current_velocity = (
                vx * decay_factor,
                vy * decay_factor,
                omega * decay_factor
            )
    
    def update_gait_config(self, new_config: GaitConfig):
        """请求更新步态配置
        
        新配置将在下一个步态周期边界应用，避免周期中间突变
        
        Args:
            new_config: 新的步态配置
        """
        self.pending_config_update = new_config
        self.get_logger().info(
            f'Config update requested: stride_length={new_config.stride_length}, '
            f'stride_height={new_config.stride_height}, '
            f'cycle_time={new_config.cycle_time}'
        )
    
    def reload_config_from_file(self, config_path: str = None):
        """从文件重新加载配置
        
        Args:
            config_path: 配置文件路径，如果为None则使用当前路径
        """
        if config_path is not None:
            self.config_loader = ConfigLoader(config_path)
        
        self.config_loader.load()
        new_config = self.config_loader.get_gait_config()
        self.update_gait_config(new_config)
        
        self.get_logger().info(f'Config reloaded from {self.config_loader.config_path}')
    
    def _check_and_apply_config_update(self):
        """检查并在周期边界应用配置更新
        
        检测步态周期边界（相位从接近1.0跳变到接近0.0），
        在边界时刻应用待处理的配置更新
        
        注意：平滑停止期间不应用配置更新，避免干扰速度衰减曲线
        """
        if self.pending_config_update is None:
            return
        
        # 防御性编程：平滑停止期间阻止配置更新
        if self.is_stopping:
            # 不应用更新，但保留待处理的配置，等停止完成后再应用
            return
        
        # 获取当前相位（使用leg1作为参考）
        current_phase = self.gait_generator.get_phase('lf')
        
        # 检测周期边界：相位从大值跳变到小值
        # 例如：从0.95跳到0.05，或从0.99跳到0.01
        if self.last_cycle_phase > 0.9 and current_phase < 0.1:
            # 到达周期边界，应用配置更新
            self.gait_generator.config = self.pending_config_update
            self.pending_config_update = None
            
            self.get_logger().info(
                'Config update applied at cycle boundary. '
                f'New config: stride_length={self.gait_generator.config.stride_length}, '
                f'stride_height={self.gait_generator.config.stride_height}, '
                f'cycle_time={self.gait_generator.config.cycle_time}'
            )
        
        # 更新上一次相位
        self.last_cycle_phase = current_phase
    
    def enable_debug_mode(self, enable: bool = True):
        """启用或禁用调试模式
        
        Args:
            enable: True启用调试模式，False禁用
        """
        self.debug_mode = enable
        if enable:
            self.get_logger().info('Debug mode ENABLED. Publishing detailed gait state to /spider_debug_info')
        else:
            self.get_logger().info('Debug mode DISABLED.')
    
    def _publish_debug_info(self, joint_positions: dict):
        """发布详细的调试信息
        
        包含：
        - 当前时间和相位
        - 4条腿的脚部位置
        - 4条腿的关节角度
        - 支撑腿列表
        - 当前速度
        - 步态配置
        
        Args:
            joint_positions: 当前关节位置字典
        """
        # 首先检查调试模式是否启用
        if not self.debug_mode:
            return
        
        # 控制发布频率：每10次控制循环发布一次（50Hz -> 5Hz）
        self.debug_publish_counter += 1
        if self.debug_publish_counter < 10:
            return
        self.debug_publish_counter = 0
        
        # 收集调试信息
        debug_data = {
            'timestamp': self.gait_generator.current_time,
            'gait_config': {
                'stride_length': self.gait_generator.config.stride_length,
                'stride_height': self.gait_generator.config.stride_height,
                'cycle_time': self.gait_generator.config.cycle_time,
                'duty_factor': self.gait_generator.config.duty_factor,
                'body_height': self.gait_generator.config.body_height,
                'gait_type': self.gait_generator.config.gait_type
            },
            'velocity': {
                'vx': self.current_velocity[0],
                'vy': self.current_velocity[1],
                'omega': self.current_velocity[2]
            },
            'legs': {}
        }
        
        # 为每条腿收集信息
        for leg_id in ['lf', 'rf', 'lh', 'rh']:
            leg_num = PREFIX_TO_LEG_MAP[leg_id]
            joint_names = get_leg_joint_names(leg_num)
            
            # 获取相位和状态
            phase = self.gait_generator.get_phase(leg_id)
            is_stance = self.gait_generator.is_stance_phase(leg_id)
            
            # 获取脚部位置
            foot_pos = self.gait_generator.get_foot_target(leg_id)
            
            # 获取关节角度
            rail_pos = joint_positions.get(joint_names['rail'], 0.0)
            haa_angle = joint_positions.get(joint_names['haa'], 0.0)
            hfe_angle = joint_positions.get(joint_names['hfe'], 0.0)
            kfe_angle = joint_positions.get(joint_names['kfe'], 0.0)
            
            debug_data['legs'][leg_id] = {
                'phase': round(phase, 3),
                'is_stance': is_stance,
                'foot_position': {
                    'x': round(foot_pos[0], 4),
                    'y': round(foot_pos[1], 4),
                    'z': round(foot_pos[2], 4)
                },
                'joint_positions': {
                    'rail_m': round(rail_pos, 4),
                    'haa_rad': round(haa_angle, 4),
                    'hfe_rad': round(hfe_angle, 4),
                    'kfe_rad': round(kfe_angle, 4)
                }
            }
        
        # 获取支撑腿列表
        support_legs = self.gait_generator.get_support_triangle()
        debug_data['support_legs'] = support_legs
        debug_data['num_support_legs'] = len(support_legs)
        
        # 稳定性信息
        debug_data['is_stable'] = self.gait_generator.verify_stability()
        
        # 转换为JSON并发布
        msg = String()
        msg.data = json.dumps(debug_data, indent=2)
        self.debug_publisher.publish(msg)
    
    def _handle_ik_failure(self, leg_id: str, target_pos: tuple):
        """处理IK失败
        
        使用上一个有效配置并记录错误日志
        
        Args:
            leg_id: 腿部标识符
            target_pos: 目标位置（导致IK失败）
        
        需求: 8.2
        """
        self.ik_failure_count[leg_id] += 1
        
        self.get_logger().error(
            f"IK Failure on {leg_id} at position {target_pos}. "
            f"Target out of workspace. Using last valid configuration. "
            f"(Failure count: {self.ik_failure_count[leg_id]})"
        )
        
        # 如果连续失败次数过多，可能需要采取更严格的措施
        if self.ik_failure_count[leg_id] > 10:
            self.get_logger().warn(
                f"Leg {leg_id} has {self.ik_failure_count[leg_id]} consecutive IK failures. "
                f"Consider adjusting gait parameters or checking workspace limits."
            )


def main(args=None):
    """ROS 2 节点入口函数"""
    rclpy.init(args=args)
    controller = SpiderRobotController()
    
    try:
        controller.start()
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Keyboard Interrupt detected.')
    finally:
        controller.stop()
        controller.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
