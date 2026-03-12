#!/bin/bash
# 在RViz中查看Dog2 URDF模型

echo "=========================================="
echo "  在RViz中查看Dog2模型"
echo "=========================================="
echo ""

cd /home/dell/aperfect/carbot_ws

echo "步骤1: 停止现有进程..."
killall -9 robot_state_publisher joint_state_publisher rviz2 2>/dev/null
sleep 1
echo ""

echo "步骤2: 编译dog2_description..."
source /opt/ros/humble/setup.bash
colcon build --packages-select dog2_description --symlink-install
echo ""

echo "步骤3: Source环境..."
source install/setup.bash
echo ""

echo "步骤4: 启动RViz..."
echo "  • 显示机器人模型"
echo "  • 显示TF坐标系"
echo "  • 显示关节状态"
echo ""

ros2 launch dog2_description view_dog2.launch.py
