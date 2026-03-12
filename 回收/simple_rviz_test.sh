#!/bin/bash
# 简单的 RViz2 测试脚本 - 使用临时文件传递 URDF

echo "=========================================="
echo "启动 RViz2 测试 CHAMP 兼容配置"
echo "=========================================="
echo ""

# Source ROS 2
source /opt/ros/humble/setup.bash
if [ -d "install" ]; then
    source install/setup.bash
fi

# 生成 URDF
echo "生成 URDF..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_champ.urdf
echo "✅ URDF 已生成: /tmp/dog2_champ.urdf"
echo ""

# 启动 robot_state_publisher（使用文件）
echo "启动 robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="file:///tmp/dog2_champ.urdf" &
RSP_PID=$!
sleep 2

# 启动 joint_state_publisher_gui
echo "启动 joint_state_publisher_gui..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!
sleep 2

# 启动 RViz2
echo "启动 RViz2..."
echo ""
echo "在 RViz2 中："
echo "1. 点击左下角 'Add' 按钮"
echo "2. 选择 'RobotModel'"
echo "3. 在左侧面板设置 Fixed Frame 为 'base_link'"
echo "4. 使用 joint_state_publisher_gui 窗口控制关节"
echo ""
rviz2

# 清理
echo ""
echo "清理进程..."
kill $RSP_PID $JSP_PID 2>/dev/null
echo "完成！"
