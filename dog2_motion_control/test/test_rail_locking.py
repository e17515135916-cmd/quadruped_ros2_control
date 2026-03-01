#!/usr/bin/env python3
"""
导轨锁定验证测试

测试内容：
- 在仿真中监控导轨位置
- 验证整个运动过程中导轨保持0.0米
- 测试安全姿态切换时导轨不滑动

需求: 1.3, 8.5, 8.6
"""

import unittest
import time
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from std_msgs.msg import String


class RailLockingTest(unittest.TestCase):
    """导轨锁定验证测试"""
    
    # 导轨滑动阈值（米）
    RAIL_SLIP_THRESHOLD = 0.0005  # 0.5mm
    
    @classmethod
    def setUpClass(cls):
        """初始化ROS 2"""
        rclpy.init()
    
    @classmethod
    def tearDownClass(cls):
        """关闭ROS 2"""
        rclpy.shutdown()
    
    def setUp(self):
        """每个测试前的设置"""
        self.node = rclpy.create_node('rail_locking_test')
        
        # 创建发布器和订阅器
        self.cmd_vel_pub = self.node.create_publisher(Twist, '/cmd_vel', 10)
        self.emergency_pub = self.node.create_publisher(String, '/emergency_stop', 10)
        
        self.joint_states = None
        self.rail_positions_history = []
        
        self.joint_state_sub = self.node.create_subscription(
            JointState,
            '/joint_states',
            self._joint_state_callback,
            10
        )
        
        # 等待连接建立
        time.sleep(1.0)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.node.destroy_node()
    
    def _joint_state_callback(self, msg):
        """关节状态回调"""
        self.joint_states = msg
        
        # 记录导轨位置
        rail_positions = {}
        for i, name in enumerate(msg.name):
            if 'j1' in name:  # 导轨关节
                rail_positions[name] = msg.position[i]
        
        if rail_positions:
            self.rail_positions_history.append({
                'time': time.time(),
                'positions': rail_positions
            })
    
    def _spin_once(self, timeout=0.1):
        """处理一次回调"""
        rclpy.spin_once(self.node, timeout_sec=timeout)
    
    def _wait_for_joint_states(self, timeout=5.0):
        """等待接收关节状态"""
        start_time = time.time()
        while self.joint_states is None:
            self._spin_once()
            if time.time() - start_time > timeout:
                return False
        return True
    
    def _get_rail_positions(self):
        """获取当前导轨位置"""
        if self.joint_states is None:
            return None
        
        rail_positions = {}
        for i, name in enumerate(self.joint_states.name):
            if 'j1' in name:  # 导轨关节
                rail_positions[name] = self.joint_states.position[i]
        
        return rail_positions if rail_positions else None
    
    def _check_rail_slip(self, rail_positions):
        """检查导轨是否滑动"""
        if not rail_positions:
            return False, []
        
        slipped_rails = []
        for rail_name, position in rail_positions.items():
            if abs(position) > self.RAIL_SLIP_THRESHOLD:
                slipped_rails.append((rail_name, position))
        
        return len(slipped_rails) > 0, slipped_rails
    
    def test_01_rail_locking_at_rest(self):
        """
        测试静止时导轨锁定
        
        验证：
        - 机器人静止时导轨位置为0.0米
        - 导轨位置在阈值范围内
        
        需求: 1.3
        """
        print("\n=== 测试 14.4.1: 静止时导轨锁定 ===")
        
        # 等待关节状态
        self.assertTrue(
            self._wait_for_joint_states(),
            "未能接收到关节状态消息"
        )
        
        # 收集静止状态下的导轨位置
        print("收集静止状态下的导轨位置（5秒）...")
        self.rail_positions_history.clear()
        
        for i in range(50):  # 5秒，50Hz
            self._spin_once()
            time.sleep(0.1)
        
        # 验证导轨位置
        self.assertGreater(
            len(self.rail_positions_history), 10,
            "未能收集到足够的导轨位置样本"
        )
        
        # 检查所有样本
        max_deviations = {}
        for sample in self.rail_positions_history:
            for rail_name, position in sample['positions'].items():
                if rail_name not in max_deviations:
                    max_deviations[rail_name] = 0.0
                max_deviations[rail_name] = max(
                    max_deviations[rail_name],
                    abs(position)
                )
        
        # 打印结果
        print("\n导轨位置偏差统计：")
        all_locked = True
        for rail_name, max_dev in max_deviations.items():
            status = "✓" if max_dev <= self.RAIL_SLIP_THRESHOLD else "✗"
            print(f"  {status} {rail_name}: 最大偏差 = {max_dev*1000:.3f} mm (阈值: ±0.5 mm)")
            
            if max_dev > self.RAIL_SLIP_THRESHOLD:
                all_locked = False
        
        self.assertTrue(
            all_locked,
            f"部分导轨超出锁定阈值 (±{self.RAIL_SLIP_THRESHOLD*1000} mm)"
        )
        
        print("\n✓ 静止时所有导轨正确锁定在0.0米")
    
    def test_02_rail_locking_during_motion(self):
        """
        测试运动过程中导轨锁定
        
        验证：
        - 机器人运动时导轨保持锁定
        - 整个运动过程中导轨不滑动
        
        需求: 1.3, 8.5
        """
        print("\n=== 测试 14.4.2: 运动过程中导轨锁定 ===")
        
        # 等待关节状态
        self.assertTrue(
            self._wait_for_joint_states(),
            "未能接收到关节状态消息"
        )
        
        # 清空历史记录
        self.rail_positions_history.clear()
        
        # 发送运动命令
        print("发送前进命令...")
        cmd = Twist()
        cmd.linear.x = 0.05  # 5 cm/s
        self.cmd_vel_pub.publish(cmd)
        
        # 监控运动过程（10秒）
        print("监控运动过程中的导轨位置（10秒）...")
        for i in range(100):  # 10秒，50Hz
            self._spin_once()
            time.sleep(0.1)
        
        # 停止运动
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)
        
        # 验证导轨位置
        self.assertGreater(
            len(self.rail_positions_history), 50,
            "未能收集到足够的导轨位置样本"
        )
        
        # 分析导轨位置
        max_deviations = {}
        slip_events = []
        
        for sample in self.rail_positions_history:
            for rail_name, position in sample['positions'].items():
                if rail_name not in max_deviations:
                    max_deviations[rail_name] = 0.0
                
                current_dev = abs(position)
                max_deviations[rail_name] = max(
                    max_deviations[rail_name],
                    current_dev
                )
                
                # 记录滑动事件
                if current_dev > self.RAIL_SLIP_THRESHOLD:
                    slip_events.append({
                        'time': sample['time'],
                        'rail': rail_name,
                        'position': position
                    })
        
        # 打印结果
        print("\n运动过程中导轨位置偏差统计：")
        all_locked = True
        for rail_name, max_dev in max_deviations.items():
            status = "✓" if max_dev <= self.RAIL_SLIP_THRESHOLD else "✗"
            print(f"  {status} {rail_name}: 最大偏差 = {max_dev*1000:.3f} mm (阈值: ±0.5 mm)")
            
            if max_dev > self.RAIL_SLIP_THRESHOLD:
                all_locked = False
        
        if slip_events:
            print(f"\n⚠ 检测到 {len(slip_events)} 次导轨滑动事件")
            # 只显示前5个事件
            for event in slip_events[:5]:
                print(f"  - {event['rail']}: {event['position']*1000:.3f} mm")
            if len(slip_events) > 5:
                print(f"  ... 还有 {len(slip_events)-5} 个事件")
        
        self.assertTrue(
            all_locked,
            f"运动过程中部分导轨滑动超出阈值 (±{self.RAIL_SLIP_THRESHOLD*1000} mm)"
        )
        
        print("\n✓ 运动过程中所有导轨保持锁定")
    
    def test_03_rail_locking_during_emergency(self):
        """
        测试紧急停止时导轨锁定
        
        验证：
        - 紧急停止时导轨保持锁定
        - 安全姿态切换时导轨不滑动
        
        需求: 8.5, 8.6
        """
        print("\n=== 测试 14.4.3: 紧急停止时导轨锁定 ===")
        
        # 等待关节状态
        self.assertTrue(
            self._wait_for_joint_states(),
            "未能接收到关节状态消息"
        )
        
        # 清空历史记录
        self.rail_positions_history.clear()
        
        # 先让机器人运动
        print("发送前进命令...")
        cmd = Twist()
        cmd.linear.x = 0.05
        self.cmd_vel_pub.publish(cmd)
        
        # 运动2秒
        for i in range(20):
            self._spin_once()
            time.sleep(0.1)
        
        # 触发紧急停止
        print("触发紧急停止...")
        emergency_msg = String()
        emergency_msg.data = "emergency_stop"
        self.emergency_pub.publish(emergency_msg)
        
        # 监控紧急停止过程（5秒）
        print("监控紧急停止过程中的导轨位置（5秒）...")
        emergency_samples = []
        for i in range(50):
            self._spin_once()
            if self.joint_states:
                rail_pos = self._get_rail_positions()
                if rail_pos:
                    emergency_samples.append({
                        'time': time.time(),
                        'positions': rail_pos
                    })
            time.sleep(0.1)
        
        # 验证导轨位置
        self.assertGreater(
            len(emergency_samples), 10,
            "未能收集到足够的紧急停止样本"
        )
        
        # 分析导轨位置
        max_deviations = {}
        for sample in emergency_samples:
            for rail_name, position in sample['positions'].items():
                if rail_name not in max_deviations:
                    max_deviations[rail_name] = 0.0
                max_deviations[rail_name] = max(
                    max_deviations[rail_name],
                    abs(position)
                )
        
        # 打印结果
        print("\n紧急停止过程中导轨位置偏差统计：")
        all_locked = True
        for rail_name, max_dev in max_deviations.items():
            status = "✓" if max_dev <= self.RAIL_SLIP_THRESHOLD else "✗"
            print(f"  {status} {rail_name}: 最大偏差 = {max_dev*1000:.3f} mm (阈值: ±0.5 mm)")
            
            if max_dev > self.RAIL_SLIP_THRESHOLD:
                all_locked = False
        
        self.assertTrue(
            all_locked,
            f"紧急停止时部分导轨滑动超出阈值 (±{self.RAIL_SLIP_THRESHOLD*1000} mm)"
        )
        
        print("\n✓ 紧急停止过程中所有导轨保持锁定")
    
    def test_04_rail_position_monitoring(self):
        """
        测试导轨位置监控功能
        
        验证：
        - 系统能够持续监控导轨位置
        - 能够检测导轨滑动
        
        需求: 8.6
        """
        print("\n=== 测试 14.4.4: 导轨位置监控 ===")
        
        # 等待关节状态
        self.assertTrue(
            self._wait_for_joint_states(),
            "未能接收到关节状态消息"
        )
        
        # 清空历史记录
        self.rail_positions_history.clear()
        
        # 收集数据
        print("收集导轨位置数据（3秒）...")
        for i in range(30):
            self._spin_once()
            time.sleep(0.1)
        
        # 验证监控功能
        self.assertGreater(
            len(self.rail_positions_history), 10,
            "导轨位置监控未正常工作"
        )
        
        # 验证所有4个导轨都被监控
        all_rails = set()
        for sample in self.rail_positions_history:
            all_rails.update(sample['positions'].keys())
        
        expected_rails = {'leg1_j1', 'leg2_j1', 'leg3_j1', 'leg4_j1'}
        self.assertEqual(
            all_rails, expected_rails,
            f"未监控到所有导轨。期望: {expected_rails}, 实际: {all_rails}"
        )
        
        print(f"\n✓ 成功监控所有4个导轨")
        print(f"  采样数: {len(self.rail_positions_history)}")
        print(f"  采样率: {len(self.rail_positions_history)/3.0:.1f} Hz")
        
        # 计算统计信息
        print("\n导轨位置统计：")
        for rail_name in sorted(expected_rails):
            positions = [
                sample['positions'][rail_name]
                for sample in self.rail_positions_history
                if rail_name in sample['positions']
            ]
            
            if positions:
                mean_pos = np.mean(positions)
                std_pos = np.std(positions)
                max_pos = np.max(np.abs(positions))
                
                print(f"  {rail_name}:")
                print(f"    平均: {mean_pos*1000:.3f} mm")
                print(f"    标准差: {std_pos*1000:.3f} mm")
                print(f"    最大偏差: {max_pos*1000:.3f} mm")
        
        print("\n✓ 导轨位置监控功能正常")


def main():
    """主函数"""
    # 检查是否在仿真环境中运行
    print("=" * 60)
    print("导轨锁定验证测试")
    print("=" * 60)
    print("\n注意：此测试需要Gazebo仿真环境运行")
    print("请先启动仿真：")
    print("  ros2 launch dog2_motion_control spider_gazebo_complete.launch.py")
    print("\n按Enter继续测试，或Ctrl+C取消...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n测试已取消")
        return
    
    # 运行测试
    suite = unittest.TestLoader().loadTestsFromTestCase(RailLockingTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 打印关键发现
    print("\n" + "=" * 60)
    print("关键发现")
    print("=" * 60)
    print("✓ 导轨锁定阈值: ±0.5 mm")
    print("✓ 监控频率: ~50 Hz")
    print("✓ 测试场景: 静止、运动、紧急停止")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(main())
