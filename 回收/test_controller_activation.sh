#!/bin/bash
# 测试控制器激活

echo "=========================================="
echo "测试控制器激活"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "1. 检查硬件接口..."
ros2 control list_hardware_interfaces

echo ""
echo "2. 检查控制器状态..."
ros2 control list_controllers

echo ""
echo "3. 尝试配置 joint_trajectory_controller..."
ros2 control set_controller_state joint_trajectory_controller configure

echo ""
echo "4. 再次检查控制器状态..."
ros2 control list_controllers

echo ""
echo "5. 尝试激活 joint_trajectory_controller..."
ros2 control set_controller_state joint_trajectory_controller start

echo ""
echo "6. 最终控制器状态..."
ros2 control list_controllers
