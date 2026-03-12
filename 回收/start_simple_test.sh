#!/bin/bash

# 最简单的Dog2 Gazebo测试

echo "=========================================="
echo "  Dog2 最简单Gazebo测试"
echo "=========================================="
echo ""

cd /home/dell/aperfect/carbot_ws
source install/setup.bash

echo "步骤1: 重新编译（确保最新代码）..."
colcon build --packages-select dog2_mpc dog2_description

echo ""
echo "步骤2: 重新source环境..."
source install/setup.bash

echo ""
echo "步骤3: 启动简化仿真..."
echo ""

ros2 launch dog2_mpc simple_crossing_sim.launch.py

