"""
Dog2 控制测试 Launch 文件
- 不启动 joint_state_publisher_gui，避免与控制脚本冲突
- 只启动 robot_state_publisher 和 rviz2
"""

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
    
    # RViz2 节点
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )
    
    # 注意：不启动 joint_state_publisher_gui
    # 关节状态由外部控制脚本发布
    
    return LaunchDescription([
        robot_state_publisher,
        rviz_node
    ])
