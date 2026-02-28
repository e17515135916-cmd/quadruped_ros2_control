#!/usr/bin/env python3
"""
Dog2 MPC + WBC 完整闭环仿真启动文件

功能：
1. 启动Gazebo仿真环境
2. 加载Dog2机器人模型
3. 启动16维MPC控制器
4. 启动简化WBC控制器
5. 启动状态发布器

使用方法：
ros2 launch dog2_mpc mpc_wbc_simulation.launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 声明参数
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    declare_mpc_horizon = DeclareLaunchArgument(
        'mpc_horizon',
        default_value='10',
        description='MPC prediction horizon'
    )
    
    declare_mpc_dt = DeclareLaunchArgument(
        'mpc_dt',
        default_value='0.05',
        description='MPC time step (seconds)'
    )
    
    declare_control_freq = DeclareLaunchArgument(
        'control_frequency',
        default_value='20.0',
        description='Control loop frequency (Hz)'
    )
    
    declare_enable_sliding = DeclareLaunchArgument(
        'enable_sliding_constraints',
        default_value='true',
        description='Enable sliding joint constraints in MPC'
    )
    
    # Gazebo启动
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'verbose': 'false'}.items()
    )
    
    # 加载Dog2 URDF
    panda_desc_pkg = get_package_share_directory('panda_description')
    urdf_file = os.path.join(panda_desc_pkg, 'urdf', 'dog2.urdf')
    
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': robot_description
        }]
    )
    
    # Spawn Dog2 in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'dog2',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'  # 初始高度50cm
        ],
        output='screen'
    )
    
    # 16维MPC节点
    mpc_node_16d = Node(
        package='dog2_mpc',
        executable='mpc_node_16d',
        name='mpc_node_16d',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'mass': 7.94,
            'horizon': LaunchConfiguration('mpc_horizon'),
            'dt': LaunchConfiguration('mpc_dt'),
            'control_frequency': LaunchConfiguration('control_frequency'),
            'enable_sliding_constraints': LaunchConfiguration('enable_sliding_constraints'),
            'enable_boundary_constraints': False
        }]
    )
    
    # 简化WBC节点
    wbc_node_simple = Node(
        package='dog2_wbc',
        executable='wbc_node_simple',
        name='wbc_node_simple',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )
    
    return LaunchDescription([
        # 参数声明
        declare_use_sim_time,
        declare_mpc_horizon,
        declare_mpc_dt,
        declare_control_freq,
        declare_enable_sliding,
        
        # 启动节点
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        mpc_node_16d,
        wbc_node_simple,
    ])
