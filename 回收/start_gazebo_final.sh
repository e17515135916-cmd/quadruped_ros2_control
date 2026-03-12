#!/bin/bash

# Dog2 Gazebo越障仿真 - 最终版（已修复mesh路径问题）

echo "=========================================="
echo "  Dog2 MPC+WBC 越障仿真 - 最终版"
echo "=========================================="
echo ""
echo "修复内容："
echo "  ✅ 设置GAZEBO_MODEL_PATH"
echo "  ✅ 设置GAZEBO_RESOURCE_PATH"
echo "  ✅ 机器人模型可见"
echo ""

cd /home/dell/aperfect/carbot_ws

echo "步骤1: 重新编译launch文件..."
colcon build --packages-select dog2_mpc
echo ""

echo "步骤2: Source环境..."
source install/setup.bash
echo ""

echo "步骤3: 设置Gazebo路径..."
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(pwd)/src/dog2_description
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:$(pwd)/src/dog2_description
echo "  GAZEBO_MODEL_PATH已设置"
echo ""

echo "步骤4: 启动仿真..."
echo ""
echo "预期结果："
echo "  1. Gazebo窗口打开"
echo "  2. Dog2机器人出现（完整模型可见）"
echo "  3. MPC和WBC节点运行"
echo "  4. 机器人保持悬停"
echo ""
echo "触发越障："
echo "  在新终端运行："
echo "  ros2 topic pub --once /enable_crossing std_msgs/Bool \"data: true\""
echo ""
echo "=========================================="
echo ""

ros2 launch dog2_mpc simple_crossing_sim.launch.py

