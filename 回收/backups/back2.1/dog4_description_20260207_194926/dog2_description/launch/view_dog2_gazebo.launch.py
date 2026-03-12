import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 获取dog2_description包的路径
    package_dir = get_package_share_directory('dog2_description')
    controllers_yaml = os.path.join(package_dir, 'config', 'ros2_controllers.yaml')
    
    # 使用 xacro 生成 robot_description（统一入口，不再读取 dog2.urdf）
    xacro_file = os.path.join(package_dir, 'urdf', 'dog2.urdf.xacro')
    
    # 启动gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
    )
    
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description_content = robot_description_config.toxml()
    
    # 准备参数
    robot_description = {'robot_description': robot_description_content}
    
    # 发布机器人状态
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )
    
    # 通过 robot_description topic 生成实体
    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        arguments=['-entity', 'dog2', '-topic', 'robot_description', '-z', '1.0'],
        output='screen'
    )
    
    # 返回LaunchDescription对象
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])