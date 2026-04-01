"""
Gait Generator - 步态生成器

生成爬行步态的相位和脚部轨迹
"""

from typing import Tuple, List, Dict
from dataclasses import dataclass
import numpy as np
import math
import rclpy.logging


@dataclass
class GaitConfig:
    """步态配置参数（保守初始值，优先保证IK可达）"""
    stride_length: float = 0.04     # 步长（米）- 保守
    stride_length_max: float = 0.10  # 步长上限（米）- 用于速度自适应限幅
    stride_height: float = 0.04     # 步高（米）- 略降低
    cycle_time: float = 2.0         # 步态周期（秒）
    duty_factor: float = 0.75       # 支撑相占比
    body_height: float = 0.20       # 身体高度（米）- 对应足端z=-0.20
    gait_type: str = "crawl"        # 步态类型

    # 落足缓冲配置（摆动相末段Z轴最小冲击收敛）
    foot_landing_buffer_enable: bool = False
    foot_landing_buffer_swing_phase_ratio: float = 0.1
    foot_landing_buffer_poly_order: int = 5
    foot_landing_buffer_target_landing_vel_z: float = 0.01


class GaitGenerator:
    """步态生成器
    
    实现爬行步态（crawl gait）：
    - 每次只有一条腿摆动，其余三条腿保持支撑
    - 腿部顺序：leg1 → leg3 → leg2 → leg4
    - 相位差：90度（360°/4腿）
    - 支撑三角形始终存在
    """
    
    # 腿部顺序映射（与项目约定一致）：1=LF, 2=LH, 3=RH, 4=RF
    LEG_ORDER = {
        'lf': 1,
        'lh': 2,
        'rh': 3,
        'rf': 4,
    }
    
    # 爬行步态相位偏移（按摆动顺序）
    # 摆动相在 [0, 0.25)，支撑相在 [0.25, 1.0)
    # 初始偏移让所有腿在 t=0 时都处于支撑相，间隔0.25保证摆动顺序。
    # lf→lh→rf→rh 依次摆动，每隔 T/4 触发一次。
    PHASE_OFFSETS = {
        'lf': 0.50,  # t=0时相位=0.50（支撑相）
        'lh': 0.75,  # t=0时相位=0.75（支撑相）
        'rf': 0.25,  # t=0时相位=0.25（支撑相起点）
        'rh': 0.00,  # t=0时相位=0.00（摆动相起点）
    }
    
    def __init__(self, config: GaitConfig, nominal_positions: Dict[str, np.ndarray] = None):
        """初始化步态生成器
        
        Args:
            config: 步态配置参数
            nominal_positions: 外部标定的名义落脚点（base_link坐标系）
        """
        self.config = config
        # stride_length 用作“基线步长”，stride_length_max 用作“速度自适应的硬上限”
        self._stride_length_limit = float(
            config.stride_length_max if getattr(config, "stride_length_max", None) is not None else config.stride_length
        )
        self.current_time = 0.0  # 当前时间（秒）
        self.velocity = (0.0, 0.0, 0.0)  # 当前速度 (vx, vy, omega)

        # 名义落脚点：优先使用外部FK标定结果，未提供时使用保守兜底值
        # 坐标系约定：X 前、Y 左、Z 上（左侧腿 Y 为正，右侧腿 Y 为负）
        # 坐标系约定：base_link 采用标准 ROS 右手系（X前、Y左、Z上）。
        # 因此左侧腿（LF/LH）Y>0，右侧腿（RF/RH）Y<0。
        default_nominal = {
            'lf': np.array([0.3, 0.2, -self.config.body_height]),
            'rf': np.array([0.3, -0.2, -self.config.body_height]),
            'lh': np.array([-0.3, 0.2, -self.config.body_height]),
            'rh': np.array([-0.3, -0.2, -self.config.body_height]),
        }
        src_nominal = nominal_positions if nominal_positions is not None else default_nominal
        self._nominal_positions: Dict[str, np.ndarray] = {
            leg_id: np.array(src_nominal[leg_id], dtype=float)
            for leg_id in ['lf', 'rf', 'lh', 'rh']
        }

        # 落足缓冲配置（从 GaitConfig 读取）
        self.enable_landing_buffer = bool(config.foot_landing_buffer_enable)
        self.swing_phase_ratio = float(config.foot_landing_buffer_swing_phase_ratio)
        self.poly_order = int(config.foot_landing_buffer_poly_order)
        self.target_landing_vel_z = float(config.foot_landing_buffer_target_landing_vel_z)
        self._landing_buffer_entry_logged: Dict[str, bool] = {
            leg_id: False for leg_id in ['lf', 'rf', 'lh', 'rh']
        }
        self._logger = rclpy.logging.get_logger("gait_generator")

        # 脚部位置记录（仅用于稳定性计算，不作为轨迹生成的数学依赖）
        self.foot_positions: Dict[str, np.ndarray] = {
            leg_id: pos.copy() for leg_id, pos in self._nominal_positions.items()
        }
        
        # 质心位置（简化假设：在base_link原点）
        self.com_position = np.array([0.0, 0.0, 0.0])
    
    def update(self, dt: float, velocity: Tuple[float, float, float]) -> None:
        """更新步态状态
        
        Args:
            dt: 时间步长（秒）
            velocity: 期望速度 (vx, vy, omega)
        """
        self.current_time += dt
        self.velocity = velocity
        
        # 根据速度调整步态参数
        self._adapt_gait_parameters(velocity)
    
    def _adapt_gait_parameters(self, velocity: Tuple[float, float, float]) -> None:
        """根据期望速度调整步态参数
        
        Args:
            velocity: 期望速度 (vx, vy, omega)
        """
        vx, vy, omega = velocity
        velocity_magnitude = math.sqrt(vx**2 + vy**2)
        
        # 步长与速度成正比（上限由配置文件给定，避免硬编码 0.04m 让大步长永远不生效）
        self.config.stride_length = min(
            velocity_magnitude * self.config.cycle_time,
            self._stride_length_limit,
        )
        
        # 允许从配置文件设置步高，不强制覆盖
        
        # 保持固定周期，避免步态中途 cycle_time 变化导致相位突跳
        # cycle_time 由配置文件给定，不在运行时动态修改
        # duty_factor 由配置文件给定；crawl 需满足至少 3 腿支撑
        # crawl 相位偏移固定为 0.25 间隔，因此 duty_factor 不能低于 0.75
        duty = float(self.config.duty_factor)
        if self.config.gait_type == "crawl":
            self.config.duty_factor = max(0.75, min(0.90, duty))
        else:
            self.config.duty_factor = max(0.55, min(0.90, duty))
    
    def get_phase(self, leg_id: str) -> float:
        """获取指定腿的当前相位
        
        Args:
            leg_id: 腿部标识 ('lf', 'rf', 'lh', 'rh')
        
        Returns:
            相位值 [0, 1)，0表示周期开始，1表示周期结束
        """
        if leg_id not in self.PHASE_OFFSETS:
            raise ValueError(f"Invalid leg_id: {leg_id}")
        
        # 计算相位：(当前时间 / 周期时间 + 相位偏移) % 1.0
        phase = (self.current_time / self.config.cycle_time + self.PHASE_OFFSETS[leg_id]) % 1.0
        return phase
    
    def is_stance_phase(self, leg_id: str) -> bool:
        """判断是否处于支撑相
        
        Args:
            leg_id: 腿部标识
        
        Returns:
            True表示支撑相，False表示摆动相
        """
        phase = self.get_phase(leg_id)
        # duty_factor = 0.75 表示75%时间支撑，25%时间摆动
        # 摆动相在相位 [0, 0.25) 区间
        swing_duration = 1.0 - self.config.duty_factor
        return phase >= swing_duration
    
    def get_support_triangle(self) -> List[str]:
        """获取当前支撑腿列表
        
        Returns:
            支撑腿的leg_id列表（应该始终有3条腿）
        """
        support_legs = []
        for leg_id in ['lf', 'rf', 'lh', 'rh']:
            if self.is_stance_phase(leg_id):
                support_legs.append(leg_id)
        return support_legs
    
    def get_phase_progress_scalar(self, leg_id: str) -> float:
        """返回当前步态在步长方向上的归一化进度标量（约在[-0.5, 0.5]）。

        该标量可作为导轨参数化IK的先验输入：
        - 负值：脚在名义点后方
        - 正值：脚在名义点前方
        """
        phase = self.get_phase(leg_id)
        swing_duration = 1.0 - self.config.duty_factor

        if self.is_stance_phase(leg_id):
            stance_phase = (phase - swing_duration) / self.config.duty_factor
            return float(0.5 - stance_phase)

        swing_phase = phase / swing_duration
        return float(swing_phase - 0.5)

    def get_foot_target(self, leg_id: str) -> Tuple[float, float, float]:
        """获取脚部目标位置（无状态锚点法防漂移）
        
        核心思想：
        - 每次计算都从固定的锚点（nominal_pos）出发
        - 不依赖历史状态，完全由当前相位决定
        - 消除累积误差和漂移
        
        Args:
            leg_id: 腿部标识
        
        Returns:
            脚部目标位置 (x, y, z) 在base_link坐标系
        """
        phase = self.get_phase(leg_id)
        is_stance = self.is_stance_phase(leg_id)
        
        # 1. 绝对锚点：使用外部FK标定的名义落脚点
        nominal_pos = self._nominal_positions[leg_id].copy()
        
        stride_vector = self._get_stride_vector()
        swing_duration = 1.0 - self.config.duty_factor

        # 零速度时直接返回名义落脚点（无水平偏移，无摆动弧）
        # Validates: Requirements 3.2
        if np.linalg.norm(stride_vector) < 1e-9:
            target_pos = nominal_pos
        elif is_stance:
            # 支撑相：身体前进 = 脚相对身体向后退
            stance_phase = (phase - swing_duration) / self.config.duty_factor
            # 轨迹：从基准点前方 (+0.5 步长) 匀速退到后方 (-0.5 步长)
            target_pos = nominal_pos + (0.5 - stance_phase) * stride_vector
        else:
            # 摆动相：脚向前迈步
            swing_phase = phase / swing_duration
            # 水平轨迹：从基准点后方 (-0.5 步长) 迈到前方 (+0.5 步长)
            target_pos = nominal_pos + (swing_phase - 0.5) * stride_vector
            # 垂直轨迹：以基准高度为底的抛物线
            height = self.config.stride_height
            target_pos[2] = nominal_pos[2] + 4 * height * swing_phase * (1 - swing_phase)

            # 摆动相末段落足缓冲（仅Z轴），保持X/Y不变
            target_pos = self._apply_landing_buffer(
                leg_id=leg_id,
                swing_phase=swing_phase,
                swing_duration=swing_duration,
                nominal_pos=nominal_pos,
                target_pos=target_pos,
            )
        
        # 更新用于稳定性计算的记录，但不作为下次轨迹的数学依赖
        self.foot_positions[leg_id] = target_pos.copy()
        
        return tuple(target_pos)
    
    def _apply_landing_buffer(
        self,
        leg_id: str,
        swing_phase: float,
        swing_duration: float,
        nominal_pos: np.ndarray,
        target_pos: np.ndarray,
    ) -> np.ndarray:
        """在摆动相末段对足端Z加入5次多项式减速缓冲。"""
        if (not self.enable_landing_buffer) or self.swing_phase_ratio <= 0.0:
            self._landing_buffer_entry_logged[leg_id] = False
            return target_pos

        buffer_start = 1.0 - self.swing_phase_ratio
        if swing_phase <= buffer_start:
            self._landing_buffer_entry_logged[leg_id] = False
            return target_pos

        # 归一化缓冲进度 [0, 1]
        buffer_phase = (swing_phase - buffer_start) / self.swing_phase_ratio
        buffer_phase = float(np.clip(buffer_phase, 0.0, 1.0))

        # 初次进入缓冲窗口时记录一次 info
        if not self._landing_buffer_entry_logged[leg_id]:
            self._landing_buffer_entry_logged[leg_id] = True
            self._logger.info(
                f"Leg {self.LEG_ORDER[leg_id]} ({leg_id.upper()}) enter landing buffer phase, "
                f"swing_phase={swing_phase:.3f}"
            )

        # 统一将 buffer_phase 映射为 s(t) 和 ds/dt（归一化时间）
        s, ds_dtau = self._poly_profile(buffer_phase)

        # 原始抛物线轨迹在摆动相中的速度 dz/d(swing_phase)
        height = self.config.stride_height
        dz_dphi_base = 4.0 * height * (1.0 - 2.0 * swing_phase)

        # 按缓冲函数缩放速度并设置落足残余速度目标
        # 约束：在缓冲末端保留小速度 target_landing_vel_z，避免完全0卡滞
        target_vel_per_phase = self.target_landing_vel_z * max(swing_duration, 1e-6)
        dz_dphi_shaped = dz_dphi_base * (1.0 - s) + target_vel_per_phase * s

        # 对应位置积分近似：使用缓冲内局部基准插值，确保末端收敛到 nominal z
        z_base = nominal_pos[2] + 4.0 * height * swing_phase * (1.0 - swing_phase)
        z_nominal = nominal_pos[2]
        z_shaped = z_base * (1.0 - s) + z_nominal * s

        target_pos_shaped = target_pos.copy()
        target_pos_shaped[2] = z_shaped

        # debug日志：打印收敛信息
        # 这里打印的是按 swing_phase 导数折算后的等效 z 速度（m/s）
        z_vel_est = dz_dphi_shaped / max(swing_duration, 1e-6)
        self._logger.debug(
            f"Leg {self.LEG_ORDER[leg_id]} buffer_phase={buffer_phase:.3f}, "
            f"Z pos={target_pos_shaped[2]:.4f}, Z vel={z_vel_est:.4f}"
        )

        return target_pos_shaped

    def _poly_profile(self, t: float) -> Tuple[float, float]:
        """返回缓冲插值 s(t) 与 ds/dt（t∈[0,1]）。"""
        if self.poly_order == 5:
            # 最小冲击五次多项式：s = 6t^5 - 15t^4 + 10t^3
            s = 6.0 * t**5 - 15.0 * t**4 + 10.0 * t**3
            ds_dt = 30.0 * t**4 - 60.0 * t**3 + 30.0 * t**2
            return float(s), float(ds_dt)

        # 降级三次（兼容配置）
        s = t**3
        ds_dt = 3.0 * t**2
        return float(s), float(ds_dt)

    def _get_stride_vector(self) -> np.ndarray:
        """计算步长向量
        
        Returns:
            步长向量 [dx, dy, 0]
        """
        vx, vy, omega = self.velocity
        
        # 简化：只考虑前进方向
        stride_length = self.config.stride_length
        
        if abs(vx) > 0.01 or abs(vy) > 0.01:
            # 归一化速度方向
            velocity_magnitude = math.sqrt(vx**2 + vy**2)
            direction = np.array([vx, vy, 0.0]) / velocity_magnitude
            stride_vector = direction * stride_length
        else:
            # 静止时步长为0
            stride_vector = np.array([0.0, 0.0, 0.0])
        
        return stride_vector
    
    def verify_stability(self) -> bool:
        """验证当前姿态的静态稳定性
        
        检查质心投影是否在支撑三角形内
        
        Returns:
            True表示稳定，False表示不稳定
        """
        support_legs = self.get_support_triangle()
        
        # 至少需要3条腿支撑
        if len(support_legs) < 3:
            return False
        
        # 获取支撑腿的脚部位置（只考虑x-y平面）
        support_points = []
        for leg_id in support_legs:
            foot_pos = self.foot_positions[leg_id]
            support_points.append(foot_pos[:2])  # 只取x, y
        
        support_points = np.array(support_points)
        
        # 质心投影（x-y平面）
        com_projection = self.com_position[:2]
        
        # 检查质心是否在支撑多边形内
        return self._point_in_polygon(com_projection, support_points)
    
    def _point_in_polygon(self, point: np.ndarray, polygon: np.ndarray) -> bool:
        """判断点是否在多边形内（射线法）
        
        Args:
            point: 点坐标 [x, y]
            polygon: 多边形顶点 [[x1, y1], [x2, y2], ...]
        
        Returns:
            True表示点在多边形内
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            
            # 检查射线是否与边相交
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        # 只有当边不是水平的时候才计算交点
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            # 如果边是垂直的或者点在交点左侧，则计数
                            if p1x == p2x or x <= xinters:
                                inside = not inside
            
            p1x, p1y = p2x, p2y
        
        return inside
    
    def calibrate_nominal_positions(self, ik_solver, standing_angles: Dict[str, tuple]) -> None:
        """从 FK 标定结果重新计算名义落脚点。

        接受标定的站立角度字典，调用 FK 计算各腿的名义落脚点，
        并更新 _nominal_positions 和 foot_positions。

        Args:
            ik_solver: KinematicsSolver 实例（需实现 solve_fk 方法）
            standing_angles: {leg_id: (s_m, haa_rad, hfe_rad, kfe_rad)} 标定的站立角度

        Requirements: 3.1, 3.4
        """
        for leg_id, angles in standing_angles.items():
            foot_pos = ik_solver.solve_fk(leg_id, angles)
            self._nominal_positions[leg_id] = np.array(foot_pos, dtype=float)
            self.foot_positions[leg_id] = self._nominal_positions[leg_id].copy()

    def compute_support_triangle_area(self) -> float:
        """计算支撑三角形的面积
        
        Returns:
            支撑三角形面积（平方米）
        """
        support_legs = self.get_support_triangle()
        
        if len(support_legs) < 3:
            return 0.0
        
        # 取前3条支撑腿
        points = []
        for leg_id in support_legs[:3]:
            foot_pos = self.foot_positions[leg_id]
            points.append(foot_pos[:2])
        
        # 使用叉积计算三角形面积
        p1, p2, p3 = points
        area = 0.5 * abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - 
                         (p3[0] - p1[0]) * (p2[1] - p1[1]))
        
        return area
