#!/usr/bin/env python3
"""
Dog2 MPC+WBC测试启动文件（无Gazebo）

只启动MPC和WBC节点，用于测试控制算法
不需要Gazebo仿真环境
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 参数声明
    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='walking',
        description='Control mode: hover, walking, or crossing'
    )
    
    declare_mpc_horizon = DeclareLaunchArgument(
        'mpc_horizon',
        default_value='10',
        description='MPC prediction horizon'
    )
    
    declare_control_freq = DeclareLaunchArgument(
        'control_frequency',
        default_value='20.0',
        description='Control loop frequency (Hz)'
    )
    
    # 完整MPC节点
    mpc_node_complete = Node(
        package='dog2_mpc',
        executable='mpc_node_complete',
        name='mpc_node_complete',
        output='screen',
        parameters=[{
            'mass': 7.94,
            'horizon': LaunchConfiguration('mpc_horizon'),
            'dt': 0.05,
            'control_frequency': LaunchConfiguration('control_frequency'),
            'enable_sliding_constraints': True,
            'mode': LaunchConfiguration('mode')
        }]
    )
    
    # WBC节点（完整版）
    wbc_node_complete = Node(
        package='dog2_wbc',
        executable='wbc_node_complete',
        name='wbc_node_complete',
        output='screen',
        parameters=[{
            'l1': 0.2,
            'l2': 0.2,
            'max_torque': 50.0,
            'max_sliding_force': 100.0
        }]
    )
    
    # 状态模拟器（替代Gazebo）
    state_simulator = Node(
        package='dog2_mpc',
        executable='state_simulator',
        name='state_simulator',
        output='screen'
    )
    
    return LaunchDescription([
        # 参数
        declare_mode,
        declare_mpc_horizon,
        declare_control_freq,
        
        # 节点
        state_simulator,
        mpc_node_complete,
        wbc_node_complete,
    ])
