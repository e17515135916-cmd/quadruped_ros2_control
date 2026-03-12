#!/bin/bash
# 测试凸包碰撞网格的Gazebo仿真（简单版本）

echo "=========================================="
echo "  凸包碰撞网格 Gazebo 测试"
echo "=========================================="
echo ""
echo "测试目标："
echo "  ✓ 验证凸包碰撞网格是否正常工作"
echo "  ✓ 检查是否解决'量子爆炸'问题"
echo "  ✓ 确认机器人稳定性"
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
echo "观察要点："
echo "  1. 机器人是否正常生成（高度1米）"
echo "  2. 落地时是否稳定"
echo "  3. 是否出现'飞走'或'爆炸'现象"
echo "  4. 腿部是否有异常抖动"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_dog2.launch.py
