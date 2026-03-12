# Dog2 机器狗稳定行走实现指南

## 📋 概述

要让 Dog2 机器狗实现稳定行走，你有两个主要方案：

### 方案 A：使用现有的 CHAMP 控制系统（推荐）
- ✅ 已经实现完整的四足步态控制
- ✅ 支持键盘控制和自动演示
- ⚠️ 需要适配到 Gazebo Fortress

### 方案 B：使用 MPC + WBC 控制系统
- ✅ 更高级的模型预测控制
- ✅ 全身动力学控制
- ⚠️ 需要适配到 Gazebo Fortress
- ⚠️ 配置更复杂

---

## 🎯 方案 A：CHAMP 控制系统（推荐新手）

### 1. 当前状态
你已经有完整的 CHAMP 配置：
- `src/dog2_champ_config/` - CHAMP 配置包
- 键盘控制脚本
- 自动演示脚本
- 步态配置文件

### 2. 需要做的工作

#### 步骤 1：更新 CHAMP 启动文件以支持 Gazebo Fortress

创建新的启动文件：`src/dog2_champ_config/launch/dog2_champ_fortress.launch.py`

```python
#!/usr/bin/env python3
"""
Dog2 + CHAMP + Gazebo Fortress 完整启动文件
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # 包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_champ_config = get_package_share_directory('dog2_champ_config')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    
    # 配置文件
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    gait_config = os.path.join(pkg_dog2_champ_config, 'config', 'gait', 'gait.yaml')
    joints_config = os.path.join(pkg_dog2_champ_config, 'config', 'joints', 'joints.yaml')
    links_config = os.path.join(pkg_dog2_champ_config, 'config', 'links', 'links.yaml')
    
    # 环境变量
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )
    
    # URDF
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={'controllers_yaml': controllers_yaml},
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # Gazebo Fortress
    world_file = '/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf'
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true'
        }.items()
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )
    
    # Spawn 机器人
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'dog2', '-z', '0.5'],
        output='screen'
    )
    
    # CHAMP Quadruped Controller
    quadruped_controller = Node(
        package='champ_base',
        executable='quadruped_controller_node',
        name='quadruped_controller',
        output='screen',
        parameters=[
            gait_config,
            joints_config,
            links_config,
            {'use_sim_time': True}
        ]
    )
    
    # State Estimator
    state_estimator = Node(
        package='champ_base',
        executable='state_estimation_node',
        name='state_estimator',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    # Joint State Broadcaster
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    
    # Joint Trajectory Controller
    joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )
    
    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        quadruped_controller,
        state_estimator,
        joint_state_broadcaster,
        joint_trajectory_controller,
    ])
```

#### 步骤 2：检查 CHAMP 是否已安装

```bash
ros2 pkg list | grep champ
```

如果没有安装，需要安装 CHAMP：

```bash
cd ~/aperfect/carbot_ws/src
git clone https://github.com/chvmp/champ.git
cd ~/aperfect/carbot_ws
colcon build --packages-select champ champ_base champ_msgs
source install/setup.bash
```

#### 步骤 3：启动完整系统

```bash
# 终端 1：启动仿真和控制
ros2 launch dog2_champ_config dog2_champ_fortress.launch.py

# 终端 2：键盘控制
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

---

## 🚀 方案 B：MPC + WBC 控制系统（高级）

### 1. 系统架构

```
┌─────────────────┐
│  Gait Planner   │ ← 步态规划
└────────┬────────┘
         │ 期望足端轨迹
         ↓
┌─────────────────┐
│   MPC (16维)    │ ← 模型预测控制
└────────┬────────┘
         │ 期望地面反力
         ↓
┌─────────────────┐
│   WBC (全身)    │ ← 全身控制
└────────┬────────┘
         │ 关节力矩命令
         ↓
┌─────────────────┐
│ Gazebo Fortress │ ← 物理仿真
└─────────────────┘
```

### 2. 需要做的工作

#### 步骤 1：编译所有控制包

```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select \
    dog2_dynamics \
    dog2_gait_planner \
    dog2_mpc \
    dog2_wbc \
    dog2_state_estimation \
    dog2_interfaces
source install/setup.bash
```

#### 步骤 2：创建 Gazebo Fortress 适配的启动文件

创建：`src/dog2_mpc/launch/mpc_wbc_fortress.launch.py`

```python
#!/usr/bin/env python3
"""
Dog2 MPC + WBC + Gazebo Fortress 完整启动文件
"""

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():
    # 包路径
    pkg_dog2_description = get_package_share_directory('dog2_description')
    pkg_dog2_mpc = get_package_share_directory('dog2_mpc')
    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    
    # 配置文件
    controllers_yaml = os.path.join(pkg_dog2_description, 'config', 'ros2_controllers.yaml')
    mpc_config = os.path.join(pkg_dog2_mpc, 'config', 'mpc_params.yaml')
    
    # 环境变量
    gazebo_model_path = os.path.join(pkg_dog2_description, '..')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gazebo_model_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + gazebo_model_path
    
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gazebo_model_path
    )
    
    # URDF
    xacro_file = os.path.join(pkg_dog2_description, 'urdf', 'dog2.urdf.xacro')
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={'controllers_yaml': controllers_yaml},
    )
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    # Gazebo Fortress
    world_file = '/usr/share/ignition/ignition-gazebo6/worlds/empty.sdf'
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true'
        }.items()
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )
    
    # Spawn 机器人
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'dog2', '-z', '0.5'],
        output='screen'
    )
    
    # 步态规划器
    gait_planner = Node(
        package='dog2_gait_planner',
        executable='gait_planner_node',
        name='gait_planner',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    # MPC 控制器 (16维)
    mpc_node = Node(
        package='dog2_mpc',
        executable='mpc_node_16d',
        name='mpc_node_16d',
        output='screen',
        parameters=[
            mpc_config,
            {
                'use_sim_time': True,
                'mass': 7.94,
                'horizon': 10,
                'dt': 0.05,
                'control_frequency': 20.0,
                'enable_sliding_constraints': True
            }
        ]
    )
    
    # WBC 控制器
    wbc_node = Node(
        package='dog2_wbc',
        executable='wbc_node_simple',
        name='wbc_node_simple',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    # 状态估计器
    state_estimator = Node(
        package='dog2_state_estimation',
        executable='state_estimator_node',
        name='state_estimator',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    # Joint State Broadcaster
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    
    # Joint Trajectory Controller
    joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )
    
    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        gait_planner,
        mpc_node,
        wbc_node,
        state_estimator,
        joint_state_broadcaster,
        joint_trajectory_controller,
    ])
```

#### 步骤 3：启动系统

```bash
# 终端 1：启动完整系统
ros2 launch dog2_mpc mpc_wbc_fortress.launch.py

# 终端 2：发送速度命令
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

---

## 🔧 调试和优化

### 1. 检查系统状态

```bash
# 查看所有节点
ros2 node list

# 查看所有话题
ros2 topic list

# 查看控制器状态
ros2 control list_controllers

# 查看关节状态
ros2 topic echo /joint_states
```

### 2. 常见问题

#### 问题 1：机器人倒下
**原因**：初始姿态不稳定或控制参数不合适

**解决方案**：
1. 调整生成高度：`-z` 参数改为 `0.6` 或 `0.7`
2. 调整步态参数：编辑 `gait.yaml`
3. 调整 PID 参数：编辑控制器配置

#### 问题 2：机器人不响应命令
**原因**：控制器未正确连接

**解决方案**：
1. 检查话题连接：`ros2 topic info /cmd_vel`
2. 检查节点运行：`ros2 node list`
3. 查看日志：`ros2 node info <node_name>`

#### 问题 3：运动不稳定
**原因**：步态参数或控制增益不合适

**解决方案**：
1. 降低速度：从 0.1 m/s 开始测试
2. 调整步高：`swing_height` 参数
3. 调整步频：`stance_duration` 参数

---

## 📊 性能优化

### 1. 步态参数调整

编辑 `src/dog2_champ_config/config/gait/gait.yaml`：

```yaml
gait:
  max_linear_velocity_x: 0.5      # 最大前进速度 (m/s)
  max_linear_velocity_y: 0.25     # 最大侧向速度 (m/s)
  max_angular_velocity_z: 1.0     # 最大旋转速度 (rad/s)
  
  swing_height: 0.04              # 抬腿高度 (m)
  stance_duration: 0.25           # 支撑相时间 (s)
  stance_depth: 0.0               # 支撑深度 (m)
  
  nominal_height: 0.25            # 标称高度 (m)
```

### 2. 控制器增益调整

编辑 `src/dog2_description/config/ros2_controllers.yaml`：

```yaml
joint_trajectory_controller:
  ros__parameters:
    gains:
      j1:  {p: 100.0, d: 10.0, i: 0.0}
      j11: {p: 100.0, d: 10.0, i: 0.0}
      # ... 其他关节
```

---

## 🎯 推荐实施路径

### 阶段 1：基础验证（1-2天）
1. ✅ 已完成：Gazebo Fortress 迁移
2. ✅ 已完成：ros2_control 配置
3. ⏳ 待完成：安装 CHAMP
4. ⏳ 待完成：创建 Fortress 适配启动文件

### 阶段 2：CHAMP 集成（2-3天）
1. 测试 CHAMP 基础功能
2. 调整步态参数
3. 实现键盘控制
4. 优化运动稳定性

### 阶段 3：高级控制（可选，1-2周）
1. 集成 MPC 控制器
2. 集成 WBC 控制器
3. 实现地形适应
4. 添加传感器反馈

---

## 📚 参考资源

- **CHAMP 文档**: https://github.com/chvmp/champ
- **ROS 2 Control**: https://control.ros.org/
- **Gazebo Fortress**: https://gazebosim.org/docs/fortress
- **四足机器人控制理论**: https://ieeexplore.ieee.org/document/8593885

---

## 💡 下一步建议

**立即开始**：
1. 检查 CHAMP 是否已安装
2. 创建 Fortress 适配的启动文件
3. 测试基础行走功能

**需要帮助时**：
- 查看日志文件
- 使用 RViz 可视化
- 逐步调试每个组件

祝你成功！🐕‍🦺🚀
