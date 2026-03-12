"""
Spider Robot Controller 启动文件

仅启动运动控制节点，不启动Gazebo仿真。
适用于已经运行Gazebo的情况，或者连接到真实硬件。

使用方法：
ros2 launch dog2_motion_control spider_controller.launch.py

可选参数：
- config_file: 步态参数配置文件路径
- use_sim_time: 是否使用仿真时间 (默认: false)
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """生成启动描述"""
    
    # 声明参数
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('dog2_motion_control'),
            'config',
            'gait_params.yaml'
        ]),
        description='步态参数配置文件路径'
    )
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='是否使用仿真时间（在Gazebo中运行时设为true）'
    )
    
    # 创建控制器节点
    spider_controller_node = Node(
        package='dog2_motion_control',
        executable='spider_controller',
        name='spider_robot_controller',
        output='screen',
        parameters=[
            LaunchConfiguration('config_file'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
    )
    
    return LaunchDescription([
        config_file_arg,
        use_sim_time_arg,
        spider_controller_node,
    ])
