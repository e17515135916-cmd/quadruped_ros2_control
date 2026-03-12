from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():
    pkg_share = FindPackageShare(package='dog2_description').find('dog2_description')
    
    # Use the modified xacro file
    xacro_file_name = 'dog2.urdf.xacro'
    xacro_path = os.path.join(pkg_share, 'urdf', xacro_file_name)
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'dog2.rviz')
    
    # Generate robot description from xacro
    robot_description_content = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            xacro_path
        ]),
        value_type=str
    )
    
    # Robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen'
    )
    
    # Joint state publisher GUI node
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )
    
    # RViz2 node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node
    ])