#!/usr/bin/env python3
"""
测试髋关节在 RViz 中的可视化
验证 x 轴旋转是否正确工作
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import math

class HipJointRVizTester(Node):
    def __init__(self):
        super().__init__('hip_joint_rviz_tester')
        
        # 创建关节状态发布器
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 等待发布器准备好
        time.sleep(1)
        
        self.get_logger().info('========================================')
        self.get_logger().info('髋关节 RViz 可视化测试')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('测试内容：')
        self.get_logger().info('1. 验证 URDF 加载无错误')
        self.get_logger().info('2. 测试髋关节 (j11, j21, j31, j41) 绕 x 轴旋转')
        self.get_logger().info('3. 检查视觉网格方向是否正确')
        self.get_logger().info('')
        
    def test_hip_joints(self):
        """测试所有髋关节的旋转"""
        
        # 定义所有关节名称
        all_joints = [
            'j11', 'j111', 'j1111',  # 腿1
            'j21', 'j211', 'j2111',  # 腿2
            'j31', 'j311', 'j3111',  # 腿3
            'j41', 'j411', 'j4111',  # 腿4
        ]
        
        hip_joints = ['j11', 'j21', 'j31', 'j41']
        
        self.get_logger().info('测试 1: 所有关节归零位置')
        self.publish_joint_positions(all_joints, [0.0] * len(all_joints))
        time.sleep(2)
        
        self.get_logger().info('✅ 零位置测试完成')
        self.get_logger().info('')
        
        # 测试每个髋关节
        for hip_joint in hip_joints:
            self.get_logger().info(f'测试 2: 测试 {hip_joint} 绕 x 轴旋转')
            
            # 正向旋转
            self.get_logger().info(f'  - {hip_joint} 旋转到 +30°')
            positions = [0.0] * len(all_joints)
            hip_idx = all_joints.index(hip_joint)
            positions[hip_idx] = math.radians(30)
            self.publish_joint_positions(all_joints, positions)
            time.sleep(1.5)
            
            # 负向旋转
            self.get_logger().info(f'  - {hip_joint} 旋转到 -30°')
            positions[hip_idx] = math.radians(-30)
            self.publish_joint_positions(all_joints, positions)
            time.sleep(1.5)
            
            # 归零
            self.get_logger().info(f'  - {hip_joint} 归零')
            positions[hip_idx] = 0.0
            self.publish_joint_positions(all_joints, positions)
            time.sleep(1)
            
            self.get_logger().info(f'✅ {hip_joint} 测试完成')
            self.get_logger().info('')
        
        self.get_logger().info('测试 3: 所有髋关节同时旋转')
        positions = [0.0] * len(all_joints)
        for hip_joint in hip_joints:
            hip_idx = all_joints.index(hip_joint)
            positions[hip_idx] = math.radians(45)
        
        self.publish_joint_positions(all_joints, positions)
        time.sleep(2)
        
        self.get_logger().info('✅ 同时旋转测试完成')
        self.get_logger().info('')
        
        # 归零
        self.get_logger().info('恢复到零位置')
        self.publish_joint_positions(all_joints, [0.0] * len(all_joints))
        time.sleep(1)
        
        self.get_logger().info('')
        self.get_logger().info('========================================')
        self.get_logger().info('测试完成！')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('请在 RViz 中验证：')
        self.get_logger().info('1. 髋关节链接 (l11, l21, l31, l41) 方向正确')
        self.get_logger().info('2. 关节旋转绕 x 轴进行')
        self.get_logger().info('3. 视觉网格与关节运动匹配')
        self.get_logger().info('')
        
    def publish_joint_positions(self, joint_names, positions):
        """发布关节位置"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = joint_names
        msg.position = positions
        self.joint_pub.publish(msg)

def main():
    rclpy.init()
    
    tester = HipJointRVizTester()
    
    try:
        tester.test_hip_joints()
        
        # 保持节点运行
        tester.get_logger().info('按 Ctrl+C 退出...')
        rclpy.spin(tester)
        
    except KeyboardInterrupt:
        tester.get_logger().info('测试中断')
    finally:
        tester.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
