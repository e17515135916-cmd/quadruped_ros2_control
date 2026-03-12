#!/usr/bin/env python3
"""
设置j31和j41的初始位置为3.142（180度）
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class InitialPositionSetter(Node):
    def __init__(self):
        super().__init__('initial_position_setter')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        time.sleep(1)
        
        self.get_logger().info('设置j31和j41的初始位置为3.142（180度）')
        
    def set_initial_position(self):
        """设置初始位置"""
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
        self.get_logger().info('已设置：j31=3.142, j41=3.142')

def main():
    rclpy.init()
    
    setter = InitialPositionSetter()
    
    try:
        setter.set_initial_position()
        time.sleep(2)
        setter.get_logger().info('完成！现在可以在RViz中查看效果')
    except KeyboardInterrupt:
        setter.get_logger().info('中断')
    finally:
        setter.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
