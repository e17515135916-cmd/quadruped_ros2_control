#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true',
    )

    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_champ_config = get_package_share_directory('dog2_champ_config')

    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')

    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )

    champ_urdf = {'urdf': robot_description_config.toxml()}

    gait_config = os.path.join(pkg_dog2_champ_config, 'config', 'gait', 'gait.yaml')
    joints_config = os.path.join(pkg_dog2_champ_config, 'config', 'joints', 'joints.yaml')
    links_config = os.path.join(pkg_dog2_champ_config, 'config', 'links', 'links.yaml')

    quadruped_controller_node = Node(
        package='champ_base',
        executable='quadruped_controller_node',
        name='quadruped_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'gazebo': True},
            {'publish_joint_states': False},
            {'publish_joint_control': True},
            {'publish_foot_contacts': False},
            {'joint_controller_topic': '/joint_trajectory_controller/joint_trajectory'},
            champ_urdf,
            joints_config,
            links_config,
            gait_config,
        ],
        remappings=[
            ('/cmd_vel/smooth', '/cmd_vel'),
        ],
    )

    state_estimator_node = Node(
        package='champ_base',
        executable='state_estimation_node',
        name='state_estimator',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'orientation_from_imu': False},
            champ_urdf,
            joints_config,
            links_config,
            gait_config,
        ],
    )

    return LaunchDescription(
        [
            declare_use_sim_time,
            quadruped_controller_node,
            state_estimator_node,
        ]
    )
