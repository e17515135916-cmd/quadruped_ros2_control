#!/bin/bash

echo "=========================================="
echo "  Dog2 Gazebo 简单测试"
echo "=========================================="
echo ""
echo "使用修复后的URDF文件测试Gazebo仿真"
echo ""

cd /home/dell/aperfect/carbot_ws

echo "步骤1: 编译..."
colcon build --packages-select dog2_description
echo ""

echo "步骤2: Source环境..."
source install/setup.bash
echo ""

echo "步骤3: 启动Gazebo..."
echo ""
echo "预期结果："
echo "  1. Gazebo窗口打开"
echo "  2. Dog2机器人出现在空中（高度0.5m）"
echo "  3. 机器人应该掉落到地面"
echo "  4. 检查物理仿真是否稳定"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description test_gazebo.launch.py
