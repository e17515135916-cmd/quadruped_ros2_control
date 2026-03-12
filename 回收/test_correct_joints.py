#!/usr/bin/env python3
"""
正确的关节控制测试
只控制 joint_trajectory_controller 管理的 12 个关节
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class CorrectJointsTest(Node):
    def __init__(self):
        super().__init__('correct_joints_test')
        
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 只包含被 joint_trajectory_controller 控制的 12 个关节
        # 不包括 j1, j2, j3, j4（导轨关节）
        self.joint_names = [
            'j11', 'j111', 'j1111',    # 腿 1 (前左) - 3个旋转关节
            'j21', 'j211', 'j2111',    # 腿 2 (前右) - 3个旋转关节
            'j31', 'j311', 'j3111',    # 腿 3 (后左) - 3个旋转关节
            'j41', 'j411', 'j4111'     # 腿 4 (后右) - 3个旋转关节
        ]
        
        self.get_logger().info('🐕 正确关节控制测试')
        self.get_logger().info(f'控制 {len(self.joint_names)} 个关节')
        self.get_logger().info('等待 2 秒...')
        
        time.sleep(2)
        self.run_test()
        
    def send_command(self, positions, duration_sec, description=""):
        """发送关节命令"""
        if description:
            self.get_logger().info(f'📤 {description}')
        
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        
        traj.points = [point]
        self.publisher.publish(traj)
    
    def run_test(self):
        """运行测试序列"""
        
        # 测试 1: 站立姿态
        self.get_logger().info('\n=== 测试 1: 站立姿态 ===')
        standing = [
            0.4, -1.0, 0.5,  # 腿 1
            0.4, -1.0, 0.5,  # 腿 2
            0.4, -1.0, 0.5,  # 腿 3
            0.4, -1.0, 0.5   # 腿 4
        ]
        self.send_command(standing, 3, "站立姿态")
        time.sleep(4)
        
        # 测试 2: 抬起前左腿
        self.get_logger().info('\n=== 测试 2: 抬起前左腿 ===')
        lift_leg1 = [
            0.8, -1.5, 0.8,  # 腿1抬起
            0.4, -1.0, 0.5,  # 腿2
            0.4, -1.0, 0.5,  # 腿3
            0.4, -1.0, 0.5   # 腿4
        ]
        self.send_command(lift_leg1, 2, "抬起前左腿")
        time.sleep(3)
        
        # 测试 3: 回到站立
        self.get_logger().info('\n=== 测试 3: 回到站立 ===')
        self.send_command(standing, 2, "回到站立")
        time.sleep(3)
        
        # 测试 4: 抬起前右腿
        self.get_logger().info('\n=== 测试 4: 抬起前右腿 ===')
        lift_leg2 = [
            0.4, -1.0, 0.5,  # 腿1
            0.8, -1.5, 0.8,  # 腿2抬起
            0.4, -1.0, 0.5,  # 腿3
            0.4, -1.0, 0.5   # 腿4
        ]
        self.send_command(lift_leg2, 2, "抬起前右腿")
        time.sleep(3)
        
        # 测试 5: 回到站立
        self.get_logger().info('\n=== 测试 5: 回到站立 ===')
        self.send_command(standing, 2, "回到站立")
        time.sleep(3)
        
        # 测试 6: 对角步态 - 抬起腿1和腿4
        self.get_logger().info('\n=== 测试 6: 对角步态 - 抬起腿1和腿4 ===')
        diagonal1 = [
            0.8, -1.5, 0.8,  # 腿1抬起
            0.4, -1.0, 0.5,  # 腿2
            0.4, -1.0, 0.5,  # 腿3
            0.8, -1.5, 0.8   # 腿4抬起
        ]
        self.send_command(diagonal1, 2, "抬起腿1和腿4")
        time.sleep(3)
        
        # 测试 7: 对角步态 - 抬起腿2和腿3
        self.get_logger().info('\n=== 测试 7: 对角步态 - 抬起腿2和腿3 ===')
        diagonal2 = [
            0.4, -1.0, 0.5,  # 腿1
            0.8, -1.5, 0.8,  # 腿2抬起
            0.8, -1.5, 0.8,  # 腿3抬起
            0.4, -1.0, 0.5   # 腿4
        ]
        self.send_command(diagonal2, 2, "抬起腿2和腿3")
        time.sleep(3)
        
        # 测试 8: 回到站立
        self.get_logger().info('\n=== 测试 8: 回到站立 ===')
        self.send_command(standing, 2, "回到站立")
        time.sleep(3)
        
        self.get_logger().info('\n✅ 测试完成！')
        self.get_logger().info('检查 Gazebo 中机器人的腿部运动')
        
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = CorrectJointsTest()
    
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
