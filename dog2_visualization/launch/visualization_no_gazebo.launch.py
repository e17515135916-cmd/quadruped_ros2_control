#!/usr/bin/env python3
"""
Dog2 Visualization Launch File (Without Gazebo)

使用状态模拟器代替 Gazebo，更轻量级

Launches:
1. State simulator (代替 Gazebo)
2. MPC controller
3. WBC controller  
4. Visualization node
5. RViz2 (optional)

Usage:
  ros2 launch dog2_visualization visualization_no_gazebo.launch.py mode:=walking
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Declare arguments
    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='walking',
        description='Control mode: hover, walking, or crossing'
    )
    
    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2'
    )
    
    # Get package directories
    dog2_viz_dir = get_package_share_directory('dog2_visualization')
    panda_desc_dir = get_package_share_directory('panda_description')
    
    # Load URDF
    urdf_file = os.path.join(panda_desc_dir, 'urdf', 'dog2.urdf')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
    )
    
    # Static TF: world -> odom
    static_tf_world_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_world_odom',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom']
    )
    
    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )
    
    # State Simulator (代替 Gazebo)
    state_simulator = Node(
        package='dog2_mpc',
        executable='state_simulator',
        name='state_simulator',
        output='screen'
    )
    
    # MPC Node
    mpc_node = Node(
        package='dog2_mpc',
        executable='mpc_node_complete',
        name='mpc_node_complete',
        output='screen',
        parameters=[{
            'mass': 7.94,
            'horizon': 10,
            'dt': 0.05,
            'control_frequency': 20.0,
            'enable_sliding_constraints': True,
            'mode': LaunchConfiguration('mode')
        }]
    )
    
    # WBC Node
    wbc_node = Node(
        package='dog2_wbc',
        executable='wbc_node_complete',
        name='wbc_node_complete',
        output='screen',
        parameters=[{
            'l1': 0.2,
            'l2': 0.2,
            'max_torque': 50.0,
            'max_sliding_force': 100.0
        }]
    )
    
    # Visualization node (直接运行 Python 模块)
    visualization_node = Node(
        package='dog2_visualization',
        executable='python3',
        name='visualization_node',
        output='screen',
        arguments=['-m', 'dog2_visualization.visualization_node'],
        parameters=[{
            'update_rate': 20.0,
        }]
    )
    
    # RViz2 configuration file
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('dog2_visualization'),
        'config', 'rviz', 'dog2_walking.rviz'
    ])
    
    # RViz2 node (conditional)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen'
    )
    
    return LaunchDescription([
        # Arguments
        declare_mode,
        declare_rviz,
        
        # Nodes
        robot_state_publisher,
        static_tf_world_odom,
        joint_state_publisher,
        state_simulator,
        mpc_node,
        wbc_node,
        visualization_node,
        rviz_node,
    ])
