#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    controllers_yaml = os.path.join(
        pkg_dog2_description,
        'config',
        'ros2_controllers_spider_position.yaml'
    )

    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )

    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={'controllers_yaml': controllers_yaml},
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

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
        parameters=[robot_description, {'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'dog2', '-z', '0.45'],
        output='screen'
    )

    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    load_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )

    load_rail_position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rail_position_controller'],
        output='screen'
    )

    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        rsp,
        spawn_entity,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[
                    load_joint_state_broadcaster,
                    load_joint_trajectory_controller,
                    load_rail_position_controller,
                ],
            )
        ),
    ])
