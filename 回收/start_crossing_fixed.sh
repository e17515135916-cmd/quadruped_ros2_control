#!/bin/bash

# Dog2 越障仿真 - 修复版（设置正确的模型路径）

echo "=========================================="
echo "  Dog2 MPC+WBC 越障仿真（修复版）"
echo "=========================================="
echo ""

cd /home/dell/aperfect/carbot_ws
source install/setup.bash

echo "步骤1: 设置Gazebo模型路径..."
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(pwd)/src/dog2_description
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:$(pwd)/src/dog2_description

echo "  GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH"
echo ""

echo "步骤2: 启动仿真..."
echo ""

ros2 launch dog2_mpc simple_crossing_sim.launch.py

