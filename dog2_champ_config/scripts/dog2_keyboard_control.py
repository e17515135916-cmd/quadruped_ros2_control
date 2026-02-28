#!/usr/bin/env python3
"""
Dog2 Keyboard Control Script
使用键盘控制Dog2四足机器人

控制键:
    W/w - 向前
    S/s - 向后
    A/a - 向左
    D/d - 向右
    Q/q - 左转
    E/e - 右转
    空格 - 停止
    X/x - 退出
"""

import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Dog2KeyboardControl(Node):
    def __init__(self):
        super().__init__('dog2_keyboard_control')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 速度参数（可调整）
        self.linear_speed = 0.3    # 线速度 m/s
        self.angular_speed = 0.5   # 角速度 rad/s
        self.lateral_speed = 0.2   # 侧向速度 m/s
        
        self.get_logger().info('Dog2 Keyboard Control Started!')
        self.get_logger().info('使用 W/A/S/D 控制移动, Q/E 控制转向, 空格停止, X 退出')
        
    def get_key(self):
        """获取键盘输入"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key
    
    def publish_velocity(self, linear_x=0.0, linear_y=0.0, angular_z=0.0):
        """发布速度命令"""
        msg = Twist()
        msg.linear.x = linear_x
        msg.linear.y = linear_y
        msg.angular.z = angular_z
        self.publisher.publish(msg)
        
    def run(self):
        """主循环"""
        try:
            while True:
                key = self.get_key()
                
                if key == 'w' or key == 'W':
                    self.get_logger().info('向前 ⬆️')
                    self.publish_velocity(linear_x=self.linear_speed)
                    
                elif key == 's' or key == 'S':
                    self.get_logger().info('向后 ⬇️')
                    self.publish_velocity(linear_x=-self.linear_speed)
                    
                elif key == 'a' or key == 'A':
                    self.get_logger().info('向左 ⬅️')
                    self.publish_velocity(linear_y=self.lateral_speed)
                    
                elif key == 'd' or key == 'D':
                    self.get_logger().info('向右 ➡️')
                    self.publish_velocity(linear_y=-self.lateral_speed)
                    
                elif key == 'q' or key == 'Q':
                    self.get_logger().info('左转 ↺')
                    self.publish_velocity(angular_z=self.angular_speed)
                    
                elif key == 'e' or key == 'E':
                    self.get_logger().info('右转 ↻')
                    self.publish_velocity(angular_z=-self.angular_speed)
                    
                elif key == ' ':
                    self.get_logger().info('停止 ⏸️')
                    self.publish_velocity()
                    
                elif key == 'x' or key == 'X':
                    self.get_logger().info('退出程序')
                    self.publish_velocity()  # 停止机器人
                    break
                    
                elif key == '\x03':  # Ctrl+C
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.publish_velocity()  # 确保退出时停止
            self.get_logger().info('已停止控制')

def main(args=None):
    rclpy.init(args=args)
    controller = Dog2KeyboardControl()
    
    try:
        controller.run()
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

