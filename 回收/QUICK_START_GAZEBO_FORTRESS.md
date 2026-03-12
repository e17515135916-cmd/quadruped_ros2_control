# Dog2 + CHAMP + Gazebo Fortress 快速启动指南

## 一键启动

```bash
# 基本启动
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

# 带 RViz 可视化
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py rviz:=true
```

## 控制机器人

### 方法 1: 键盘控制

```bash
# 在新终端中运行
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

按键说明：
- `W` - 前进
- `S` - 后退
- `A` - 左移
- `D` - 右移
- `Q` - 左转
- `E` - 右转
- `SPACE` - 停止
- `X` - 退出

### 方法 2: 直接发布命令

```bash
# 前进
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# 停止
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## 启动选项

```bash
# 无 GUI（headless）
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py gazebo_gui:=false

# 自定义世界
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py world:=/path/to/world.sdf

# 组合选项
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py \
  rviz:=true \
  gazebo_gui:=true \
  use_sim_time:=true
```

## 监控系统

### 检查节点

```bash
ros2 node list
```

应该看到：
- `/robot_state_publisher`
- `/controller_manager`
- `/quadruped_controller`
- `/state_estimation`
- `/base_to_footprint_ekf`
- `/footprint_to_odom_ekf`

### 检查话题

```bash
ros2 topic list
```

关键话题：
- `/cmd_vel` - 速度命令输入
- `/joint_states` - 关节状态
- `/odom` - 里程计输出
- `/foot_contacts` - 足部接触状态

### 查看 TF 树

```bash
ros2 run tf2_tools view_frames
# 生成 frames.pdf
```

### 监控里程计

```bash
ros2 topic echo /odom
```

### 监控关节状态

```bash
ros2 topic echo /joint_states
```

## 故障排除

### 问题：Gazebo 无法启动

```bash
# 检查 Gazebo Fortress 是否安装
gz sim --version

# 如果未安装
sudo apt install gz-fortress
```

### 问题：找不到 CHAMP 包

```bash
# 检查 CHAMP 是否安装
ros2 pkg list | grep champ

# 如果未安装，克隆并构建
cd ~/carbot_ws/src
git clone --recursive https://github.com/chvmp/champ -b ros2
cd ~/carbot_ws
colcon build --packages-select champ_base champ_msgs
source install/setup.bash
```

### 问题：控制器加载失败

```bash
# 检查控制器状态
ros2 control list_controllers

# 手动加载控制器
ros2 control load_controller joint_state_broadcaster
ros2 control load_controller joint_trajectory_controller
```

### 问题：机器人掉落

- 检查初始高度是否足够（默认 z=0.5m）
- 检查滑动副是否正确锁定
- 检查关节限位是否正确

## 系统要求

### 最低配置

- CPU: 4 核心, 2.0 GHz
- RAM: 8 GB
- GPU: 集成显卡
- OS: Ubuntu 22.04

### 推荐配置

- CPU: 8 核心, 3.0 GHz
- RAM: 16 GB
- GPU: 独立显卡
- OS: Ubuntu 22.04

## 依赖安装

### 一键安装脚本

```bash
# 运行安装脚本（如果存在）
bash scripts/install_champ_gazebo.sh
```

### 手动安装

```bash
# Gazebo Fortress
sudo apt install gz-fortress

# ROS 2 Gazebo 包
sudo apt install \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-gz-ros2-control

# ros2_control
sudo apt install \
  ros-humble-controller-manager \
  ros-humble-joint-state-broadcaster \
  ros-humble-joint-trajectory-controller

# robot_localization
sudo apt install ros-humble-robot-localization

# CHAMP
cd ~/carbot_ws/src
git clone --recursive https://github.com/chvmp/champ -b ros2
cd ~/carbot_ws
colcon build
```

## 性能优化

### 提高实时因子

```bash
# 降低物理更新频率（在 URDF 中）
# 或使用更简单的碰撞模型
```

### 减少 CPU 使用

```bash
# 使用 headless 模式
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py gazebo_gui:=false
```

### 减少内存使用

```bash
# 不启动 RViz
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py rviz:=false
```

## 常用命令

### 重启系统

```bash
# Ctrl+C 停止当前启动
# 然后重新启动
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

### 清理构建

```bash
rm -rf build/ install/ log/
colcon build
```

### 查看日志

```bash
# 实时查看日志
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py 2>&1 | tee launch.log

# 查看特定节点日志
ros2 node info /quadruped_controller
```

## 开发提示

### 修改配置后

```bash
# 重新构建
colcon build --packages-select dog2_champ_config

# 重新 source
source install/setup.bash

# 重新启动
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

### 调试模式

```bash
# 启用详细日志
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py --log-level debug
```

### 录制数据

```bash
# 录制所有话题
ros2 bag record -a

# 录制特定话题
ros2 bag record /cmd_vel /odom /joint_states
```

## 相关文档

- 详细文档: `TASK_5.1_LAUNCH_FILE_COMPLETION.md`
- 完整总结: `TASK_5_COMPLETION_SUMMARY.md`
- 设计文档: `.kiro/specs/champ-gazebo-motion/design.md`
- 需求文档: `.kiro/specs/champ-gazebo-motion/requirements.md`

## 支持

如有问题，请检查：
1. 所有依赖是否正确安装
2. 工作空间是否正确构建
3. 环境是否正确 source
4. 配置文件是否存在且正确

## 快速测试

```bash
# 1. 启动系统
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

# 2. 等待 7 秒（系统启动）

# 3. 在新终端发送测试命令
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# 4. 观察机器人是否开始行走

# 5. 停止
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## 成功标志

系统正常运行时，你应该看到：
- ✅ Gazebo 窗口打开，显示 Dog2 机器人
- ✅ 机器人站立在地面上（不掉落）
- ✅ 所有节点正常运行（`ros2 node list`）
- ✅ 关节状态正常发布（`ros2 topic echo /joint_states`）
- ✅ 发送速度命令后机器人开始行走
- ✅ 里程计数据正常更新（`ros2 topic echo /odom`）

祝使用愉快！🚀
