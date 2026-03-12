#!/usr/bin/env python3
"""
测试髋关节支架在RViz中的可视化
验证：
1. 支架是否有水平平台几何
2. 平台方向是否正确（平行于地面）
3. 髋关节是否绕X轴旋转（前后运动）
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class HipBracketTester(Node):
    def __init__(self):
        super().__init__('hip_bracket_tester')
        
        # 创建发布器
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 等待发布器准备好
        time.sleep(1)
        
        self.get_logger().info('========================================')
        self.get_logger().info('髋关节支架RViz测试')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('测试内容：')
        self.get_logger().info('1. 验证支架有水平平台几何（box primitives）')
        self.get_logger().info('2. 验证平台方向正确（平行于地面）')
        self.get_logger().info('3. 验证髋关节绕X轴旋转（前后运动）')
        self.get_logger().info('')
        
    def test_hip_joint_rotation(self):
        """测试髋关节旋转 - 应该是前后运动（X轴）"""
        
        self.get_logger().info('测试1: 髋关节零位')
        self.get_logger().info('所有关节角度设为0，观察腿部方向')
        self.publish_joint_state(j11=0.0, j21=0.0, j31=0.0, j41=0.0)
        time.sleep(3)
        
        self.get_logger().info('')
        self.get_logger().info('测试2: 髋关节正向旋转（+45度）')
        self.get_logger().info('腿应该向前摆动（X轴正方向）')
        angle = math.radians(45)
        self.publish_joint_state(j11=angle, j21=angle, j31=angle, j41=angle)
        time.sleep(3)
        
        self.get_logger().info('')
        self.get_logger().info('测试3: 髋关节负向旋转（-45度）')
        self.get_logger().info('腿应该向后摆动（X轴负方向）')
        angle = math.radians(-45)
        self.publish_joint_state(j11=angle, j21=angle, j31=angle, j41=angle)
        time.sleep(3)
        
        self.get_logger().info('')
        self.get_logger().info('测试4: 髋关节循环运动')
        self.get_logger().info('观察腿部是否做前后摆动（不是左右摆动）')
        
        for i in range(3):
            # 向前
            for angle_deg in range(0, 46, 5):
                angle = math.radians(angle_deg)
                self.publish_joint_state(j11=angle, j21=angle, j31=angle, j41=angle)
                time.sleep(0.1)
            
            # 向后
            for angle_deg in range(45, -46, -5):
                angle = math.radians(angle_deg)
                self.publish_joint_state(j11=angle, j21=angle, j31=angle, j41=angle)
                time.sleep(0.1)
            
            # 回到零位
            for angle_deg in range(-45, 1, 5):
                angle = math.radians(angle_deg)
                self.publish_joint_state(j11=angle, j21=angle, j31=angle, j41=angle)
                time.sleep(0.1)
        
        self.get_logger().info('')
        self.get_logger().info('测试5: 回到零位')
        self.publish_joint_state(j11=0.0, j21=0.0, j31=0.0, j41=0.0)
        time.sleep(2)
        
        self.get_logger().info('')
        self.get_logger().info('========================================')
        self.get_logger().info('测试完成！')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('请在RViz中验证：')
        self.get_logger().info('✓ 支架显示为两个box（垂直体 + 水平平台）')
        self.get_logger().info('✓ 水平平台平行于地面（XY平面）')
        self.get_logger().info('✓ 髋关节旋转时，腿做前后运动（不是左右）')
        self.get_logger().info('✓ 旋转轴是X轴（红色轴）')
        self.get_logger().info('')
        
    def publish_joint_state(self, j11=0.0, j21=0.0, j31=0.0, j41=0.0,
                           j111=0.0, j211=0.0, j311=0.0, j411=0.0):
        """发布关节状态"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 所有关节名称
        msg.name = [
            'j1', 'j11', 'j111',  # 腿1：棱柱、髋、膝
            'j2', 'j21', 'j211',  # 腿2
            'j3', 'j31', 'j311',  # 腿3
            'j4', 'j41', 'j411',  # 腿4
        ]
        
        # 关节位置（棱柱关节设为0，只测试髋关节和膝关节）
        msg.position = [
            0.0, j11, j111,   # 腿1
            0.0, j21, j211,   # 腿2
            0.0, j31, j311,   # 腿3
            0.0, j41, j411,   # 腿4
        ]
        
        self.joint_pub.publish(msg)

def main():
    rclpy.init()
    
    tester = HipBracketTester()
    
    try:
        # 运行测试
        tester.test_hip_joint_rotation()
        
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
