#!/bin/bash
# 启动 Dog2 Gazebo 带 GUI

echo "🐕 启动 Dog2 Gazebo (带 GUI)"
echo "============================"
echo ""

cd ~/aperfect/carbot_ws
source install/setup.bash

echo "🚀 启动 Gazebo Fortress..."
echo "   GUI 窗口应该会打开"
echo ""
echo "启动后，在另一个终端运行："
echo "   python3 test_correct_joints.py"
echo ""
echo "按 Ctrl+C 停止"
echo ""

ros2 launch dog2_description dog2_fortress_with_gui.launch.py
