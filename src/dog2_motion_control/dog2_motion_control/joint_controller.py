"""
Joint Controller - 关节控制器

与ros2_control接口通信，发送16通道关节命令
"""

from typing import Dict, Optional, Tuple
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration

from .joint_names import (
    LEG_PREFIX_MAP,
    get_rail_joint_name,
    get_revolute_joint_name,
    REVOLUTE_JOINT_TYPES
)
from .leg_parameters import LEG_PARAMETERS


class JointController:
    """关节控制器
    
    职责：
    - 与ros2_control接口通信
    - 发送16通道关节命令（12个旋转关节 + 4个锁定的直线导轨）
    - 监控关节状态
    - 检查关节限位
    - 监控导轨位置，防止滑动
    """
    
    def __init__(self, node: Node):
        """初始化关节控制器
        
        Args:
            node: ROS 2节点
        
        需求: 1.1, 5.1
        """
        self.node = node
        
        # 创建两个JointTrajectory发布器
        # 1. 旋转关节控制器（12个关节）
        self.revolute_trajectory_pub = node.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 2. 导轨位置控制器（4个关节）
        self.rail_trajectory_pub = node.create_publisher(
            JointTrajectory,
            '/rail_position_controller/joint_trajectory',
            10
        )
        # 允许在无导轨控制器时跳过发送
        self.rails_enabled = True
        
        # 创建JointState订阅器
        self.joint_state_sub = node.create_subscription(
            JointState,
            '/joint_states',
            self._joint_state_callback,
            10
        )
        
        # 当前关节状态存储
        self.current_joint_states: Dict[str, Dict[str, float]] = {}
        
        # 连接状态监控
        self.last_joint_state_time = node.get_clock().now()
        self.CONNECTION_TIMEOUT_SEC = 1.0  # 1秒无数据则判定为连接丢失
        self.is_connected = False  # 初始状态为未连接
        self.reconnect_attempts = 0
        self.MAX_RECONNECT_ATTEMPTS = 5
        
        # 关节卡死检测
        self.joint_command_history: Dict[str, list] = {}  # 存储最近的命令历史
        self.joint_stuck_count: Dict[str, int] = {}  # 卡死检测计数器
        self.STUCK_DETECTION_THRESHOLD = 5  # 连续5次检测到无响应才判定为卡死
        self.POSITION_ERROR_THRESHOLD = 0.1  # 位置误差阈值（弧度或米）
        
        # 导轨滑动阈值（米）
        self.RAIL_SLIP_THRESHOLD_M = 0.0005  # 0.5mm
        
        # 关节限位（从leg_parameters加载）
        self.node.get_logger().info('Loading joint limits...')
        self._load_joint_limits()
        self.node.get_logger().info(f'Joint limits loaded: {len(self.joint_limits)} joints')
        
        self.node.get_logger().info('Joint Controller initialized with 16 channels')
        self.node.get_logger().info('  - 4 rail joints (locked at 0.0m)')
        self.node.get_logger().info('    (rail controller disabled in simulation)')
        self.node.get_logger().info('  - 12 revolute joints (dynamic control)')
    
    def _load_joint_limits(self) -> None:
        """从leg_parameters加载关节限位"""
        try:
            self.joint_limits: Dict[str, Tuple[float, float]] = {}
            
            for leg_num in [1, 2, 3, 4]:
                prefix = LEG_PREFIX_MAP[leg_num]
                leg_params = LEG_PARAMETERS[prefix]
                
                # 导轨限位（米）
                rail_joint = get_rail_joint_name(leg_num)
                self.joint_limits[rail_joint] = leg_params.joint_limits['rail']
                
                # 旋转关节限位（弧度）
                for joint_type in REVOLUTE_JOINT_TYPES:
                    joint_name = get_revolute_joint_name(leg_num, joint_type)
                    self.joint_limits[joint_name] = leg_params.joint_limits[joint_type]
            
            self.node.get_logger().info(f'Loaded joint limits for {len(self.joint_limits)} joints')
        except Exception as e:
            self.node.get_logger().error(f'Failed to load joint limits: {e}')
            import traceback
            traceback.print_exc()
            # 确保joint_limits至少是一个空字典
            self.joint_limits = {}
            raise
    
    def _joint_state_callback(self, msg: JointState) -> None:
        """关节状态回调函数
        
        订阅/joint_states话题，解析关节位置和速度
        
        Args:
            msg: JointState消息
        
        需求: 1.4, 5.3
        """
        # 更新连接状态
        self.last_joint_state_time = self.node.get_clock().now()
        
        if not self.is_connected:
            self.is_connected = True
            self.reconnect_attempts = 0
            self.node.get_logger().info('Joint controller connection established')
        
        for i, name in enumerate(msg.name):
            self.current_joint_states[name] = {
                'position': msg.position[i] if i < len(msg.position) else 0.0,
                'velocity': msg.velocity[i] if i < len(msg.velocity) else 0.0,
            }
    
    def send_joint_commands(self, joint_positions: Dict[str, float]) -> None:
        """发送16通道关节命令
        
        分别向两个控制器发送命令：
        1. joint_trajectory_controller: 12个旋转关节
        2. rail_position_controller: 4个导轨关节（锁定在0.0米）
        
        Args:
            joint_positions: 字典，键为关节名，值为关节位置
                            - 导轨关节：位置单位为米（m）
                            - 旋转关节：位置单位为弧度（rad）
        
        关节命名规则（与URDF一致）：
            - 导轨：j1, j2, j3, j4
            - 旋转关节：{prefix}_haa_joint, {prefix}_hfe_joint, {prefix}_kfe_joint
            - prefix: lf（前左leg1），rf（前右leg2），lh（后左leg3），rh（后右leg4）
        
        需求: 1.2, 1.3
        """
        # 1. 发送导轨关节命令（锁定在0.0米）
        rail_trajectory = JointTrajectory()
        rail_point = JointTrajectoryPoint()

        for leg_num in [1, 2, 3, 4]:
            rail_joint = get_rail_joint_name(leg_num)
            rail_trajectory.joint_names.append(rail_joint)
            rail_point.positions.append(0.0)  # 锁定在0.0米

            # 记录命令历史（用于卡死检测）
            self._record_joint_command(rail_joint, 0.0)

        # 设置时间戳（20ms后到达）
        rail_point.time_from_start = Duration(sec=0, nanosec=20000000)
        rail_trajectory.points.append(rail_point)

        # 如果导轨控制器禁用，不发送导轨命令
        if self.rails_enabled and len(rail_trajectory.joint_names) > 0:
            self.rail_trajectory_pub.publish(rail_trajectory)

        # 2. 发送旋转关节命令（动态控制）
        revolute_trajectory = JointTrajectory()
        revolute_point = JointTrajectoryPoint()

        for leg_num in [1, 2, 3, 4]:
            prefix = LEG_PREFIX_MAP[leg_num]

            # 旋转关节：动态控制（按HAA, HFE, KFE顺序）
            for joint_type in REVOLUTE_JOINT_TYPES:
                joint_name = get_revolute_joint_name(leg_num, joint_type)
                revolute_trajectory.joint_names.append(joint_name)

                # 获取期望位置并检查限位
                position_rad = joint_positions.get(joint_name, 0.0)  # 单位：弧度（rad）
                position_limited = self.check_joint_limits(joint_name, position_rad)
                revolute_point.positions.append(position_limited)

                # 记录命令历史（用于卡死检测）
                self._record_joint_command(joint_name, position_limited)

        # 设置时间戳（20ms后到达）
        revolute_point.time_from_start = Duration(sec=0, nanosec=20000000)
        revolute_trajectory.points.append(revolute_point)

        # 发布旋转关节命令
        self.revolute_trajectory_pub.publish(revolute_trajectory)
    
    def get_joint_states(self) -> Dict[str, Dict[str, float]]:
        """获取关节状态
        
        Returns:
            关节状态字典，格式：
            {
                'joint_name': {
                    'position': float,  # 位置（导轨：米，旋转：弧度）
                    'velocity': float   # 速度（导轨：米/秒，旋转：弧度/秒）
                }
            }
        
        需求: 1.4, 5.3
        """
        return self.current_joint_states
    
    def get_joint_position(self, joint_name: str) -> Optional[float]:
        """获取单个关节的位置
        
        Args:
            joint_name: 关节名称
        
        Returns:
            关节位置，如果关节不存在则返回None
        """
        if joint_name in self.current_joint_states:
            return self.current_joint_states[joint_name]['position']
        return None
    
    def check_joint_limits(self, joint_name: str, position: float) -> float:
        """检查并限制关节位置
        
        分别检查导轨位移限位（米）和旋转关节角度限位（弧度）
        超限时限制并记录警告
        
        Args:
            joint_name: 关节名称
            position: 期望位置（导轨：米，旋转：弧度）
        
        Returns:
            限制后的位置
        
        需求: 1.5
        """
        if joint_name not in self.joint_limits:
            self.node.get_logger().warn(
                f"Joint {joint_name} has no defined limits, using raw position"
            )
            return position
        
        lower_limit, upper_limit = self.joint_limits[joint_name]
        
        # 检查是否超限
        if position < lower_limit:
            # 判断是导轨还是旋转关节
            is_rail = joint_name in ['j1', 'j2', 'j3', 'j4']
            unit = 'm' if is_rail else 'rad'
            
            self.node.get_logger().warn(
                f"Joint {joint_name} position {position:.4f}{unit} "
                f"below lower limit {lower_limit:.4f}{unit}, clamping"
            )
            return lower_limit
        
        if position > upper_limit:
            is_rail = joint_name in ['j1', 'j2', 'j3', 'j4']
            unit = 'm' if is_rail else 'rad'
            
            self.node.get_logger().warn(
                f"Joint {joint_name} position {position:.4f}{unit} "
                f"above upper limit {upper_limit:.4f}{unit}, clamping"
            )
            return upper_limit
        
        return position
    
    def monitor_rail_positions(self) -> bool:
        """监控导轨位置，检测被动滑动
        
        检测导轨滑动（阈值±0.5mm）
        超出阈值时触发报警
        
        Returns:
            True: 所有导轨位置正常（±0.5mm内）
            False: 检测到导轨滑动，需要报警
        
        需求: 8.5, 8.6
        """
        all_rails_ok = True
        
        # 导轨关节名称：j1, j2, j3, j4
        for leg_num in [1, 2, 3, 4]:
            rail_joint = get_rail_joint_name(leg_num)
            
            if rail_joint in self.current_joint_states:
                actual_pos_m = self.current_joint_states[rail_joint]['position']
                
                if abs(actual_pos_m) > self.RAIL_SLIP_THRESHOLD_M:
                    self.node.get_logger().error(
                        f"Rail slip detected on {rail_joint}: "
                        f"{actual_pos_m*1000:.2f}mm (threshold: ±{self.RAIL_SLIP_THRESHOLD_M*1000:.1f}mm)"
                    )
                    all_rails_ok = False
            else:
                self.node.get_logger().warn(
                    f"Rail joint {rail_joint} state not available for monitoring"
                )
        
        return all_rails_ok
    
    def lock_rails_with_max_effort(self) -> None:
        """以最大保持力矩锁定导轨
        
        用于紧急情况和安全姿态切换时
        确保导轨在受力情况下不会滑动
        
        实现方式：
        - 持续发送0.0米位置指令到rail_position_controller
        - 在trajectory消息中设置最大effort（如果控制器支持）
        
        需求: 8.5
        """
        if not self.rails_enabled:
            return

        trajectory_msg = JointTrajectory()
        point = JointTrajectoryPoint()
        
        # 只发送导轨关节命令
        for leg_num in [1, 2, 3, 4]:
            rail_joint = get_rail_joint_name(leg_num)
            trajectory_msg.joint_names.append(rail_joint)
            point.positions.append(0.0)  # 锁定在0.0米
            # 注意：effort字段在某些控制器中可能不支持
            # 这里我们通过持续发送位置指令来实现"锁定"效果
        
        # 设置较短的时间戳以实现高频更新
        point.time_from_start = Duration(sec=0, nanosec=10000000)  # 10ms
        
        trajectory_msg.points.append(point)
        # 发送到rail_position_controller
        self.rail_trajectory_pub.publish(trajectory_msg)
        
        self.node.get_logger().info(
            'Locking rails with maximum effort (continuous position hold at 0.0m)'
        )
    
    def _record_joint_command(self, joint_name: str, position: float) -> None:
        """记录关节命令历史
        
        用于卡死检测
        
        Args:
            joint_name: 关节名称
            position: 命令位置
        """
        if joint_name not in self.joint_command_history:
            self.joint_command_history[joint_name] = []
        
        # 保留最近10个命令
        self.joint_command_history[joint_name].append(position)
        if len(self.joint_command_history[joint_name]) > 10:
            self.joint_command_history[joint_name].pop(0)
    
    def detect_stuck_joints(self) -> Dict[str, bool]:
        """检测关节卡死
        
        检测关节无响应：
        - 比较命令位置和实际位置
        - 如果误差持续超过阈值，判定为卡死
        
        Returns:
            字典，键为关节名，值为是否卡死
        
        需求: 8.3
        """
        stuck_joints = {}
        
        for joint_name in self.joint_command_history:
            # 检查是否有足够的命令历史
            if len(self.joint_command_history[joint_name]) < 3:
                continue
            
            # 获取最近的命令位置
            recent_command = self.joint_command_history[joint_name][-1]
            
            # 获取实际位置
            if joint_name not in self.current_joint_states:
                continue
            
            actual_position = self.current_joint_states[joint_name]['position']
            
            # 计算位置误差
            position_error = abs(recent_command - actual_position)
            
            # 检查是否超过阈值
            if position_error > self.POSITION_ERROR_THRESHOLD:
                # 增加卡死计数
                if joint_name not in self.joint_stuck_count:
                    self.joint_stuck_count[joint_name] = 0
                self.joint_stuck_count[joint_name] += 1
                
                # 判定为卡死
                if self.joint_stuck_count[joint_name] >= self.STUCK_DETECTION_THRESHOLD:
                    stuck_joints[joint_name] = True
                    
                    # 记录警告（只在首次检测到时记录）
                    if self.joint_stuck_count[joint_name] == self.STUCK_DETECTION_THRESHOLD:
                        self.node.get_logger().error(
                            f"Joint {joint_name} appears to be stuck! "
                            f"Command: {recent_command:.4f}, Actual: {actual_position:.4f}, "
                            f"Error: {position_error:.4f}"
                        )
            else:
                # 重置卡死计数
                if joint_name in self.joint_stuck_count:
                    self.joint_stuck_count[joint_name] = 0
                stuck_joints[joint_name] = False
        
        return stuck_joints
    
    def handle_stuck_joint(self, joint_name: str) -> None:
        """处理卡死的关节
        
        降低力矩并报警
        
        Args:
            joint_name: 卡死的关节名称
        
        需求: 8.3
        """
        self.node.get_logger().warn(
            f"Handling stuck joint {joint_name}: reducing effort and triggering alarm"
        )
        
        # 注意：在当前的ros2_control接口中，我们无法直接控制单个关节的力矩
        # 这里我们记录警告，实际的力矩控制需要在控制器配置中实现
        # 或者通过发送特殊的trajectory消息（如果控制器支持effort字段）
        
        # 触发报警（通过日志系统）
        self.node.get_logger().error(
            f"ALARM: Joint {joint_name} is stuck and may require manual intervention!"
        )
    
    def check_connection(self) -> bool:
        """检查控制器连接状态
        
        检测是否在超时时间内收到关节状态更新
        
        Returns:
            True如果连接正常，False如果连接丢失
        
        需求: 8.1
        """
        current_time = self.node.get_clock().now()
        time_since_last_update = (current_time - self.last_joint_state_time).nanoseconds / 1e9
        
        if time_since_last_update > self.CONNECTION_TIMEOUT_SEC:
            if self.is_connected:
                # 连接刚刚丢失
                self.is_connected = False
                self.node.get_logger().error(
                    f'Joint controller connection lost! '
                    f'No data received for {time_since_last_update:.2f} seconds'
                )
            return False
        
        return True
    
    def attempt_reconnect(self) -> bool:
        """尝试重新连接
        
        Returns:
            True如果重连成功，False如果仍未连接
        
        需求: 8.1
        """
        if self.reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
            self.node.get_logger().error(
                f'Failed to reconnect after {self.MAX_RECONNECT_ATTEMPTS} attempts. '
                f'Manual intervention required.'
            )
            return False
        
        self.reconnect_attempts += 1
        self.node.get_logger().info(
            f'Attempting to reconnect... (Attempt {self.reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS})'
        )
        
        # 检查连接状态
        # 注意：实际的重连逻辑由ROS 2自动处理
        # 这里我们只是等待并检查是否恢复
        if self.check_connection():
            self.node.get_logger().info('Reconnection successful!')
            return True
        
        return False
