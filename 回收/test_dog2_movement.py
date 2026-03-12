#!/usr/bin/env python3
"""
测试 Dog2 机器狗运动
发送简单的关节轨迹命令让机器狗动起来
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math


class Dog2MovementTest(Node):
    def __init__(self):
        super().__init__('dog2_movement_test')
        
        # 创建轨迹发布器
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 等待发布器准备好
        self.get_logger().info('等待 2 秒让系统准备好...')
        self.create_timer(2.0, self.send_movement_command)
        
    def send_movement_command(self):
        """发送让机器狗腿部运动的命令"""
        self.get_logger().info('发送运动命令...')
        
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
        
        # 创建多个轨迹点，让机器狗做简单的腿部运动
        
        # 点 1: 初始位置 (0秒)
        point1 = JointTrajectoryPoint()
        point1.positions = [0.0] * 16
        point1.time_from_start = Duration(sec=0, nanosec=0)
        
        # 点 2: 抬起前腿 (2秒)
        point2 = JointTrajectoryPoint()
        point2.positions = [
            0.0, 0.5, -0.8, 0.0,  # 腿1: 抬起
            0.0, 0.5, -0.8, 0.0,  # 腿2: 抬起
            0.0, 0.0, 0.0, 0.0,   # 腿3: 保持
            0.0, 0.0, 0.0, 0.0    # 腿4: 保持
        ]
        point2.time_from_start = Duration(sec=2, nanosec=0)
        
        # 点 3: 放下前腿，抬起后腿 (4秒)
        point3 = JointTrajectoryPoint()
        point3.positions = [
            0.0, 0.0, 0.0, 0.0,   # 腿1: 放下
            0.0, 0.0, 0.0, 0.0,   # 腿2: 放下
            0.0, 0.5, -0.8, 0.0,  # 腿3: 抬起
            0.0, 0.5, -0.8, 0.0   # 腿4: 抬起
        ]
        point3.time_from_start = Duration(sec=4, nanosec=0)
        
        # 点 4: 回到初始位置 (6秒)
        point4 = JointTrajectoryPoint()
        point4.positions = [0.0] * 16
        point4.time_from_start = Duration(sec=6, nanosec=0)
        
        traj.points = [point1, point2, point3, point4]
        
        # 发布轨迹
        self.publisher.publish(traj)
        self.get_logger().info('✅ 运动命令已发送！机器狗应该开始运动了。')
        self.get_logger().info('   - 0-2秒: 抬起前腿')
        self.get_logger().info('   - 2-4秒: 放下前腿，抬起后腿')
        self.get_logger().info('   - 4-6秒: 回到初始位置')
        
        # 10秒后关闭节点
        self.create_timer(10.0, self.shutdown)
        
    def shutdown(self):
        self.get_logger().info('测试完成，关闭节点')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = Dog2MovementTest()
    
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
