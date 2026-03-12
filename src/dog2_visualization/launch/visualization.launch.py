#!/usr/bin/env python3
"""
Complete Dog2 Visualization Launch File

Launches:
1. Gazebo simulation
2. MPC controller
3. WBC controller  
4. Visualization node
5. RViz2 (optional)

Usage:
  # Walking mode with RViz2
  ros2 launch dog2_visualization visualization.launch.py mode:=walking

  # Crossing mode
  ros2 launch dog2_visualization visualization.launch.py mode:=crossing
  
  # Without RViz2
  ros2 launch dog2_visualization visualization.launch.py mode:=walking rviz:=false
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
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
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    # Get package directories
    dog2_mpc_dir = get_package_share_directory('dog2_mpc')
    dog2_viz_dir = get_package_share_directory('dog2_visualization')
    
    # Include complete simulation launch (Gazebo + MPC + WBC)
    complete_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(dog2_mpc_dir, 'launch', 'complete_simulation.launch.py')
        ),
        launch_arguments={
            'mode': LaunchConfiguration('mode'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )
    
    # Visualization node
    visualization_node = Node(
        package='dog2_visualization',
        executable='visualization_node.py',
        name='visualization_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
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
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen'
    )
    
    return LaunchDescription([
        # Arguments
        declare_mode,
        declare_rviz,
        declare_use_sim_time,
        
        # Nodes
        complete_sim_launch,
        visualization_node,
        rviz_node,
    ])
