#!/usr/bin/env python3
"""
RViz verification script for hip joint axis change (Z to X).

This script launches RViz with the modified robot model to verify:
1. Hip joints (j11, j21, j31, j41) rotate about X-axis (forward/backward)
2. Visual appearance remains unchanged
3. Joint control works correctly

Requirements validated: 6.1, 6.2, 6.5, 2.3
"""

from launch import LaunchDescription
from launch_ros.actions import Node
import os
import subprocess


def generate_launch_description():
    """Generate launch description for RViz verification."""
    
    # Path to the xacro file (will be processed to URDF)
    xacro_path = os.path.join(os.getcwd(), 'src/dog2_description/urdf/dog2.urdf.xacro')
    
    # Process xacro to URDF
    try:
        result = subprocess.run(
            ['xacro', xacro_path],
            capture_output=True,
            text=True,
            check=True
        )
        robot_description_content = result.stdout
        print("✓ Successfully processed xacro to URDF")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error processing xacro: {e}")
        print(f"  stderr: {e.stderr}")
        raise
    
    # Robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen'
    )
    
    # Joint state publisher GUI node for manual testing
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )
    
    # RViz2 node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )
    
    print("\n" + "="*70)
    print("Hip Joint Axis Verification in RViz")
    print("="*70)
    print("\nInstructions:")
    print("1. RViz will open with the robot model")
    print("2. Add 'RobotModel' display if not already present")
    print("3. Use the joint_state_publisher_gui sliders to test hip joints:")
    print("   - j11 (Front Left Hip)")
    print("   - j21 (Front Right Hip)")
    print("   - j31 (Rear Left Hip)")
    print("   - j41 (Rear Right Hip)")
    print("\nExpected behavior:")
    print("✓ Hip joints should rotate FORWARD/BACKWARD (about X-axis)")
    print("✓ Visual appearance should be unchanged")
    print("✓ Joint limits: ±150° (±2.618 rad)")
    print("\nPrevious behavior (for comparison):")
    print("✗ Hip joints rotated LEFT/RIGHT (about Z-axis)")
    print("="*70 + "\n")
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node
    ])


if __name__ == '__main__':
    generate_launch_description()
