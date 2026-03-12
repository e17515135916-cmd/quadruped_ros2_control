#!/bin/bash
# 检查 Gazebo 启动日志中的错误

echo "=========================================="
echo "检查 Gazebo 日志"
echo "=========================================="
echo ""

echo "请在另一个终端启动 Gazebo："
echo "  ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py"
echo ""
echo "然后按 Enter 继续..."
read

echo ""
echo "检查 controller_manager 日志..."
ros2 node info /controller_manager 2>&1 | head -20

echo ""
echo "检查硬件接口..."
ros2 control list_hardware_interfaces

echo ""
echo "检查控制器状态..."
ros2 control list_controllers

echo ""
echo "尝试激活 joint_trajectory_controller..."
ros2 control set_controller_state joint_trajectory_controller start 2>&1 | head -10
