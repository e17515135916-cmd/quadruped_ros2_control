#!/bin/bash
# 检查 robot_description 参数是否正确发布

echo "=========================================="
echo "检查 robot_description 参数"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "1. 检查 robot_state_publisher 节点的参数..."
ros2 param list /robot_state_publisher 2>/dev/null | grep robot_description

echo ""
echo "2. 尝试获取 robot_description 参数（前100个字符）..."
ros2 param get /robot_state_publisher robot_description 2>/dev/null | head -c 100

echo ""
echo ""
echo "3. 检查参数长度..."
PARAM_LENGTH=$(ros2 param get /robot_state_publisher robot_description 2>/dev/null | wc -c)
echo "robot_description 参数长度: $PARAM_LENGTH 字符"

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="
