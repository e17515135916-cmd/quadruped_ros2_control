from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # 获取包路径
    pkg_share = get_package_share_directory('dog2_description')
    controllers_yaml = os.path.join(pkg_share, 'config', 'ros2_controllers.yaml')
    
    # 设置gazebo资源路径
    gazebo_model_path = os.path.join(pkg_share, 'meshes')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ":" + gazebo_model_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = gazebo_model_path
    
    # 创建Gazebo模型目录
    gazebo_models_path = os.path.join(pkg_share, 'models')
    os.makedirs(os.path.join(gazebo_models_path, 'dog2'), exist_ok=True)
    
    # 创建model.config文件
    model_config_path = os.path.join(gazebo_models_path, 'dog2', 'model.config')
    with open(model_config_path, 'w') as model_config:
        model_config.write('''<?xml version="1.0"?>
<model>
  <name>dog2</name>
  <version>1.0</version>
  <sdf version="1.5">model.sdf</sdf>
  <author>
    <name>Generated</name>
    <email>n/a</email>
  </author>
  <description>
    Dog2 robot model
  </description>
</model>
''')
    
    # 创建model.sdf文件 - 使用URDF文件内容
    model_sdf_path = os.path.join(gazebo_models_path, 'dog2', 'model.sdf')
    
    # 使用 xacro 生成 robot_description（统一入口，不再读取 dog2.urdf）
    xacro_file = os.path.join(pkg_share, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={
            'controllers_yaml': controllers_yaml,
        },
    )
    robot_description_content = robot_description_config.toxml()
    
    # 写入SDF文件
    with open(model_sdf_path, 'w') as model_sdf:
        model_sdf.write('''<?xml version="1.0" ?>
<sdf version="1.5">
  <model name="dog2">
''')
        # 插入URDF内容
        model_sdf.write(robot_description_content.replace('<?xml version="1.0" encoding="utf-8"?>', '')
                                         .replace('<robot', '<robot xmlns:xacro="http://www.ros.org/wiki/xacro"')
                                         .replace('</robot>', '</model>\n</sdf>'))
    
    # 将models目录添加到GAZEBO_MODEL_PATH
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ":" + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = gazebo_models_path
    
    # 机器人状态发布
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )
    
    # 创建关节状态发布器节点
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )
    
    # 将模型路径导出为参数，直接在启动Gazebo时加载模型
    os.environ['GAZEBO_MODEL_DATABASE_URI'] = ''
    
    # 创建临时的world文件，将模型嵌入其中
    world_file_path = os.path.join(pkg_share, 'worlds', 'dog2.world')
    os.makedirs(os.path.join(pkg_share, 'worlds'), exist_ok=True)
    
    with open(world_file_path, 'w') as world_file:
        world_file.write('''
<?xml version="1.0" ?>
<sdf version="1.5">
  <world name="default">
    <include>
      <uri>model://sun</uri>
    </include>
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://dog2</uri>
      <pose>0 0 0.4 0 0 0</pose>
    </include>
  </world>
</sdf>
''')
    
    # 启动Gazebo，直接加载world文件
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_file_path, '-s', 'libgazebo_ros_init.so', 
             '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node,
        gazebo
    ]) 