"""
腿部参数数据模型

定义机器人腿部的几何参数、关节限位和坐标系转换信息
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

from .joint_semantics import (
    COXA_ORIGIN_RPY,
    FEMUR_ORIGIN_RPY,
    LEG_BASE_RPY,
    RAIL_LIMITS_BY_LEG,
    TIBIA_ORIGIN_RPY,
)


@dataclass
class LegParameters:
    """
    单条腿的参数配置
    
    Attributes:
        leg_id: 腿部标识符 ('lf', 'rf', 'lh', 'rh')
        leg_num: 腿部编号 (1, 2, 3, 4)
        base_position: 腿部基座在base_link中的位置 [x, y, z] (米)
        base_rotation: 腿部坐标系旋转 [roll, pitch, yaw] (弧度)
        hip_offset:  rail_link -> coxa_joint 的位移 [x, y, z] (米)
        hip_rpy: coxa_joint origin 的固定 rpy [roll, pitch, yaw] (弧度)
        knee_offset: coxa_link -> femur_joint 的位移 [x, y, z] (米)
        knee_rpy: femur_joint origin 的固定 rpy [roll, pitch, yaw] (弧度)
        tibia_offset: femur_link -> tibia_joint 的位移 [x, y, z] (米)
        tibia_rpy: tibia_joint origin 的固定 rpy [roll, pitch, yaw] (弧度)
        link_lengths: 链长 (HFE到KFE, KFE到foot) (米)
        joint_limits: 关节限位字典 {'rail': (下限, 上限), 'coxa': (下限, 上限), ...}
        foot_tip_offset_tibia: foot_link 原点在 tibia_link 坐标系下的平移（与 URDF *_foot_fixed 一致）
        rail_locked: 导轨是否锁定（当前阶段为True）
    """
    leg_id: str
    leg_num: int
    base_position: np.ndarray
    base_rotation: np.ndarray
    hip_offset: np.ndarray
    hip_rpy: np.ndarray
    knee_offset: np.ndarray
    knee_rpy: np.ndarray
    tibia_offset: np.ndarray
    tibia_rpy: np.ndarray
    link_lengths: Tuple[float, float, float]
    joint_limits: Dict[str, Tuple[float, float]]
    shin_xyz: np.ndarray = None  # tibia_link 上 inertial 参考偏移（CAD CoM；与 URDF inertial origin 一致）
    foot_tip_offset_tibia: np.ndarray = None  # foot_link 在 tibia_link 系下平移，与 dog2.urdf.xacro foot_tip_xyz 一致
    rail_locked: bool = True
    
    def __post_init__(self):
        """验证参数有效性"""
        if self.leg_id not in ['lf', 'rf', 'lh', 'rh']:
            raise ValueError(f"Invalid leg_id: {self.leg_id}")
        if self.leg_num not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid leg_num: {self.leg_num}")
        if len(self.link_lengths) != 3:
            raise ValueError(f"link_lengths must have 3 elements, got {len(self.link_lengths)}")
        if self.hip_offset.shape != (3,) or self.knee_offset.shape != (3,) or self.tibia_offset.shape != (3,):
            raise ValueError("hip_offset/knee_offset/tibia_offset must be 3D vectors")
        if self.hip_rpy.shape != (3,) or self.knee_rpy.shape != (3,) or self.tibia_rpy.shape != (3,):
            raise ValueError("hip_rpy/knee_rpy/tibia_rpy must be 3D vectors")
        if self.shin_xyz is None:
            raise ValueError("shin_xyz must be provided (tibia_link inertial origin offset)")
        if np.asarray(self.shin_xyz).shape != (3,):
            raise ValueError("shin_xyz must be a 3D vector")
        if self.foot_tip_offset_tibia is None:
            raise ValueError("foot_tip_offset_tibia must be provided (URDF foot_tip_xyz in tibia_link frame)")
        if np.asarray(self.foot_tip_offset_tibia).shape != (3,):
            raise ValueError("foot_tip_offset_tibia must be a 3D vector")


def create_leg_parameters() -> Dict[str, LegParameters]:
    """
    创建所有4条腿的参数配置
    
    根据URDF文件提取的几何参数和关节限位
    
    Returns:
        字典，键为leg_id ('lf', 'rf', 'lh', 'rh')，值为LegParameters对象
    """
    # 从URDF提取的关键尺寸（米）
    # - HAA(=coxa) 关节原点：hip_xyz（不同腿略有差异）
    # - HFE(=femur) 关节原点：knee_xyz（左/右腿符号不同）
    # - KFE(=tibia) 关节原点：固定 xyz="0 -0.15201 0.12997"
    # 现阶段 IK 仍按“3R解析近似模型”实现，link_lengths 保持兼容字段。
    L1 = 0.055
    L2 = 0.15201
    L3 = 0.299

    link_lengths = (L1, L2, L3)

    # foot_tip in tibia_link frame: YZ 与 xacro 一致；X 横向收拢；Y +半直径后 −1.5×直径（沿 −tibia Y）；Z 下调与 xacro 一致
    FOOT_TIP_LATERAL_INBOARD_M = 0.024
    FOOT_SPHERE_RADIUS_M = 0.012
    FOOT_TIP_PLUS_Y_HALF_DIAMETER_M = FOOT_SPHERE_RADIUS_M  # 半直径 = r（d=2r）
    FOOT_TIP_MINUS_Y_ONE_AND_HALF_DIAMETER_M = 3.0 * FOOT_SPHERE_RADIUS_M  # 1.5×直径 = 3r
    # 沿 tibia_link Z 累计下调；较「2×3/4 d + 2 d」上调 3×球直径（与 xacro 一致）
    FOOT_TIP_Z_DOWN_M = (
        2.0 * 0.75 * 2.0 * FOOT_SPHERE_RADIUS_M
        + 2.0 * (2.0 * FOOT_SPHERE_RADIUS_M)
        - 3.0 * (2.0 * FOOT_SPHERE_RADIUS_M)
    )

    def _foot_tip_yz(sy: float, sz: float, length: float) -> np.ndarray:
        n = float(np.linalg.norm(np.array([sy, sz], dtype=float)))
        return np.array([0.0, sy / n * length, sz / n * length], dtype=float)

    foot12 = _foot_tip_yz(-0.143524743603395, -0.0694046953395906, L3)
    foot12[0] = FOOT_TIP_LATERAL_INBOARD_M
    foot12[1] += FOOT_TIP_PLUS_Y_HALF_DIAMETER_M - FOOT_TIP_MINUS_Y_ONE_AND_HALF_DIAMETER_M
    foot12[2] -= FOOT_TIP_Z_DOWN_M
    foot3 = _foot_tip_yz(-0.143524743603395, -0.0694046953395908, L3)
    foot3[0] = -FOOT_TIP_LATERAL_INBOARD_M
    foot3[1] += FOOT_TIP_PLUS_Y_HALF_DIAMETER_M - FOOT_TIP_MINUS_Y_ONE_AND_HALF_DIAMETER_M
    foot3[2] -= FOOT_TIP_Z_DOWN_M
    foot4 = _foot_tip_yz(-0.1429895138560395, -0.0691152554666486, L3)
    foot4[0] = -FOOT_TIP_LATERAL_INBOARD_M
    foot4[1] += FOOT_TIP_PLUS_Y_HALF_DIAMETER_M - FOOT_TIP_MINUS_Y_ONE_AND_HALF_DIAMETER_M
    foot4[2] -= FOOT_TIP_Z_DOWN_M

    # 关节限位（从URDF提取）
    # 导轨：prismatic joint limits
    # 旋转关节：revolute joint limits（弧度）
    joint_limits_template = {
        'coxa': (-2.618, 2.618),   # coxa关节限位（约±150度）
        'femur': (-2.8, 2.8),      # femur关节限位（约±160度）
        'tibia': (-2.8, 2.8),      # tibia关节限位（约±160度）
    }
    
    # 腿部1：左前 (lf) -> leg1
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg1_params = LegParameters(
        leg_id='lf',
        leg_num=1,
        base_position=np.array([0.1246, 0.0625, 0.0]),
        base_rotation=LEG_BASE_RPY.copy(),
        hip_offset=np.array([-0.016, 0.0199, 0.055]),
        hip_rpy=COXA_ORIGIN_RPY.copy(),
        knee_offset=np.array([-0.0233, -0.055, 0.0274]),
        knee_rpy=FEMUR_ORIGIN_RPY.copy(),
        tibia_offset=np.array([0.0, -0.15201, 0.12997]),
        tibia_rpy=TIBIA_ORIGIN_RPY.copy(),
        link_lengths=link_lengths,
        joint_limits={
            'rail': RAIL_LIMITS_BY_LEG['lf'],  # +q = base_link +X
            **joint_limits_template
        },
        shin_xyz=np.array([0.0255, -0.1435, -0.0694]),
        foot_tip_offset_tibia=foot12.copy(),
        rail_locked=True
    )

    # 腿部2：左后 (lh) -> leg2
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg2_params = LegParameters(
        leg_id='lh',
        leg_num=2,
        base_position=np.array([0.3711, 0.0625, 0.0]),
        base_rotation=LEG_BASE_RPY.copy(),
        hip_offset=np.array([0.016, 0.0199, 0.055]),
        hip_rpy=COXA_ORIGIN_RPY.copy(),
        knee_offset=np.array([-0.0233, -0.055, 0.0274]),
        knee_rpy=FEMUR_ORIGIN_RPY.copy(),
        tibia_offset=np.array([0.0, -0.15201, 0.12997]),
        tibia_rpy=TIBIA_ORIGIN_RPY.copy(),
        link_lengths=link_lengths,
        joint_limits={
            'rail': RAIL_LIMITS_BY_LEG['lh'],  # +q = base_link +X
            **joint_limits_template
        },
        shin_xyz=np.array([0.0255, -0.1435, -0.0694]),
        foot_tip_offset_tibia=foot12.copy(),
        rail_locked=True
    )

    # 腿部3：右后 (rh) -> leg3
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg3_params = LegParameters(
        leg_id='rh',
        leg_num=3,
        base_position=np.array([0.3711, 0.2475, 0.0]),
        base_rotation=LEG_BASE_RPY.copy(),
        hip_offset=np.array([0.016, 0.0199, -0.055]),
        hip_rpy=COXA_ORIGIN_RPY.copy(),
        knee_offset=np.array([-0.0233, -0.055, -0.0254]),
        knee_rpy=FEMUR_ORIGIN_RPY.copy(),
        tibia_offset=np.array([0.0, -0.15201, 0.12997]),
        tibia_rpy=TIBIA_ORIGIN_RPY.copy(),
        link_lengths=link_lengths,
        joint_limits={
            'rail': RAIL_LIMITS_BY_LEG['rh'],  # +q = base_link +X
            **joint_limits_template
        },
        shin_xyz=np.array([-0.0265, -0.1435, -0.0694]),
        foot_tip_offset_tibia=foot3.copy(),
        rail_locked=True
    )

    # 腿部4：右前 (rf) -> leg4
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg4_params = LegParameters(
        leg_id='rf',
        leg_num=4,
        base_position=np.array([0.1291, 0.2575, 0.0]),
        base_rotation=LEG_BASE_RPY.copy(),
        hip_offset=np.array([-0.0116, 0.0199, -0.055]),
        hip_rpy=COXA_ORIGIN_RPY.copy(),
        knee_offset=np.array([-0.0233, -0.055, -0.0254]),
        knee_rpy=FEMUR_ORIGIN_RPY.copy(),
        tibia_offset=np.array([0.0, -0.15201, 0.12997]),
        tibia_rpy=TIBIA_ORIGIN_RPY.copy(),
        link_lengths=link_lengths,
        joint_limits={
            'rail': RAIL_LIMITS_BY_LEG['rf'],  # +q = base_link +X
            **joint_limits_template
        },
        shin_xyz=np.array([-0.0265, -0.1430, -0.0691]),
        foot_tip_offset_tibia=foot4.copy(),
        rail_locked=True
    )

    return {
        'lf': leg1_params,
        'lh': leg2_params,
        'rh': leg3_params,
        'rf': leg4_params,
    }


# 预创建的全局参数对象（方便快速访问）
LEG_PARAMETERS = create_leg_parameters()


def get_leg_parameters(leg_id: str) -> LegParameters:
    """
    获取指定腿部的参数
    
    Args:
        leg_id: 腿部标识符 ('lf', 'rf', 'lh', 'rh')
    
    Returns:
        LegParameters对象
    
    Raises:
        ValueError: 如果leg_id无效
    """
    if leg_id not in LEG_PARAMETERS:
        raise ValueError(f"Invalid leg_id: {leg_id}. Must be one of {list(LEG_PARAMETERS.keys())}")
    return LEG_PARAMETERS[leg_id]


# 示例用法
if __name__ == '__main__':
    print("腿部参数配置：\n")
    for leg_id, params in LEG_PARAMETERS.items():
        print(f"{leg_id} (leg{params.leg_num}):")
        print(f"  基座位置: {params.base_position}")
        print(f"  基座旋转 (rpy): {params.base_rotation}")
        print(f"  链长: {params.link_lengths}")
        print(f"  导轨限位: {params.joint_limits['rail']}")
        print(f"  导轨锁定: {params.rail_locked}")
        print()
