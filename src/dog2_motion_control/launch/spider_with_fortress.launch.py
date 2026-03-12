#!/usr/bin/env python3
"""
蜘蛛机器人 + Gazebo Fortress启动文件

基于dog2_description/dog2_fortress_with_control.launch.py
添加了spider_robot_controller节点

使用方法：
ros2 launch dog2_motion_control spider_with_fortress.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """生成启动描述"""
    
    # 获取包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_motion_control = get_package_share_directory('dog2_motion_control')
    
    # 配置文件
    config_file = os.path.join(pkg_dog2_motion_control, 'config', 'gait_params.yaml')
    
    # 包含dog2_description的Fortress启动文件
    # 这个文件已经验证可以正确启动Gazebo和加载机器人
    dog2_fortress_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dog2_description, 'launch', 'dog2_fortress_with_control.launch.py')
        )
    )
    
    # 延迟启动spider_robot_controller
    # 等待Gazebo、机器人和控制器都完全启动
    spider_controller_node = TimerAction(
        period=10.0,  # 等待10秒确保一切就绪
        actions=[
            Node(
                package='dog2_motion_control',
                executable='spider_controller',
                name='spider_robot_controller',
                output='screen',
                parameters=[
                    config_file,
                    {'use_sim_time': False}
                ],
            )
        ]
    )
    
    return LaunchDescription([
        # 启动Gazebo Fortress + Dog2机器人 + 控制器
        dog2_fortress_launch,
        
        # 启动蜘蛛机器人运动控制节点
        spider_controller_node,
    ])
