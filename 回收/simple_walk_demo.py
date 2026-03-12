#!/usr/bin/env python3
"""
Dog2 简单行走演示
不依赖 CHAMP，直接使用关节轨迹控制实现简单的步态
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math
import time


class SimpleWalkDemo(Node):
    def __init__(self):
        super().__init__('simple_walk_demo')
        
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
        
        self.get_logger().info('🐕 Dog2 简单行走演示启动')
        self.get_logger().info('等待 2 秒...')
        
        # 等待系统准备好
        time.sleep(2)
        
        # 执行演示序列
        self.demo_sequence()
        
    def create_trajectory_point(self, positions, time_sec):
        """创建轨迹点"""
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=time_sec, nanosec=0)
        return point
        
    def send_trajectory(self, points, description=""):
        """发送轨迹"""
        if description:
            self.get_logger().info(f'📍 {description}')
            
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        traj.points = points
        self.publisher.publish(traj)
        
    def standing_pose(self):
        """站立姿态"""
        return [
            0.0, 0.4, -1.0, 0.5,  # 腿 1
            0.0, 0.4, -1.0, 0.5,  # 腿 2
            0.0, 0.4, -1.0, 0.5,  # 腿 3
            0.0, 0.4, -1.0, 0.5   # 腿 4
        ]
        
    def lift_leg(self, leg_num, base_pose):
        """抬起指定的腿"""
        pose = base_pose.copy()
        offset = (leg_num - 1) * 4
        pose[offset + 1] = 0.8   # 髋关节向上
        pose[offset + 2] = -1.5  # 大腿向上弯曲
        pose[offset + 3] = 0.8   # 小腿向上
        return pose
        
    def demo_sequence(self):
        """演示序列"""
        base_pose = self.standing_pose()
        
        # 1. 站立
        self.get_logger().info('\n=== 阶段 1: 站立 ===')
        self.send_trajectory([
            self.create_trajectory_point(base_pose, 2)
        ], "站立姿态")
        time.sleep(3)
        
        # 2. 对角步态演示（trot gait）
        self.get_logger().info('\n=== 阶段 2: 对角步态演示 ===')
        
        # 抬起腿 1 和腿 4（对角线）
        pose1 = base_pose.copy()
        pose1[1] = 0.8; pose1[2] = -1.5; pose1[3] = 0.8   # 腿 1 抬起
        pose1[13] = 0.8; pose1[14] = -1.5; pose1[15] = 0.8  # 腿 4 抬起
        
        # 放下腿 1 和腿 4，抬起腿 2 和腿 3
        pose2 = base_pose.copy()
        pose2[5] = 0.8; pose2[6] = -1.5; pose2[7] = 0.8   # 腿 2 抬起
        pose2[9] = 0.8; pose2[10] = -1.5; pose2[11] = 0.8  # 腿 3 抬起
        
        # 循环 3 次
        for i in range(3):
            self.get_logger().info(f'  步态循环 {i+1}/3')
            
            # 抬起腿 1 和腿 4
            self.send_trajectory([
                self.create_trajectory_point(pose1, 1)
            ], f"抬起前左腿和后右腿")
            time.sleep(1.5)
            
            # 抬起腿 2 和腿 3
            self.send_trajectory([
                self.create_trajectory_point(pose2, 1)
            ], f"抬起前右腿和后左腿")
            time.sleep(1.5)
        
        # 3. 回到站立
        self.get_logger().info('\n=== 阶段 3: 回到站立 ===')
        self.send_trajectory([
            self.create_trajectory_point(base_pose, 2)
        ], "站立姿态")
        time.sleep(3)
        
        # 4. 单腿抬起演示
        self.get_logger().info('\n=== 阶段 4: 单腿抬起演示 ===')
        for leg in range(1, 5):
            self.send_trajectory([
                self.create_trajectory_point(self.lift_leg(leg, base_pose), 1)
            ], f"抬起腿 {leg}")
            time.sleep(1.5)
            
            self.send_trajectory([
                self.create_trajectory_point(base_pose, 1)
            ], f"放下腿 {leg}")
            time.sleep(1.5)
        
        # 5. 完成
        self.get_logger().info('\n=== ✅ 演示完成 ===')
        self.get_logger().info('机器狗保持站立姿态')
        
        # 保持节点运行
        time.sleep(2)
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = SimpleWalkDemo()
    
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
