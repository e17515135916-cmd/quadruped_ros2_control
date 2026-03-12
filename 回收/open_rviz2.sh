#!/bin/bash
# 启动 RViz2 查看机器人模型

echo "=========================================="
echo "启动 RViz2"
echo "=========================================="

# Source 环境
source install/setup.bash

# 启动 robot_state_publisher
echo "启动 robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(xacro src/dog2_description/urdf/dog2.urdf.xacro)" &
RSP_PID=$!

# 等待一下
sleep 2

# 启动 joint_state_publisher_gui
echo "启动 joint_state_publisher_gui..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!

# 等待一下
sleep 2

# 启动 RViz2
echo "启动 RViz2..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "=========================================="
echo "RViz2 已启动"
echo "=========================================="
echo ""
echo "在 RViz2 中："
echo "1. 点击 Add -> RobotModel"
echo "2. 设置 Fixed Frame 为 'base_link'"
echo "3. 在 joint_state_publisher_gui 中调整关节"
echo ""
echo "按 Ctrl+C 停止所有进程"
echo "=========================================="

# 等待用户中断
wait $RVIZ_PID

# 清理
echo "清理进程..."
kill $RSP_PID $JSP_PID 2>/dev/null
