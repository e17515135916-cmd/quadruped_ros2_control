#!/bin/bash
# 捕获 Gazebo 启动日志

echo "=========================================="
echo "捕获 Gazebo 启动日志"
echo "=========================================="
echo ""
echo "这个脚本会启动 Gazebo 并将日志保存到文件"
echo "请等待 15 秒让系统完全启动"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# Source 环境
source /opt/ros/humble/setup.bash
source install/setup.bash

# 启动并捕获日志
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py 2>&1 | tee gazebo_startup_log.txt
