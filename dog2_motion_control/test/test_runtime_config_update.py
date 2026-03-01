"""
测试运行时参数更新功能
"""

import pytest
import time
import rclpy
from dog2_motion_control.spider_robot_controller import SpiderRobotController
from dog2_motion_control.gait_generator import GaitConfig


@pytest.fixture(scope='module')
def ros_context():
    """初始化和清理ROS上下文"""
    rclpy.init()
    yield
    rclpy.shutdown()


class TestRuntimeConfigUpdate:
    """测试运行时配置更新"""
    
    def test_update_gait_config_request(self, ros_context):
        """测试请求配置更新"""
        controller = SpiderRobotController()
        
        # 创建新配置
        new_config = GaitConfig(
            stride_length=0.12,
            stride_height=0.08,
            cycle_time=1.8,
            duty_factor=0.75,
            body_height=0.22,
            gait_type="crawl"
        )
        
        # 请求更新
        controller.update_gait_config(new_config)
        
        # 验证更新请求已记录
        assert controller.pending_config_update is not None
        assert controller.pending_config_update.stride_length == 0.12
        assert controller.pending_config_update.stride_height == 0.08
    
    def test_config_update_at_cycle_boundary(self, ros_context):
        """测试配置在周期边界应用"""
        controller = SpiderRobotController()
        controller.start()
        
        # 初始配置
        initial_stride_length = controller.gait_generator.config.stride_length
        
        # 创建新配置
        new_config = GaitConfig(
            stride_length=0.15,
            stride_height=0.07,
            cycle_time=1.5,
            duty_factor=0.75,
            body_height=0.25,
            gait_type="crawl"
        )
        
        # 请求更新
        controller.update_gait_config(new_config)
        
        # 模拟运行到周期边界之前
        # 设置相位为0.5（周期中间）
        controller.gait_generator.current_time = controller.gait_generator.config.cycle_time * 0.5
        controller.last_cycle_phase = 0.5
        
        # 调用检查方法
        controller._check_and_apply_config_update()
        
        # 配置不应该被应用（还没到周期边界）
        assert controller.pending_config_update is not None
        assert controller.gait_generator.config.stride_length == initial_stride_length
        
        # 模拟到达周期边界
        # 设置上一次相位为0.95，当前相位为0.05
        controller.last_cycle_phase = 0.95
        controller.gait_generator.current_time = controller.gait_generator.config.cycle_time * 0.05
        
        # 调用检查方法
        controller._check_and_apply_config_update()
        
        # 配置应该被应用
        assert controller.pending_config_update is None
        assert controller.gait_generator.config.stride_length == 0.15
        assert controller.gait_generator.config.stride_height == 0.07
        assert controller.gait_generator.config.cycle_time == 1.5
        
        controller.stop()
    
    def test_no_mid_cycle_update(self, ros_context):
        """测试周期中间不会应用更新"""
        controller = SpiderRobotController()
        controller.start()
        
        initial_config = controller.gait_generator.config
        
        # 创建新配置
        new_config = GaitConfig(
            stride_length=0.20,
            stride_height=0.10,
            cycle_time=1.0,
            duty_factor=0.75,
            body_height=0.30,
            gait_type="crawl"
        )
        
        # 请求更新
        controller.update_gait_config(new_config)
        
        # 模拟在周期中间多次调用
        for phase in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            controller.last_cycle_phase = phase - 0.05
            controller.gait_generator.current_time = controller.gait_generator.config.cycle_time * phase
            controller._check_and_apply_config_update()
            
            # 配置不应该被应用
            assert controller.pending_config_update is not None
            assert controller.gait_generator.config.stride_length == initial_config.stride_length
        
        controller.stop()
    
    def test_multiple_config_updates(self, ros_context):
        """测试多次配置更新"""
        controller = SpiderRobotController()
        controller.start()
        
        # 第一次更新
        config1 = GaitConfig(
            stride_length=0.10,
            stride_height=0.06,
            cycle_time=2.0,
            duty_factor=0.75,
            body_height=0.20,
            gait_type="crawl"
        )
        controller.update_gait_config(config1)
        
        # 第二次更新（覆盖第一次）
        config2 = GaitConfig(
            stride_length=0.12,
            stride_height=0.08,
            cycle_time=1.8,
            duty_factor=0.75,
            body_height=0.22,
            gait_type="crawl"
        )
        controller.update_gait_config(config2)
        
        # 应该只有最后一次更新被记录
        assert controller.pending_config_update is not None
        assert controller.pending_config_update.stride_length == 0.12
        
        # 模拟到达周期边界
        controller.last_cycle_phase = 0.95
        controller.gait_generator.current_time = controller.gait_generator.config.cycle_time * 0.05
        controller._check_and_apply_config_update()
        
        # 应该应用最后一次更新
        assert controller.gait_generator.config.stride_length == 0.12
        assert controller.gait_generator.config.stride_height == 0.08
        
        controller.stop()
    
    def test_cycle_boundary_detection(self, ros_context):
        """测试周期边界检测逻辑"""
        controller = SpiderRobotController()
        
        # 测试各种相位跳变情况
        test_cases = [
            # (last_phase, current_phase, should_trigger)
            (0.95, 0.05, True),   # 正常周期边界
            (0.99, 0.01, True),   # 接近1.0的边界
            (0.92, 0.08, True),   # 稍微宽松的边界
            (0.5, 0.6, False),    # 周期中间
            (0.8, 0.9, False),    # 接近边界但未跨越
            (0.1, 0.2, False),    # 周期开始阶段
            (0.05, 0.95, False),  # 反向跳变（不应该触发）
        ]
        
        for last_phase, current_phase, should_trigger in test_cases:
            # 重置状态
            controller.pending_config_update = GaitConfig(stride_length=0.99)
            controller.last_cycle_phase = last_phase
            controller.gait_generator.current_time = controller.gait_generator.config.cycle_time * current_phase
            
            # 调用检查方法
            controller._check_and_apply_config_update()
            
            if should_trigger:
                # 应该应用更新
                assert controller.pending_config_update is None, \
                    f"Failed to apply update at boundary: {last_phase} -> {current_phase}"
            else:
                # 不应该应用更新
                assert controller.pending_config_update is not None, \
                    f"Incorrectly applied update at: {last_phase} -> {current_phase}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
