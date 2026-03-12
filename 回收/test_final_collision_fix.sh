#!/bin/bash
# 最终碰撞修复测试

echo "=========================================="
echo "  最终碰撞修复测试"
echo "=========================================="
echo ""
echo "修复方案:"
echo "  ✅ 移除小腿碰撞几何体"
echo "  ✅ 只保留脚部球体碰撞"
echo "  ✅ 降低接触刚度 kp: 1000000 → 10000"
echo "  ✅ 降低阻尼系数 kd: 100 → 10"
echo ""
echo "原理:"
echo "  • 小腿不需要碰撞检测"
echo "  • 脚部球体处理所有地面接触"
echo "  • 避免小腿-脚部碰撞冲突"
echo "  • 更低的刚度提高数值稳定性"
echo ""
echo "预期效果:"
echo "  ✓ 机器人平稳落地"
echo "  ✓ 无异常抖动"
echo "  ✓ 无'飞走'或'爆炸'现象"
echo "  ✓ 稳定站立"
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
