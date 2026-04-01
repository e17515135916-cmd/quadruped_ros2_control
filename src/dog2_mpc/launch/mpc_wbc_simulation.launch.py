#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    control_param_file = PathJoinSubstitution(
        [FindPackageShare("dog2_mpc"), "config", "dog2_ctrl_params.yaml"]
    )
    xacro_file = PathJoinSubstitution(
        [FindPackageShare("dog2_description"), "urdf", "dog2.urdf.xacro"]
    )
    robot_description = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])
        ),
        launch_arguments={"verbose": "false"}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time, "robot_description": robot_description}],
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-entity", "dog2", "-topic", "robot_description", "-x", "0.0", "-y", "0.0", "-z", "0.5"],
        output="screen",
    )

    mpc_node_16d = Node(
        package="dog2_mpc",
        executable="mpc_node_16d",
        name="mpc_node_16d",
        output="screen",
        parameters=[control_param_file, {"use_sim_time": use_sim_time}],
    )

    wbc_node_simple = Node(
        package="dog2_wbc",
        executable="wbc_node_simple",
        name="wbc_node_simple",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            gazebo_launch,
            robot_state_publisher,
            spawn_entity,
            mpc_node_16d,
            wbc_node_simple,
        ]
    )
