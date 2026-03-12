#!/usr/bin/env python3
"""
持续发布初始关节状态，直到joint_state_publisher_gui接管
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class InitialJointStatePublisher(Node):
    def __init__(self):
        super().__init__('initial_joint_state_publisher')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 创建定时器，每0.1秒发布一次
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        self.get_logger().info('开始发布初始关节状态（j31=3.142, j41=3.142）')
        self.get_logger().info('等待joint_state_publisher_gui启动...')
        
        self.count = 0
        
    def publish_joint_states(self):
        """发布关节状态"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        msg.name = [
            'j1', 'j11', 'j111',
            'j2', 'j21', 'j211',
            'j3', 'j31', 'j311',
            'j4', 'j41', 'j411',
        ]
        
        # j31和j41设为3.142，其他为0
        msg.position = [
            0.0, 0.0, 0.0,      # 腿1
            0.0, 0.0, 0.0,      # 腿2
            0.0, 3.142, 0.0,    # 腿3：j31=3.142
            0.0, 3.142, 0.0,    # 腿4：j41=3.142
        ]
        
        self.joint_pub.publish(msg)
        
        self.count += 1
        if self.count == 10:
            self.get_logger().info('已发布初始状态，GUI应该已经接管')
        elif self.count == 50:
            self.get_logger().info('持续发布中... 如果GUI已启动，可以按Ctrl+C停止此节点')

def main():
    rclpy.init()
    
    publisher = InitialJointStatePublisher()
    
    try:
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        publisher.get_logger().info('停止发布')
    finally:
        publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
