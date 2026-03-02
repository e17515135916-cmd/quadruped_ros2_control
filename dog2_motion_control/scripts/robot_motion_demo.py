#!/usr/bin/env python3
"""
蜘蛛机器人Gazebo运动演示脚本

此脚本演示如何通过发送速度命令让机器人在Gazebo中运动
"""

import rclpy
from geometry_msgs.msg import Twist
import time
import sys

def main():
    rclpy.init()
    node = rclpy.create_node('robot_motion_demo')
    
    # 创建速度发布器
    cmd_vel_pub = node.create_publisher(Twist, '/cmd_vel', 10)
    
    print("="*60)
    print("蜘蛛机器人Gazebo运动演示")
    print("="*60)
    
    # 等待发布器就绪
    time.sleep(1)
    
    # 演示1: 前进
    print("\n[演示1] 机器人前进 (5秒)...")
    cmd = Twist()
    cmd.linear.x = 0.15  # 前进0.15 m/s
    for _ in range(50):  # 50 * 0.1秒 = 5秒
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    # 停止
    print("[停止] 停止运动...")
    cmd.linear.x = 0.0
    for _ in range(10):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # 演示2: 左转
    print("\n[演示2] 机器人左转 (5秒)...")
    cmd.linear.x = 0.0
    cmd.angular.z = 0.3  # 逆时针旋转0.3 rad/s
    for _ in range(50):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    # 停止
    print("[停止] 停止旋转...")
    cmd.angular.z = 0.0
    for _ in range(10):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # 演示3: 右转
    print("\n[演示3] 机器人右转 (5秒)...")
    cmd.angular.z = -0.3  # 顺时针旋转-0.3 rad/s
    for _ in range(50):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    # 停止
    print("[停止] 停止旋转...")
    cmd.angular.z = 0.0
    for _ in range(10):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # 演示4: 前进+转向（曲线运动）
    print("\n[演示4] 机器人曲线运动 (5秒)...")
    cmd.linear.x = 0.1
    cmd.angular.z = 0.2
    for _ in range(50):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    # 停止
    print("[停止] 停止运动...")
    cmd.linear.x = 0.0
    cmd.angular.z = 0.0
    for _ in range(10):
        cmd_vel_pub.publish(cmd)
        time.sleep(0.1)
    
    print("\n" + "="*60)
    print("演示完成！机器人已停止")
    print("="*60)
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
