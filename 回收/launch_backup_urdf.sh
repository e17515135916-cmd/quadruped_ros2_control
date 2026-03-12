#!/bin/bash
# Launch RViz with backup URDF from back2.1

echo "=========================================="
echo "Launching RViz with Backup URDF"
echo "=========================================="

BACKUP_URDF="/home/dell/aperfect/carbot_ws/backups/back2.1/dog3_description/urdf/dog2.urdf.xacro"

if [ ! -f "$BACKUP_URDF" ]; then
    echo "❌ Backup URDF not found: $BACKUP_URDF"
    exit 1
fi

echo "Using URDF: $BACKUP_URDF"
echo ""

# Source ROS 2 environment
source /opt/ros/humble/setup.bash
source install/setup.bash

# Generate URDF from backup xacro
echo "Generating URDF from backup xacro..."
xacro "$BACKUP_URDF" > /tmp/dog2_backup.urdf

if [ $? -ne 0 ]; then
    echo "❌ Error generating URDF from backup"
    exit 1
fi

echo "✓ URDF generated successfully"
echo ""

# Create temporary launch file
cat > /tmp/view_backup_urdf.launch.py << 'EOF'
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    urdf_file = '/tmp/dog2_backup.urdf'
    
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
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
            output='screen',
            arguments=['-d', os.path.join(os.environ.get('HOME', '/home/dell'), 
                                         'aperfect/carbot_ws/install/dog2_description/share/dog2_description/rviz/dog2.rviz')]
        )
    ])
EOF

echo "Starting RViz with backup URDF..."
echo ""

ros2 launch /tmp/view_backup_urdf.launch.py

echo ""
echo "RViz closed."
