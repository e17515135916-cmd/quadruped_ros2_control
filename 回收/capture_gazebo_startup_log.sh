#!/bin/bash
# 捕获 Gazebo 启动日志以诊断控制器问题

echo "=========================================="
echo "启动 Gazebo 并捕获日志"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

LOG_FILE="/tmp/gazebo_startup_$(date +%Y%m%d_%H%M%S).log"

echo "日志将保存到: $LOG_FILE"
echo ""
echo "正在启动 Gazebo..."
echo "请等待约 10 秒，然后按 Ctrl+C 停止"
echo ""

ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py 2>&1 | tee "$LOG_FILE"
