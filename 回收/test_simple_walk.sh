#!/bin/bash
# Dog2 简单行走测试脚本
# 
# 使用方法：
# 1. 在终端 1 运行此脚本启动 Gazebo 和控制器
# 2. 在终端 2 运行: python3 simple_walk_demo.py

echo "🐕 Dog2 简单行走测试"
echo "===================="
echo ""
echo "步骤 1: 编译 dog2_description 包..."

cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install

if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi

echo ""
echo "✅ 编译成功"
echo ""
echo "步骤 2: 加载环境..."
source install/setup.bash

echo ""
echo "步骤 3: 启动 Gazebo Fortress + 控制器..."
echo ""
echo "⚠️  Gazebo 启动后，请在另一个终端运行："
echo "   cd ~/aperfect/carbot_ws"
echo "   source install/setup.bash"
echo "   python3 simple_walk_demo.py"
echo ""
echo "按 Ctrl+C 停止仿真"
echo ""

ros2 launch dog2_description dog2_fortress_with_control.launch.py
