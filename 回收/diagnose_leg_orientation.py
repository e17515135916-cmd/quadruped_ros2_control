#!/usr/bin/env python3
"""
诊断腿部方向问题
分析移除RPY旋转后的几何关系
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import math

class LegOrientationDiagnostic(Node):
    def __init__(self):
        super().__init__('leg_orientation_diagnostic')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        time.sleep(1)
        
        self.get_logger().info('========================================')
        self.get_logger().info('腿部方向诊断')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        
    def diagnose(self):
        """诊断不同关节角度下的腿部方向"""
        
        self.get_logger().info('测试1: 所有关节为零')
        self.get_logger().info('观察：腿的初始方向')
        self.publish_joint_state(j11=0, j21=0, j31=0, j41=0)
        time.sleep(4)
        
        self.get_logger().info('')
        self.get_logger().info('测试2: 髋关节 +90度 (1.5708 rad)')
        self.get_logger().info('观察：腿应该向前摆动')
        self.publish_joint_state(j11=1.5708, j21=1.5708, j31=1.5708, j41=1.5708)
        time.sleep(4)
        
        self.get_logger().info('')
        self.get_logger().info('测试3: 髋关节 -90度 (-1.5708 rad)')
        self.get_logger().info('观察：腿应该向后摆动')
        self.publish_joint_state(j11=-1.5708, j21=-1.5708, j31=-1.5708, j41=-1.5708)
        time.sleep(4)
        
        self.get_logger().info('')
        self.get_logger().info('测试4: 回到零位')
        self.publish_joint_state(j11=0, j21=0, j31=0, j41=0)
        time.sleep(2)
        
        self.get_logger().info('')
        self.get_logger().info('========================================')
        self.get_logger().info('诊断问题：')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('请描述你看到的问题：')
        self.get_logger().info('1. 零位时腿的方向是什么？（向下/向前/向后/向侧面）')
        self.get_logger().info('2. 髋关节旋转时，腿往哪个方向运动？')
        self.get_logger().info('3. 大腿（thigh）的方向看起来对吗？')
        self.get_logger().info('')
        self.get_logger().info('可能的问题：')
        self.get_logger().info('- 如果腿向侧面伸出：可能需要调整thigh的visual RPY')
        self.get_logger().info('- 如果腿向前/后伸出：可能需要调整knee joint的RPY')
        self.get_logger().info('- 如果腿方向完全错误：可能需要重新考虑坐标系')
        self.get_logger().info('')
        
    def publish_joint_state(self, j11=0, j21=0, j31=0, j41=0):
        """发布关节状态"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        msg.name = [
            'j1', 'j11', 'j111',
            'j2', 'j21', 'j211',
            'j3', 'j31', 'j311',
            'j4', 'j41', 'j411',
        ]
        
        msg.position = [
            0.0, j11, 0.0,
            0.0, j21, 0.0,
            0.0, j31, 0.0,
            0.0, j41, 0.0,
        ]
        
        self.joint_pub.publish(msg)

def main():
    rclpy.init()
    
    diagnostic = LegOrientationDiagnostic()
    
    try:
        diagnostic.diagnose()
        diagnostic.get_logger().info('按 Ctrl+C 退出...')
        time.sleep(5)
    except KeyboardInterrupt:
        diagnostic.get_logger().info('诊断中断')
    finally:
        diagnostic.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
