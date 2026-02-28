from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():
    pkg_share = FindPackageShare(package='dog2_description').find('dog2_description')
    
    xacro_file_name = 'dog2.urdf.xacro'
    xacro_path = os.path.join(pkg_share, 'urdf', xacro_file_name)
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'dog2.rviz')

    robot_description_content = ParameterValue(
        Command(['xacro ', xacro_path]),
        value_type=str
    )
    
    # 机器人状态发布节点
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen'
    )
    
    # 固定的关节状态发布节点（不带GUI，所有关节在零位）
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'use_gui': False}],
        output='screen'
    )
    
    # RViz2节点
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz_node
    ])
