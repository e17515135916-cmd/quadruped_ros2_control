"""
基础测试 - 验证测试框架是否正常工作
"""

import pytest


def test_imports():
    """测试基本导入是否正常"""
    import numpy as np
    import scipy
    from hypothesis import given, strategies as st
    
    assert np is not None
    assert scipy is not None


def test_package_imports():
    """测试包模块是否可以导入"""
    from dog2_motion_control import spider_robot_controller
    from dog2_motion_control import kinematics_solver
    from dog2_motion_control import gait_generator
    from dog2_motion_control import trajectory_planner
    from dog2_motion_control import joint_controller
    
    assert spider_robot_controller is not None
    assert kinematics_solver is not None
    assert gait_generator is not None
    assert trajectory_planner is not None
    assert joint_controller is not None


def test_gait_config():
    """测试步态配置数据类"""
    from dog2_motion_control.gait_generator import GaitConfig
    
    config = GaitConfig()
    assert config.stride_length == 0.08
    assert config.stride_height == 0.05
    assert config.cycle_time == 2.0
    assert config.duty_factor == 0.75
    assert config.body_height == 0.2
    assert config.gait_type == "crawl"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
