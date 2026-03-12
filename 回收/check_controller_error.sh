#!/bin/bash
# 检查控制器错误详情

echo "=========================================="
echo "检查控制器详细信息"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 控制器列表和状态："
echo "-------------------------------------------"
ros2 control list_controllers
echo ""

echo "2. 控制器硬件接口："
echo "-------------------------------------------"
ros2 control list_hardware_interfaces
echo ""

echo "3. joint_trajectory_controller 配置："
echo "-------------------------------------------"
ros2 param list /controller_manager 2>/dev/null | grep joint_trajectory
echo ""

echo "4. 尝试获取控制器详细信息："
echo "-------------------------------------------"
ros2 control list_controller_types 2>/dev/null
echo ""

echo "=========================================="
echo "诊断建议"
echo "=========================================="
echo ""
echo "请查看 Gazebo 启动终端的日志，寻找："
echo "  - [ERROR] 开头的错误信息"
echo "  - joint_trajectory_controller 相关的错误"
echo "  - 'Not acceptable command interfaces' 错误"
echo ""
echo "如果看到关节名称错误，说明配置文件还没有生效"
echo "需要重新编译并重启系统"
