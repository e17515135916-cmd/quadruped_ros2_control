#!/usr/bin/env python3
"""
蜘蛛机器人完整仿真启动文件（带RViz可视化）

功能：
1. 启动 Gazebo Fortress 仿真环境
2. 加载 Dog2 机器人模型
3. 启动 ros2_control 控制器
4. 启动蜘蛛机器人运动控制节点
5. 启动 RViz2 可视化

使用方法：
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py

可选参数：
- config_file: 步态参数配置文件路径
- rviz_config: RViz配置文件路径
- world: 世界文件路径
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """生成启动描述"""
    
    # 获取包路径
    pkg_dog2_motion_control = get_package_share_directory('dog2_motion_control')
    
    # 声明启动参数
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('dog2_motion_control'),
            'config',
            'gait_params.yaml'
        ]),
        description='步态参数配置文件路径'
    )
    
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            FindPackageShare('dog2_motion_control'),
            'config',
            'spider_robot.rviz'
        ]),
        description='RViz配置文件路径'
    )
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf',
        description='Gazebo世界文件路径'
    )
    
    # 包含完整的Gazebo启动文件
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dog2_motion_control, 'launch', 'spider_gazebo_complete.launch.py')
        ),
        launch_arguments={
            'config_file': LaunchConfiguration('config_file'),
            'use_gui': 'true',
            'world': LaunchConfiguration('world'),
        }.items()
    )
    
    # 启动RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}]
    )
    
    return LaunchDescription([
        # 声明参数
        config_file_arg,
        rviz_config_arg,
        world_arg,
        
        # 启动Gazebo和控制器
        gazebo_launch,
        
        # 启动RViz
        rviz_node,
    ])
