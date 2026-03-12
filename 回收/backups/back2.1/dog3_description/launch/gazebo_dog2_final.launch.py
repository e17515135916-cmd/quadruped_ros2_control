#!/usr/bin/env python3
"""
Dog2 Gazebo 仿真启动文件 - 最终版本
使用标准的Gazebo ROS包启动方式
修复了 mesh 文件路径问题
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # 获取包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    
    # 关键修复：设置 Gazebo 模型路径环境变量
    # 这样 Gazebo 就能找到 package:// 路径中的 mesh 文件
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        gazebo_model_path = os.environ['GAZEBO_MODEL_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=gazebo_model_path
    )
    
    # 同时设置 Gazebo 资源路径
    gazebo_resource_path = pkg_dog2_description
    if 'GAZEBO_RESOURCE_PATH' in os.environ:
        gazebo_resource_path = os.environ['GAZEBO_RESOURCE_PATH'] + ':' + gazebo_resource_path
    
    set_gazebo_resource_path = SetEnvironmentVariable(
        name='GAZEBO_RESOURCE_PATH',
        value=gazebo_resource_path
    )
    
    # 世界文件路径（使用空世界）
    world_file = os.path.join(pkg_gazebo_ros, 'worlds', 'empty.world')
    
    # 处理xacro文件生成URDF
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # Gazebo启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # 启动Gazebo（使用标准的gzserver launch文件）
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file, 'verbose': 'true'}.items()
    )
    
    # 启动Gazebo客户端
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )
    
    # Robot State Publisher节点
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )
    
    # Spawn机器人实体
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'dog2',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        # 首先设置环境变量
        set_gazebo_model_path,
        set_gazebo_resource_path,
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        gazebo,
        gazebo_client,
        robot_state_publisher,
        spawn_entity,
    ])
