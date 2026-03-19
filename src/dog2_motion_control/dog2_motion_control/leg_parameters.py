"""
腿部参数数据模型

定义机器人腿部的几何参数、关节限位和坐标系转换信息
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import math
import numpy as np


@dataclass
class LegParameters:
    """
    单条腿的参数配置
    
    Attributes:
        leg_id: 腿部标识符 ('lf', 'rf', 'lh', 'rh')
        leg_num: 腿部编号 (1, 2, 3, 4)
        base_position: 腿部基座在base_link中的位置 [x, y, z] (米)
        base_rotation: 腿部坐标系旋转 [roll, pitch, yaw] (弧度)
        link_lengths: 链长 (HAA到HFE, HFE到KFE, KFE到foot) (米)
        joint_limits: 关节限位字典 {'rail': (下限, 上限), 'haa': (下限, 上限), ...}
        rail_locked: 导轨是否锁定（当前阶段为True）
    """
    leg_id: str
    leg_num: int
    base_position: np.ndarray
    base_rotation: np.ndarray
    link_lengths: Tuple[float, float, float]
    joint_limits: Dict[str, Tuple[float, float]]
    rail_locked: bool = True
    
    def __post_init__(self):
        """验证参数有效性"""
        if self.leg_id not in ['lf', 'rf', 'lh', 'rh']:
            raise ValueError(f"Invalid leg_id: {self.leg_id}")
        if self.leg_num not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid leg_num: {self.leg_num}")
        if len(self.link_lengths) != 3:
            raise ValueError(f"link_lengths must have 3 elements, got {len(self.link_lengths)}")


def create_leg_parameters() -> Dict[str, LegParameters]:
    """
    创建所有4条腿的参数配置
    
    根据URDF文件提取的几何参数和关节限位
    
    Returns:
        字典，键为leg_id ('lf', 'rf', 'lh', 'rh')，值为LegParameters对象
    """
    # 从URDF提取的关键尺寸（米）
    # 链长：HAA到HFE距离, HFE到KFE距离(大腿), KFE到foot距离(小腿)
    L1 = 0.055  # HAA关节到HFE关节的距离（近似）
    L2 = 0.152  # HFE关节到KFE关节的距离（大腿长度）
    L3 = 0.299  # KFE关节到脚部的距离（小腿长度）
    
    link_lengths = (L1, L2, L3)
    
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
        base_rotation=np.array([math.pi / 2, 0.0, 0.0]),
        link_lengths=link_lengths,
        joint_limits={
            'rail': (-0.111, 0.0),  # 前左导轨向负方向移动
            **joint_limits_template
        },
        rail_locked=True
    )

    # 腿部2：左后 (lh) -> leg2
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg2_params = LegParameters(
        leg_id='lh',
        leg_num=2,
        base_position=np.array([0.3711, 0.0625, 0.0]),
        base_rotation=np.array([math.pi / 2, 0.0, 0.0]),
        link_lengths=link_lengths,
        joint_limits={
            'rail': (0.0, 0.111),  # 后左导轨向正方向移动
            **joint_limits_template
        },
        rail_locked=True
    )

    # 腿部3：右后 (rh) -> leg3
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg3_params = LegParameters(
        leg_id='rh',
        leg_num=3,
        base_position=np.array([0.3711, 0.1825, 0.0]),
        base_rotation=np.array([math.pi / 2, 0.0, -math.pi]),
        link_lengths=link_lengths,
        joint_limits={
            'rail': (-0.111, 0.0),  # 后右导轨向负方向移动
            **joint_limits_template
        },
        rail_locked=True
    )

    # 腿部4：右前 (rf) -> leg4
    # base_position 与 URDF leg anchor 保持一致（base_link-local）
    leg4_params = LegParameters(
        leg_id='rf',
        leg_num=4,
        base_position=np.array([0.1291, 0.1825, 0.0]),
        base_rotation=np.array([math.pi / 2, 0.0, -math.pi]),
        link_lengths=link_lengths,
        joint_limits={
            'rail': (0.0, 0.111),  # 前右导轨向正方向移动
            **joint_limits_template
        },
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
