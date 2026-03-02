#!/usr/bin/env python3
"""
蜘蛛机器人完整仿真启动文件

功能：
1. 启动 Gazebo Fortress 仿真环境
2. 加载 Dog2 机器人模型
3. 启动 ros2_control 控制器
4. 启动蜘蛛机器人运动控制节点

使用方法：
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py

可选参数：
- config_file: 步态参数配置文件路径
- use_gui: 是否启动Gazebo GUI (默认: true)
- world: 世界文件路径 (默认: empty.sdf)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    RegisterEventHandler,
    DeclareLaunchArgument,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition
import xacro


def generate_launch_description():
    """生成启动描述"""
    
    # 获取包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_motion_control = get_package_share_directory('dog2_motion_control')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    
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
    
    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='是否启动Gazebo GUI'
    )
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf',
        description='Gazebo世界文件路径'
    )
    
    # 配置文件路径
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    
    # 设置Gazebo模型路径环境变量
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )
    
    # 处理xacro文件生成URDF
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # 启动Gazebo Fortress
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': [
                '-r ',
                LaunchConfiguration('world'),
                ' ',
                # 根据use_gui参数决定是否添加-s标志（无头模式）
            ],
            'on_exit_shutdown': 'true'
        }.items(),
        condition=IfCondition(LaunchConfiguration('use_gui'))
    )
    
    # 无GUI模式的Gazebo
    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': [
                '-r -s ',
                LaunchConfiguration('world'),
            ],
            'on_exit_shutdown': 'true'
        }.items(),
        condition=UnlessCondition(LaunchConfiguration('use_gui'))
    )
    
    # Robot State Publisher节点
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )
    
    # 在Gazebo中生成机器人
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'dog2',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5',  # 在地面上方0.5米生成，避免穿模
        ],
        output='screen'
    )
    
    # 加载Joint State Broadcaster
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    
    # 加载Joint Trajectory Controller（控制12个旋转关节）
    load_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )
    
    # 加载Rail Position Controller（控制4个导轨关节，锁定在0.0）
    load_rail_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rail_position_controller'],
        output='screen'
    )
    
    # 启动蜘蛛机器人运动控制节点
    spider_controller_node = Node(
        package='dog2_motion_control',
        executable='spider_controller',
        name='spider_robot_controller',
        output='screen',
        parameters=[
            LaunchConfiguration('config_file'),
            {'use_sim_time': True}  # 使用仿真时间
        ],
    )
    
    return LaunchDescription([
        # 声明参数
        config_file_arg,
        use_gui_arg,
        world_arg,
        
        # 设置环境变量
        set_gazebo_model_path,
        
        # 启动Gazebo
        gazebo,
        gazebo_headless,
        
        # 启动Robot State Publisher
        robot_state_publisher,
        
        # 生成机器人
        spawn_entity,
        
        # 等待机器人生成后再加载控制器和运动控制节点
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[
                    load_joint_state_broadcaster,
                    load_joint_trajectory_controller,
                    load_rail_position_controller,
                    spider_controller_node,  # 在控制器加载后启动运动控制节点
                ],
            )
        ),
    ])
