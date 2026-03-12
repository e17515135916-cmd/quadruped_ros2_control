#!/bin/bash

# 快速启动Dog2行走测试

echo "=========================================="
echo "Dog2 行走测试 - 快速启动"
echo "=========================================="
echo ""

# 进入工作空间
cd /home/dell/aperfect/carbot_ws

# 设置环境
echo "设置ROS2环境..."
source install/setup.bash

echo ""
echo "启动仿真系统（行走模式）..."
echo ""

# 启动仿真
ros2 launch dog2_mpc complete_simulation.launch.py mode:=walking

echo ""
echo "仿真已停止"
