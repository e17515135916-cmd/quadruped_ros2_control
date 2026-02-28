# Dog2 机器人控制指南

## 🚀 快速启动

### 1. 启动仿真环境
```bash
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

这将启动：
- ✅ Gazebo仿真器（户外世界）
- ✅ Dog2四足机器人模型
- ✅ 运动控制器
- ✅ 状态估计器
- ✅ 所有必要的控制节点

---

## 🎮 控制方式

### 方式一：键盘控制（推荐）

在**新终端**中运行：
```bash
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

**控制键：**
- `W` - 向前 ⬆️
- `S` - 向后 ⬇️
- `A` - 向左 ⬅️
- `D` - 向右 ➡️
- `Q` - 左转 ↺
- `E` - 右转 ↻
- `空格` - 停止 ⏸️
- `X` - 退出程序

---

### 方式二：自动演示

在**新终端**中运行：
```bash
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_motion_demo.py
```

这将自动演示Dog2的9种运动能力：
1. 向前行走
2. 向后行走
3. 原地左转
4. 原地右转
5. 向左侧移
6. 向右侧移
7. 弧线运动（前进+左转）
8. 弧线运动（前进+右转）
9. 对角线运动

---

### 方式三：手动发布命令

使用ROS 2命令行工具：

**向前走：**
```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**左转：**
```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

**停止：**
```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

---

### 方式四：使用champ_teleop（需要安装）

如果已安装champ_teleop包：
```bash
ros2 run champ_teleop teleop_twist_keyboard
```

---

## 📊 监控机器人状态

### 查看里程计信息
```bash
ros2 topic echo /odom
```

### 查看关节状态
```bash
ros2 topic echo /joint_states
```

### 查看脚部接触信息
```bash
ros2 topic echo /foot_contacts
```

### 查看所有话题
```bash
ros2 topic list
```

### 查看所有节点
```bash
ros2 node list
```

---

## ⚙️ 速度参数调整

可以在脚本中修改速度参数：

**dog2_keyboard_control.py (第23-25行):**
```python
self.linear_speed = 0.3    # 线速度 m/s (推荐: 0.1-0.5)
self.angular_speed = 0.5   # 角速度 rad/s (推荐: 0.3-1.0)
self.lateral_speed = 0.2   # 侧向速度 m/s (推荐: 0.1-0.3)
```

---

## 🔧 故障排除

### 机器人不动？
1. 检查节点是否运行：
   ```bash
   ros2 node list | grep quadruped
   ```
   应该看到 `/quadruped_controller`

2. 检查话题是否有订阅者：
   ```bash
   ros2 topic info /cmd_vel
   ```
   应该显示至少1个订阅者

3. 检查关节控制器：
   ```bash
   ros2 control list_controllers
   ```

### 机器人倒下或不稳定？
- 调整步态参数：`src/dog2_champ_config/config/gait/gait.yaml`
- 检查关节配置：`src/dog2_champ_config/config/joints/joints.yaml`

---

## 📝 配置文件说明

- **gait.yaml** - 步态参数（速度、步高、姿态等）
- **joints.yaml** - 关节映射和控制参数
- **links.yaml** - 连杆映射
- **ros_control.yaml** - ROS 2 Control配置

---

## 🎯 下一步

1. 调整步态参数优化运动性能
2. 添加传感器（如激光雷达、相机）
3. 实现自主导航
4. 添加地形感知功能

---

## 📚 相关资源

- CHAMP项目: https://github.com/chvmp/champ
- ROS 2文档: https://docs.ros.org/
- Gazebo文档: https://gazebosim.org/

---

**享受你的Dog2机器人！** 🐕‍🦺🎉

