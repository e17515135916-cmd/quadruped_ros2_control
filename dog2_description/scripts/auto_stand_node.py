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
        
        self.rail_publisher = self.create_publisher(
            JointTrajectory,
            '/rail_position_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        
        self.rail_names = ['j1', 'j2', 'j3', 'j4']
        
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
        """发送蜘蛛型站立姿态 (适配统一坐标系)"""
        # 在统一坐标系下 (Z轴向上)：
        # HAA (侧摆): 0.0 (居中)
        # HFE (大腿): 0.8 (向外展)
        # KFE (膝盖): 1.5 (向下支撑)
        # 注意：由于 HFE 是绕 Z 旋转（经过 RPY=1.57 0 0 变换后的局部轴）
        # 具体的数值可能需要根据仿真效果微调
        standing_positions = [
            0.0, 0.8, 1.5,  # LF
            0.0, 0.8, 1.5,  # RF
            0.0, 0.8, 1.5,  # LH
            0.0, 0.8, 1.5   # RH
        ]
        
        point = JointTrajectoryPoint()
        point.positions = standing_positions
        point.time_from_start = Duration(sec=3, nanosec=0)
        
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        traj.points = [point]
        
        self.publisher.publish(traj)
        
        # 同时确保导轨关节 (j1-j4) 保持在 0 位
        rail_point = JointTrajectoryPoint()
        rail_point.positions = [0.0, 0.0, 0.0, 0.0]
        rail_point.time_from_start = Duration(sec=1, nanosec=0)
        
        rail_traj = JointTrajectory()
        rail_traj.joint_names = self.rail_names
        rail_traj.points = [rail_point]
        self.rail_publisher.publish(rail_traj)
        
        self.get_logger().info('📤 蜘蛛型站立轨迹及导轨锁定命令已发布')


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
