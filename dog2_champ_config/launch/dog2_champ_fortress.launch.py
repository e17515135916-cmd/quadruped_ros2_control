#!/usr/bin/env python3
"""
Dog2 + CHAMP + Gazebo Fortress 完整启动文件

功能：
1. 启动 Gazebo Fortress 仿真环境
2. 加载 Dog2 机器人模型（12 DOF，滑动副锁定）
3. 启动 ros2_control 控制器
4. 启动 CHAMP 四足控制器
5. 启动状态估计器和 EKF 融合
6. 准备接收 /cmd_vel 命令

使用方法：
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

可选参数：
- use_sim_time:=true/false (默认: true)
- gazebo_gui:=true/false (默认: true)
- rviz:=true/false (默认: false)
- world:=<world_file_path> (默认: empty.sdf)

控制方法：
# 终端 2：键盘控制
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py

# 或者直接发布速度命令
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # 包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_champ_config = get_package_share_directory('dog2_champ_config')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    try:
        pkg_champ_base = get_package_share_directory('champ_base')
    except:
        pkg_champ_base = None
    
    # 配置文件
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    gait_config = os.path.join(pkg_dog2_champ_config, 'config', 'gait', 'gait.yaml')
    joints_config = os.path.join(pkg_dog2_champ_config, 'config', 'joints', 'joints.yaml')
    links_config = os.path.join(pkg_dog2_champ_config, 'config', 'links', 'links.yaml')
    
    # 启动参数
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_gazebo_gui = DeclareLaunchArgument(
        'gazebo_gui',
        default_value='true',
        description='Launch Gazebo with GUI'
    )
    
    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz for visualization'
    )
    
    declare_world = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='World file to load (default: empty.sdf)'
    )
    
    # 环境变量 - Gazebo 模型路径
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )
    
    # 处理 URDF
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={'controllers_yaml': controllers_yaml},
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # 1. 启动 Gazebo Fortress (Time 0s)
    world_file_path = LaunchConfiguration('world')
    gazebo_gui_arg = LaunchConfiguration('gazebo_gui')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r ', world_file_path],
            'on_exit_shutdown': 'true'
        }.items()
    )
    
    # 2. Robot State Publisher (Time 0.5s)
    robot_state_publisher = TimerAction(
        period=0.5,
        actions=[
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[
                    robot_description,
                    {'use_sim_time': LaunchConfiguration('use_sim_time')}
                ]
            )
        ]
    )
    
    # 3. Spawn Dog2 机器人 (Time 1s, z=0.5m)
    spawn_entity = TimerAction(
        period=1.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'dog2',
                    '-z', '0.5'
                ],
                output='screen'
            )
        ]
    )
    
    # 4. Joint State Broadcaster (Time 3s)
    joint_state_broadcaster = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster'],
                output='screen',
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
            )
        ]
    )
    
    # 5. Joint Trajectory Controller (Time 4s)
    joint_trajectory_controller = TimerAction(
        period=4.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_trajectory_controller'],
                output='screen',
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
            )
        ]
    )
    
    # 6. CHAMP Quadruped Controller (Time 5s)
    quadruped_controller = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='quadruped_controller_node',
                name='quadruped_controller',
                output='screen',
                parameters=[
                    gait_config,
                    joints_config,
                    links_config,
                    {
                        'gazebo': True,
                        'publish_joint_states': False,  # Let joint_state_broadcaster handle this
                        'publish_joint_control': True,
                        'publish_foot_contacts': True,
                        'joint_controller_topic': 'joint_trajectory_controller/joint_trajectory',
                        'use_sim_time': LaunchConfiguration('use_sim_time')
                    }
                ],
                remappings=[
                    ('cmd_vel/smooth', '/cmd_vel'),
                ],
            )
        ]
    )
    
    # 7. State Estimation Node (Time 5s)
    state_estimator = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='state_estimation_node',
                name='state_estimation',
                output='screen',
                parameters=[
                    {
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                        'orientation_from_imu': False  # Use kinematic estimation
                    }
                ]
            )
        ]
    )
    
    # 8. EKF Nodes (Time 6s)
    # EKF for base to footprint
    base_to_footprint_ekf = None
    footprint_to_odom_ekf = None
    
    if pkg_champ_base:
        base_to_footprint_ekf = TimerAction(
            period=6.0,
            actions=[
                Node(
                    package='robot_localization',
                    executable='ekf_node',
                    name='base_to_footprint_ekf',
                    output='screen',
                    parameters=[
                        {
                            'base_link_frame': 'base_link',
                            'use_sim_time': LaunchConfiguration('use_sim_time')
                        },
                        os.path.join(pkg_champ_base, 'config', 'ekf', 'base_to_footprint.yaml')
                    ],
                    remappings=[('odometry/filtered', 'odom/local')]
                )
            ]
        )
        
        # EKF for footprint to odom
        footprint_to_odom_ekf = TimerAction(
            period=6.0,
            actions=[
                Node(
                    package='robot_localization',
                    executable='ekf_node',
                    name='footprint_to_odom_ekf',
                    output='screen',
                    parameters=[
                        {
                            'base_link_frame': 'base_link',
                            'use_sim_time': LaunchConfiguration('use_sim_time')
                        },
                        os.path.join(pkg_champ_base, 'config', 'ekf', 'footprint_to_odom.yaml')
                    ],
                    remappings=[('odometry/filtered', 'odom')]
                )
            ]
        )
    
    # 9. RViz (可选)
    rviz_config = os.path.join(pkg_dog2_champ_config, 'rviz', 'dog2_champ.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    # 构建启动描述
    launch_description_list = [
        # 声明参数
        declare_use_sim_time,
        declare_gazebo_gui,
        declare_rviz,
        declare_world,
        
        # 设置环境变量
        set_gazebo_model_path,
        
        # 启动节点（按时序）
        gazebo,                      # Time 0s
        robot_state_publisher,       # Time 0.5s
        spawn_entity,                # Time 1s
        joint_state_broadcaster,     # Time 3s
        joint_trajectory_controller, # Time 4s
        quadruped_controller,        # Time 5s
        state_estimator,             # Time 5s
    ]
    
    # 添加 EKF 节点（如果 CHAMP 包可用）
    if base_to_footprint_ekf:
        launch_description_list.append(base_to_footprint_ekf)  # Time 6s
    if footprint_to_odom_ekf:
        launch_description_list.append(footprint_to_odom_ekf)  # Time 6s
    
    # 添加 RViz（可选）
    launch_description_list.append(rviz_node)
    
    return LaunchDescription(launch_description_list)

