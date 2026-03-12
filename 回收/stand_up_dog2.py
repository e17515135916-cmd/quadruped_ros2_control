#!/usr/bin/env python3
"""
让 Dog2 机器狗站立起来
设置一个稳定的站立姿态
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math


class Dog2StandUp(Node):
    def __init__(self):
        super().__init__('dog2_stand_up')
        
        # 创建轨迹发布器
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 等待发布器准备好
        self.get_logger().info('等待 1 秒让系统准备好...')
        self.create_timer(1.0, self.send_stand_command)
        
    def send_stand_command(self):
        """发送站立姿态命令"""
        self.get_logger().info('发送站立命令...')
        
        # 创建轨迹消息
        traj = JointTrajectory()
        traj.joint_names = [
            # 腿 1 (前左)
            'j1', 'j11', 'j111', 'j1111',
            # 腿 2 (前右)
            'j2', 'j21', 'j211', 'j2111',
            # 腿 3 (后左)
            'j3', 'j31', 'j311', 'j3111',
            # 腿 4 (后右)
            'j4', 'j41', 'j411', 'j4111'
        ]
        
        # 站立姿态：
        # - 棱柱关节 (j1, j2, j3, j4): 保持在 0
        # - 髋关节 (j11, j21, j31, j41): 向外展开约 30度 (0.5 rad)
        # - 大腿关节 (j111, j211, j311, j411): 向下弯曲约 60度 (-1.0 rad)
        # - 小腿关节 (j1111, j2111, j3111, j4111): 保持在 0
        
        # 点 1: 慢慢站起来 (3秒)
        point1 = JointTrajectoryPoint()
        point1.positions = [
            # 腿 1 (前左)
            0.0,   # j1 棱柱
            0.5,   # j11 髋关节
            -1.0,  # j111 大腿
            0.0,   # j1111 小腿
            # 腿 2 (前右)
            0.0,   # j2 棱柱
            0.5,   # j21 髋关节
            -1.0,  # j211 大腿
            0.0,   # j2111 小腿
            # 腿 3 (后左)
            0.0,   # j3 棱柱
            0.5,   # j31 髋关节
            -1.0,  # j311 大腿
            0.0,   # j3111 小腿
            # 腿 4 (后右)
            0.0,   # j4 棱柱
            0.5,   # j41 髋关节
            -1.0,  # j411 大腿
            0.0    # j4111 小腿
        ]
        point1.time_from_start = Duration(sec=3, nanosec=0)
        
        traj.points = [point1]
        
        # 发布轨迹
        self.publisher.publish(traj)
        self.get_logger().info('✅ 站立命令已发送！')
        self.get_logger().info('   机器狗将在 3 秒内站立起来')
        self.get_logger().info('   髋关节: 0.5 rad (约 28.6°)')
        self.get_logger().info('   大腿关节: -1.0 rad (约 -57.3°)')
        
        # 5秒后关闭节点
        self.create_timer(5.0, self.shutdown)
        
    def shutdown(self):
        self.get_logger().info('站立完成，保持姿态')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = Dog2StandUp()
    
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
