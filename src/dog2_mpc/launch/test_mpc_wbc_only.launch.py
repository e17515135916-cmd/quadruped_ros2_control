#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    mode = LaunchConfiguration("mode")
    control_param_file = PathJoinSubstitution(
        [FindPackageShare("dog2_mpc"), "config", "dog2_ctrl_params.yaml"]
    )

    state_simulator = Node(
        package="dog2_mpc",
        executable="state_simulator",
        name="state_simulator",
        output="screen",
    )

    mpc_node_complete = Node(
        package="dog2_mpc",
        executable="mpc_node_complete",
        name="mpc_node_complete",
        output="screen",
        parameters=[control_param_file, {"mode": mode}],
    )

    wbc_node_complete = Node(
        package="dog2_wbc",
        executable="wbc_node_complete",
        name="wbc_node_complete",
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("mode", default_value="walking"),
            state_simulator,
            mpc_node_complete,
            wbc_node_complete,
        ]
    )
