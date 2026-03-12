#!/usr/bin/env python3
"""
Dog2 Gazebo Fortress 自动站立启动文件

功能：
1. 启动 Gazebo Fortress 仿真环境
2. 加载 Dog2 机器人模型
3. 启动 ros2_control 控制器
4. 自动发送站立姿态命令

使用方法：
ros2 launch dog2_description dog2_fortress_auto_stand.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, 
    SetEnvironmentVariable, 
    RegisterEventHandler,
    TimerAction
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    
    # 设置环境变量
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )
    
    # 处理 xacro 文件
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # 世界文件路径
    world_file = '/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf'
    
    # 启动 Gazebo Fortress
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true'
        }.items()
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )
    
    # Spawn 机器人（高度设置为 0.6m，给站立留出空间）
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'dog2',
            '-z', '0.6'  # 提高初始高度
        ],
        output='screen'
    )
    
    # 加载 Joint State Broadcaster
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    
    # 加载 Joint Trajectory Controller（控制 3 个旋转关节）
    load_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )
    
    # 加载 Rail Position Controller（控制 4 个移动关节，锁定导轨）
    load_rail_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rail_position_controller'],
        output='screen'
    )
    
    # 自动站立节点（在控制器加载后 2 秒启动）
    auto_stand_node = Node(
        package='dog2_description',
        executable='auto_stand_node.py',
        name='auto_stand_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        
        # 等待机器人生成后再加载控制器
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[
                    load_joint_state_broadcaster,
                    load_joint_trajectory_controller,
                    load_rail_position_controller,  # 添加导轨控制器
                    # 控制器加载后等待 3 秒再发送站立命令
                    TimerAction(
                        period=3.0,
                        actions=[auto_stand_node]
                    )
                ],
            )
        ),
    ])
