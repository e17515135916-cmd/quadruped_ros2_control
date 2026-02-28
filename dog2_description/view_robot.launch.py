import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 获取URDF文件的路径
    xacro_file = os.path.join(get_package_share_directory('dog2_description'), 'urdf', 'dog2.urdf.xacro') #将dog2_description更改为你的包名称，将dog2.urdf.xacro更改为你的URDF文件名。
    controllers_yaml = os.path.join(get_package_share_directory('dog2_description'), 'config', 'ros2_controllers.yaml')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_desc = robot_description_config.toxml()

    # 定义robot_state_publisher节点
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 创建启动描述
    return LaunchDescription([
        robot_state_publisher_node
    ])
