#!/usr/bin/env python3
"""
直接测试关节运动 - 诊断版本
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class DirectMovementTest(Node):
    def __init__(self):
        super().__init__('direct_movement_test')
        
        # 订阅关节状态
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # 发布轨迹命令
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'j1', 'j11', 'j111', 'j1111',
            'j2', 'j21', 'j211', 'j2111',
            'j3', 'j31', 'j311', 'j3111',
            'j4', 'j41', 'j411', 'j4111'
        ]
        
        self.current_positions = None
        self.get_logger().info('🔍 直接运动测试启动')
        self.get_logger().info('等待关节状态...')
        
    def joint_state_callback(self, msg):
        """接收关节状态"""
        if self.current_positions is None:
            self.current_positions = {}
            self.get_logger().info(f'✅ 接收到关节状态，共 {len(msg.name)} 个关节')
            
            # 显示当前关节位置
            for name, pos in zip(msg.name, msg.position):
                self.current_positions[name] = pos
                self.get_logger().info(f'  {name}: {pos:.3f}')
            
            # 开始测试
            self.get_logger().info('\n开始运动测试...')
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
        self.traj_pub.publish(traj)
        
        self.get_logger().info(f'   发送位置: {[f"{p:.2f}" for p in positions[:4]]}...')
    
    def run_test(self):
        """运行测试序列"""
        
        # 测试 1: 站立姿态
        self.get_logger().info('\n=== 测试 1: 站立姿态 ===')
        standing = [
            0.0, 0.4, -1.0, 0.5,
            0.0, 0.4, -1.0, 0.5,
            0.0, 0.4, -1.0, 0.5,
            0.0, 0.4, -1.0, 0.5
        ]
        self.send_command(standing, 3, "站立姿态")
        time.sleep(4)
        
        # 测试 2: 抬起前左腿
        self.get_logger().info('\n=== 测试 2: 抬起前左腿 ===')
        lift_leg1 = [
            0.0, 0.8, -1.5, 0.8,  # 腿1抬起
            0.0, 0.4, -1.0, 0.5,
            0.0, 0.4, -1.0, 0.5,
            0.0, 0.4, -1.0, 0.5
        ]
        self.send_command(lift_leg1, 2, "抬起前左腿")
        time.sleep(3)
        
        # 测试 3: 回到站立
        self.get_logger().info('\n=== 测试 3: 回到站立 ===')
        self.send_command(standing, 2, "回到站立")
        time.sleep(3)
        
        # 测试 4: 所有腿向前
        self.get_logger().info('\n=== 测试 4: 所有腿向前 ===')
        all_forward = [
            -0.3, 0.4, -1.0, 0.5,
            -0.3, 0.4, -1.0, 0.5,
            -0.3, 0.4, -1.0, 0.5,
            -0.3, 0.4, -1.0, 0.5
        ]
        self.send_command(all_forward, 2, "所有腿向前")
        time.sleep(3)
        
        # 测试 5: 所有腿向后
        self.get_logger().info('\n=== 测试 5: 所有腿向后 ===')
        all_backward = [
            0.3, 0.4, -1.0, 0.5,
            0.3, 0.4, -1.0, 0.5,
            0.3, 0.4, -1.0, 0.5,
            0.3, 0.4, -1.0, 0.5
        ]
        self.send_command(all_backward, 2, "所有腿向后")
        time.sleep(3)
        
        # 测试 6: 回到站立
        self.get_logger().info('\n=== 测试 6: 回到站立 ===')
        self.send_command(standing, 2, "回到站立")
        time.sleep(3)
        
        self.get_logger().info('\n✅ 测试完成！')
        self.get_logger().info('如果机器人没有移动，可能的原因：')
        self.get_logger().info('  1. 控制器未正确启动')
        self.get_logger().info('  2. 关节限位问题')
        self.get_logger().info('  3. Gazebo物理参数问题')
        
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = DirectMovementTest()
    
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
