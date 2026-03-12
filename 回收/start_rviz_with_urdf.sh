#!/bin/bash
# 使用生成的URDF文件启动RViz2

source install/setup.bash

URDF_FILE="src/dog2_description/urdf/dog2.urdf"

echo "使用URDF文件: $URDF_FILE"
echo ""

# 启动robot_state_publisher
echo "启动robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!
sleep 2

# 启动joint_state_publisher_gui
echo "启动joint_state_publisher_gui..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!
sleep 1

# 启动RViz2
echo "启动RViz2..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "✓ 所有进程已启动"
echo ""
echo "在RViz2中:"
echo "1. 点击左下角 'Add' 按钮"
echo "2. 选择 'RobotModel'"
echo "3. 设置 Fixed Frame 为 'base_link'"
echo ""
echo "按Ctrl+C停止..."

wait $RVIZ_PID
kill $RSP_PID $JSP_PID 2>/dev/null
