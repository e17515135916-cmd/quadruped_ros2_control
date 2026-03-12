#!/bin/bash
# 最简单的 RViz 测试方法

set -e

echo "=========================================="
echo "CHAMP 配置 RViz2 测试"
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
echo "✅ URDF 已生成"
echo ""

# 创建临时 launch 文件
cat > /tmp/champ_rviz_launch.py << 'EOF'
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    # 读取 URDF
    with open('/tmp/dog2_champ.urdf', 'r') as f:
        robot_desc = f.read()
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        )
    ])
EOF

echo "启动 RViz2..."
echo ""
echo "在 RViz2 中："
echo "1. 点击 'Add' → 选择 'RobotModel'"
echo "2. 设置 Fixed Frame 为 'base_link'"
echo "3. 使用 GUI 窗口控制关节"
echo ""

ros2 launch /tmp/champ_rviz_launch.py

echo ""
echo "完成！"
