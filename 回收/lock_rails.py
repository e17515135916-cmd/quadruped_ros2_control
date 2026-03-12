#!/usr/bin/env python3
"""
锁定导轨位置脚本
将所有 4 个移动关节（j1, j2, j3, j4）设置为 0 位置并保持
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time


class LockRails(Node):
    def __init__(self):
        super().__init__('lock_rails')
        
        # 发布到 rail_position_controller
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/rail_position_controller/commands',
            10
        )
        
        self.get_logger().info('🔒 导轨锁定节点启动')
        self.get_logger().info('等待 1 秒...')
        
        # 等待系统准备好
        time.sleep(1.0)
        
        # 发送锁定命令
        self.lock_rails()
        
        self.get_logger().info('✅ 导轨已锁定在零位')
        self.get_logger().info('所有移动关节 (j1, j2, j3, j4) = 0.0')
        
        # 保持节点运行
        time.sleep(2.0)
        rclpy.shutdown()
        
    def lock_rails(self):
        """锁定所有导轨在零位"""
        msg = Float64MultiArray()
        # 4 个移动关节都设置为 0
        msg.data = [0.0, 0.0, 0.0, 0.0]
        
        self.publisher.publish(msg)
        self.get_logger().info('📤 导轨锁定命令已发布: [0.0, 0.0, 0.0, 0.0]')


def main(args=None):
    rclpy.init(args=args)
    node = LockRails()
    
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
