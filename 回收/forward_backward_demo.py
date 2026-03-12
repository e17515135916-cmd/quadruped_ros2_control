#!/usr/bin/env python3
"""
Dog2 前进后退演示
实现前进和后退运动，使用对角步态（trot gait）
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class ForwardBackwardDemo(Node):
    def __init__(self):
        super().__init__('forward_backward_demo')
        
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
        
        self.get_logger().info('🐕 Dog2 前进后退演示启动')
        self.get_logger().info('等待 2 秒...')
        
        # 等待系统准备好
        time.sleep(2)
        
        # 执行前进后退演示
        self.forward_backward_demo()
        
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
    
    # ========== 前进步态 ==========
    def forward_step_phase1(self):
        """前进 - 抬起腿1和腿4，向前摆动"""
        return [
            -0.3, 0.8, -1.5, 0.8,   # 腿 1: 向前摆动 + 抬起
            0.0, 0.4, -1.0, 0.5,    # 腿 2: 支撑
            0.0, 0.4, -1.0, 0.5,    # 腿 3: 支撑
            -0.3, 0.8, -1.5, 0.8    # 腿 4: 向前摆动 + 抬起
        ]
    
    def forward_step_phase2(self):
        """前进 - 放下腿1和腿4"""
        return [
            -0.2, 0.4, -1.0, 0.5,   # 腿 1: 放下
            0.2, 0.4, -1.0, 0.5,    # 腿 2: 向后
            0.2, 0.4, -1.0, 0.5,    # 腿 3: 向后
            -0.2, 0.4, -1.0, 0.5    # 腿 4: 放下
        ]
    
    def forward_step_phase3(self):
        """前进 - 抬起腿2和腿3，向前摆动"""
        return [
            0.0, 0.4, -1.0, 0.5,    # 腿 1: 支撑
            -0.3, 0.8, -1.5, 0.8,   # 腿 2: 向前摆动 + 抬起
            -0.3, 0.8, -1.5, 0.8,   # 腿 3: 向前摆动 + 抬起
            0.0, 0.4, -1.0, 0.5     # 腿 4: 支撑
        ]
    
    def forward_step_phase4(self):
        """前进 - 放下腿2和腿3"""
        return [
            0.2, 0.4, -1.0, 0.5,    # 腿 1: 向后
            -0.2, 0.4, -1.0, 0.5,   # 腿 2: 放下
            -0.2, 0.4, -1.0, 0.5,   # 腿 3: 放下
            0.2, 0.4, -1.0, 0.5     # 腿 4: 向后
        ]
    
    # ========== 后退步态 ==========
    def backward_step_phase1(self):
        """后退 - 抬起腿1和腿4，向后摆动"""
        return [
            0.3, 0.8, -1.5, 0.8,    # 腿 1: 向后摆动 + 抬起
            0.0, 0.4, -1.0, 0.5,    # 腿 2: 支撑
            0.0, 0.4, -1.0, 0.5,    # 腿 3: 支撑
            0.3, 0.8, -1.5, 0.8     # 腿 4: 向后摆动 + 抬起
        ]
    
    def backward_step_phase2(self):
        """后退 - 放下腿1和腿4"""
        return [
            0.2, 0.4, -1.0, 0.5,    # 腿 1: 放下
            -0.2, 0.4, -1.0, 0.5,   # 腿 2: 向前
            -0.2, 0.4, -1.0, 0.5,   # 腿 3: 向前
            0.2, 0.4, -1.0, 0.5     # 腿 4: 放下
        ]
    
    def backward_step_phase3(self):
        """后退 - 抬起腿2和腿3，向后摆动"""
        return [
            0.0, 0.4, -1.0, 0.5,    # 腿 1: 支撑
            0.3, 0.8, -1.5, 0.8,    # 腿 2: 向后摆动 + 抬起
            0.3, 0.8, -1.5, 0.8,    # 腿 3: 向后摆动 + 抬起
            0.0, 0.4, -1.0, 0.5     # 腿 4: 支撑
        ]
    
    def backward_step_phase4(self):
        """后退 - 放下腿2和腿3"""
        return [
            -0.2, 0.4, -1.0, 0.5,   # 腿 1: 向前
            0.2, 0.4, -1.0, 0.5,    # 腿 2: 放下
            0.2, 0.4, -1.0, 0.5,    # 腿 3: 放下
            -0.2, 0.4, -1.0, 0.5    # 腿 4: 向前
        ]
        
    def forward_backward_demo(self):
        """前进后退演示"""
        base_pose = self.standing_pose()
        
        # 1. 站立准备
        self.get_logger().info('\n=== 🟢 阶段 1: 站立准备 ===')
        self.send_trajectory([
            self.create_trajectory_point(base_pose, 2)
        ], "站立姿态")
        time.sleep(3)
        
        # 2. 前进
        self.get_logger().info('\n=== ⬆️  阶段 2: 前进运动 ===')
        num_forward_steps = 3
        
        for i in range(num_forward_steps):
            self.get_logger().info(f'\n  前进步态 {i+1}/{num_forward_steps}')
            
            self.send_trajectory([
                self.create_trajectory_point(self.forward_step_phase1(), 1)
            ], "前进: 抬起前左腿和后右腿")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.forward_step_phase2(), 1)
            ], "前进: 放下腿，身体前移")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.forward_step_phase3(), 1)
            ], "前进: 抬起前右腿和后左腿")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.forward_step_phase4(), 1)
            ], "前进: 放下腿，身体前移")
            time.sleep(1.2)
        
        # 3. 停顿
        self.get_logger().info('\n=== ⏸️  阶段 3: 停顿 ===')
        self.send_trajectory([
            self.create_trajectory_point(base_pose, 2)
        ], "回到站立姿态")
        time.sleep(3)
        
        # 4. 后退
        self.get_logger().info('\n=== ⬇️  阶段 4: 后退运动 ===')
        num_backward_steps = 3
        
        for i in range(num_backward_steps):
            self.get_logger().info(f'\n  后退步态 {i+1}/{num_backward_steps}')
            
            self.send_trajectory([
                self.create_trajectory_point(self.backward_step_phase1(), 1)
            ], "后退: 抬起前左腿和后右腿")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.backward_step_phase2(), 1)
            ], "后退: 放下腿，身体后移")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.backward_step_phase3(), 1)
            ], "后退: 抬起前右腿和后左腿")
            time.sleep(1.2)
            
            self.send_trajectory([
                self.create_trajectory_point(self.backward_step_phase4(), 1)
            ], "后退: 放下腿，身体后移")
            time.sleep(1.2)
        
        # 5. 最终站立
        self.get_logger().info('\n=== 🟢 阶段 5: 停止并站立 ===')
        self.send_trajectory([
            self.create_trajectory_point(base_pose, 2)
        ], "回到站立姿态")
        time.sleep(3)
        
        # 6. 完成
        self.get_logger().info('\n=== ✅ 前进后退演示完成 ===')
        self.get_logger().info('机器狗应该已经完成前进和后退运动')
        self.get_logger().info('检查 Gazebo 中机器人的位置变化')
        
        # 保持节点运行
        time.sleep(2)
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = ForwardBackwardDemo()
    
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
