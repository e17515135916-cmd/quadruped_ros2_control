#!/bin/bash
# 使用正确的xacro源文件启动RViz2

source install/setup.bash

# 生成URDF
echo "生成URDF..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_current.urdf

if [ $? -ne 0 ]; then
    echo "错误: xacro处理失败"
    exit 1
fi

echo "URDF已生成到 /tmp/dog2_current.urdf"

# 验证足端关节
echo ""
echo "验证足端关节偏移:"
grep -A 2 'joint name="j[1-4]1111"' /tmp/dog2_current.urdf | grep "origin"

echo ""
echo "启动robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat /tmp/dog2_current.urdf)" &
RSP_PID=$!
sleep 2

echo "启动joint_state_publisher_gui..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!
sleep 1

echo "启动RViz2..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "✓ 所有进程已启动"
echo "  robot_state_publisher: PID $RSP_PID"
echo "  joint_state_publisher_gui: PID $JSP_PID"
echo "  rviz2: PID $RVIZ_PID"
echo ""
echo "在RViz2中添加RobotModel显示，Fixed Frame设置为'base_link'"
echo ""
echo "按Ctrl+C停止所有进程..."

# 等待
wait $RVIZ_PID
kill $RSP_PID $JSP_PID 2>/dev/null
