#!/usr/bin/env python3
"""
Dog2 完整功能仿真启动文件

功能：
1. Gazebo仿真环境
2. 完整MPC控制器（行走+越障）
3. WBC控制器
4. 参考轨迹生成
5. 足端接触检测

使用方法：
# 悬停模式
ros2 launch dog2_mpc complete_simulation.launch.py mode:=hover

# 行走模式
ros2 launch dog2_mpc complete_simulation.launch.py mode:=walking

# 越障模式
ros2 launch dog2_mpc complete_simulation.launch.py mode:=crossing
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 参数声明
    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='hover',
        description='Control mode: hover, walking, or crossing'
    )
    
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
    
    declare_control_freq = DeclareLaunchArgument(
        'control_frequency',
        default_value='20.0',
        description='Control loop frequency (Hz)'
    )
    
    # Gazebo启动
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'verbose': 'false',
            'gui': 'true',
            'pause': 'false'
        }.items()
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
            '-z', '0.5'
        ],
        output='screen'
    )
    
    # 完整MPC节点
    mpc_node_complete = Node(
        package='dog2_mpc',
        executable='mpc_node_complete',
        name='mpc_node_complete',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'mass': 11.8,
            'horizon': LaunchConfiguration('mpc_horizon'),
            'dt': 0.05,
            'control_frequency': LaunchConfiguration('control_frequency'),
            'enable_sliding_constraints': True,
            'mode': LaunchConfiguration('mode')
        }]
    )
    
    # WBC节点（完整版）
    wbc_node_complete = Node(
        package='dog2_wbc',
        executable='wbc_node_complete',
        name='wbc_node_complete',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'l1': 0.2,
            'l2': 0.2,
            'max_torque': 50.0,
            'max_sliding_force': 100.0
        }]
    )
    
    # Static TF: world -> odom (固定变换)
    static_tf_world_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_world_odom',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom'],
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )
    
    # Static TF: odom -> base_link (由Gazebo的ground truth提供)
    # 这个变换会被Gazebo的p3d插件或odom插件覆盖
    static_tf_odom_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_odom_base',
        arguments=['0', '0', '0.5', '0', '0', '0', 'odom', 'base_link'],
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )
    
    # Joint State Publisher (发布默认关节状态)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )
    
    return LaunchDescription([
        # 参数
        declare_mode,
        declare_use_sim_time,
        declare_mpc_horizon,
        declare_control_freq,
        
        # 节点
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        static_tf_world_odom,
        static_tf_odom_base,
        joint_state_publisher,
        mpc_node_complete,
        wbc_node_complete,
    ])
