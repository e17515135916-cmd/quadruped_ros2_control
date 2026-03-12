#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
import os


def generate_launch_description():
    # Path to the modified URDF
    urdf_path = os.path.join(os.getcwd(), 'src/dog2_description/urdf/dog2_modified.urdf')
    
    # Read URDF content
    with open(urdf_path, 'r') as infp:
        robot_description_content = infp.read()
    
    # Robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen'
    )
    
    # Joint state publisher GUI node
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )
    
    # RViz2 node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node
    ])


if __name__ == '__main__':
    generate_launch_description()