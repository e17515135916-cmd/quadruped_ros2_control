#!/bin/bash
# 在 RViz 中查看机器人

cd /home/dell/aperfect/carbot_ws
source install/setup.bash

# 杀死之前的进程
killall -9 robot_state_publisher joint_state_publisher_gui rviz2 2>/dev/null
sleep 1

echo "========================================="
echo "在 RViz 中查看 DOG2 机器人"
echo "========================================="
echo ""
echo "RViz 将显示："
echo "1. 机器人的 visual mesh（外观）"
echo "2. 可以切换显示碰撞几何体（cylinder）"
echo "3. 可以通过 GUI 控制关节角度"
echo ""
echo "启动中..."
echo ""

# 启动 RViz
ros2 launch dog2_description view_dog2.launch.py
