"""
Gait Generator - 步态生成器

生成爬行步态的相位和脚部轨迹
"""

from typing import Tuple, List, Dict
from dataclasses import dataclass
import numpy as np
import math
from .leg_parameters import get_leg_parameters


@dataclass
class GaitConfig:
    """步态配置参数"""
    stride_length: float = 0.08     # 步长（米）
    stride_height: float = 0.05     # 步高（米）
    cycle_time: float = 2.0         # 步态周期（秒）
    duty_factor: float = 0.75       # 支撑相占比
    body_height: float = 0.16       # 身体高度（米）
    gait_type: str = "crawl"        # 步态类型


class GaitGenerator:
    """步态生成器
    
    实现爬行步态（crawl gait）：
    - 每次只有一条腿摆动，其余三条腿保持支撑
    - 腿部顺序：leg1 → leg3 → leg2 → leg4
    - 相位差：90度（360°/4腿）
    - 支撑三角形始终存在
    """
    
    # 腿部顺序映射：leg_id -> leg_num
    LEG_ORDER = {
        'lf': 1,  # leg1: 前左
        'lh': 3,  # leg3: 后左
        'rf': 2,  # leg2: 前右
        'rh': 4,  # leg4: 后右
    }
    
    # 爬行步态相位偏移（按摆动顺序）
    # 摆动相在 [0, 0.25)，支撑相在 [0.25, 1.0)
    # 要实现 leg1 → leg3 → leg2 → leg4 的摆动顺序：
    # - leg1 在相位0.0开始摆动
    # - leg3 在相位0.0开始摆动（需要在T/4后）→ 相位偏移 -0.25 = 0.75
    # - leg2 在相位0.0开始摆动（需要在T/2后）→ 相位偏移 -0.5 = 0.5
    # - leg4 在相位0.0开始摆动（需要在3T/4后）→ 相位偏移 -0.75 = 0.25
    PHASE_OFFSETS = {
        'lf': 0.0,    # leg1: 在t=0时相位=0.0，立即摆动
        'lh': 0.75,   # leg3: 在t=0时相位=0.75，在t=T/4时相位=0.0，开始摆动
        'rf': 0.5,    # leg2: 在t=0时相位=0.5，在t=T/2时相位=0.0，开始摆动
        'rh': 0.25,   # leg4: 在t=0时相位=0.25，在t=3T/4时相位=0.0，开始摆动
    }
    
    def __init__(self, config: GaitConfig):
        """初始化步态生成器
        
        Args:
            config: 步态配置参数
        """
        self.config = config
        self.current_time = 0.0  # 当前时间（秒）
        self.velocity = (0.0, 0.0, 0.0)  # 当前速度 (vx, vy, omega)
        
        # 脚部位置记录（仅用于稳定性计算，不作为轨迹生成的数学依赖）
        self.foot_positions: Dict[str, np.ndarray] = {
            'lf': np.array([0.3, -0.2, -self.config.body_height]),
            'rf': np.array([0.3, 0.2, -self.config.body_height]),
            'lh': np.array([-0.3, -0.2, -self.config.body_height]),
            'rh': np.array([-0.3, 0.2, -self.config.body_height]),
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
        
        # 步长与速度成正比（爬行步态步长较小）
        self.config.stride_length = min(velocity_magnitude * self.config.cycle_time, 0.06)
        
        # 允许从配置文件设置步高，不强制覆盖
        
        # 速度较快时可以适当缩短周期，但仍保持静态稳定
        if velocity_magnitude > 0.15:
            self.config.cycle_time = 1.5
        else:
            self.config.cycle_time = 2.0
        
        # 始终保持75% duty factor确保3腿着地
        self.config.duty_factor = 0.75
    
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
        
        # 1. 绝对锚点：蜘蛛式外展姿态（与新机械结构匹配）
        leg_params = get_leg_parameters(leg_id)
        x_offset = 0.02 if 'f' in leg_id else -0.02
        y_offset = 0.1075 if 'l' in leg_id else -0.1075

        nominal_pos = leg_params.base_position + np.array([
            x_offset,
            y_offset,
            -self.config.body_height
        ])
        
        stride_vector = self._get_stride_vector()
        swing_duration = 1.0 - self.config.duty_factor
        
        if is_stance:
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
        
        # 更新用于稳定性计算的记录，但不作为下次轨迹的数学依赖
        self.foot_positions[leg_id] = target_pos.copy()
        
        return tuple(target_pos)
    
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
