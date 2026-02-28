#!/usr/bin/env python3
"""
Dog2 简化越障仿真启动文件

使用dog2_visual.urdf（包含完整Gazebo插件）
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # 使用带Gazebo插件的URDF
    panda_desc_pkg = get_package_share_directory('panda_description')
    urdf_file = os.path.join(panda_desc_pkg, 'urdf', 'dog2_visual.urdf')
    
    # 设置Gazebo模型路径（关键修复！）
    panda_desc_src = os.path.join(os.getcwd(), 'src', 'panda_description')
    gazebo_model_path = SetEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        panda_desc_src + ':' + os.environ.get('GAZEBO_MODEL_PATH', '')
    )
    gazebo_resource_path = SetEnvironmentVariable(
        'GAZEBO_RESOURCE_PATH', 
        panda_desc_src + ':' + os.environ.get('GAZEBO_RESOURCE_PATH', '')
    )
    
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    # 启动Gazebo
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description
        }]
    )
    
    # Spawn Dog2
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'dog2',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )
    
    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # MPC节点（完整版）
    mpc_node = Node(
        package='dog2_mpc',
        executable='mpc_node_complete',
        name='mpc_node_complete',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mass': 11.8,
            'horizon': 10,
            'dt': 0.05,
            'control_frequency': 20.0,
            'enable_sliding_constraints': True,
            'mode': 'crossing'
        }]
    )
    
    # WBC节点（完整版）
    wbc_node = Node(
        package='dog2_wbc',
        executable='wbc_node_complete',
        name='wbc_node_complete',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'l1': 0.2,
            'l2': 0.2,
            'max_torque': 50.0,
            'max_sliding_force': 100.0
        }]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo_model_path,  # 设置模型路径
        gazebo_resource_path,  # 设置资源路径
        gazebo,
        robot_state_publisher,
        spawn_entity,
        joint_state_publisher,
        mpc_node,
        wbc_node,
    ])
