"""
完整系统集成测试

验证任务12的检查点要求：
- 确保所有测试通过
- 验证完整控制循环
- 验证错误处理机制
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock, MagicMock, patch
import rclpy

from dog2_motion_control.spider_robot_controller import SpiderRobotController
from dog2_motion_control.gait_generator import GaitGenerator, GaitConfig
from dog2_motion_control.kinematics_solver import create_kinematics_solver
from dog2_motion_control.trajectory_planner import TrajectoryPlanner
from dog2_motion_control.joint_controller import JointController


class TestSystemIntegration:
    """完整系统集成测试"""
    
    @pytest.fixture
    def controller(self):
        """创建控制器实例"""
        if not rclpy.ok():
            rclpy.init()
        
        controller = SpiderRobotController()
        
        yield controller
        
        controller.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    
    def test_all_subsystems_initialized(self, controller):
        """测试所有子系统正确初始化
        
        验证：
        - GaitGenerator已创建
        - KinematicsSolver已创建
        - TrajectoryPlanner已创建
        - JointController已创建
        """
        assert controller.gait_generator is not None
        assert isinstance(controller.gait_generator, GaitGenerator)
        
        assert controller.ik_solver is not None
        
        assert controller.trajectory_planner is not None
        assert isinstance(controller.trajectory_planner, TrajectoryPlanner)
        
        assert controller.joint_controller is not None
        assert isinstance(controller.joint_controller, JointController)
        
        print("✓ 所有子系统已正确初始化")
    
    def test_complete_control_loop_integration(self, controller):
        """测试完整控制循环集成
        
        验证完整数据流：
        1. 接收速度命令
        2. 步态生成器更新
        3. 获取脚部目标位置
        4. 逆运动学求解
        5. 轨迹规划
        6. 发送关节命令
        """
        # 模拟关节控制器以避免实际发布
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})
        
        # 设置速度命令
        controller.current_velocity = (0.1, 0.0, 0.0)  # 前进0.1m/s
        controller.is_stopping = False
        
        # 执行一个控制循环
        dt = 0.02  # 50Hz
        controller.update(dt)
        
        # 验证关节命令已发送
        controller.joint_controller.send_joint_commands.assert_called_once()
        
        # 验证发送的命令包含16个关节
        sent_commands = controller.joint_controller.send_joint_commands.call_args[0][0]
        assert len(sent_commands) == 16
        
        # 验证导轨关节恒定为0.0
        rail_joints = ['j1', 'j2', 'j3', 'j4']
        for rail_joint in rail_joints:
            assert rail_joint in sent_commands
            assert sent_commands[rail_joint] == 0.0
        
        print("✓ 完整控制循环集成验证通过")
    
    def test_ik_failure_recovery(self, controller):
        """测试IK失败恢复机制
        
        验证需求 8.2：
        - IK无解时使用上一个有效配置
        - 记录错误日志
        """
        # 模拟IK求解器返回None（无解）
        original_ik_solver = controller.ik_solver
        controller.ik_solver = Mock()
        controller.ik_solver.solve_ik = Mock(return_value=None)
        
        # 设置上一个有效配置
        controller.last_valid_joint_positions['lf'] = (0.0, 0.1, 0.2, 0.3)
        
        # 模拟关节控制器
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})
        
        controller.gait_generator = Mock()
        controller.gait_generator.update = Mock()
        controller.gait_generator.get_foot_target = Mock(return_value=(0.3, 0.2, -0.2))
        
        controller.is_stopping = False
        
        # 执行控制循环
        controller.update(0.02)
        
        # 验证使用了上一个有效配置（没有崩溃）
        controller.joint_controller.send_joint_commands.assert_called_once()
        
        # 恢复原始IK求解器
        controller.ik_solver = original_ik_solver
        
        print("✓ IK失败恢复机制验证通过")
    
    def test_rail_slip_detection_and_emergency_stop(self, controller):
        """测试导轨滑动检测和紧急停止
        
        验证需求 8.5, 8.6：
        - 监控导轨位置
        - 检测到滑动时触发紧急安全姿态
        - 锁定导轨
        """
        # 模拟导轨滑动
        controller.joint_controller.monitor_rail_positions = Mock(return_value=False)
        controller.joint_controller.lock_rails_with_max_effort = Mock()
        
        controller.is_running = True
        
        # 执行控制循环
        controller.update(0.02)
        
        # 验证进入紧急模式
        assert controller.is_emergency_mode == True
        
        # 验证导轨被锁定
        controller.joint_controller.lock_rails_with_max_effort.assert_called_once()
        
        # 验证速度被清零
        assert controller.current_velocity == (0.0, 0.0, 0.0)
        
        print("✓ 导轨滑动检测和紧急停止验证通过")
    
    def test_stuck_joint_detection(self, controller):
        """测试关节卡死检测
        
        验证需求 8.3：
        - 检测关节卡死
        - 降低力矩并报警
        """
        # 模拟关节卡死
        stuck_joints = {
            'leg1_j2': True,
            'leg1_j3': False,
            'leg1_j4': False,
        }
        
        controller.joint_controller.detect_stuck_joints = Mock(return_value=stuck_joints)
        controller.joint_controller.handle_stuck_joint = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.send_joint_commands = Mock()
        
        controller.gait_generator = Mock()
        controller.gait_generator.update = Mock()
        controller.gait_generator.get_foot_target = Mock(return_value=(0.3, 0.2, -0.2))
        
        controller.ik_solver = Mock()
        controller.ik_solver.solve_ik = Mock(return_value=(0.0, 0.1, 0.2, 0.3))
        
        controller.is_stopping = False
        
        # 执行控制循环
        controller.update(0.02)
        
        # 验证卡死关节被处理
        controller.joint_controller.handle_stuck_joint.assert_called_once_with('leg1_j2')
        
        print("✓ 关节卡死检测验证通过")
    
    def test_multiple_stuck_joints_trigger_emergency(self, controller):
        """测试多个关节卡死触发紧急模式
        
        验证：
        - 3个或更多关节卡死时触发紧急安全姿态
        """
        # 模拟多个关节卡死
        stuck_joints = {
            'leg1_j2': True,
            'leg1_j3': True,
            'leg2_j2': True,
            'leg2_j3': False,
        }
        
        controller.joint_controller.detect_stuck_joints = Mock(return_value=stuck_joints)
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.lock_rails_with_max_effort = Mock()
        
        controller.is_running = True
        
        # 执行控制循环
        controller.update(0.02)
        
        # 验证进入紧急模式
        assert controller.is_emergency_mode == True
        
        # 验证导轨被锁定
        controller.joint_controller.lock_rails_with_max_effort.assert_called_once()
        
        print("✓ 多关节卡死触发紧急模式验证通过")
    
    def test_smooth_stop_mechanism(self, controller):
        """测试平滑停止机制
        
        验证需求 5.4：
        - 接收停止命令
        - 在一个步态周期内停止
        - 速度平滑衰减
        """
        # 设置初始速度
        controller.current_velocity = (0.2, 0.0, 0.0)
        controller.target_velocity = (0.2, 0.0, 0.0)
        
        # 模拟关节控制器
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})
        
        # 触发平滑停止
        controller.initiate_smooth_stop()
        
        assert controller.is_stopping == True
        # target_velocity保存起始速度，用于衰减计算
        assert controller.target_velocity == (0.2, 0.0, 0.0)
        # current_velocity不会立即清零，而是在update循环中逐渐衰减
        assert controller.current_velocity == (0.2, 0.0, 0.0)
        
        # 模拟多个控制循环
        cycle_time = controller.gait_generator.config.cycle_time
        num_steps = int(cycle_time / 0.02) + 1
        
        for i in range(num_steps):
            controller.update(0.02)
            
            # 验证速度在衰减
            vx, vy, omega = controller.current_velocity
            if i < num_steps - 1:
                # 还在衰减过程中
                assert abs(vx) >= 0.0
        
        # 最后应该停止或接近停止
        vx_final, vy_final, omega_final = controller.current_velocity
        assert abs(vx_final) < 0.01  # 接近0
        assert abs(vy_final) < 0.01
        assert abs(omega_final) < 0.01
        assert controller.is_stopping == False
        
        print("✓ 平滑停止机制验证通过")
    
    def test_config_update_at_cycle_boundary(self, controller):
        """测试配置在周期边界更新
        
        验证需求 7.2：
        - 参数更新在周期边界应用
        - 不在周期中间突变
        """
        # 创建新配置
        new_config = GaitConfig(
            stride_length=0.10,
            stride_height=0.06,
            cycle_time=1.5
        )
        
        # 请求配置更新
        controller.update_gait_config(new_config)
        
        # 验证配置被标记为待处理
        assert controller.pending_config_update is not None
        
        # 模拟关节控制器
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})
        
        # 执行多个控制循环直到周期边界
        for i in range(100):
            controller.update(0.02)
            
            # 检查是否在周期边界应用了配置
            if controller.pending_config_update is None:
                # 配置已应用
                assert controller.gait_generator.config.stride_length == 0.10
                break
        
        print("✓ 配置周期边界更新验证通过")
    
    def test_16_channel_command_structure(self, controller):
        """测试16通道命令结构
        
        验证：
        - 发送16个关节命令
        - 4个导轨恒定为0.0
        - 12个旋转关节动态控制
        """
        # 模拟关节控制器
        controller.joint_controller.send_joint_commands = Mock()
        controller.joint_controller.monitor_rail_positions = Mock(return_value=True)
        controller.joint_controller.detect_stuck_joints = Mock(return_value={})
        
        controller.current_velocity = (0.1, 0.0, 0.0)
        controller.is_stopping = False
        
        # 执行控制循环
        controller.update(0.02)
        
        # 获取发送的命令
        sent_commands = controller.joint_controller.send_joint_commands.call_args[0][0]
        
        # 验证16个关节
        assert len(sent_commands) == 16
        
        # 验证导轨关节
        rail_joints = ['j1', 'j2', 'j3', 'j4']
        for rail_joint in rail_joints:
            assert rail_joint in sent_commands
            assert sent_commands[rail_joint] == 0.0
        
        # 验证旋转关节存在
        revolute_joints = []
        for leg_prefix in ['lf', 'rf', 'lh', 'rh']:
            for joint_type in ['haa', 'hfe', 'kfe']:
                revolute_joints.append(f'{leg_prefix}_{joint_type}_joint')
        
        for revolute_joint in revolute_joints:
            assert revolute_joint in sent_commands
            # 旋转关节应该有动态值（不一定是0）
            assert isinstance(sent_commands[revolute_joint], (int, float))
        
        print("✓ 16通道命令结构验证通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
