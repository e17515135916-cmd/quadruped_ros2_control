#!/usr/bin/env python3
"""
让 Dog2 机器狗稳定站立
使用更合理的关节角度
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math


class Dog2StableStand(Node):
    def __init__(self):
        super().__init__('dog2_stable_stand')
        
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.get_logger().info('准备让机器狗稳定站立...')
        self.create_timer(1.0, self.send_stable_stand)
        
    def send_stable_stand(self):
        """发送稳定站立姿态"""
        self.get_logger().info('发送稳定站立命令...')
        
        traj = JointTrajectory()
        traj.joint_names = [
            'j1', 'j11', 'j111', 'j1111',    # 腿 1
            'j2', 'j21', 'j211', 'j2111',    # 腿 2
            'j3', 'j31', 'j311', 'j3111',    # 腿 3
            'j4', 'j41', 'j411', 'j4111'     # 腿 4
        ]
        
        # 更稳定的站立姿态：
        # - 髋关节稍微向外 (0.3 rad ≈ 17°)
        # - 大腿向下弯曲 (-1.2 rad ≈ -69°)
        # - 小腿向前弯曲 (0.6 rad ≈ 34°) 来支撑身体
        
        point = JointTrajectoryPoint()
        point.positions = [
            # 腿 1 (前左)
            0.0,    # j1 棱柱
            0.3,    # j11 髋关节
            -1.2,   # j111 大腿
            0.6,    # j1111 小腿
            # 腿 2 (前右)
            0.0,    # j2 棱柱
            0.3,    # j21 髋关节
            -1.2,   # j211 大腿
            0.6,    # j2111 小腿
            # 腿 3 (后左)
            0.0,    # j3 棱柱
            0.3,    # j31 髋关节
            -1.2,   # j311 大腿
            0.6,    # j3111 小腿
            # 腿 4 (后右)
            0.0,    # j4 棱柱
            0.3,    # j41 髋关节
            -1.2,   # j411 大腿
            0.6     # j4111 小腿
        ]
        point.time_from_start = Duration(sec=2, nanosec=0)
        
        traj.points = [point]
        self.publisher.publish(traj)
        
        self.get_logger().info('✅ 稳定站立命令已发送！')
        self.get_logger().info('   髋关节: 0.3 rad (17°)')
        self.get_logger().info('   大腿: -1.2 rad (-69°)')
        self.get_logger().info('   小腿: 0.6 rad (34°)')
        
        self.create_timer(4.0, self.shutdown)
        
    def shutdown(self):
        self.get_logger().info('姿态设置完成')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = Dog2StableStand()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
