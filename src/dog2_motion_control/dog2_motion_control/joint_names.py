"""
关节命名常量 - 与URDF严格一致

根据 dog2.urdf.xacro 定义的真实关节名称
"""

from typing import Dict, List

# 腿部编号到URDF前缀的映射
LEG_PREFIX_MAP: Dict[int, str] = {
    1: 'lf',  # leg1 = 左前 (left front)
    2: 'lh',  # leg2 = 左后 (left hind)
    3: 'rh',  # leg3 = 右后 (right hind)
    4: 'rf',  # leg4 = 右前 (right front)
}

# 反向映射：URDF前缀到腿部编号
PREFIX_TO_LEG_MAP: Dict[str, int] = {
    'lf': 1,
    'lh': 2,
    'rh': 3,
    'rf': 4,
}

# 导轨关节名称（prismatic joints）
# 顺序按 leg_num=1..4: lf, lh, rh, rf
RAIL_JOINTS: List[str] = [
    'lf_rail_joint',
    'lh_rail_joint',
    'rh_rail_joint',
    'rf_rail_joint',
]

# 旋转关节类型（与URDF一致）
REVOLUTE_JOINT_TYPES: List[str] = ['coxa', 'femur', 'tibia']


def get_rail_joint_name(leg_num: int) -> str:
    """获取导轨关节名称
    
    Args:
        leg_num: 腿部编号 (1-4)
    
    Returns:
        导轨关节名称，如 'lf_rail_joint'
    """
    if leg_num not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid leg number: {leg_num}. Must be 1-4.")
    # leg_num 映射: 1->lf, 2->lh, 3->rh, 4->rf
    prefix = LEG_PREFIX_MAP[leg_num]
    return f'{prefix}_rail_joint'


def get_revolute_joint_name(leg_num: int, joint_type: str) -> str:
    """获取旋转关节名称
    
    Args:
        leg_num: 腿部编号 (1-4)
        joint_type: 关节类型 ('coxa', 'femur', 'tibia')
    
    Returns:
        旋转关节名称，如 'lf_coxa_joint'
    """
    if leg_num not in LEG_PREFIX_MAP:
        raise ValueError(f"Invalid leg number: {leg_num}. Must be 1-4.")
    if joint_type not in REVOLUTE_JOINT_TYPES:
        raise ValueError(f"Invalid joint type: {joint_type}. Must be one of {REVOLUTE_JOINT_TYPES}.")
    
    prefix = LEG_PREFIX_MAP[leg_num]
    return f'{prefix}_{joint_type}_joint'


def get_all_joint_names() -> List[str]:
    """获取所有16个关节的名称（按URDF中ros2_control的顺序）
    
    Returns:
        关节名称列表，顺序为：
        lf_rail_joint, lf_coxa_joint, lf_femur_joint, lf_tibia_joint,
        lh_rail_joint, lh_coxa_joint, lh_femur_joint, lh_tibia_joint,
        rh_rail_joint, rh_coxa_joint, rh_femur_joint, rh_tibia_joint,
        rf_rail_joint, rf_coxa_joint, rf_femur_joint, rf_tibia_joint
    """
    joint_names = []
    for leg_num in [1, 2, 3, 4]:
        # 导轨
        joint_names.append(get_rail_joint_name(leg_num))
        # 旋转关节
        for joint_type in REVOLUTE_JOINT_TYPES:
            joint_names.append(get_revolute_joint_name(leg_num, joint_type))
    return joint_names


def get_leg_joint_names(leg_num: int) -> Dict[str, str]:
    """获取某条腿的所有关节名称
    
    Args:
        leg_num: 腿部编号 (1-4)
    
    Returns:
        字典，键为关节类型，值为关节名称
        例如：{
            'rail': 'lf_rail_joint',
            'coxa': 'lf_coxa_joint',
            'femur': 'lf_femur_joint',
            'tibia': 'lf_tibia_joint'
        }
    """
    return {
        'rail': get_rail_joint_name(leg_num),
        'coxa': get_revolute_joint_name(leg_num, 'coxa'),
        'femur': get_revolute_joint_name(leg_num, 'femur'),
        'tibia': get_revolute_joint_name(leg_num, 'tibia'),
    }


# 预定义的所有关节名称（方便快速访问）
ALL_JOINT_NAMES = get_all_joint_names()

# 示例用法
if __name__ == '__main__':
    print("所有关节名称（按顺序）：")
    for i, name in enumerate(ALL_JOINT_NAMES, 1):
        print(f"{i:2d}. {name}")
    
    print("\n腿部1的关节：")
    leg1_joints = get_leg_joint_names(1)
    for joint_type, joint_name in leg1_joints.items():
        print(f"  {joint_type}: {joint_name}")
