#!/bin/bash
# 简单测试 URDF 是否能在 RViz 中显示

source install/setup.bash

echo "测试 URDF 编译..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf 2>&1

if [ $? -eq 0 ]; then
    echo "✓ URDF 编译成功"
    echo "Link 数量: $(grep -c '<link name=' /tmp/dog2_test.urdf)"
    echo "Joint 数量: $(grep -c '<joint name=' /tmp/dog2_test.urdf)"
    
    echo ""
    echo "启动 RViz..."
    ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat /tmp/dog2_test.urdf)" &
    RSP_PID=$!
    sleep 2
    
    ros2 run joint_state_publisher_gui joint_state_publisher_gui &
    JSP_PID=$!
    sleep 2
    
    rviz2 &
    RVIZ_PID=$!
    
    echo ""
    echo "进程已启动:"
    echo "  robot_state_publisher: $RSP_PID"
    echo "  joint_state_publisher_gui: $JSP_PID"
    echo "  rviz2: $RVIZ_PID"
    echo ""
    echo "在 RViz 中："
    echo "1. Add -> RobotModel"
    echo "2. Fixed Frame: base_link"
    echo ""
    echo "按 Ctrl+C 停止"
    
    wait $RVIZ_PID
    kill $RSP_PID $JSP_PID 2>/dev/null
else
    echo "✗ URDF 编译失败"
    cat /tmp/dog2_test.urdf
fi
