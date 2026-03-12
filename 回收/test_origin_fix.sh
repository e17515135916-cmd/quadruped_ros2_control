#!/bin/bash
# 测试Origin修复效果

echo "=========================================="
echo "  Origin修复测试"
echo "=========================================="
echo ""
echo "修复内容:"
echo "  ✅ 大腿碰撞origin修正为几何中心"
echo "  ✅ 小腿碰撞已移除（避免冲突）"
echo "  ✅ 脚部接触刚度降低 (kp=10000)"
echo ""
echo "原理:"
echo "  • Origin偏移防止关节处重叠"
echo "  • 移除小腿碰撞避免小腿-脚部冲突"
echo "  • 降低刚度提高数值稳定性"
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
echo "观察要点:"
echo "  ✓ 机器人是否平稳落地"
echo "  ✓ 大腿-小腿关节是否正常"
echo "  ✓ 是否还会'飞走'"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_dog2.launch.py
