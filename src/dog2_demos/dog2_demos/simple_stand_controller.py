#!/usr/bin/env python3
"""
Dog2 简单站立控制器

功能：
- 让Dog2从初始姿态过渡到站立姿态
- 保持稳定的站立姿态
- 为后续演示做准备

使用方法：
    ros2 run dog2_demos simple_stand_controller

作者：Dog2开发团队
日期：2025-01-12
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class SimpleStandController(Node):
    """简单站立控制器"""
    
    def __init__(self):
        super().__init__('simple_stand_controller')
        
        # 发布关节位置命令
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_group_position_controller/commands',
            10
        )
        
        self.joint_pub_alt = self.create_publisher(
            Float64MultiArray,
            '/dog2/joint_group_position_controller/commands',
            10
        )
        
        # 定时器：50Hz
        self.timer = self.create_timer(0.02, self.control_callback)
        
        # 状态（使用 ROS 时钟以支持仿真时间）
        self.start_time = self.get_clock().now()
        self.transition_duration = 3.0  # 3秒过渡时间
        
        # 目标站立姿态
        self.target_sliding = [0.0, 0.0, 0.0, 0.0]  # 滑动关节：中立位置
        self.target_rotating = [
            0.5, -0.8, 0.0,  # 右后腿
            0.5, -0.8, 0.0,  # 右前腿
            0.5, -0.8, 0.0,  # 左前腿
            0.5, -0.8, 0.0,  # 左后腿
        ]
        
        self.get_logger().info('=' * 60)
        self.get_logger().info('Dog2 站立控制器已启动！')
        self.get_logger().info('=' * 60)
        self.get_logger().info('正在让机器人站立...')
        self.get_logger().info('')
    
    def control_callback(self):
        """控制回调函数"""
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
        
        # 创建消息
        msg = Float64MultiArray()
        
        if elapsed < self.transition_duration:
            # 过渡阶段：平滑插值
            alpha = elapsed / self.transition_duration
            alpha = min(1.0, alpha)  # 限制在[0,1]
            
            # 滑动关节：从0平滑过渡到目标
            current_sliding = [s * alpha for s in self.target_sliding]
            
            # 旋转关节：从0平滑过渡到目标
            current_rotating = [r * alpha for r in self.target_rotating]
            
            msg.data = current_sliding + current_rotating
            
            if int(elapsed * 50) % 50 == 0:  # 每秒打印一次
                self.get_logger().info(f'过渡中... {elapsed:.1f}s / {self.transition_duration:.1f}s')
        else:
            # 稳定阶段：保持目标姿态
            msg.data = self.target_sliding + self.target_rotating
            
            if int(elapsed * 50) % 250 == 0:  # 每5秒打印一次
                self.get_logger().info('✓ 机器人已稳定站立')
        
        # 发布命令
        self.joint_pub.publish(msg)
        self.joint_pub_alt.publish(msg)


def main(args=None):
    """主函数"""
    rclpy.init(args=args)
    
    node = SimpleStandController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('')
        node.get_logger().info('控制器已停止')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

