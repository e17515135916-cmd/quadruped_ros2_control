#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')

    spawn_z_arg = DeclareLaunchArgument(
        'spawn_z',
        default_value='1.0',
        description='Spawn height for free-fall drop test (m)'
    )

    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )

    xacro_file = PathJoinSubstitution([
        FindPackageShare('dog2_description'),
        'urdf', 'dog2.urdf.xacro'
    ])
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    world_file = '/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf'
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true'
        }.items()
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'dog2',
            '-z', LaunchConfiguration('spawn_z')
        ],
        output='screen'
    )

    return LaunchDescription([
        spawn_z_arg,
        set_gazebo_model_path,
        gazebo,
        rsp,
        spawn_entity,
    ])
