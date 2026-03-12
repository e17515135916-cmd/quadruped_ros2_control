#!/bin/bash
# 检查 Gazebo 中加载的模型

echo "=========================================="
echo "检查 Gazebo 模型"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 检查 Gazebo 话题..."
gz topic -l | grep -i dog2
echo ""

echo "2. 检查模型信息..."
gz model -m dog2 -i 2>/dev/null || echo "无法获取模型信息"
echo ""

echo "3. 检查关节列表..."
gz model -m dog2 -j 2>/dev/null || echo "无法获取关节列表"
echo ""

echo "4. 检查 gz_ros2_control 插件..."
gz model -m dog2 -p 2>/dev/null | grep -i control || echo "未找到 control 插件"
