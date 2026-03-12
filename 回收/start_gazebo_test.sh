#!/bin/bash

echo "=========================================="
echo "  Dog2 Gazebo 完整测试"
echo "=========================================="
echo ""
echo "使用修复后的dog2.urdf.xacro文件"
echo ""

cd /home/dell/aperfect/carbot_ws

# 先停止所有Gazebo进程
echo "步骤0: 清理旧的Gazebo进程..."
pkill -9 gzserver
pkill -9 gzclient
sleep 2
echo ""

echo "步骤1: 编译dog2_description包..."
colcon build --packages-select dog2_description --symlink-install
echo ""

echo "步骤2: Source环境..."
source install/setup.bash
echo ""

echo "步骤3: 启动Gazebo仿真..."
echo ""
echo "预期结果："
echo "  1. Gazebo服务器启动（gzserver）"
echo "  2. Gazebo客户端启动（gzclient）- GUI窗口"
echo "  3. 5秒后Dog2机器人出现在空中（高度0.5m）"
echo "  4. 机器人掉落到地面"
echo "  5. 检查物理仿真是否稳定"
echo ""
echo "如果机器人不可见，检查："
echo "  - Gazebo左侧模型列表中是否有'dog2'"
echo "  - 控制台是否有错误信息"
echo "  - mesh文件路径是否正确"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_test.launch.py
