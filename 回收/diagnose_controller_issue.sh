#!/bin/bash
# 完整诊断控制器问题

echo "=========================================="
echo "完整系统诊断"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "1. 检查 Gazebo 是否运行..."
if pgrep -f "gz sim" > /dev/null; then
    echo "✅ Gazebo 正在运行"
else
    echo "❌ Gazebo 未运行"
    echo ""
    echo "请先启动 Gazebo："
    echo "  ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py"
    exit 1
fi

echo ""
echo "2. 检查 ROS 2 节点..."
ros2 node list

echo ""
echo "3. 检查 controller_manager 是否存在..."
if ros2 node list | grep -q "/controller_manager"; then
    echo "✅ controller_manager 正在运行"
else
    echo "❌ controller_manager 未运行"
    echo "   这说明 Gazebo ros2_control 插件没有正确加载"
    exit 1
fi

echo ""
echo "4. 检查硬件接口..."
ros2 control list_hardware_interfaces

echo ""
echo "5. 检查控制器列表..."
ros2 control list_controllers

echo ""
echo "6. 检查控制器配置..."
ros2 param list /controller_manager | grep joint_trajectory_controller

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
