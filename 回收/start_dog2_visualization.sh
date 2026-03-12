#!/bin/bash
# Dog2 可视化快速启动脚本

echo "========================================="
echo "  Dog2 机器人可视化系统"
echo "========================================="
echo ""
echo "正在启动："
echo "  ✓ Gazebo 仿真环境"
echo "  ✓ MPC 控制器"
echo "  ✓ WBC 控制器"
echo "  ✓ 可视化节点"
echo "  ✓ RViz2"
echo ""
echo "模式: 行走模式 (walking)"
echo ""
echo "启动后，在新终端中发送速度命令："
echo "  ros2 topic pub /cmd_vel geometry_msgs/Twist \"{linear: {x: 0.1}}\""
echo ""
echo "========================================="
echo ""

# Source环境
source install/setup.bash

# 启动可视化系统
ros2 launch dog2_visualization visualization.launch.py mode:=walking
