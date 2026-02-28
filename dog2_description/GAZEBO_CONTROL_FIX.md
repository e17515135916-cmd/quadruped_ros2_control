# Gazebo ROS 2 Control 配置修复

## 问题描述

在 `dog2.urdf.xacro` 和 `dog2.urdf` 文件的末尾，`gazebo_ros2_control` 插件部分缺失了加载配置文件的路径。如果不补上这一行，Gazebo 启动后会加载机器人，但所有关节都会失去控制（瘫痪），因为 ROS 2 不知道该加载哪个控制器。

## 修复内容

### 1. 创建控制器配置文件

创建了 `src/dog2_description/config/ros2_controllers.yaml` 文件，包含：

- **controller_manager**: 控制器管理器配置
  - 更新频率：100 Hz
  - 定义了两个控制器：
    - `joint_state_broadcaster`: 关节状态广播器
    - `joint_group_effort_controller`: 关节组力矩控制器

- **joint_state_broadcaster**: 关节状态发布配置
  - 发布频率：50 Hz

- **joint_group_effort_controller**: 力矩控制器配置
  - 控制所有 12 个关节（4条腿 × 3个关节）
  - 接口类型：effort（力矩控制）

### 2. 修改 URDF 文件

在两个文件中的 `gazebo_ros2_control` 插件部分添加了控制器配置文件路径：

#### dog2.urdf.xacro
```xml
<gazebo>
  <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
    <parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
    <robot_param>robot_description</robot_param>
    <robot_param_node>robot_state_publisher</robot_param_node>
  </plugin>
</gazebo>
```

#### dog2.urdf
```xml
<gazebo>
  <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
    <parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
    <robot_param>robot_description</robot_param>
    <robot_param_node>robot_state_publisher</robot_param_node>
  </plugin>
</gazebo>
```

## 关键改动

添加的关键行：
```xml
<parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
```

这一行告诉 Gazebo 的 ROS 2 Control 插件从哪里加载控制器配置，确保：
1. 控制器管理器能够正确初始化
2. 关节状态广播器能够发布关节状态
3. 力矩控制器能够接收并执行控制命令
4. 机器人在 Gazebo 中不会"瘫痪"

## 验证

修复后，启动 Gazebo 时：
1. 控制器管理器会自动加载配置
2. 关节状态会正常发布到 `/joint_states` 话题
3. 可以通过 `/joint_group_effort_controller/commands` 话题发送控制命令
4. 机器人关节能够正常响应控制指令

## 相关文件

- `src/dog2_description/urdf/dog2.urdf.xacro` - Xacro 源文件（已修复）
- `src/dog2_description/urdf/dog2.urdf` - 生成的 URDF 文件（已修复）
- `src/dog2_description/config/ros2_controllers.yaml` - 控制器配置文件（新建）

## 修复日期

2026-01-26
