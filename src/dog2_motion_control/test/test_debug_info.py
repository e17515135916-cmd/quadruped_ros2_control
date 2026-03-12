"""
测试调试信息发布功能
"""

import pytest
import rclpy
import json
import time
from std_msgs.msg import String
from dog2_motion_control.spider_robot_controller import SpiderRobotController
from dog2_motion_control.gait_generator import GaitConfig


@pytest.fixture(scope='module')
def ros_context():
    """初始化和清理ROS上下文"""
    rclpy.init()
    yield
    rclpy.shutdown()


class TestDebugInfo:
    """测试调试信息发布"""
    
    def test_debug_mode_enable_disable(self, ros_context):
        """测试启用和禁用调试模式"""
        controller = SpiderRobotController()
        
        # 初始状态应该是禁用
        assert controller.debug_mode == False
        
        # 启用调试模式
        controller.enable_debug_mode(True)
        assert controller.debug_mode == True
        
        # 禁用调试模式
        controller.enable_debug_mode(False)
        assert controller.debug_mode == False
    
    def test_no_debug_when_disabled(self, ros_context):
        """测试禁用调试模式时不发布信息"""
        controller = SpiderRobotController()
        controller.enable_debug_mode(False)  # 确保禁用
        
        # 创建订阅者
        received_messages = []
        
        def debug_callback(msg):
            received_messages.append(msg.data)
        
        subscriber = controller.create_subscription(
            String,
            '/spider_debug_info',
            debug_callback,
            10
        )
        
        # 手动调用_publish_debug_info（不启动控制循环）
        # 注意：由于计数器逻辑，前9次不会发布，第10次会发布
        # 但由于debug_mode=False，应该在第一次检查时就返回
        joint_positions = {
            'j1': 0.0, 'j2': 0.0, 'j3': 0.0, 'j4': 0.0,
            'j5': 0.0, 'j6': 0.0, 'j7': 0.0, 'j8': 0.0,
            'j9': 0.0, 'j10': 0.0, 'j11': 0.0, 'j12': 0.0,
            'j13': 0.0, 'j14': 0.0, 'j15': 0.0, 'j16': 0.0
        }
        
        # 重置计数器以确保会触发发布逻辑
        controller.debug_publish_counter = 9
        
        # 调用一次（这会触发计数器>=10的条件）
        controller._publish_debug_info(joint_positions)
        rclpy.spin_once(controller, timeout_sec=0.01)
        
        # 由于debug_mode=False，应该在早期返回，不发布消息
        assert len(received_messages) == 0
    
    def test_debug_publisher_exists(self, ros_context):
        """测试调试发布器是否创建"""
        controller = SpiderRobotController()
        
        # 验证发布器存在
        assert controller.debug_publisher is not None
        
        # 验证发布器话题正确
        topic_names = [name for name, _ in controller.get_publisher_names_and_types_by_node(
            controller.get_name(), controller.get_namespace()
        )]
        assert '/spider_debug_info' in topic_names
    
    def test_debug_publish_counter(self, ros_context):
        """测试调试发布计数器"""
        controller = SpiderRobotController()
        controller.enable_debug_mode(True)
        
        # 初始计数器应该是0
        assert controller.debug_publish_counter == 0
        
        joint_positions = {}
        
        # 调用9次，不应该发布
        for i in range(9):
            controller._publish_debug_info(joint_positions)
            assert controller.debug_publish_counter == i + 1
        
        # 第10次应该发布并重置计数器
        controller._publish_debug_info(joint_positions)
        assert controller.debug_publish_counter == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

