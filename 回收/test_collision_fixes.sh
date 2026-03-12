#!/bin/bash
# 测试碰撞修复效果

echo "=========================================="
echo "  碰撞修复测试 - 降低接触刚度"
echo "=========================================="
echo ""
echo "修复内容:"
echo "  ✅ 使用凸包碰撞网格（17个文件）"
echo "  ✅ 降低接触刚度 kp: 1000000 → 10000"
echo "  ✅ 降低阻尼系数 kd: 100 → 10"
echo ""
echo "预期效果:"
echo "  • 机器人平稳落地"
echo "  • 无异常抖动"
echo "  • 无'飞走'现象"
echo ""

cd /home/dell/aperfect/carbot_ws

echo "步骤1: Source环境..."
source /opt/ros/humble/setup.bash
source install/setup.bash
echo ""

echo "步骤2: 设置Gazebo路径..."
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(pwd)/install/dog2_description/share
echo "  GAZEBO_MODEL_PATH已设置"
echo ""

echo "步骤3: 启动Gazebo..."
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_dog2.launch.py
