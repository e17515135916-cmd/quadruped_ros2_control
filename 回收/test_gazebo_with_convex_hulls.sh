#!/bin/bash
# 测试使用凸包碰撞网格的Gazebo仿真

echo "=========================================="
echo "启动Gazebo测试（使用凸包碰撞网格）"
echo "=========================================="

# 设置ROS2环境
source /opt/ros/humble/setup.bash
source install/setup.bash

# 启动Gazebo
echo "正在启动Gazebo..."
echo "使用启动文件: gazebo_dog2.launch.py"
echo ""
echo "观察要点："
echo "  ✓ 机器人是否稳定站立"
echo "  ✓ 接触地面时是否正常"
echo "  ✓ 是否还会'飞走'或'爆炸'"
echo ""
ros2 launch dog2_description gazebo_dog2.launch.py
