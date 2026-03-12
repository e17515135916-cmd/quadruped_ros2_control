#!/usr/bin/env python3
"""
Dog2 Gazebo测试启动文件 - 使用修复后的URDF
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # 获取包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    
    # 使用 xacro 生成 robot_description（统一入口，不再读取 dog2.urdf）
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description = robot_description_config.toxml()
    
    # 启动Gazebo（空世界）
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 
                        'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'verbose': 'true'}.items()
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_description
        }]
    )
    
    # Spawn机器人到Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'dog2',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'  # 悬空0.5米，避免初始碰撞
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
