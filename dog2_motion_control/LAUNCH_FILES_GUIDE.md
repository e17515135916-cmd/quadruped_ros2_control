# 蜘蛛机器人启动文件使用指南

本文档说明如何使用dog2_motion_control包中的启动文件和配置文件。

## 目录结构

```
dog2_motion_control/
├── launch/
│   ├── spider_controller.launch.py          # 仅启动控制器节点
│   ├── spider_gazebo_complete.launch.py     # 完整Gazebo仿真
│   └── spider_gazebo_rviz.launch.py         # Gazebo + RViz可视化
└── config/
    ├── gait_params.yaml                     # 默认步态参数
    ├── gait_params_fast.yaml                # 快速测试配置
    ├── gait_params_stable.yaml              # 稳定步态配置
    ├── spider_robot.rviz                    # 完整RViz配置
    └── spider_robot_simple.rviz             # 简化RViz配置
```

## 启动文件说明

### 1. spider_gazebo_complete.launch.py

**功能**: 启动完整的Gazebo仿真环境，包括：
- Gazebo Fortress仿真器
- Dog2机器人模型
- ros2_control控制器
- 蜘蛛机器人运动控制节点

**使用方法**:
```bash
# 使用默认配置启动
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py

# 使用自定义配置文件
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py \
  config_file:=/path/to/custom_config.yaml

# 无GUI模式（无头模式）
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py \
  use_gui:=false

# 使用自定义世界文件
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py \
  world:=/path/to/world.sdf
```

**参数**:
- `config_file`: 步态参数配置文件路径（默认: gait_params.yaml）
- `use_gui`: 是否启动Gazebo GUI（默认: true）
- `world`: Gazebo世界文件路径（默认: empty.sdf）

### 2. spider_gazebo_rviz.launch.py

**功能**: 启动Gazebo仿真和RViz可视化

**使用方法**:
```bash
# 使用默认配置启动
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py

# 使用自定义RViz配置
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py \
  rviz_config:=/path/to/custom.rviz

# 使用快速测试配置
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py \
  config_file:=$(ros2 pkg prefix dog2_motion_control)/share/dog2_motion_control/config/gait_params_fast.yaml
```

**参数**:
- `config_file`: 步态参数配置文件路径
- `rviz_config`: RViz配置文件路径（默认: spider_robot.rviz）
- `world`: Gazebo世界文件路径

### 3. spider_controller.launch.py

**功能**: 仅启动运动控制节点，不启动Gazebo

**使用场景**:
- Gazebo已经在运行
- 连接到真实硬件
- 与其他仿真器集成

**使用方法**:
```bash
# 使用默认配置启动
ros2 launch dog2_motion_control spider_controller.launch.py

# 在Gazebo仿真中使用（启用仿真时间）
ros2 launch dog2_motion_control spider_controller.launch.py \
  use_sim_time:=true

# 使用自定义配置
ros2 launch dog2_motion_control spider_controller.launch.py \
  config_file:=/path/to/config.yaml
```

**参数**:
- `config_file`: 步态参数配置文件路径
- `use_sim_time`: 是否使用仿真时间（默认: false）

## 配置文件说明

### 1. gait_params.yaml（默认配置）

标准爬行步态配置，适用于大多数场景。

**关键参数**:
- 步长: 0.08米
- 步高: 0.05米
- 周期: 2.0秒
- 支撑相占比: 75%

### 2. gait_params_fast.yaml（快速测试）

用于快速测试和调试的配置。

**特点**:
- 更快的步态周期（1秒）
- 较小的步长和步高
- 启用调试输出

**使用场景**:
- 快速验证功能
- 调试步态算法
- 演示和测试

### 3. gait_params_stable.yaml（稳定步态）

用于需要高稳定性的场景。

**特点**:
- 非常慢的步态周期（3秒）
- 更小的步长
- 更高的支撑相占比（80%）
- 更严格的稳定性约束

**使用场景**:
- 狭窄空间作业
- 不平整地面
- 需要极高稳定性的任务

## RViz配置说明

### 1. spider_robot.rviz（完整配置）

包含所有可视化元素：
- 机器人模型
- TF坐标系
- 脚部轨迹（红色）
- 支撑三角形（绿色）
- 质心投影（蓝色）

**注意**: 需要在配置文件中启用调试模式才能看到轨迹和支撑三角形。

### 2. spider_robot_simple.rviz（简化配置）

仅显示基本元素：
- 机器人模型
- 网格
- TF坐标系（简化）

**使用场景**: 性能受限的系统或只需要查看机器人状态

## 常见使用场景

### 场景1: 快速测试步态

```bash
# 启动Gazebo和RViz，使用快速配置
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py \
  config_file:=$(ros2 pkg prefix dog2_motion_control)/share/dog2_motion_control/config/gait_params_fast.yaml
```

### 场景2: 稳定性测试

```bash
# 使用稳定配置，启用调试输出
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py \
  config_file:=$(ros2 pkg prefix dog2_motion_control)/share/dog2_motion_control/config/gait_params_stable.yaml
```

### 场景3: 无头仿真（CI/CD）

```bash
# 无GUI模式，用于自动化测试
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py \
  use_gui:=false
```

### 场景4: 调试可视化

1. 修改配置文件启用调试模式：
```yaml
debug:
  enabled: true
  publish_foot_trajectory: true
  publish_support_triangle: true
  log_level: "DEBUG"
```

2. 启动带RViz的仿真：
```bash
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py \
  config_file:=/path/to/debug_config.yaml
```

## 发送速度命令

启动仿真后，可以通过`/cmd_vel`话题发送速度命令：

```bash
# 前进
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# 后退
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: -0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# 左转
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}"

# 停止
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## 监控系统状态

### 查看关节状态
```bash
ros2 topic echo /joint_states
```

### 查看调试信息（需要启用调试模式）
```bash
# 脚部轨迹
ros2 topic echo /spider_robot/foot_trajectories

# 支撑三角形
ros2 topic echo /spider_robot/support_triangle

# 质心投影
ros2 topic echo /spider_robot/com_projection
```

### 查看日志
```bash
ros2 run rqt_console rqt_console
```

## 故障排除

### 问题1: Gazebo启动失败

**解决方案**:
```bash
# 检查Gazebo是否已安装
gz sim --version

# 清理Gazebo缓存
rm -rf ~/.gz/sim
```

### 问题2: 控制器加载失败

**解决方案**:
```bash
# 检查控制器状态
ros2 control list_controllers

# 重新加载控制器
ros2 control load_controller joint_trajectory_controller
ros2 control load_controller rail_position_controller
```

### 问题3: RViz无法显示机器人

**解决方案**:
- 检查`/robot_description`话题是否发布
- 确认Fixed Frame设置为`world`或`base_link`
- 检查TF树是否完整：`ros2 run tf2_tools view_frames`

### 问题4: 机器人不响应cmd_vel

**解决方案**:
- 检查控制器节点是否运行：`ros2 node list`
- 查看节点日志：`ros2 node info /spider_robot_controller`
- 确认话题连接：`ros2 topic info /cmd_vel`

## 性能优化

### 降低CPU使用率
1. 使用无GUI模式
2. 降低控制频率（修改配置文件中的`control.frequency`）
3. 使用简化的RViz配置

### 提高仿真速度
1. 减少Gazebo渲染质量
2. 使用更简单的碰撞模型
3. 降低物理引擎更新频率

## 下一步

完成启动文件配置后，可以：
1. 运行集成测试（任务14）
2. 在Gazebo中验证步态
3. 测试不同的速度命令
4. 调整步态参数优化性能

## 相关文档

- [需求文档](../../.kiro/specs/spider-robot-basic-motion/requirements.md)
- [设计文档](../../.kiro/specs/spider-robot-basic-motion/design.md)
- [任务列表](../../.kiro/specs/spider-robot-basic-motion/tasks.md)
- [ROS 2 Launch文档](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Gazebo文档](https://gazebosim.org/docs)
