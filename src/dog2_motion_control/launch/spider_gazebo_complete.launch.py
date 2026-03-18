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
    TimerAction,
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
            '-z', '0.3',  # 在地面上方0.3米生成，减少落地冲击
        ],
        output='screen'
    )
    
    # 加载Joint State Broadcaster
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '-c', '/controller_manager',
            '-t', 'joint_state_broadcaster/JointStateBroadcaster',
            '--param-file', controllers_yaml,
            '--controller-manager-timeout', '120',
        ],
        output='screen'
    )
    
    # 加载Joint Trajectory Controller（控制12个旋转关节）
    load_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_trajectory_controller',
            '-c', '/controller_manager',
            '-t', 'joint_trajectory_controller/JointTrajectoryController',
            '--param-file', controllers_yaml,
            '--controller-manager-timeout', '120',
        ],
        output='screen'
    )

    # 加载Rail Position Controller（控制4个导轨关节）
    load_rail_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'rail_position_controller',
            '-c', '/controller_manager',
            '-t', 'joint_trajectory_controller/JointTrajectoryController',
            '--param-file', controllers_yaml,
            '--controller-manager-timeout', '120',
        ],
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
            {'use_sim_time': False, 'debug_mode': True}
        ],
    )

    # 延迟启动 Joint State Broadcaster，等待 Gazebo 内部的 controller_manager 就绪
    delayed_joint_state_broadcaster = TimerAction(
        period=10.0,
        actions=[load_joint_state_broadcaster],
    )

    # Joint State Broadcaster 启动后再启动轨迹控制器
    start_joint_trajectory = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_joint_trajectory_controller],
        )
    )

    # 轨迹控制器启动后再启动导轨控制器
    start_rail_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_trajectory_controller,
            on_exit=[load_rail_position_controller],
        )
    )

    # 导轨控制器启动后再启动主控制节点
    start_remaining_nodes = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_rail_position_controller,
            on_exit=[
                spider_controller_node,
            ],
        )
    )

    # spawner 指定唯一 controller_manager 名称，避免重复同名节点冲突
    set_controller_manager_name = SetEnvironmentVariable(
        name='RCUTILS_LOGGING_USE_STDOUT',
        value='1'
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
                    delayed_joint_state_broadcaster,
                ],
            )
        ),
        start_joint_trajectory,
        start_rail_controller,
        start_remaining_nodes,
    ])
