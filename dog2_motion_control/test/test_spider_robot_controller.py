"""
测试主控制器（SpiderRobotController）

验证：
- 控制器初始化
- 主控制循环
- cmd_vel订阅
- 平滑停止功能
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock, MagicMock, patch
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# 导入被测试的模块
from dog2_motion_control.spider_robot_controller import SpiderRobotController


class TestSpiderRobotController:
    """测试主控制器"""
    
    @pytest.fixture
    def mock_rclpy(self):
        """初始化 rclpy 上下文"""
        # 不需要mock，使用真实的rclpy
        pass
    
    @pytest.fixture
    def controller(self, mock_rclpy):
        """创建控制器实例"""
        # 初始化 rclpy
        if not rclpy.ok():
            rclpy.init()
        
        # 创建真实的控制器实例
        controller = SpiderRobotController()
        
        yield controller
        
        # 清理
        controller.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    
    def test_initialization(self, controller):
        """测试控制器初始化
        
        验证需求 1.1, 5.1：
        - 创建所有子系统实例
        - 初始化机器人状态
        - 设置控制循环定时器（50Hz）
        """
        # 验证子系统已创建
        assert controller.gait_generator is not None
        assert controller.ik_solver is not None
        assert controller.trajectory_planner is not None
        assert controller.joint_controller is not None
        
        # 验证状态变量已初始化
        assert controller.current_velocity == (0.0, 0.0, 0.0)
        assert controller.target_velocity == (0.0, 0.0, 0.0)
        assert controller.is_running == False
        assert controller.is_stopping == False
        
        # 验证定时器周期（50Hz = 0.02秒）
        assert controller.timer_period == 0.02
    
    def test_cmd_vel_callback_normal(self, controller):
        """测试正常速度命令处理
        
        验证需求 5.2：
        - 订阅/cmd_vel话题
        - 解析速度命令（vx, vy, omega）
        """
        # 创建速度命令消息
        msg = Twist()
        msg.linear.x = 0.1
        msg.linear.y = 0.05
        msg.angular.z = 0.2
        
        # 调用回调函数
        controller._cmd_vel_callback(msg)
        
        # 验证速度已更新
        assert controller.current_velocity == (0.1, 0.05, 0.2)
        assert controller.target_velocity == (0.1, 0.05, 0.2)
        assert controller.is_stopping == False
    
    def test_cmd_vel_callback_stop(self, controller):
        """测试停止命令处理
        
        验证需求 5.4：
        - 接收停止命令
        - 启动平滑停止
        """
        # 设置初始状态
        controller.is_running = True
        controller.current_velocity = (0.1, 0.05, 0.2)
        controller.gait_generator = Mock()
        controller.gait_generator.current_time = 1.0
        
        # 创建停止命令消息（所有速度接近零）
        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.angular.z = 0.0
        
        # 调用回调函数
        controller._cmd_vel_callback(msg)
        
        # 验证平滑停止已启动
        assert controller.is_stopping == True
        assert controller.stop_start_time == 1.0
        # target_velocity 应该保存当前速度
        assert controller.target_velocity == (0.1, 0.05, 0.2)
    
    def test_smooth_stop_progress(self, controller):
        """测试平滑停止过程
        
        验证需求 5.4：
        - 速度平滑衰减
        - 在一个步态周期内停止
        """
        # 设置初始状态
        controller.is_stopping = True
        controller.target_velocity = (0.2, 0.1, 0.3)
        controller.stop_start_time = 0.0
        controller.gait_generator = Mock()
        controller.gait_generator.config = Mock()
        controller.gait_generator.config.cycle_time = 2.0
        
        # 测试停止过程中间点（50%进度）
        controller.gait_generator.current_time = 1.0
        controller._handle_smooth_stop()
        
        # 验证速度衰减到50%
        expected_velocity = (0.1, 0.05, 0.15)
        assert abs(controller.current_velocity[0] - expected_velocity[0]) < 0.01
        assert abs(controller.current_velocity[1] - expected_velocity[1]) < 0.01
        assert abs(controller.current_velocity[2] - expected_velocity[2]) < 0.01
        assert controller.is_stopping == True
        
        # 测试停止完成（100%进度）
        controller.gait_generator.current_time = 2.0
        controller._handle_smooth_stop()
        
        # 验证速度已归零
        assert controller.current_velocity == (0.0, 0.0, 0.0)
        assert controller.is_stopping == False
    
    def test_update_main_loop(self, controller):
        """测试主控制循环
        
        验证需求 1.2, 2.1, 3.1：
        - 更新步态生成器
        - 获取脚部目标位置
        - 调用IK求解器
        - 发送关节命令
        """
        # 模拟子系统
        controller.joint_controller = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})  # 返回空字典表示没有卡死
        
        controller.gait_generator = Mock()
        controller.gait_generator.update = Mock()
        controller.gait_generator.get_foot_target = Mock(return_value=(0.3, 0.2, -0.2))
        
        controller.ik_solver = Mock()
        controller.ik_solver.solve_ik = Mock(return_value=(0.0, 0.1, 0.2, 0.3))
        
        controller.is_stopping = False
        
        # 调用主控制循环
        dt = 0.02
        controller.update(dt)
        
        # 验证步态生成器已更新
        controller.gait_generator.update.assert_called_once_with(dt, controller.current_velocity)
        
        # 验证IK求解器被调用了4次（4条腿）
        assert controller.ik_solver.solve_ik.call_count == 4
        
        # 验证关节命令已发送
        controller.joint_controller.send_joint_commands.assert_called_once()
        
        # 验证发送的命令包含16个关节
        sent_commands = controller.joint_controller.send_joint_commands.call_args[0][0]
        assert len(sent_commands) == 16  # 4条腿 × 4个关节
    
    def test_emergency_stop_on_rail_slip(self, controller):
        """测试导轨滑动时的紧急停止
        
        验证需求 8.5, 8.6：
        - 监控导轨位置
        - 检测到滑动时紧急停止
        """
        # 模拟导轨滑动
        controller.joint_controller = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=False)
        controller.joint_controller.lock_rails_with_max_effort = Mock()
        
        controller.is_running = True
        controller.timer = Mock()
        
        # 调用主控制循环
        controller.update(0.02)
        
        # 验证进入紧急模式（而不是立即停止）
        assert controller.is_emergency_mode == True
        # 验证导轨被锁定
        controller.joint_controller.lock_rails_with_max_effort.assert_called_once()
        # 验证速度被清零
        assert controller.current_velocity == (0.0, 0.0, 0.0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
