# Dog2 机器人运动指南

## 🎯 快速启动

### 方法 1：一键启动（推荐）

```bash
# 在终端 1 中运行
./start_dog2_gui.sh
```

这会启动 Gazebo Fortress 并显示 GUI 窗口。

然后在**另一个终端**中运行：

```bash
# 在终端 2 中运行
source install/setup.bash
python3 test_correct_joints.py
```

### 方法 2：手动启动

**终端 1 - 启动 Gazebo：**
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_description dog2_fortress_with_gui.launch.py
```

**终端 2 - 运行测试：**
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 test_correct_joints.py
```

---

## 📋 可用的测试脚本

### 1. `test_correct_joints.py` - 基础腿部运动测试
测试内容：
- 站立姿态
- 单腿抬起（前左、前右）
- 对角步态（抬起腿1+腿4，抬起腿2+腿3）

```bash
python3 test_correct_joints.py
```

### 2. `forward_backward_demo.py` - 前进后退演示
测试内容：
- 前进 3 步
- 停顿
- 后退 3 步

```bash
python3 forward_backward_demo.py
```

### 3. `test_direct_movement.py` - 诊断测试
用于诊断关节状态和控制器连接。

```bash
python3 test_direct_movement.py
```

---

## 🔧 重要说明

### 关节配置

Dog2 机器人有 **16 个关节**：
- **4 个导轨关节**（j1, j2, j3, j4）- 被 `rail_position_controller` 控制，通常锁定
- **12 个旋转关节**（j11, j111, j1111, ...）- 被 `joint_trajectory_controller` 控制

**所有运动脚本只控制 12 个旋转关节！**

### 关节命名规则

每条腿有 3 个旋转关节：
```
腿 1 (前左): j11  (髋关节), j111  (大腿), j1111 (小腿)
腿 2 (前右): j21  (髋关节), j211  (大腿), j2111 (小腿)
腿 3 (后左): j31  (髋关节), j311  (大腿), j3111 (小腿)
腿 4 (后右): j41  (髋关节), j411  (大腿), j4111 (小腿)
```

### 典型关节位置

**站立姿态：**
```python
[0.4, -1.0, 0.5] * 4  # 每条腿相同
```

**抬起腿：**
```python
[0.8, -1.5, 0.8]  # 髋关节向上，大腿和小腿弯曲
```

---

## 🐛 故障排除

### 问题 1：机器人不动

**可能原因：**
1. 控制器未正确启动
2. Gazebo GUI 没有打开（无法观察）
3. 关节限位问题

**解决方案：**
```bash
# 检查控制器状态
ros2 control list_controllers

# 应该看到：
# joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
# joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active
```

### 问题 2：Gazebo GUI 不显示

**解决方案：**
确保使用 `dog2_fortress_with_gui.launch.py` 而不是 `dog2_fortress_with_control.launch.py`

```bash
# 正确的启动文件
ros2 launch dog2_description dog2_fortress_with_gui.launch.py
```

### 问题 3：控制器加载失败

**检查日志：**
```bash
# 查看 Gazebo 输出
# 应该看到：
# [INFO] [gz_ros2_control]: Loading joint: j11
# [INFO] [gz_ros2_control]: Loading joint: j111
# ...
```

如果看到错误，可能需要重新编译：
```bash
colcon build --packages-select dog2_description
source install/setup.bash
```

---

## 📊 观察机器人运动

在 Gazebo GUI 中：

1. **查看机器人** - 应该能看到 Dog2 机器人悬浮在空中（z=0.5m）
2. **观察腿部** - 运行测试脚本时，腿应该会抬起和放下
3. **检查位置** - 前进/后退演示应该会改变机器人的位置

### 预期行为

**test_correct_joints.py：**
- 机器人先站立
- 前左腿抬起
- 前右腿抬起
- 对角步态（腿1+腿4，腿2+腿3）

**forward_backward_demo.py：**
- 机器人向前移动约 1-2 米
- 停顿
- 机器人向后移动回到原位

---

## 🎮 下一步

### 实现真正的行走

要让机器人真正行走（而不只是抬腿），需要：

1. **更复杂的步态规划** - 协调所有腿的运动
2. **身体姿态控制** - 保持身体平衡
3. **接触力反馈** - 检测脚是否接触地面

### 使用 CHAMP 控制系统

CHAMP 是一个完整的四足机器人控制框架，已经实现了：
- 步态生成
- 逆运动学
- 键盘控制
- 自动演示

参考 `DOG2_WALKING_GUIDE.md` 了解如何集成 CHAMP。

---

## 📝 文件说明

### 启动文件
- `dog2_fortress_with_gui.launch.py` - 带 GUI 的 Gazebo 启动文件
- `dog2_fortress_with_control.launch.py` - 无 GUI 的 Gazebo 启动文件（用于无头服务器）

### 测试脚本
- `test_correct_joints.py` - 基础腿部运动测试
- `forward_backward_demo.py` - 前进后退演示
- `test_direct_movement.py` - 诊断测试

### 配置文件
- `src/dog2_description/config/ros2_controllers.yaml` - 控制器配置
- `src/dog2_description/urdf/dog2.urdf.xacro` - 机器人模型

---

## ✅ 成功标志

如果一切正常，你应该看到：

1. ✅ Gazebo GUI 窗口打开
2. ✅ Dog2 机器人加载在场景中
3. ✅ 运行测试脚本时，机器人的腿会移动
4. ✅ 终端输出显示命令发送成功
5. ✅ 没有错误消息

---

## 🆘 需要帮助？

如果遇到问题：

1. 检查 Gazebo 是否正确安装：`gz sim --version`
2. 检查 ROS 2 环境：`ros2 pkg list | grep dog2`
3. 查看日志文件：`~/.ros/log/`
4. 重新编译：`colcon build --packages-select dog2_description`

祝你成功！🐕‍🦺🚀
