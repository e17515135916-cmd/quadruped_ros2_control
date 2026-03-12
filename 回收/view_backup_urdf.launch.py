#!/usr/bin/env python3
"""
启动文件：在RViz2中查看备份的URDF
文件: backups/before_restore_20260202_150821/dog2.urdf.xacro
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # 获取当前工作目录
    workspace_dir = os.getcwd()
    backup_xacro = os.path.join(workspace_dir, 'backups/before_restore_20260202_150821/dog2.urdf.xacro')
    
    # 检查文件是否存在
    if not os.path.exists(backup_xacro):
        raise FileNotFoundError(f"找不到备份文件: {backup_xacro}")
    
    print(f"正在加载备份URDF: {backup_xacro}")
    
    # 处理xacro文件
    robot_description = ParameterValue(
        Command(['xacro ', backup_xacro]),
        value_type=str
    )
    
    # Robot State Publisher节点
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }]
    )
    
    # Joint State Publisher节点（带GUI）
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{
            'use_sim_time': False
        }]
    )
    
    # RViz2节点
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(workspace_dir, 'config.rviz')] if os.path.exists(os.path.join(workspace_dir, 'config.rviz')) else []
    )
    
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
