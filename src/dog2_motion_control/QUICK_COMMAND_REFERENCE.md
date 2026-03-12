# 蜘蛛机器人Gazebo运动 - 命令速查表

## 📋 一句话启动

```bash
# 启动Gazebo + 机器人控制器
cd ~/aperfect/carbot_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && \
  ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=true
```

## 🎮 常用运动命令

在**新终端**中执行（记得先source环境）：

```bash
source /opt/ros/humble/setup.bash && source ~/aperfect/carbot_ws/install/setup.bash
```

### 1️⃣ 前进（慢）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.05}}" -r 10
```

### 2️⃣ 前进（中等）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.15}}" -r 10
```

### 3️⃣ 前进（快）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.25}}" -r 10
```

### 4️⃣ 后退
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: -0.15}}" -r 10
```

### 5️⃣ 左转（缓）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{angular: {z: 0.15}}" -r 10
```

### 6️⃣ 左转（急）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{angular: {z: 0.4}}" -r 10
```

### 7️⃣ 右转（缓）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{angular: {z: -0.15}}" -r 10
```

### 8️⃣ 右转（急）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{angular: {z: -0.4}}" -r 10
```

### 9️⃣ 前进+左转（曲线）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.1}, angular: {z: 0.2}}" -r 10
```

### 🔟 前进+右转（曲线）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.1}, angular: {z: -0.2}}" -r 10
```

### ❌ 停止（立即）
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{}" --once
```

## 🎬 完整运动序列脚本

使用演示脚本自动演示多种运动：

```bash
source /opt/ros/humble/setup.bash && source ~/aperfect/carbot_ws/install/setup.bash && \
  python3 ~/aperfect/carbot_ws/src/dog2_motion_control/scripts/robot_motion_demo.py
```

## 📊 速度参数对照表

| 运动描述 | linear.x | angular.z | 说明 |
|--------|----------|-----------|------|
| 静止 | 0 | 0 | 停止 |
| 超慢前进 | 0.05 | 0 | 谨慎爬行 |
| 慢速前进 | 0.1 | 0 | 稳定步态 |
| 中速前进 | 0.15 | 0 | 正常运动 |
| 快速前进 | 0.25 | 0 | 加速运动 |
| 缓慢转向 | 0 | ±0.2 | 精确转向 |
| 正常转向 | 0 | ±0.3 | 普通转向 |
| 快速转向 | 0 | ±0.5 | 急速转向 |
| 曲线运动1 | 0.1 | 0.1 | 缓慢转弯 |
| 曲线运动2 | 0.15 | 0.2 | 中等转弯 |
| 曲线运动3 | 0.2 | 0.3 | 急速转弯 |

## 🔍 实时监测命令

### 查看当前速度命令
```bash
ros2 topic echo /cmd_vel
```

### 查看关节状态
```bash
ros2 topic echo /joint_states -n 5
```

### 列出所有活动节点
```bash
ros2 node list
```

### 列出所有话题
```bash
ros2 topic list
```

## 🛠️ 配置文件编辑

快速编辑步态参数（需要重启仿真才能生效）：

```bash
nano ~/aperfect/carbot_ws/src/dog2_motion_control/config/gait_params.yaml
```

关键参数：
- `cycle_time`: 步态周期（秒）- 越小越快
- `stride_length`: 步长（米）- 控制步距  
- `stride_height`: 步高（米）- 脚抬起高度
- `body_height`: 身体高度（米）- 离地面距离

## 💾 保存运动序列

录制运动数据：
```bash
ros2 bag record /cmd_vel -o my_motion.bag
```

回放运动数据：
```bash
ros2 bag play my_motion.bag
```

## 🚨 常见问题快速解决

### 问题：机器人没反应
```bash
# 检查控制器是否运行
ros2 node list | grep spider

# 检查cmd_vel话题是否存在
ros2 topic list | grep cmd_vel

# 重启仿真
# 按Ctrl+C停止第一个终端，重新执行启动命令
```

### 问题：仿真太慢
降低gazebo加载的复杂度：
```bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=false
```

### 问题：编译失败
重新编译：
```bash
cd ~/aperfect/carbot_ws && source /opt/ros/humble/setup.bash && colcon build --symlink-install
```

## 📱 一键启动脚本

创建 `start_robot.sh`：

```bash
#!/bin/bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=true
```

使用方法：
```bash
chmod +x start_robot.sh
./start_robot.sh
```

## 🎯 实用组合命令

### 让机器人走一个正方形
```bash
# 前进
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.1}}" -r 10 &
sleep 5
# 左转90度
kill %1
ros2 topic pub /cmd_vel geometry_msgs/Twist "{angular: {z: 0.3}}" -r 10 &
sleep 5.24
# 重复4次...
```

更简单的做法是使用演示脚本或自己编写Python脚本。

## 🔗 相关资源

- **详细指南**: `RUN_ROBOT_GAZEBO.md`
- **成功报告**: `ROBOT_RUNNING_SUCCESS.md`
- **快速开始**: `QUICK_START.md`
- **原理文档**: `SPIDER_ROBOT_CONTROLLER_IMPLEMENTATION.md`

---

💡 **提示**: 所有命令都需要机器人已启动！确保第一个终端的仿真环境正常运行。
