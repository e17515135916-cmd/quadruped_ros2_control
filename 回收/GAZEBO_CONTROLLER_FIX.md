# Gazebo 控制器加载问题修复指南

## 问题描述

机器人在 Gazebo 中不移动，原因是：
1. ✅ Gazebo 已正确加载 16 个关节接口（4 个滑动副 + 12 个腿部关节）
2. ❌ `joint_trajectory_controller` 处于 `inactive` 状态
3. ❌ 尝试激活控制器失败

## 根本原因

从用户提供的日志可以看到：
```
joint_trajectory_controller joint_trajectory_controller/JointTrajectoryController  inactive
joint_state_broadcaster     joint_state_broadcaster/JointStateBroadcaster          active
```

`joint_trajectory_controller` 加载了但是是 `inactive` 状态，需要激活。

## 已完成的修复

### 1. 修复 URDF ros2_control 部分 ✅
- 将关节名称从原始名称（j11, j111 等）改为 CHAMP 名称（lf_haa_joint, lf_hfe_joint 等）
- 文件：`src/dog2_description/urdf/dog2.urdf.xacro`

### 2. 修复 links.yaml ✅
- 将链接名称从原始名称（l11, l111 等）改为 CHAMP 名称（lf_hip_link, lf_upper_leg_link 等）
- 文件：`src/dog2_champ_config/config/links/links.yaml`

### 3. 修复启动文件 ✅
- 使用临时文件方法让 Gazebo 加载完整 URDF（包含 ros2_control 标签）
- 文件：`src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py`

### 4. 修复 Gazebo 插件配置 ✅
- 移除了 `<parameters>` 标签（虽然 xacro 会展开路径，但这不是问题）
- 文件：`src/dog2_description/urdf/dog2.urdf.xacro`

## 下一步：激活控制器

控制器已经加载但处于 `inactive` 状态。需要手动激活：

### 方法 1：使用 ros2 control 命令

```bash
# 1. Source 环境
source /opt/ros/humble/setup.bash
source install/setup.bash

# 2. 检查控制器状态
ros2 control list_controllers

# 3. 激活 joint_trajectory_controller
ros2 control set_controller_state joint_trajectory_controller start

# 4. 验证状态
ros2 control list_controllers
```

### 方法 2：修改启动文件

在启动文件中，`spawner` 命令默认会激活控制器。如果没有激活，可能是时序问题。

检查 `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py` 中的 spawner 命令：

```python
joint_trajectory_controller = TimerAction(
    period=4.0,
    actions=[
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_trajectory_controller'],  # 默认会激活
            output='screen',
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        )
    ]
)
```

如果需要显式激活，可以添加 `--activate` 参数：

```python
arguments=['joint_trajectory_controller', '--activate'],
```

## 测试步骤

1. **重启 Gazebo 系统**（如果还在运行）：
   ```bash
   # 在 Gazebo 终端按 Ctrl+C 停止
   # 然后重新启动
   ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
   ```

2. **等待系统完全启动**（约 7 秒）

3. **检查控制器状态**：
   ```bash
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 control list_controllers
   ```

4. **如果 joint_trajectory_controller 是 inactive，手动激活**：
   ```bash
   ros2 control set_controller_state joint_trajectory_controller start
   ```

5. **测试键盘控制**：
   ```bash
   ./start_keyboard_control.sh
   # 按 W 键向前移动
   ```

## 预期结果

- `joint_state_broadcaster`: active
- `joint_trajectory_controller`: active
- 按 W 键后，机器人应该开始移动

## 如果还是不工作

检查 CHAMP quadruped_controller 的日志：
```bash
ros2 node info /quadruped_controller
ros2 topic echo /joint_trajectory_controller/joint_trajectory --once
```

确认 CHAMP 是否在发布关节轨迹命令。
