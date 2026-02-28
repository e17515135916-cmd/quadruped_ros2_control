from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory, get_package_prefix
from launch.substitutions import LaunchConfiguration
import os
import re
import xacro

def generate_launch_description():
    gui = LaunchConfiguration('gui')

    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='false',
    )

    # 获取包路径
    pkg_share = get_package_share_directory('dog2_description')
    install_dir = get_package_prefix('dog2_description')
    controllers_yaml = os.path.join(pkg_share, 'config', 'ros2_controllers.yaml')
    
    # 设置 GAZEBO_MODEL_PATH，确保 Gazebo 能找到 mesh 文件
    # package://dog2_description/meshes/... 会在 GAZEBO_MODEL_PATH 中查找 dog2_description 目录
    gazebo_model_path = os.path.join(install_dir, 'share')
    
    if 'GAZEBO_MODEL_PATH' in os.environ:
        gazebo_model_path += os.pathsep + os.environ['GAZEBO_MODEL_PATH']

    set_gazebo_model_path = SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path)

    # 避免部分机器/驱动下 gzclient 因 OpenGL 问题闪退
    set_software_rendering = SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1')

    # 使用 xacro 生成 robot_description（统一入口，不再读取 dog2.urdf）
    xacro_file = os.path.join(pkg_share, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description_content = robot_description_config.toxml()

    # gazebo_ros2_control 可能会把 robot_description 通过参数注入内部节点。
    # 若 URDF 中包含换行/大段注释，rcl 参数解析可能失败，导致 controller_manager 起不来。
    # 这里做最小净化：去掉 XML 注释并压成单行。
    robot_description_content = re.sub(r'<\?xml.*?\?>', '', robot_description_content, flags=re.DOTALL)
    robot_description_content = re.sub(r'<!--.*?-->', '', robot_description_content, flags=re.DOTALL)
    robot_description_content = re.sub(r'\s+', ' ', robot_description_content).strip()
    
    # 获取gazebo_ros包的launch文件路径
    gazebo_ros = get_package_share_directory('gazebo_ros')

    # 启动Gazebo world：优先使用 champ_gazebo 的 outdoor.world；若未安装则回退到 empty.world
    try:
        champ_gazebo = get_package_share_directory('champ_gazebo')
        world_path = os.path.join(champ_gazebo, 'worlds', 'outdoor.world')
    except PackageNotFoundError:
        world_path = os.path.join(gazebo_ros, 'worlds', 'empty.world')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_path,
            # 默认不启动 GUI，避免部分机器上 gzclient Ogre 断言崩溃
            'gui': gui,
        }.items()
    )
    
    # 移除 robot_state_publisher_node，由 CHAMP bringup 统一启动
    # 移除 joint_state_publisher_node，由 CHAMP 控制器统一发布
    
    # 添加 robot_state_publisher，确保 gazebo_ros2_control 能获取 robot_description
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True,
        }]
    )

    # 添加机器人到Gazebo (延迟执行，确保 robot_description 已发布)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'dog2', '-topic', '/robot_description', '-z', '1.0'],
        output='screen'
    )
    spawn_entity_delayed = TimerAction(period=2.0, actions=[spawn_entity])

    # 加载并启动控制器（延迟更久，确保 controller_manager 已启动）
    # NOTE: controller_manager/spawner 在部分机器上会遇到 service call 10s 超时，导致重试后出现 "already loaded"。
    # 这里改用 ros2 control CLI 并显式指定 timeout，提高稳定性。
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'for i in $(seq 1 120); do '
            '  ros2 service list 2>/dev/null | grep -q "^/controller_manager/list_controllers$" && break; '
            '  sleep 1; '
            'done; '
            'for i in $(seq 1 5); do '
            '  ros2 control load_controller -c /controller_manager joint_state_broadcaster && exit 0; '
            '  sleep 2; '
            'done; '
            'exit 1'
        ],
        output='screen',
    )

    # controller_manager 要求先 configure（inactive）再 activate
    configure_joint_state_broadcaster = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'for i in $(seq 1 5); do '
            '  ros2 control set_controller_state -c /controller_manager joint_state_broadcaster inactive && exit 0; '
            '  sleep 2; '
            'done; '
            'exit 1'
        ],
        output='screen',
    )

    activate_joint_state_broadcaster = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'for i in $(seq 1 5); do '
            '  ros2 control set_controller_state -c /controller_manager joint_state_broadcaster active && exit 0; '
            '  sleep 2; '
            'done; '
            'exit 1'
        ],
        output='screen',
    )

    load_joint_trajectory_controller = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'for i in $(seq 1 5); do '
            '  ros2 control load_controller -c /controller_manager joint_trajectory_controller && exit 0; '
            '  sleep 2; '
            'done; '
            'exit 1'
        ],
        output='screen',
    )
    set_joint_trajectory_controller_inactive = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'for i in $(seq 1 5); do '
            '  ros2 control set_controller_state -c /controller_manager joint_trajectory_controller inactive && exit 0; '
            '  sleep 2; '
            'done; '
            'exit 1'
        ],
        output='screen',
    )

    load_joint_state_broadcaster_delayed = TimerAction(
        period=10.0,
        actions=[
            load_joint_state_broadcaster,
            configure_joint_state_broadcaster,
            activate_joint_state_broadcaster,
        ],
    )
    load_joint_group_effort_controller_delayed = TimerAction(
        period=12.0,
        actions=[load_joint_trajectory_controller, set_joint_trajectory_controller_inactive],
    )

    return LaunchDescription([
        declare_gui,
        set_gazebo_model_path,
        set_software_rendering,
        gazebo,
        node_robot_state_publisher,
        spawn_entity_delayed,
        load_joint_state_broadcaster_delayed,
        load_joint_group_effort_controller_delayed
    ])