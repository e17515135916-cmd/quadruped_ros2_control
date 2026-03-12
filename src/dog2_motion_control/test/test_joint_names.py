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
    assert LEG_PREFIX_MAP[2] == 'rf'  # 前右
    assert LEG_PREFIX_MAP[3] == 'lh'  # 后左
    assert LEG_PREFIX_MAP[4] == 'rh'  # 后右


def test_prefix_to_leg_mapping():
    """测试前缀到腿部编号的反向映射"""
    assert PREFIX_TO_LEG_MAP['lf'] == 1
    assert PREFIX_TO_LEG_MAP['rf'] == 2
    assert PREFIX_TO_LEG_MAP['lh'] == 3
    assert PREFIX_TO_LEG_MAP['rh'] == 4


def test_rail_joints():
    """测试导轨关节名称列表"""
    assert RAIL_JOINTS == ['j1', 'j2', 'j3', 'j4']


def test_revolute_joint_types():
    """测试旋转关节类型列表"""
    assert REVOLUTE_JOINT_TYPES == ['haa', 'hfe', 'kfe']


def test_get_rail_joint_name():
    """测试获取导轨关节名称"""
    assert get_rail_joint_name(1) == 'j1'
    assert get_rail_joint_name(2) == 'j2'
    assert get_rail_joint_name(3) == 'j3'
    assert get_rail_joint_name(4) == 'j4'
    
    # 测试无效输入
    with pytest.raises(ValueError):
        get_rail_joint_name(0)
    with pytest.raises(ValueError):
        get_rail_joint_name(5)


def test_get_revolute_joint_name():
    """测试获取旋转关节名称"""
    # 前左腿（leg1）
    assert get_revolute_joint_name(1, 'haa') == 'lf_haa_joint'
    assert get_revolute_joint_name(1, 'hfe') == 'lf_hfe_joint'
    assert get_revolute_joint_name(1, 'kfe') == 'lf_kfe_joint'
    
    # 前右腿（leg2）
    assert get_revolute_joint_name(2, 'haa') == 'rf_haa_joint'
    assert get_revolute_joint_name(2, 'hfe') == 'rf_hfe_joint'
    assert get_revolute_joint_name(2, 'kfe') == 'rf_kfe_joint'
    
    # 后左腿（leg3）
    assert get_revolute_joint_name(3, 'haa') == 'lh_haa_joint'
    assert get_revolute_joint_name(3, 'hfe') == 'lh_hfe_joint'
    assert get_revolute_joint_name(3, 'kfe') == 'lh_kfe_joint'
    
    # 后右腿（leg4）
    assert get_revolute_joint_name(4, 'haa') == 'rh_haa_joint'
    assert get_revolute_joint_name(4, 'hfe') == 'rh_hfe_joint'
    assert get_revolute_joint_name(4, 'kfe') == 'rh_kfe_joint'
    
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
        'j1', 'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
        # Leg 2 (rf)
        'j2', 'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
        # Leg 3 (lh)
        'j3', 'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
        # Leg 4 (rh)
        'j4', 'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint',
    ]
    
    assert all_joints == expected_order


def test_get_leg_joint_names():
    """测试获取单条腿的所有关节名称"""
    # Leg 1 (lf)
    leg1_joints = get_leg_joint_names(1)
    assert leg1_joints['rail'] == 'j1'
    assert leg1_joints['haa'] == 'lf_haa_joint'
    assert leg1_joints['hfe'] == 'lf_hfe_joint'
    assert leg1_joints['kfe'] == 'lf_kfe_joint'
    
    # Leg 2 (rf)
    leg2_joints = get_leg_joint_names(2)
    assert leg2_joints['rail'] == 'j2'
    assert leg2_joints['haa'] == 'rf_haa_joint'
    
    # Leg 3 (lh)
    leg3_joints = get_leg_joint_names(3)
    assert leg3_joints['rail'] == 'j3'
    assert leg3_joints['haa'] == 'lh_haa_joint'
    
    # Leg 4 (rh)
    leg4_joints = get_leg_joint_names(4)
    assert leg4_joints['rail'] == 'j4'
    assert leg4_joints['haa'] == 'rh_haa_joint'


def test_all_joint_names_constant():
    """测试预定义的ALL_JOINT_NAMES常量"""
    assert len(ALL_JOINT_NAMES) == 16
    assert ALL_JOINT_NAMES == get_all_joint_names()


def test_urdf_consistency():
    """测试与URDF的一致性（关键测试）"""
    # 这些是从dog2.urdf.xacro中提取的真实关节名称
    urdf_joint_names = [
        'j1', 'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
        'j2', 'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
        'j3', 'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
        'j4', 'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint',
    ]
    
    # 我们生成的名称必须与URDF完全一致
    assert ALL_JOINT_NAMES == urdf_joint_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
