# Dog2 键盘控制快速启动指南

## 🎯 目标

通过键盘控制 Dog2 四足机器人在 Gazebo 仿真中移动。

## ✅ 前提条件检查

在开始之前，确认以下内容：

### 1. 系统要求
- ✅ Ubuntu 22.04
- ✅ ROS 2 Humble
- ✅ Gazebo Fortress
- ✅ 已编译的工作空间

### 2. 检查文件是否存在

```bash
# 检查启动文件
ls src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py

# 检查键盘控制脚本
ls src/dog2_champ_config/scripts/dog2_keyboard_control.py

# 检查 CHAMP 包
ls src/champ
```

如果所有文件都存在，说明系统已准备就绪！

## 🚀 方法一：使用快速启动脚本（推荐）

### 终端 1：启动 Gazebo 系统

```bash
cd ~/aperfect/carbot_ws
./quick_start_keyboard_control.sh
```

等待约 7 秒，直到看到系统启动完成的消息。

### 终端 2：启动键盘控制

打开新终端：

```bash
cd ~/aperfect/carbot_ws
./start_keyboard_control.sh
```

## 🎮 方法二：手动启动（详细步骤）

### 步骤 1：编译工作空间（如果还没编译）

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select dog2_champ_config dog2_description champ_base champ_msgs
```

### 步骤 2：启动 Gazebo + CHAMP 系统

在终端 1 中：

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

**等待约 7 秒**，系统启动时序：
- Time 0s: 启动 Gazebo Fortress
- Time 0.5s: 启动 robot_state_publisher
- Time 1s: 生成 Dog2 机器人（高度 0.5m）
- Time 3s: 加载 joint_state_broadcaster
- Time 4s: 加载 joint_trajectory_controller
- Time 5s: 启动 CHAMP quadruped_controller
- Time 5s: 启动 state_estimation_node
- Time 6s: 启动 EKF 节点
- Time 7s: ✅ **系统就绪！**

### 步骤 3：启动键盘控制

在终端 2 中（新终端）：

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

或者直接运行：

```bash
cd ~/aperfect/carbot_ws
./start_keyboard_control.sh
```

## 🎮 键盘控制说明

### 移动控制

| 按键 | 功能 | 速度 |
|------|------|------|
| W/w | 向前移动 | 0.3 m/s |
| S/s | 向后移动 | -0.3 m/s |
| A/a | 向左平移 | 0.2 m/s |
| D/d | 向右平移 | -0.2 m/s |
| Q/q | 左转 | 0.5 rad/s |
| E/e | 右转 | -0.5 rad/s |

### 功能键

| 按键 | 功能 |
|------|------|
| 空格 | 停止所有运动 |
| X/x | 退出程序 |

## 📝 测试步骤

### 1. 基本前进测试

1. 确保 Gazebo 窗口可见
2. 在键盘控制终端按 `W` 键
3. 观察机器人向前行走
4. 按 `空格` 键停止

### 2. 多方向测试

1. 按 `W` - 向前走 2 秒
2. 按 `空格` - 停止
3. 按 `A` - 向左平移 2 秒
4. 按 `空格` - 停止
5. 按 `Q` - 左转 2 秒
6. 按 `空格` - 停止

### 3. 组合动作测试

1. 按 `W` - 向前走
2. 同时按 `Q` - 边走边左转（弧线运动）
3. 按 `空格` - 停止

## 🔍 故障排除

### 问题 1：Gazebo 启动失败

**症状**：Gazebo 窗口不出现或报错

**解决方案**：
```bash
# 检查 Gazebo 是否安装
gz sim --version

# 如果未安装，安装 Gazebo Fortress
sudo apt update
sudo apt install gz-fortress
```

### 问题 2：机器人不出现

**症状**：Gazebo 启动了，但没有机器人

**解决方案**：
```bash
# 检查 robot_description 话题
ros2 topic echo /robot_description --once

# 检查是否有错误消息
ros2 topic echo /rosout
```

### 问题 3：键盘控制无响应

**症状**：按键后机器人不动

**解决方案**：

1. 检查 /cmd_vel 话题是否发布：
```bash
ros2 topic echo /cmd_vel
```

2. 检查 CHAMP 控制器是否运行：
```bash
ros2 node list | grep quadruped_controller
```

3. 检查关节控制器是否加载：
```bash
ros2 control list_controllers
```

应该看到：
- `joint_state_broadcaster` [active]
- `joint_trajectory_controller` [active]

### 问题 4：机器人倒下

**症状**：机器人生成后立即倒下

**可能原因**：
- 初始高度不够
- 关节控制器未正确加载
- CHAMP 控制器未启动

**解决方案**：
1. 等待完整的 7 秒启动时间
2. 检查所有控制器状态
3. 重新启动系统

### 问题 5：编译错误

**症状**：colcon build 失败

**解决方案**：
```bash
# 清理并重新编译
rm -rf build/ install/ log/
colcon build --packages-select dog2_champ_config dog2_description champ_base champ_msgs
```

## 📊 验证系统状态

### 检查所有节点是否运行

```bash
ros2 node list
```

应该看到：
- `/robot_state_publisher`
- `/quadruped_controller`
- `/state_estimation`
- `/base_to_footprint_ekf`
- `/footprint_to_odom_ekf`
- `/controller_manager`

### 检查所有话题

```bash
ros2 topic list
```

应该看到：
- `/cmd_vel` - 速度命令输入
- `/joint_states` - 关节状态
- `/odom` - 里程计
- `/foot_contacts` - 足端接触

### 检查控制器状态

```bash
ros2 control list_controllers
```

应该看到：
```
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active
```

## 🎥 预期行为

### 正常启动流程

1. **Gazebo 窗口出现**（约 1 秒）
2. **机器人出现在空中**（z=0.5m，约 1 秒）
3. **机器人落地并站立**（约 3-5 秒）
4. **机器人保持稳定站立姿态**（约 7 秒后）
5. **准备接收键盘命令**

### 正常行走行为

按 `W` 键后：
1. 机器人开始抬腿
2. 四条腿交替移动（对角步态）
3. 身体保持稳定，高度约 0.20m
4. 平滑向前移动

## 📚 相关文档

- [任务完成总结](TASK_7.1_KEYBOARD_CONTROL_COMPLETION.md)
- [键盘控制详细文档](src/dog2_champ_config/scripts/README_KEYBOARD_CONTROL.md)
- [CHAMP Gazebo 需求文档](.kiro/specs/champ-gazebo-motion/requirements.md)
- [CHAMP Gazebo 设计文档](.kiro/specs/champ-gazebo-motion/design.md)

## 🎯 快速命令参考

```bash
# 启动系统（终端 1）
./quick_start_keyboard_control.sh

# 启动键盘控制（终端 2）
./start_keyboard_control.sh

# 或者手动启动
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py  # 终端 1
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py  # 终端 2

# 检查系统状态
ros2 node list
ros2 topic list
ros2 control list_controllers

# 手动发布速度命令（测试）
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## ✅ 成功标志

如果一切正常，你应该能够：

1. ✅ Gazebo 窗口正常显示
2. ✅ Dog2 机器人出现并站立
3. ✅ 按 `W` 键后机器人向前行走
4. ✅ 按 `空格` 键后机器人停止
5. ✅ 所有方向控制都响应正常

## 🎉 恭喜！

如果你能看到机器人响应键盘命令并移动，说明系统工作正常！

现在你可以：
- 尝试不同的移动模式
- 调整速度参数
- 测试复杂的运动轨迹
- 开发更高级的控制算法

祝你使用愉快！🚀
