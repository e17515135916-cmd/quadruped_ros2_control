"""
Trajectory Planner - 轨迹规划器

生成平滑的关节角度轨迹

使用无状态解析平滑相位（Analytical Smooth Phase）方法：
- 五次多项式插值确保起止点速度和加速度都为零
- 无需实例化scipy对象，计算量极小
- 适合50Hz实时控制循环

⚠️ 重要架构注意事项：
本模块在**笛卡尔空间**生成轨迹（返回 XYZ 坐标），但安全检查方法
（check_joint_velocity_constraints, verify_trajectory_safety）期望
**关节空间**轨迹（关节角度字典）。

在主控制器中使用时，必须创建包装函数将笛卡尔轨迹转换为关节轨迹：
    cartesian_traj = planner.plan_swing_trajectory(...)
    joint_traj = lambda t: ik_solver.solve_ik(leg_id, cartesian_traj(t))
    planner.check_joint_velocity_constraints(joint_traj, ...)

详见：TRAJECTORY_SPACE_MISMATCH_WARNING.md
"""

from typing import Callable, Dict, Tuple, Optional
import numpy as np


class TrajectoryPlanner:
    """轨迹规划器
    
    使用解析平滑相位方法生成轨迹，确保：
    1. 起止点速度为零（避免冲击）
    2. 起止点加速度为零（避免Jerk）
    3. 计算量极小（无需scipy插值对象）
    """
    
    def __init__(self, joint_velocity_limits: Optional[Dict[str, float]] = None):
        """初始化轨迹规划器
        
        Args:
            joint_velocity_limits: 关节速度限制字典
                格式: {'rail': max_vel_m_per_s, 'haa': max_vel_rad_per_s, ...}
                如果为None，使用默认值
        """
        # 默认关节速度限制
        if joint_velocity_limits is None:
            self.joint_velocity_limits = {
                'rail': 0.1,    # 导轨最大速度：0.1 m/s
                'haa': 2.0,     # HAA最大角速度：2.0 rad/s
                'hfe': 2.0,     # HFE最大角速度：2.0 rad/s
                'kfe': 2.0,     # KFE最大角速度：2.0 rad/s
            }
        else:
            self.joint_velocity_limits = joint_velocity_limits
    
    @staticmethod
    def smooth_phase(s: float) -> float:
        """平滑相位函数（五次多项式）
        
        将线性相位 s ∈ [0, 1] 映射到平滑相位 φ(s) ∈ [0, 1]
        
        数学性质：
        - φ(0) = 0, φ(1) = 1
        - φ'(0) = 0, φ'(1) = 0  （速度为零）
        - φ''(0) = 0, φ''(1) = 0 （加速度为零）
        
        五次多项式：φ(s) = 6s^5 - 15s^4 + 10s^3
        
        Args:
            s: 归一化时间 [0, 1]
        
        Returns:
            平滑相位 [0, 1]
        """
        # 限制在 [0, 1] 范围内
        s = np.clip(s, 0.0, 1.0)
        # 五次多项式：确保起止速度和加速度都为零
        return 6.0 * s**5 - 15.0 * s**4 + 10.0 * s**3
    
    def plan_swing_trajectory(self, start_pos: np.ndarray, end_pos: np.ndarray,
                             duration: float, height: float) -> Callable[[float], np.ndarray]:
        """规划摆动相轨迹
        
        使用解析平滑相位方法生成摆动轨迹：
        - 水平方向：平滑插值（起止速度和加速度为零）
        - 垂直方向：平滑插值 + 平滑抛物线抬起
        
        Args:
            start_pos: 起始位置 (x, y, z) 米
            end_pos: 结束位置 (x, y, z) 米
            duration: 持续时间（秒）
            height: 抬起高度（米）
        
        Returns:
            轨迹函数 f(t) -> position，其中 t ∈ [0, duration]
        """
        # 防御性检查：避免除零错误
        if duration <= 1e-5:
            # 持续时间过短，直接返回终点位置
            return lambda t: end_pos.copy()
        
        def trajectory(t: float) -> np.ndarray:
            """
            计算时刻t的位置
            
            Args:
                t: 时间，范围 [0, duration]
            
            Returns:
                位置 (x, y, z) 米
            """
            # 归一化时间 [0, 1]
            s = np.clip(t / duration, 0.0, 1.0)
            
            # 平滑相位（确保起止速度和加速度为零）
            phi = self.smooth_phase(s)
            
            # 水平方向：平滑插值
            x = start_pos[0] + phi * (end_pos[0] - start_pos[0])
            y = start_pos[1] + phi * (end_pos[1] - start_pos[1])
            
            # 垂直方向：平滑插值 + 平滑抛物线抬起
            # 基础高度：平滑插值
            z_base = start_pos[2] + phi * (end_pos[2] - start_pos[2])
            
            # 抬起高度：使用平滑相位的抛物线
            # phi * (1 - phi) 在 phi=0.5 时达到最大值 0.25
            # 乘以 4 * height 使最大抬起高度为 height
            z_lift = 4.0 * height * phi * (1.0 - phi)
            
            z = z_base + z_lift
            
            return np.array([x, y, z])
        
        return trajectory
    
    def plan_stance_trajectory(self, start_pos: np.ndarray, end_pos: np.ndarray,
                              duration: float) -> Callable[[float], np.ndarray]:
        """规划支撑相轨迹
        
        使用解析平滑相位方法生成支撑相轨迹。
        确保起止点速度和加速度都为零，避免冲击力。
        
        Args:
            start_pos: 起始位置 (x, y, z) 米
            end_pos: 结束位置 (x, y, z) 米
            duration: 持续时间（秒）
        
        Returns:
            轨迹函数 f(t) -> position，其中 t ∈ [0, duration]
        """
        # 防御性检查：避免除零错误
        if duration <= 1e-5:
            # 持续时间过短，直接返回终点位置
            return lambda t: end_pos.copy()
        
        def trajectory(t: float) -> np.ndarray:
            """
            计算时刻t的位置
            
            Args:
                t: 时间，范围 [0, duration]
            
            Returns:
                位置 (x, y, z) 米
            """
            # 归一化时间 [0, 1]
            s = np.clip(t / duration, 0.0, 1.0)
            
            # 平滑相位（确保起止速度和加速度为零）
            phi = self.smooth_phase(s)
            
            # 所有维度使用平滑插值
            x = start_pos[0] + phi * (end_pos[0] - start_pos[0])
            y = start_pos[1] + phi * (end_pos[1] - start_pos[1])
            z = start_pos[2] + phi * (end_pos[2] - start_pos[2])
            
            return np.array([x, y, z])
        
        return trajectory

    def check_joint_velocity_constraints(
        self,
        joint_trajectory: Callable[[float], Dict[str, float]],
        duration: float,
        num_samples: int = 50
    ) -> Tuple[bool, float]:
        """检查关节轨迹是否满足速度约束
        
        通过采样轨迹并计算数值导数来检查速度约束。
        
        Args:
            joint_trajectory: 关节轨迹函数 f(t) -> {'rail': pos, 'haa': angle, ...}
            duration: 轨迹持续时间（秒）
            num_samples: 采样点数量
        
        Returns:
            (is_valid, max_violation_ratio): 
                - is_valid: 是否满足所有速度约束
                - max_violation_ratio: 最大违反比率（>1表示超速）
        """
        dt = duration / (num_samples - 1)
        max_violation_ratio = 0.0
        
        for i in range(num_samples - 1):
            t1 = i * dt
            t2 = (i + 1) * dt
            
            # 获取两个时刻的关节位置
            joints1 = joint_trajectory(t1)
            joints2 = joint_trajectory(t2)
            
            # 计算每个关节的速度
            for joint_name in joints1.keys():
                if joint_name not in self.joint_velocity_limits:
                    continue
                
                # 数值导数
                velocity = abs(joints2[joint_name] - joints1[joint_name]) / dt
                limit = self.joint_velocity_limits[joint_name]
                
                # 计算违反比率
                violation_ratio = velocity / limit
                max_violation_ratio = max(max_violation_ratio, violation_ratio)
        
        is_valid = max_violation_ratio <= 1.0
        return is_valid, max_violation_ratio
    
    def adjust_trajectory_duration(
        self,
        joint_trajectory: Callable[[float], Dict[str, float]],
        initial_duration: float,
        num_samples: int = 50,
        safety_factor: float = 1.1
    ) -> float:
        """自动调整轨迹时间以满足速度约束
        
        如果轨迹违反速度约束，自动延长持续时间。
        
        Args:
            joint_trajectory: 关节轨迹函数
            initial_duration: 初始持续时间（秒）
            num_samples: 采样点数量
            safety_factor: 安全系数（>1.0），用于留出余量
        
        Returns:
            调整后的持续时间（秒）
        """
        is_valid, max_violation_ratio = self.check_joint_velocity_constraints(
            joint_trajectory, initial_duration, num_samples
        )
        
        if is_valid:
            return initial_duration
        
        # 根据最大违反比率调整时间
        # 新时间 = 旧时间 × 违反比率 × 安全系数
        adjusted_duration = initial_duration * max_violation_ratio * safety_factor
        
        return adjusted_duration

    def verify_trajectory_safety(
        self,
        joint_trajectory: Callable[[float], Dict[str, float]],
        joint_limits: Dict[str, Tuple[float, float]],
        duration: float,
        num_samples: int = 50
    ) -> Tuple[bool, Dict[str, Tuple[float, float, float]]]:
        """验证轨迹安全性：所有关节位置在限位内
        
        分别检查导轨位移限位（米）和旋转关节角度限位（弧度）。
        
        Args:
            joint_trajectory: 关节轨迹函数 f(t) -> {'rail': pos, 'haa': angle, ...}
            joint_limits: 关节限位字典 {'rail': (min, max), 'haa': (min, max), ...}
            duration: 轨迹持续时间（秒）
            num_samples: 采样点数量
        
        Returns:
            (is_safe, violations): 
                - is_safe: 是否所有关节都在限位内
                - violations: 违反限位的关节信息
                  格式: {'joint_name': (actual_value, min_limit, max_limit)}
        """
        is_safe = True
        violations: Dict[str, Tuple[float, float, float]] = {}
        
        # 采样轨迹
        for i in range(num_samples):
            t = i * duration / (num_samples - 1)
            joints = joint_trajectory(t)
            
            # 检查每个关节
            for joint_name, position in joints.items():
                if joint_name not in joint_limits:
                    continue
                
                min_limit, max_limit = joint_limits[joint_name]
                
                # 检查是否超出限位
                if position < min_limit or position > max_limit:
                    is_safe = False
                    # 记录违反信息（只记录第一次违反）
                    if joint_name not in violations:
                        violations[joint_name] = (position, min_limit, max_limit)
        
        return is_safe, violations
    
    def clamp_trajectory_to_limits(
        self,
        joint_trajectory: Callable[[float], Dict[str, float]],
        joint_limits: Dict[str, Tuple[float, float]],
        duration: float
    ) -> Callable[[float], Dict[str, float]]:
        """将轨迹限制在关节限位内
        
        创建一个新的轨迹函数，确保所有关节位置都在安全范围内。
        
        Args:
            joint_trajectory: 原始关节轨迹函数
            joint_limits: 关节限位字典
            duration: 轨迹持续时间（秒）
        
        Returns:
            限制后的轨迹函数
        """
        def clamped_trajectory(t: float) -> Dict[str, float]:
            """限制后的轨迹"""
            joints = joint_trajectory(t)
            clamped_joints = {}
            
            for joint_name, position in joints.items():
                if joint_name in joint_limits:
                    min_limit, max_limit = joint_limits[joint_name]
                    clamped_joints[joint_name] = np.clip(position, min_limit, max_limit)
                else:
                    clamped_joints[joint_name] = position
            
            return clamped_joints
        
        return clamped_trajectory


# ============================================================================
# 使用示例和重要注意事项
# ============================================================================

"""
使用示例：

1. 基本轨迹生成（笛卡尔空间）：
    planner = TrajectoryPlanner()
    
    start_pos = np.array([0.0, 0.0, -0.3])
    end_pos = np.array([0.1, 0.0, -0.3])
    
    # 摆动相轨迹
    swing_traj = planner.plan_swing_trajectory(start_pos, end_pos, 
                                               duration=1.0, height=0.05)
    foot_pos = swing_traj(0.5)  # 获取 t=0.5s 时的脚部位置
    
    # 支撑相轨迹
    stance_traj = planner.plan_stance_trajectory(start_pos, end_pos, 
                                                 duration=1.0)

2. ⚠️ 安全检查（需要关节空间轨迹）：
    
    # 错误用法 ❌
    # planner.check_joint_velocity_constraints(swing_traj, 1.0)  
    # TypeError: swing_traj 返回 np.ndarray，不是 Dict[str, float]
    
    # 正确用法 ✅ - 必须先转换到关节空间
    from kinematics_solver import KinematicsSolver
    
    ik_solver = KinematicsSolver(leg_params)
    
    def joint_trajectory(t: float) -> Dict[str, float]:
        # 1. 获取笛卡尔位置
        foot_pos = swing_traj(t)
        
        # 2. 逆运动学求解
        rail_m, haa_rad, hfe_rad, kfe_rad = ik_solver.solve_ik('lf', foot_pos)
        
        # 3. 返回关节字典
        return {
            'rail': rail_m,
            'haa': haa_rad,
            'hfe': hfe_rad,
            'kfe': kfe_rad
        }
    
    # 现在可以安全检查
    is_valid, ratio = planner.check_joint_velocity_constraints(
        joint_trajectory, duration=1.0
    )
    
    is_safe, violations = planner.verify_trajectory_safety(
        joint_trajectory,
        joint_limits={'rail': (-0.1, 0.1), 'haa': (-2.6, 2.6), ...},
        duration=1.0
    )

3. 完整工作流（在主控制器中）：
    
    # 生成笛卡尔轨迹
    cartesian_traj = planner.plan_swing_trajectory(start, end, 1.0, 0.05)
    
    # 包装为关节轨迹
    joint_traj = lambda t: convert_to_joint_space(cartesian_traj(t))
    
    # 速度检查
    is_valid, ratio = planner.check_joint_velocity_constraints(joint_traj, 1.0)
    
    if not is_valid:
        # 自动调整时间
        new_duration = planner.adjust_trajectory_duration(joint_traj, 1.0)
        # 重新生成轨迹...
    
    # 安全性验证
    is_safe, violations = planner.verify_trajectory_safety(
        joint_traj, joint_limits, 1.0
    )
    
    if is_safe:
        # 执行轨迹
        for t in np.linspace(0, 1.0, 50):
            joints = joint_traj(t)
            send_to_robot(joints)

关键要点：
- plan_swing_trajectory / plan_stance_trajectory 返回笛卡尔轨迹
- check_joint_velocity_constraints / verify_trajectory_safety 需要关节轨迹
- 必须在主控制器中实现空间转换包装函数
- 详见：TRAJECTORY_SPACE_MISMATCH_WARNING.md
"""
