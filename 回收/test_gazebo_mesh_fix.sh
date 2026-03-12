#!/bin/bash
# 测试修复后的 Gazebo mesh 路径问题

echo "=========================================="
echo "启动 Gazebo 测试 - Mesh 路径修复版本"
echo "=========================================="

# Source ROS 2 环境
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "正在启动 Gazebo..."
echo "如果看到机器人模型正常显示，说明修复成功！"
echo ""
echo "按 Ctrl+C 停止仿真"
echo ""

# 启动 Gazebo
ros2 launch dog2_description gazebo_dog2_final.launch.py
