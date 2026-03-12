# 让机器人在Gazebo中动起来 - 快速启动指南

## 概述

本指南将帮助你在Gazebo仿真环境中让蜘蛛机器人（Dog2）动起来。

## 前置条件

- ROS 2 Humble已安装
- Gazebo Fortress已安装
- 工作空间已编译

## 快速启动步骤

### 1. 编译工作空间（如果还未编译）

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

### 2. 启动Gazebo仿真环境和机器人控制器

打开**终端1**，执行：

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=true
```

**预期输出：**
- Gazebo窗口打开
- 控制器输出："Spider Robot Controller is READY"
- 机器人在Gazebo中显示为四足机器人模型
- 机器人自动进入初始站立姿态

### 3. 发送运动命令

#### 方式A: 使用演示脚本（推荐）

打开**终端2**，执行：

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 src/dog2_motion_control/scripts/robot_motion_demo.py
```

这个脚本将演示以下运动：
- ✓ 前进（Forward）
- ✓ 左转（Turn Left）
- ✓ 右转（Turn Right）
- ✓ 曲线运动（Curved Motion）

#### 方式B: 手动发送速度命令

打开**终端2**，使用以下命令：

**前进运动：**
```bash
source /opt/ros/humble/setup.bash
source ~/aperfect/carbot_ws/install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.15, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" -r 10
```

**旋转运动（左转）：**
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}" -r 10
```

**旋转运动（右转）：**
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.3}}" -r 10
```

**曲线运动：**
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.2}}" -r 10
```

**停止运动：**
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once
```

## 控制参数说明

### Twist消息格式：

```python
geometry_msgs/Twist:
  linear:
    x: 前进速度 (m/s)，正值前进，负值后退
    y: 侧移速度 (m/s)，目前未实现
    z: 竖直速度 (m/s)，不适用于地面机器人
  angular:
    x: 绕X轴旋转速度 (rad/s)，不适用
    y: 绕Y轴旋转速度 (rad/s)，不适用
    z: 绕Z轴旋转速度 (rad/s)，正值逆时针，负值顺时针
```

### 建议的速度范围：

| 运动类型 | linear.x | angular.z | 说明 |
|---------|----------|-----------|------|
| 慢速前进 | 0.05 - 0.1 | 0.0 | 稳定爬行 |
| 中速前进 | 0.1 - 0.2 | 0.0 | 正常步态 |
| 快速前进 | 0.2 - 0.3 | 0.0 | 加快步态 |
| 缓慢旋转 | 0.0 | ±0.1 - 0.2 | 平稳转向 |
| 快速旋转 | 0.0 | ±0.3 - 0.5 | 急速转向 |
| 曲线运动 | 0.1 | 0.1 - 0.3 | 结合前进和旋转 |

## 机器人运动系统工作流程

```
1. 用户发送速度命令 (/cmd_vel)
   ↓
2. SpiderRobotController接收命令
   ↓
3. GaitGenerator生成步态参数
   ↓
4. TrajectoryPlanner规划平滑轨迹
   ↓
5. KinematicsSolver进行逆运动学求解
   ↓
6. JointController生成关节轨迹
   ↓
7. ros2_control发送给Gazebo
   ↓
8. Gazebo仿真执行，机器人运动
```

## 配置参数

机器人的步态参数保存在：
```
~/aperfect/carbot_ws/src/dog2_motion_control/config/gait_params.yaml
```

主要参数：
- `cycle_time`: 步态周期（秒）- 越小越快
- `stride_length`: 步长（米）- 控制步距
- `stride_height`: 步高（米）- 脚抬起的高度
- `body_height`: 身体高度（米）- 身体距地面的距离
- `duty_factor`: 支撑相占比 - 控制稳定性

## 故障排除

### 问题1: Gazebo窗口打不开但控制器运行正常

这是正常的！可以在后台运行，机器人照样会动。添加 `use_gui:=false` 参数：
```bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=false
```

### 问题2: 机器人没有响应速度命令

检查以下事项：
1. 确保控制器已启动：`ros2 node list | grep spider`
2. 检查是否有错误：查看终端1的输出
3. 重新启动仿真环境

### 问题3: 机器人运动不稳定或抖动

这可能是由以下原因导致：
1. 速度命令过大 - 降低linear.x或angular.z的值
2. Gazebo仿真时间步长问题 - 使用默认配置
3. 关节控制器增益需要调整

### 问题4: 控制器报错 "Failed to parse config"

确保参数文件格式正确。使用标准YAML格式，以 `ros__parameters:` 开头。

## 高级用法

### 使用ROS 2 Teleop发送命令

如果已安装 `teleop_twist_keyboard`：
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel
```

### 记录和回放运动

记录运动：
```bash
ros2 bag record /cmd_vel
```

回放运动：
```bash
ros2 bag play rosbag2_*
```

### 使用RViz可视化

```bash
ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py
```

## 下一步

- 修改 `gait_params.yaml` 尝试不同的步态参数
- 实现自定义行为和导航算法
- 集成SLAM进行自主导航
- 添加传感器仿真（相机、雷达等）

## 参考资源

- [ROS 2官方文档](https://docs.ros.org/en/humble/)
- [Gazebo官方文档](https://gazebosim.org/)
- [项目README](./README.md)
- [运动控制实现详情](./SPIDER_ROBOT_CONTROLLER_IMPLEMENTATION.md)

## 获取帮助

如遇问题，检查以下日志文件：
```bash
cat ~/.ros/log/latest/spider_robot_controller/
```

或查看项目中的troubleshooting文档：
```bash
ls -la ~/aperfect/carbot_ws/src/dog2_motion_control/*.md
```

---

**祝你使用愉快！🤖**
