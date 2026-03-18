"""
运动学求解器

实现腿部的逆运动学(IK)和正运动学(FK)求解
支持4条腿的坐标系转换
"""

from typing import Optional, Tuple, Dict
import numpy as np
from .leg_parameters import LegParameters, get_leg_parameters


class KinematicsSolver:
    """
    运动学求解器
    
    负责计算腿部的逆运动学和正运动学
    当前阶段：导轨锁定在0.0米，只求解3个旋转关节
    """
    
    def __init__(self, leg_params: Dict[str, LegParameters]):
        """
        初始化运动学求解器
        
        Args:
            leg_params: 腿部参数字典，键为leg_id
        """
        self.leg_params = leg_params
    
    def _rotation_matrix_from_rpy(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        """
        从RPY角度创建旋转矩阵
        
        Args:
            roll: 绕X轴旋转（弧度）
            pitch: 绕Y轴旋转（弧度）
            yaw: 绕Z轴旋转（弧度）
        
        Returns:
            3x3旋转矩阵
        """
        # 绕X轴旋转
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll), np.cos(roll)]
        ])
        
        # 绕Y轴旋转
        Ry = np.array([
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])
        
        # 绕Z轴旋转
        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw), np.cos(yaw), 0],
            [0, 0, 1]
        ])
        
        # 组合旋转：R = Rz * Ry * Rx
        return Rz @ Ry @ Rx
    
    def _transform_to_leg_frame(self, foot_pos: np.ndarray, leg_id: str) -> np.ndarray:
        """
        将脚部位置从base_link坐标系转换到腿部局部坐标系
        
        Args:
            foot_pos: 脚部位置在base_link坐标系 [x, y, z] (米)
            leg_id: 腿部标识符
        
        Returns:
            脚部位置在腿部局部坐标系 [x, y, z] (米)
        """
        params = self.leg_params[leg_id]
        
        # 平移到腿部基座坐标系
        pos_relative = foot_pos - params.base_position
        
        # 应用旋转变换（从base_link到腿部坐标系）
        roll, pitch, yaw = params.base_rotation
        R = self._rotation_matrix_from_rpy(roll, pitch, yaw)
        
        # 转换到腿部局部坐标系
        pos_local = R.T @ pos_relative
        
        return pos_local
    
    def _transform_from_leg_frame(self, pos_local: np.ndarray, leg_id: str) -> np.ndarray:
        """
        将位置从腿部局部坐标系转换到base_link坐标系
        
        Args:
            pos_local: 位置在腿部局部坐标系 [x, y, z] (米)
            leg_id: 腿部标识符
        
        Returns:
            位置在base_link坐标系 [x, y, z] (米)
        """
        params = self.leg_params[leg_id]
        
        # 应用旋转变换（从腿部坐标系到base_link）
        roll, pitch, yaw = params.base_rotation
        R = self._rotation_matrix_from_rpy(roll, pitch, yaw)
        
        # 转换到base_link坐标系
        pos_base = R @ pos_local
        
        # 平移到base_link坐标系
        pos_global = pos_base + params.base_position
        
        return pos_global
    
    def solve_ik(self, leg_id: str, foot_pos: Tuple[float, float, float], 
                 rail_offset: float = 0.0) -> Optional[Tuple[float, float, float, float]]:
        """
        求解逆运动学
        
        Args:
            leg_id: 腿部标识符 ('lf', 'rf', 'lh', 'rh')
            foot_pos: 脚部目标位置 (x, y, z) 在base_link坐标系，单位：米
            rail_offset: 导轨位移（当前阶段固定传入0.0），单位：米
        
        Returns:
            (s_m, θ_haa_rad, θ_hfe_rad, θ_kfe_rad) 或 None（如果无解）
            - s_m: 导轨位移，单位：米
            - θ_haa_rad: HAA关节角度，单位：弧度
            - θ_hfe_rad: HFE关节角度，单位：弧度
            - θ_kfe_rad: KFE关节角度，单位：弧度
        """
        params = self.leg_params[leg_id]
        
        # 当前阶段：导轨锁定在0.0米
        # 未来扩展：可以传入非零的rail_offset
        s_m = rail_offset
        
        # 关键安全检查：验证导轨位移在限位范围内
        rail_min, rail_max = params.joint_limits['rail']
        if s_m < rail_min or s_m > rail_max:
            # 导轨位移超出限位，返回无解
            return None
        
        # 将步态目标转换到腿部局部坐标系
        foot_pos_array = np.array(foot_pos)
        foot_pos_local = self._transform_to_leg_frame(foot_pos_array, leg_id)

        # 4-DoF冗余降维：减去导轨位移，得到相对于HAA关节的位置
        # 导轨沿着腿部局部坐标系的X轴移动
        foot_pos_local[0] = foot_pos_local[0] - s_m

        # 提取局部坐标
        px, py, pz = foot_pos_local  # 单位：米

        # 坐标系修正：将向下的Z轴视为正
        pz = -pz
        
        # 提取链长
        L1, L2, L3 = params.link_lengths
        
        # 步骤1: 计算HAA角度（弧度）
        # HAA控制腿部的侧向张开/收回
        theta_haa_rad = np.arctan2(py, pz)
        
        # 步骤2: 计算HFE和KFE角度（2R平面机械臂）
        # 投影到平面后的径向距离
        r = np.sqrt(py**2 + pz**2) - L1  # 单位：米
        
        # 到目标点的距离
        d = np.sqrt(r**2 + px**2)  # 单位：米
        
        # 检查工作空间（三角不等式）
        if d > L2 + L3 or d < abs(L2 - L3):
            # 无解：目标点超出工作空间
            return None
        
        # 使用余弦定理计算KFE角度
        cos_theta_kfe = (d**2 - L2**2 - L3**2) / (2 * L2 * L3)
        
        # 数值稳定性检查
        if cos_theta_kfe < -1.0:
            cos_theta_kfe = -1.0
        elif cos_theta_kfe > 1.0:
            cos_theta_kfe = 1.0
        
        theta_kfe_rad = np.arccos(cos_theta_kfe)  # 单位：弧度
        
        # 计算HFE角度
        alpha = np.arctan2(px, r)  # 弧度
        beta = np.arctan2(L3 * np.sin(theta_kfe_rad), 
                         L2 + L3 * np.cos(theta_kfe_rad))  # 弧度
        theta_hfe_rad = alpha - beta  # 弧度
        
        # 检查关节限位
        if not self._check_joint_limits(leg_id, theta_haa_rad, theta_hfe_rad, theta_kfe_rad):
            return None
        
        return (s_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad)
    
    def _check_joint_limits(self, leg_id: str, theta_haa: float, 
                           theta_hfe: float, theta_kfe: float) -> bool:
        """
        检查关节角度是否在限位范围内
        
        Args:
            leg_id: 腿部标识符
            theta_haa: HAA关节角度（弧度）
            theta_hfe: HFE关节角度（弧度）
            theta_kfe: KFE关节角度（弧度）
        
        Returns:
            True如果所有关节都在限位内，否则False
        """
        params = self.leg_params[leg_id]
        limits = params.joint_limits
        
        # 检查HAA
        haa_min, haa_max = limits['haa']
        if theta_haa < haa_min or theta_haa > haa_max:
            return False
        
        # 检查HFE
        hfe_min, hfe_max = limits['hfe']
        if theta_hfe < hfe_min or theta_hfe > hfe_max:
            return False
        
        # 检查KFE
        kfe_min, kfe_max = limits['kfe']
        if theta_kfe < kfe_min or theta_kfe > kfe_max:
            return False
        
        return True
    
    def solve_fk(self, leg_id: str, 
                 joint_positions: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        """
        求解正运动学
        
        Args:
            leg_id: 腿部标识符 ('lf', 'rf', 'lh', 'rh')
            joint_positions: 关节位置 (s_m, θ_haa_rad, θ_hfe_rad, θ_kfe_rad)
                - s_m: 导轨位移，单位：米
                - θ_haa_rad: HAA关节角度，单位：弧度
                - θ_hfe_rad: HFE关节角度，单位：弧度
                - θ_kfe_rad: KFE关节角度，单位：弧度
        
        Returns:
            脚部位置在base_link坐标系 (x, y, z) 元组（米）
        """
        params = self.leg_params[leg_id]
        s_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad = joint_positions
        
        # 提取链长
        L1, L2, L3 = params.link_lengths
        
        # 在腿部局部坐标系中计算脚部位置
        # HAA关节产生的侧向偏移
        r_haa = L1
        
        # HFE和KFE关节在平面内的运动
        # HFE关节位置（相对于HAA）
        x_hfe = 0.0
        y_hfe = r_haa * np.sin(theta_haa_rad)
        z_hfe = r_haa * np.cos(theta_haa_rad)
        
        # KFE关节位置（相对于HFE）
        x_kfe = L2 * np.sin(theta_hfe_rad)
        r_kfe = L2 * np.cos(theta_hfe_rad)
        
        # 脚部位置（相对于KFE）
        x_foot_rel = L3 * np.sin(theta_hfe_rad + theta_kfe_rad)
        r_foot_rel = L3 * np.cos(theta_hfe_rad + theta_kfe_rad)
        
        # 组合得到脚部在腿部局部坐标系的位置（相对于HAA关节）
        px = x_hfe + x_kfe + x_foot_rel
        py = y_hfe + (r_kfe + r_foot_rel) * np.sin(theta_haa_rad)
        pz = z_hfe + (r_kfe + r_foot_rel) * np.cos(theta_haa_rad)
        
        # 关键修复：加上导轨位移
        # 导轨沿着腿部局部坐标系的X轴移动
        px = px + s_m
        
        pos_local = np.array([px, py, pz])
        
        # 转换到base_link坐标系
        pos_global = self._transform_from_leg_frame(pos_local, leg_id)
        
        # 转换为元组以符合类型契约
        return (float(pos_global[0]), float(pos_global[1]), float(pos_global[2]))


# 便捷函数
def create_kinematics_solver() -> KinematicsSolver:
    """
    创建运动学求解器实例
    
    Returns:
        KinematicsSolver对象
    """
    from .leg_parameters import LEG_PARAMETERS
    return KinematicsSolver(LEG_PARAMETERS)


# 示例用法
if __name__ == '__main__':
    solver = create_kinematics_solver()
    
    print("运动学求解器测试\n")
    
    # 测试leg1 (lf)的IK和FK
    leg_id = 'lf'
    target_pos = (1.0, -0.9, 0.0)  # 示例目标位置（米）
    
    print(f"目标位置 ({leg_id}): {target_pos}")
    
    # 逆运动学
    joint_angles = solver.solve_ik(leg_id, target_pos)
    if joint_angles is not None:
        s, theta_haa, theta_hfe, theta_kfe = joint_angles
        print(f"IK解:")
        print(f"  导轨位移: {s:.4f} m")
        print(f"  HAA角度: {np.degrees(theta_haa):.2f}°")
        print(f"  HFE角度: {np.degrees(theta_hfe):.2f}°")
        print(f"  KFE角度: {np.degrees(theta_kfe):.2f}°")
        
        # 正运动学验证
        result_pos = solver.solve_fk(leg_id, joint_angles)
        print(f"FK结果: {result_pos}")
        print(f"误差: {np.linalg.norm(result_pos - np.array(target_pos)):.6f} m")
    else:
        print("IK无解（目标位置超出工作空间）")
