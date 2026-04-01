"""
测试关节命名模块 - 确保与URDF一致
"""

import pytest
from dog2_motion_control.joint_names import (
    LEG_PREFIX_MAP,
    PREFIX_TO_LEG_MAP,
    RAIL_JOINTS,
    REVOLUTE_JOINT_TYPES,
    get_rail_joint_name,
    get_revolute_joint_name,
    get_all_joint_names,
    get_leg_joint_names,
    ALL_JOINT_NAMES
)


def test_leg_prefix_mapping():
    """测试腿部编号到前缀的映射"""
    assert LEG_PREFIX_MAP[1] == 'lf'  # 前左
    assert LEG_PREFIX_MAP[2] == 'lh'  # 左后
    assert LEG_PREFIX_MAP[3] == 'rh'  # 右后
    assert LEG_PREFIX_MAP[4] == 'rf'  # 右前


def test_prefix_to_leg_mapping():
    """测试前缀到腿部编号的反向映射"""
    assert PREFIX_TO_LEG_MAP['lf'] == 1
    assert PREFIX_TO_LEG_MAP['lh'] == 2
    assert PREFIX_TO_LEG_MAP['rh'] == 3
    assert PREFIX_TO_LEG_MAP['rf'] == 4


def test_rail_joints():
    """测试导轨关节名称列表"""
    assert RAIL_JOINTS == ['lf_rail_joint', 'lh_rail_joint', 'rh_rail_joint', 'rf_rail_joint']


def test_revolute_joint_types():
    """测试旋转关节类型列表"""
    assert REVOLUTE_JOINT_TYPES == ['coxa', 'femur', 'tibia']


def test_get_rail_joint_name():
    """测试获取导轨关节名称"""
    assert get_rail_joint_name(1) == 'lf_rail_joint'
    assert get_rail_joint_name(2) == 'lh_rail_joint'
    assert get_rail_joint_name(3) == 'rh_rail_joint'
    assert get_rail_joint_name(4) == 'rf_rail_joint'
    
    # 测试无效输入
    with pytest.raises(ValueError):
        get_rail_joint_name(0)
    with pytest.raises(ValueError):
        get_rail_joint_name(5)


def test_get_revolute_joint_name():
    """测试获取旋转关节名称"""
    # 前左腿（leg1）
    assert get_revolute_joint_name(1, 'coxa') == 'lf_coxa_joint'
    assert get_revolute_joint_name(1, 'femur') == 'lf_femur_joint'
    assert get_revolute_joint_name(1, 'tibia') == 'lf_tibia_joint'
    
    # 左后腿（leg2）
    assert get_revolute_joint_name(2, 'coxa') == 'lh_coxa_joint'
    assert get_revolute_joint_name(2, 'femur') == 'lh_femur_joint'
    assert get_revolute_joint_name(2, 'tibia') == 'lh_tibia_joint'
    
    # 右后腿（leg3）
    assert get_revolute_joint_name(3, 'coxa') == 'rh_coxa_joint'
    assert get_revolute_joint_name(3, 'femur') == 'rh_femur_joint'
    assert get_revolute_joint_name(3, 'tibia') == 'rh_tibia_joint'
    
    # 右前腿（leg4）
    assert get_revolute_joint_name(4, 'coxa') == 'rf_coxa_joint'
    assert get_revolute_joint_name(4, 'femur') == 'rf_femur_joint'
    assert get_revolute_joint_name(4, 'tibia') == 'rf_tibia_joint'
    
    # 测试无效输入
    with pytest.raises(ValueError):
        get_revolute_joint_name(1, 'invalid')
    with pytest.raises(ValueError):
        get_revolute_joint_name(5, 'haa')


def test_get_all_joint_names():
    """测试获取所有关节名称（验证顺序和数量）"""
    all_joints = get_all_joint_names()
    
    # 应该有16个关节
    assert len(all_joints) == 16
    
    # 验证顺序（与URDF中ros2_control的顺序一致）
    expected_order = [
        # Leg 1 (lf)
        'lf_rail_joint', 'lf_coxa_joint', 'lf_femur_joint', 'lf_tibia_joint',
        # Leg 2 (lh)
        'lh_rail_joint', 'lh_coxa_joint', 'lh_femur_joint', 'lh_tibia_joint',
        # Leg 3 (rh)
        'rh_rail_joint', 'rh_coxa_joint', 'rh_femur_joint', 'rh_tibia_joint',
        # Leg 4 (rf)
        'rf_rail_joint', 'rf_coxa_joint', 'rf_femur_joint', 'rf_tibia_joint',
    ]
    
    assert all_joints == expected_order


def test_get_leg_joint_names():
    """测试获取单条腿的所有关节名称"""
    # Leg 1 (lf)
    leg1_joints = get_leg_joint_names(1)
    assert leg1_joints['rail'] == 'lf_rail_joint'
    assert leg1_joints['coxa'] == 'lf_coxa_joint'
    assert leg1_joints['femur'] == 'lf_femur_joint'
    assert leg1_joints['tibia'] == 'lf_tibia_joint'
    
    # Leg 2 (lh)
    leg2_joints = get_leg_joint_names(2)
    assert leg2_joints['rail'] == 'lh_rail_joint'
    assert leg2_joints['coxa'] == 'lh_coxa_joint'
    
    # Leg 3 (rh)
    leg3_joints = get_leg_joint_names(3)
    assert leg3_joints['rail'] == 'rh_rail_joint'
    assert leg3_joints['coxa'] == 'rh_coxa_joint'
    
    # Leg 4 (rf)
    leg4_joints = get_leg_joint_names(4)
    assert leg4_joints['rail'] == 'rf_rail_joint'
    assert leg4_joints['coxa'] == 'rf_coxa_joint'


def test_all_joint_names_constant():
    """测试预定义的ALL_JOINT_NAMES常量"""
    assert len(ALL_JOINT_NAMES) == 16
    assert ALL_JOINT_NAMES == get_all_joint_names()


def test_urdf_consistency():
    """测试与URDF的一致性（关键测试）"""
    # 这些是从dog2.urdf.xacro中提取的真实关节名称
    urdf_joint_names = [
        'lf_rail_joint', 'lf_coxa_joint', 'lf_femur_joint', 'lf_tibia_joint',
        'lh_rail_joint', 'lh_coxa_joint', 'lh_femur_joint', 'lh_tibia_joint',
        'rh_rail_joint', 'rh_coxa_joint', 'rh_femur_joint', 'rh_tibia_joint',
        'rf_rail_joint', 'rf_coxa_joint', 'rf_femur_joint', 'rf_tibia_joint',
    ]
    
    # 我们生成的名称必须与URDF完全一致
    assert ALL_JOINT_NAMES == urdf_joint_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
