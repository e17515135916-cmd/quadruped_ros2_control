from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import xacro


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    gui = LaunchConfiguration('gui')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
    )

    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
    )

    pkg_share = get_package_share_directory('dog2_description')
    controllers_yaml = os.path.join(pkg_share, 'config', 'ros2_controllers.yaml')

    xacro_file = os.path.join(pkg_share, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    gz_sim_share = get_package_share_directory('ros_gz_sim')

    gz_resource_path = os.path.join(pkg_share, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + os.pathsep + gz_resource_path

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path,
    )

    world_file = '/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf'

    gz_args_gui = f'-r {world_file}'
    gz_args_headless = f'-r -s {world_file}'

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': LaunchConfiguration('gz_args'),
            'on_exit_shutdown': 'true',
        }.items(),
    )

    declare_gz_args = DeclareLaunchArgument(
        'gz_args',
        default_value=gz_args_gui,
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}],
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'dog2', '-z', '0.5'],
        output='screen',
    )

    spawn_entity_delayed = TimerAction(period=2.0, actions=[spawn_entity])

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager', '--controller-manager-timeout', '60'],
        output='screen',
    )

    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller', '--controller-manager', '/controller_manager', '--controller-manager-timeout', '60'],
        output='screen',
    )

    rail_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rail_position_controller', '--controller-manager', '/controller_manager', '--controller-manager-timeout', '60'],
        output='screen',
    )

    controllers_delayed = TimerAction(
        period=6.0,
        actions=[
            joint_state_broadcaster_spawner,
            joint_trajectory_controller_spawner,
            rail_position_controller_spawner,
        ],
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_gui,
        declare_gz_args,
        set_gz_resource_path,
        gz_sim,
        robot_state_publisher,
        spawn_entity_delayed,
        controllers_delayed,
    ])
