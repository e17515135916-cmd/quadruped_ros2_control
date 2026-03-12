#!/usr/bin/env python3
"""
Dog2 四自由度腿部逆运动学求解器 (Python 实现)

关节链结构（每条腿）：
1. j${leg_num}   - 移动关节（prismatic）- 直线导轨，沿 X 轴
2. j${leg_num}1  - 旋转关节（revolute） - 髋关节侧摆（HAA）
3. j${leg_num}11 - 旋转关节（revolute） - 髋关节俯仰（HFE）
4. j${leg_num}111- 旋转关节（revolute） - 膝关节（KFE）

求解策略：
- 直线导轨位置作为输入参数（参数化策略）
- 基于给定的导轨位置，求解剩余 3 个旋转关节的解析解
"""

import numpy as np
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class LegGeometry:
    """腿部几何参数"""
    # 从基座到移动关节的偏移
    base_to_prismatic_offset: np.ndarray
    
    # 从移动关节到髋关节侧摆轴的偏移
    prismatic_to_haa_offset: np.ndarray
    
    # 从髋关节侧摆轴到髋关节俯仰轴的偏移
    haa_to_hfe_offset: np.ndarray
    
    # 大腿长度（髋关节俯仰轴到膝关节）
    thigh_length: float
    
    # 小腿长度（膝关节到足端）
    shin_length: float
    
    # 关节限位
    prismatic_lower: float
    prismatic_upper: float
    haa_lower: float
    haa_upper: float
    hfe_lower: float
    hfe_upper: float
    kfe_lower: float
    kfe_upper: float


@dataclass
class IKSolution:
    """逆运动学求解结果"""
    prismatic: float  # 移动关节位置 [m]
    haa: float        # 髋关节侧摆角度 [rad]
    hfe: float        # 髋关节俯仰角度 [rad]
    kfe: float        # 膝关节角度 [rad]
    valid: bool       # 解是否有效
    error_msg: str = ""  # 错误信息


class LegIK4DOF:
    """Dog2 四自由度腿部逆运动学求解器"""
    
    def __init__(self, geometry: LegGeometry):
        """
        构造函数
        
        Args:
            geometry: 腿部几何参数
        """
        self.geometry = geometry
    
    def solve(self, foot_position_base: np.ndarray, 
              prismatic_position: float) -> IKSolution:
        """
        求解逆运动学（给定移动关节位置）
        
        Args:
            foot_position_base: 足端在基座坐标系中的目标位置 [x, y, z]
            prismatic_position: 移动关节的位置（参数化输入）[m]
        
        Returns:
            IKSolution: 逆运动学解
        
        求解流程：
        1. 使用给定的 prismatic_position 计算移动关节的位置
        2. 将足端位置转换到移动关节坐标系
        3. 求解 HAA（髋关节侧摆）
        4. 将问题投影到 HFE-KFE 平面
        5. 使用 2R 平面逆运动学求解 HFE 和 KFE
        """
        solution = IKSolution(
            prismatic=prismatic_position,
            haa=0.0,
            hfe=0.0,
            kfe=0.0,
            valid=False
        )
        
        # 步骤 1: 计算移动关节在基座坐标系中的位置
        # 移动关节沿 X 轴移动，从 base_to_prismatic_offset 开始
        prismatic_pos = self.geometry.base_to_prismatic_offset.copy()
        prismatic_pos[0] += prismatic_position  # 沿 -X 方向移动
        
        # 步骤 2: 计算髋关节侧摆轴（HAA）在基座坐标系中的位置
        haa_pos = prismatic_pos + self.geometry.prismatic_to_haa_offset
        
        # 步骤 3: 计算从 HAA 到足端的向量
        haa_to_foot = foot_position_base - haa_pos
        
        # 步骤 4: 求解 HAA（髋关节侧摆角度）
        # 注意：虽然 URDF 中 axis="1 0 0"，但由于 rpy="0 0 1.5708"（Z 轴旋转 90 度），
        # 实际上关节在父坐标系中是绕 Y 轴旋转的
        # HAA 控制腿在 X-Z 平面的侧向摆动
        haa_distance_xz = np.sqrt(haa_to_foot[0]**2 + haa_to_foot[2]**2)
        
        if haa_distance_xz < 1e-6:
            solution.error_msg = "足端位置太接近 HAA 轴"
            return solution
        
        # HAA 角度（绕 Y 轴旋转，从 X 轴到足端在 X-Z 平面的投影）
        # 对于 Y 轴旋转：正角度使 X 轴向 Z 轴旋转
        solution.haa = np.arctan2(haa_to_foot[2], haa_to_foot[0])
        
        # 步骤 5: 计算髋关节俯仰轴（HFE）在基座坐标系中的位置
        # HFE 相对于 HAA 有一个偏移
        # 对于 Y 轴旋转，旋转矩阵为：
        # Ry(θ) = [ cos(θ)  0  sin(θ)]
        #         [   0     1    0   ]
        #         [-sin(θ)  0  cos(θ)]
        hfe_offset_rotated = np.array([
            self.geometry.haa_to_hfe_offset[0] * np.cos(solution.haa) + 
            self.geometry.haa_to_hfe_offset[2] * np.sin(solution.haa),
            self.geometry.haa_to_hfe_offset[1],
            -self.geometry.haa_to_hfe_offset[0] * np.sin(solution.haa) + 
            self.geometry.haa_to_hfe_offset[2] * np.cos(solution.haa)
        ])
        
        hfe_pos = haa_pos + hfe_offset_rotated
        
        # 步骤 6: 将问题投影到 HFE-KFE 平面
        # 在这个平面内，我们有一个 2R 机械臂问题
        hfe_to_foot = foot_position_base - hfe_pos
        
        # 计算在 HFE 平面内的坐标
        # 对于 Y 轴旋转，平面在旋转后的 X-Y 局部坐标系中
        plane_x = (hfe_to_foot[0] * np.cos(solution.haa) - 
                   hfe_to_foot[2] * np.sin(solution.haa))
        plane_y = hfe_to_foot[1]
        
        # 步骤 7: 求解 2R 平面逆运动学
        success, hfe, kfe = self._solve_2r_plane_ik(
            plane_x, plane_y,
            self.geometry.thigh_length,
            self.geometry.shin_length
        )
        
        if not success:
            solution.error_msg = "2R 平面逆运动学无解（目标点超出工作空间）"
            return solution
        
        solution.hfe = hfe
        solution.kfe = kfe
        
        # 步骤 8: 检查关节限位
        if not self._check_joint_limits(solution.prismatic, solution.haa,
                                        solution.hfe, solution.kfe):
            solution.error_msg = "关节超出限位"
            return solution
        
        solution.valid = True
        return solution
    
    def solve_with_optimization(self, foot_position_base: np.ndarray,
                                prismatic_preference: float = 0.0) -> IKSolution:
        """
        求解逆运动学（自动优化移动关节位置）
        
        Args:
            foot_position_base: 足端在基座坐标系中的目标位置 [x, y, z]
            prismatic_preference: 移动关节的偏好位置（默认为中间位置）[m]
        
        Returns:
            IKSolution: 逆运动学解
        
        优化策略：
        - 尝试使用 prismatic_preference
        - 如果无解，在允许范围内搜索最优位置
        """
        # 首先尝试使用偏好位置
        solution = self.solve(foot_position_base, prismatic_preference)
        if solution.valid:
            return solution
        
        # 如果偏好位置无解，搜索最优位置
        num_samples = 20
        best_error = float('inf')
        best_solution = IKSolution(0, 0, 0, 0, False, "在整个移动关节范围内都无解")
        
        for i in range(num_samples):
            prismatic = (self.geometry.prismatic_lower + 
                        (self.geometry.prismatic_upper - self.geometry.prismatic_lower) * 
                        i / (num_samples - 1))
            
            candidate = self.solve(foot_position_base, prismatic)
            if candidate.valid:
                # 计算与偏好位置的距离
                error = abs(prismatic - prismatic_preference)
                if error < best_error:
                    best_error = error
                    best_solution = candidate
        
        return best_solution
    
    def forward_kinematics(self, prismatic: float, haa: float,
                          hfe: float, kfe: float) -> np.ndarray:
        """
        正运动学（验证用）
        
        Args:
            prismatic: 移动关节位置 [m]
            haa: 髋关节侧摆角度 [rad] (绕 Y 轴旋转)
            hfe: 髋关节俯仰角度 [rad]
            kfe: 膝关节角度 [rad]
        
        Returns:
            足端在基座坐标系中的位置 [x, y, z]
        """
        # 移动关节位置
        prismatic_pos = self.geometry.base_to_prismatic_offset.copy()
        prismatic_pos[0] += prismatic
        
        # HAA 位置
        haa_pos = prismatic_pos + self.geometry.prismatic_to_haa_offset
        
        # HFE 位置（考虑 HAA 绕 Y 轴旋转）
        # 对于 Y 轴旋转，旋转矩阵为：
        # Ry(θ) = [ cos(θ)  0  sin(θ)]
        #         [   0     1    0   ]
        #         [-sin(θ)  0  cos(θ)]
        hfe_offset_rotated = np.array([
            self.geometry.haa_to_hfe_offset[0] * np.cos(haa) + 
            self.geometry.haa_to_hfe_offset[2] * np.sin(haa),
            self.geometry.haa_to_hfe_offset[1],
            -self.geometry.haa_to_hfe_offset[0] * np.sin(haa) + 
            self.geometry.haa_to_hfe_offset[2] * np.cos(haa)
        ])
        
        hfe_pos = haa_pos + hfe_offset_rotated
        
        # 大腿末端位置（膝关节）
        thigh_x = self.geometry.thigh_length * np.cos(hfe)
        thigh_y = self.geometry.thigh_length * np.sin(hfe)
        
        # 小腿末端位置（足端）
        shin_x = self.geometry.shin_length * np.cos(hfe + kfe)
        shin_y = self.geometry.shin_length * np.sin(hfe + kfe)
        
        # 在 HFE 平面内的位置
        plane_x = thigh_x + shin_x
        plane_y = thigh_y + shin_y
        
        # 转换回基座坐标系（考虑 HAA 绕 Y 轴旋转）
        # plane_x 在 X-Z 平面内，需要通过 Y 轴旋转变换
        foot_pos = np.array([
            hfe_pos[0] + plane_x * np.cos(haa),
            hfe_pos[1] + plane_y,
            hfe_pos[2] + plane_x * np.sin(haa)
        ])
        
        return foot_pos
    
    def _solve_2r_plane_ik(self, x: float, y: float, l1: float, l2: float) -> Tuple[bool, float, float]:
        """
        求解 2R 平面逆运动学（HFE-KFE）
        
        Args:
            x: 目标点 X 坐标（在 HFE 平面内）
            y: 目标点 Y 坐标（在 HFE 平面内）
            l1: 大腿长度
            l2: 小腿长度
        
        Returns:
            (success, hfe, kfe): 是否成功，髋关节俯仰角度，膝关节角度
        """
        distance_sq = x**2 + y**2
        distance = np.sqrt(distance_sq)
        
        # 检查是否在工作空间内（添加小的容差以处理数值误差）
        if distance > l1 + l2 + 1e-6 or distance < abs(l1 - l2) - 1e-6:
            return False, 0.0, 0.0
        
        # 使用余弦定理求解膝关节角度
        cos_kfe = (l1**2 + l2**2 - distance_sq) / (2.0 * l1 * l2)
        
        # 数值稳定性检查
        cos_kfe = np.clip(cos_kfe, -1.0, 1.0)
        
        # 膝关节角度（肘向上配置，负角度表示弯曲）
        # 注意：根据 URDF，膝关节的上限是 0，下限是 -2.8
        # cos_kfe 是两个连杆之间的夹角的余弦
        # 当腿伸直时，夹角 = 0，cos = 1，kfe = 0
        # 当腿弯曲时，夹角 > 0，cos < 1，kfe < 0
        # 关节角度 = -(π - 夹角) = 夹角 - π
        angle_between_links = np.arccos(cos_kfe)
        kfe = angle_between_links - np.pi
        
        # 求解髋关节俯仰角度
        alpha = np.arctan2(y, x)
        
        # 处理完全伸直的特殊情况
        if abs(distance - (l1 + l2)) < 1e-6:
            # 腿完全伸直，beta = 0
            beta = 0.0
        else:
            cos_beta = (l1**2 + distance_sq - l2**2) / (2.0 * l1 * distance)
            cos_beta = np.clip(cos_beta, -1.0, 1.0)
            beta = np.arccos(cos_beta)
        
        hfe = alpha - beta
        
        return True, hfe, kfe
    
    def _check_joint_limits(self, prismatic: float, haa: float,
                           hfe: float, kfe: float) -> bool:
        """检查关节限位"""
        if prismatic < self.geometry.prismatic_lower or prismatic > self.geometry.prismatic_upper:
            return False
        if haa < self.geometry.haa_lower or haa > self.geometry.haa_upper:
            return False
        if hfe < self.geometry.hfe_lower or hfe > self.geometry.hfe_upper:
            return False
        if kfe < self.geometry.kfe_lower or kfe > self.geometry.kfe_upper:
            return False
        return True


def create_dog2_leg_geometry(leg_num: int) -> LegGeometry:
    """
    创建 Dog2 腿部几何参数（基于 URDF）
    
    Args:
        leg_num: 腿编号（1-4）
            1: 前左
            2: 前右
            3: 后左
            4: 后右
    
    Returns:
        LegGeometry: 腿部几何参数
    """
    # 从基座到移动关节的偏移（根据 URDF origin）
    if leg_num == 1:
        base_to_prismatic_offset = np.array([1.1026, -0.80953, 0.2649])
    elif leg_num == 2:
        base_to_prismatic_offset = np.array([1.1026, 0.80953, 0.2649])
    elif leg_num == 3:
        base_to_prismatic_offset = np.array([-1.1026, -0.80953, 0.2649])
    elif leg_num == 4:
        base_to_prismatic_offset = np.array([-1.1026, 0.80953, 0.2649])
    else:
        raise ValueError(f"Invalid leg number: {leg_num}. Must be 1-4.")
    
    # 从移动关节到 HAA 的偏移（根据 URDF hip_joint_xyz）
    prismatic_to_haa_offset = np.array([-0.016, 0.0199, 0.055])
    
    # 从 HAA 到 HFE 的偏移（根据 URDF knee_joint_xyz）
    haa_to_hfe_offset = np.array([-0.0233, -0.055, 0.0274])
    
    # 大腿长度（根据 URDF j${leg_num}111 origin）
    thigh_length = np.sqrt(0.15201**2 + 0.12997**2)
    
    # 小腿长度（根据 URDF j${leg_num}1111 origin）
    shin_length = 0.299478
    
    return LegGeometry(
        base_to_prismatic_offset=base_to_prismatic_offset,
        prismatic_to_haa_offset=prismatic_to_haa_offset,
        haa_to_hfe_offset=haa_to_hfe_offset,
        thigh_length=thigh_length,
        shin_length=shin_length,
        prismatic_lower=-0.1,  # 需要根据实际 URDF 调整
        prismatic_upper=0.1,
        haa_lower=-2.618,      # ±150°
        haa_upper=2.618,
        hfe_lower=-2.8,        # ±160°
        hfe_upper=2.8,
        kfe_lower=-2.8,
        kfe_upper=0.0          # 根据 URDF，膝关节只能向一个方向弯曲
    )
