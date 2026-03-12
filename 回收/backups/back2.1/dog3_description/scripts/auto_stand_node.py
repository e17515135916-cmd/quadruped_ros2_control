#!/usr/bin/env python3
"""
自动站立节点
在机器人生成后自动发送站立姿态命令
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class AutoStandNode(Node):
    def __init__(self):
        super().__init__('auto_stand_node')
        
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'j1', 'j11', 'j111', 'j1111',    # 腿 1 (前左)
            'j2', 'j21', 'j211', 'j2111',    # 腿 2 (前右)
            'j3', 'j31', 'j311', 'j3111',    # 腿 3 (后左)
            'j4', 'j41', 'j411', 'j4111'     # 腿 4 (后右)
        ]
        
        self.get_logger().info('🤖 自动站立节点启动')
        self.get_logger().info('等待 1 秒后发送站立命令...')
        
        # 等待 1 秒确保控制器完全准备好
        time.sleep(1.0)
        
        # 发送站立姿态
        self.send_standing_pose()
        
        self.get_logger().info('✅ 站立命令已发送')
        self.get_logger().info('机器人应该在 3 秒内站立起来')
        
        # 保持节点运行 5 秒后自动退出
        time.sleep(5.0)
        self.get_logger().info('自动站立节点完成任务，退出')
        rclpy.shutdown()
        
    def send_standing_pose(self):
        """发送站立姿态"""
        # 站立姿态：所有腿都弯曲以支撑身体
        standing_positions = [
            0.0, 0.4, -1.0, 0.5,  # 腿 1
            0.0, 0.4, -1.0, 0.5,  # 腿 2
            0.0, 0.4, -1.0, 0.5,  # 腿 3
            0.0, 0.4, -1.0, 0.5   # 腿 4
        ]
        
        point = JointTrajectoryPoint()
        point.positions = standing_positions
        point.time_from_start = Duration(sec=3, nanosec=0)  # 3 秒内完成站立
        
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        traj.points = [point]
        
        self.publisher.publish(traj)
        self.get_logger().info('📤 站立轨迹已发布')


def main(args=None):
    rclpy.init(args=args)
    node = AutoStandNode()
    
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
