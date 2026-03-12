#!/usr/bin/env python3
"""
快速站立脚本
在 Gazebo 启动后运行此脚本让机器人站立
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


def main():
    rclpy.init()
    node = Node('quick_stand')
    
    publisher = node.create_publisher(
        JointTrajectory,
        '/joint_trajectory_controller/joint_trajectory',
        10
    )
    
    joint_names = [
        'j1', 'j11', 'j111', 'j1111',    # 腿 1 (前左)
        'j2', 'j21', 'j211', 'j2111',    # 腿 2 (前右)
        'j3', 'j31', 'j311', 'j3111',    # 腿 3 (后左)
        'j4', 'j41', 'j411', 'j4111'     # 腿 4 (后右)
    ]
    
    # 站立姿态
    standing_positions = [
        0.0, 0.4, -1.0, 0.5,  # 腿 1
        0.0, 0.4, -1.0, 0.5,  # 腿 2
        0.0, 0.4, -1.0, 0.5,  # 腿 3
        0.0, 0.4, -1.0, 0.5   # 腿 4
    ]
    
    point = JointTrajectoryPoint()
    point.positions = standing_positions
    point.time_from_start = Duration(sec=3, nanosec=0)
    
    traj = JointTrajectory()
    traj.joint_names = joint_names
    traj.points = [point]
    
    node.get_logger().info('🤖 发送站立命令...')
    
    # 等待一下确保话题连接
    import time
    time.sleep(0.5)
    
    publisher.publish(traj)
    
    node.get_logger().info('✅ 站立命令已发送！')
    node.get_logger().info('机器人应该在 3 秒内站立起来')
    
    time.sleep(1)
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
