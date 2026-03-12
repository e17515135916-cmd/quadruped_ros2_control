#!/bin/bash
# 测试缩水大法修复效果

echo "=========================================="
echo "  缩水大法测试（Scale Down Fix）"
echo "=========================================="
echo ""
echo "修复方案:"
echo "  ✅ 碰撞网格缩小10% (scale=0.9)"
echo "  ✅ 视觉模型保持原样"
echo "  ✅ 在关节处创造间隙"
echo ""
echo "原理:"
echo "  • 大腿和小腿的碰撞体都缩小10%"
echo "  • 在膝关节处自动产生间隙"
echo "  • 防止物理引擎检测到重叠"
echo "  • 视觉上看起来完全正常"
echo ""
echo "优点:"
echo "  ✓ 不需要修改STL文件"
echo "  ✓ 不需要计算origin偏移"
echo "  ✓ 一行代码解决问题"
echo "  ✓ 工程师常用的'急救'方案"
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
echo "  ✓ 是否还会'飞走'"
echo "  ✓ 腿部运动是否流畅"
echo ""
echo "如果还有问题，可以进一步缩小到0.85或0.8"
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_description gazebo_dog2.launch.py
