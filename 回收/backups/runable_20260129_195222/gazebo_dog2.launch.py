from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory, get_package_prefix
from launch.substitutions import LaunchConfiguration
import os
import re
import xacro

def generate_launch_description():
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

    # 使用 xacro 生成 robot_description（统一入口，不再读取 dog2.urdf）
    xacro_file = os.path.join(pkg_share, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description_content = robot_description_config.toxml()

    # gazebo_ros2_control 插件解析 <parameters> 时不一定支持 $(find ...) 这种替换。
    # 这里把它替换为绝对路径，确保插件能读到 ros2_controllers.yaml。
    robot_description_content = robot_description_content.replace(
        '$(find dog2_description)/config/ros2_controllers.yaml',
        controllers_yaml,
    )

    # gazebo_ros2_control 可能会把 robot_description 通过参数注入内部节点。
    # 若 URDF 中包含换行/大段注释，rcl 参数解析可能失败，导致 controller_manager 起不来。
    # 这里做最小净化：去掉 XML 注释并压成单行。
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
        launch_arguments={'world': world_path}.items()
    )
    
    # 移除 robot_state_publisher_node，由 CHAMP bringup 统一启动
    # 移除 joint_state_publisher_node，由 CHAMP 控制器统一发布
    
    # 添加 robot_state_publisher，确保 gazebo_ros2_control 能获取 robot_description
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
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
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager", "--param-file", controllers_yaml],
        output="screen",
    )
    load_joint_group_effort_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager", "--param-file", controllers_yaml],
        output="screen",
    )
    load_joint_state_broadcaster_delayed = TimerAction(period=4.0, actions=[load_joint_state_broadcaster])
    load_joint_group_effort_controller_delayed = TimerAction(period=4.5, actions=[load_joint_group_effort_controller])

    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        node_robot_state_publisher,
        spawn_entity_delayed,
        load_joint_state_broadcaster_delayed,
        load_joint_group_effort_controller_delayed
    ])