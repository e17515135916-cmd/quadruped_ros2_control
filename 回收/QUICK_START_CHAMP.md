# Dog2 + CHAMP 快速启动指南

## 🎯 目标
使用 CHAMP 框架实现 Dog2 机器狗的基础运动控制（前进、后退、转向、侧移）

---

## 📋 步骤 1：安装 CHAMP

### 方法 A：使用安装脚本（推荐）

```bash
cd ~/aperfect/carbot_ws
chmod +x install_champ.sh
./install_champ.sh
```

### 方法 B：手动安装

```bash
# 1. 克隆 CHAMP 仓库
cd ~/aperfect/carbot_ws/src
git clone -b ros2 https://github.com/chvmp/champ.git

# 2. 安装依赖
sudo apt-get update
sudo apt-get install -y \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-controller-manager \
    ros-humble-joint-trajectory-controller

# 3. 编译
cd ~/aperfect/carbot_ws
colcon build --packages-select champ champ_base champ_msgs --symlink-install
source install/setup.bash
```

---

## 🚀 步骤 2：启动仿真

### 终端 1：启动 Gazebo Fortress + CHAMP

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_champ_config dog2_champ_fortress.launch.py
```

**启动过程**（约 10 秒）：
1. ✅ Gazebo Fortress 启动
2. ✅ Dog2 机器人生成
3. ✅ ros2_control 控制器加载
4. ✅ CHAMP 四足控制器启动
5. ✅ 状态估计器启动

**成功标志**：
- Gazebo GUI 显示机器狗
- 终端显示 "quadruped_controller" 节点运行
- 没有错误信息

---

## 🎮 步骤 3：控制机器狗

### 方法 A：键盘控制（推荐）

**终端 2**：
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

**控制键**：
- `W` - 向前走 ⬆️
- `S` - 向后走 ⬇️
- `A` - 向左走 ⬅️
- `D` - 向右走 ➡️
- `Q` - 左转 ↺
- `E` - 右转 ↻
- `空格` - 停止 ⏸️
- `X` - 退出

### 方法 B：命令行控制

**向前走**：
```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**左转**：
```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

**停止**：
```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### 方法 C：自动演示

**终端 2**：
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_motion_demo.py
```

这将自动演示 9 种运动模式。

---

## 🔧 步骤 4：调试和优化

### 检查系统状态

```bash
# 查看所有节点
ros2 node list

# 应该看到：
# /quadruped_controller
# /state_estimator
# /robot_state_publisher
# /controller_manager

# 查看控制器状态
ros2 control list_controllers

# 应该看到：
# joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
# joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active

# 查看话题
ros2 topic list | grep cmd_vel
# 应该看到：/cmd_vel

# 查看关节状态
ros2 topic echo /joint_states --once
```

### 常见问题

#### 问题 1：机器人倒下
**原因**：初始姿态不稳定

**解决方案**：
1. 调整生成高度：编辑启动文件，将 `-z` 改为 `0.6` 或 `0.7`
2. 调整步态参数：编辑 `src/dog2_champ_config/config/gait/gait.yaml`

```yaml
gait:
  nominal_height: 0.30  # 增加站立高度
  swing_height: 0.05    # 增加抬腿高度
```

#### 问题 2：机器人不响应命令
**原因**：CHAMP 控制器未正确连接

**解决方案**：
```bash
# 检查 quadruped_controller 是否运行
ros2 node info /quadruped_controller

# 检查 /cmd_vel 话题
ros2 topic info /cmd_vel

# 应该显示至少 1 个订阅者
```

#### 问题 3：运动不稳定
**原因**：速度太快或步态参数不合适

**解决方案**：
1. 降低速度：从 0.1 m/s 开始测试
2. 调整步态参数：

编辑 `src/dog2_champ_config/config/gait/gait.yaml`：
```yaml
gait:
  max_linear_velocity_x: 0.3    # 降低最大速度
  max_angular_velocity_z: 0.5   # 降低旋转速度
  stance_duration: 0.3          # 增加支撑时间
```

#### 问题 4：CHAMP 包未找到
**错误信息**：`Package 'champ_base' not found`

**解决方案**：
```bash
# 重新编译
cd ~/aperfect/carbot_ws
colcon build --packages-select champ champ_base champ_msgs --symlink-install
source install/setup.bash

# 验证安装
ros2 pkg list | grep champ
```

---

## 📊 性能调优

### 1. 速度参数调整

编辑 `src/dog2_champ_config/config/gait/gait.yaml`：

```yaml
gait:
  # 最大速度
  max_linear_velocity_x: 0.5      # 前进速度 (m/s)
  max_linear_velocity_y: 0.25     # 侧向速度 (m/s)
  max_angular_velocity_z: 1.0     # 旋转速度 (rad/s)
  
  # 步态参数
  swing_height: 0.04              # 抬腿高度 (m) - 增加可提高越障能力
  stance_duration: 0.25           # 支撑时间 (s) - 增加可提高稳定性
  stance_depth: 0.0               # 支撑深度 (m)
  
  # 姿态参数
  nominal_height: 0.25            # 标称高度 (m) - 机器人站立高度
  com_x_translation: 0.0          # 重心 X 偏移 (m)
```

### 2. 关节映射检查

编辑 `src/dog2_champ_config/config/joints/joints.yaml`：

确保关节名称与 URDF 中的关节名称匹配：
```yaml
joints:
  left_front:
    hip: "j1"
    upper_leg: "j11"
    lower_leg: "j111"
  
  right_front:
    hip: "j2"
    upper_leg: "j21"
    lower_leg: "j211"
  
  left_hind:
    hip: "j3"
    upper_leg: "j31"
    lower_leg: "j311"
  
  right_hind:
    hip: "j4"
    upper_leg: "j41"
    lower_leg: "j411"
```

### 3. 控制器增益调整

编辑 `src/dog2_description/config/ros2_controllers.yaml`：

```yaml
joint_trajectory_controller:
  ros__parameters:
    gains:
      j1:  {p: 100.0, d: 10.0, i: 0.0}
      j11: {p: 100.0, d: 10.0, i: 0.0}
      j111: {p: 100.0, d: 10.0, i: 0.0}
      # ... 其他关节
```

---

## 🎯 测试清单

完成以下测试以验证系统正常工作：

- [ ] Gazebo Fortress 成功启动
- [ ] Dog2 机器人正确生成
- [ ] ros2_control 控制器加载成功
- [ ] CHAMP 控制器运行正常
- [ ] 机器人能够站立不倒
- [ ] 响应 /cmd_vel 命令
- [ ] 能够向前走
- [ ] 能够向后走
- [ ] 能够左转
- [ ] 能够右转
- [ ] 能够侧向移动
- [ ] 运动稳定流畅

---

## 📈 下一步：切换到 MPC + WBC

完成 CHAMP 基础运动测试后，你可以切换到 MPC + WBC 系统进行高级越障控制：

### 准备工作

1. **编译 MPC/WBC 包**：
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

2. **创建 MPC + WBC 启动文件**：
   - 我会帮你创建适配 Gazebo Fortress 的启动文件
   - 配置 MPC 参数
   - 配置 WBC 参数

3. **测试越障功能**：
   - 添加障碍物到仿真环境
   - 测试机器人越障能力
   - 调整控制参数

---

## 📚 参考资源

- **CHAMP GitHub**: https://github.com/chvmp/champ
- **CHAMP 文档**: https://github.com/chvmp/champ/wiki
- **ROS 2 Control**: https://control.ros.org/
- **Gazebo Fortress**: https://gazebosim.org/docs/fortress

---

## 💡 提示

1. **从慢速开始**：初次测试时使用低速（0.1-0.2 m/s）
2. **逐步增加**：确认稳定后再逐步提高速度
3. **保存日志**：记录成功的参数配置
4. **备份配置**：修改参数前备份原始配置文件

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看终端错误信息
2. 检查 ROS 2 日志：`ros2 run rqt_console rqt_console`
3. 使用 RViz 可视化：`rviz2`
4. 查看本文档的"常见问题"部分

祝你成功！🐕‍🦺🚀
