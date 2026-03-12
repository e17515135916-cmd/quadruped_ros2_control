#!/bin/bash
# 停止 Gazebo 和所有相关进程

echo "停止 Gazebo 和相关进程..."

# 停止 Gazebo
pkill -9 gzserver
pkill -9 gzclient
pkill -9 gazebo

# 停止 ROS2 节点
pkill -9 -f "quadruped_controller"
pkill -9 -f "state_estimation"
pkill -9 -f "contact_sensor"
pkill -9 -f "robot_state_publisher"
pkill -9 -f "controller_manager"

echo "完成！"
