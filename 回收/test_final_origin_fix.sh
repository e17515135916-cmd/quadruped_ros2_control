#!/bin/bash
# 最终Origin修复测试

echo "=========================================="
echo "  最终Origin修复测试"
echo "=========================================="
echo ""
echo "修复内容:"
echo "  ✅ 大腿collision origin: (0,0,0) → (0.026, -0.076, 0.065)"
echo "  ✅ 小腿collision: 已移除"
echo "  ✅ 脚部接触刚度: kp=10000, kd=10"
echo ""
echo "原理:"
echo "  • Origin偏移使碰撞体中心对齐几何中心"
echo "  • 防止大腿末端与膝关节处重叠"
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
echo "  ✓ 大腿-膝关节是否有重叠"
echo "  ✓ 是否还会'飞走'"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_dog2.launch.py
