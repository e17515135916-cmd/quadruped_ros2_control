#!/usr/bin/env python3
"""
Dog2 运动演示脚本
自动演示Dog2四足机器人的各种运动能力
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class Dog2MotionDemo(Node):
    def __init__(self):
        super().__init__('dog2_motion_demo')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Dog2 Motion Demo Started! 🐕')
        
    def publish_velocity(self, linear_x=0.0, linear_y=0.0, angular_z=0.0, duration=2.0):
        """发布速度命令并持续指定时间"""
        msg = Twist()
        msg.linear.x = linear_x
        msg.linear.y = linear_y
        msg.angular.z = angular_z
        
        start_time = time.time()
        rate = self.create_rate(20)  # 20 Hz
        
        while time.time() - start_time < duration:
            self.publisher.publish(msg)
            rate.sleep()
            
    def stop(self, duration=1.0):
        """停止并等待"""
        self.get_logger().info('停止 ⏸️')
        self.publish_velocity(0.0, 0.0, 0.0, duration)
        
    def run_demo(self):
        """运行完整演示"""
        try:
            self.get_logger().info('=' * 50)
            self.get_logger().info('开始运动演示...')
            self.get_logger().info('=' * 50)
            
            # 1. 向前走
            self.get_logger().info('1️⃣  向前行走 ⬆️')
            self.publish_velocity(linear_x=0.3, duration=3.0)
            self.stop()
            
            # 2. 向后走
            self.get_logger().info('2️⃣  向后行走 ⬇️')
            self.publish_velocity(linear_x=-0.2, duration=3.0)
            self.stop()
            
            # 3. 原地左转
            self.get_logger().info('3️⃣  原地左转 ↺')
            self.publish_velocity(angular_z=0.5, duration=3.0)
            self.stop()
            
            # 4. 原地右转
            self.get_logger().info('4️⃣  原地右转 ↻')
            self.publish_velocity(angular_z=-0.5, duration=3.0)
            self.stop()
            
            # 5. 向左侧移
            self.get_logger().info('5️⃣  向左侧移 ⬅️')
            self.publish_velocity(linear_y=0.2, duration=3.0)
            self.stop()
            
            # 6. 向右侧移
            self.get_logger().info('6️⃣  向右侧移 ➡️')
            self.publish_velocity(linear_y=-0.2, duration=3.0)
            self.stop()
            
            # 7. 前进+左转（弧线运动）
            self.get_logger().info('7️⃣  弧线运动（前进+左转）🌙')
            self.publish_velocity(linear_x=0.3, angular_z=0.3, duration=4.0)
            self.stop()
            
            # 8. 前进+右转（弧线运动）
            self.get_logger().info('8️⃣  弧线运动（前进+右转）🌙')
            self.publish_velocity(linear_x=0.3, angular_z=-0.3, duration=4.0)
            self.stop()
            
            # 9. 对角线运动
            self.get_logger().info('9️⃣  对角线运动 ↗️')
            self.publish_velocity(linear_x=0.2, linear_y=0.15, duration=3.0)
            self.stop()
            
            self.get_logger().info('=' * 50)
            self.get_logger().info('✅ 演示完成！Dog2真棒！🎉')
            self.get_logger().info('=' * 50)
            
        except KeyboardInterrupt:
            self.get_logger().info('演示被中断')
        finally:
            self.stop()

def main(args=None):
    rclpy.init(args=args)
    demo = Dog2MotionDemo()
    
    try:
        demo.run_demo()
    finally:
        demo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

