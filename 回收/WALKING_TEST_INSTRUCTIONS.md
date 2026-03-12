# Dog2 行走测试完整说明

## 📋 测试概述

我们创建了两个行走演示脚本：

1. **simple_walk_demo.py** - 基础动作演示（原地步态）
2. **forward_walk_demo.py** - 前进行走演示（实际移动）

## 🚀 快速开始

### 步骤 1：编译和准备环境

```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
```

### 步骤 2：启动 Gazebo Fortress（终端 1）

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_description dog2_fortress_with_control.launch.py
```

**等待看到以下信息**：
```
[INFO] [spawner-joint_state_broadcaster]: Loaded joint_state_broadcaster
[INFO] [spawner-joint_trajectory_controller]: Loaded joint_trajectory_controller
```

### 步骤 3：运行行走演示（终端 2）

#### 选项 A：基础动作演示

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 simple_walk_demo.py
```

这个演示会：
- 站立
- 执行对角步态（原地）
- 单腿抬起演示

#### 选项 B：前进行走演示（推荐）

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 forward_walk_demo.py
```

这个演示会：
- 站立
- 执行 5 个完整的前进步态周期
- 机器人应该向前移动

## 🔍 验证测试结果

### 1. 检查控制器状态

在新终端中运行：

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 control list_controllers
```

应该看到：
```
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active
```

### 2. 监控机器人位置

在新终端中运行：

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 topic echo /joint_states --once
```

### 3. 在 Gazebo 中观察

打开 Gazebo GUI，你应该看到：
- 机器人成功站立
- 腿部按照步态规律运动
- （forward_walk_demo）机器人向前移动

### 4. 检查机器人位置变化

```bash
# 监控机器人的世界坐标
gz topic -e -t /model/dog2/pose
```

或者使用我们的监控脚本：

```bash
./monitor_robot_position.sh
```

## 📊 预期结果

### simple_walk_demo.py

**终端输出**：
```
🐕 Dog2 简单行走演示启动
等待 2 秒...

=== 阶段 1: 站立 ===
📍 站立姿态

=== 阶段 2: 对角步态演示 ===
  步态循环 1/3
📍 抬起前左腿和后右腿
📍 抬起前右腿和后左腿
...

=== ✅ 演示完成 ===
```

**Gazebo 中的表现**：
- 机器人站立稳定
- 对角线的腿同时抬起和放下
- 机器人保持在原地

### forward_walk_demo.py

**终端输出**：
```
🐕 Dog2 前进行走演示启动
等待 2 秒...

=== 阶段 1: 站立准备 ===
📍 站立姿态

=== 阶段 2: 前进行走 ===

  步态周期 1/5
📍 抬起前左腿和后右腿，向前摆动
📍 放下腿，身体向前移动
📍 抬起前右腿和后左腿，向前摆动
📍 放下腿，身体向前移动
...

=== ✅ 前进演示完成 ===
机器狗应该已经向前移动了一段距离
```

**Gazebo 中的表现**：
- 机器人站立稳定
- 执行对角步态
- **机器人向前移动**（这是关键！）
- 移动距离约 1-2 米

## 🛠️ 故障排除

### 问题 1：机器人倒下

**可能原因**：
- 关节角度过大
- 重心不稳
- 碰撞问题

**解决方法**：
1. 调整关节角度（减小抬腿高度）
2. 增加步态周期时间
3. 检查 URDF 中的惯性参数

**修改示例**（在 forward_walk_demo.py 中）：
```python
def forward_step_phase1(self):
    return [
        -0.2, 0.6, -1.3, 0.7,   # 减小角度
        0.0, 0.4, -1.0, 0.5,
        0.0, 0.4, -1.0, 0.5,
        -0.2, 0.6, -1.3, 0.7
    ]
```

### 问题 2：机器人不移动

**检查步骤**：

1. 确认控制器已加载：
```bash
ros2 control list_controllers
```

2. 确认话题正常：
```bash
ros2 topic list | grep joint_trajectory
ros2 topic hz /joint_trajectory_controller/joint_trajectory
```

3. 手动测试关节控制：
```bash
ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['j1'],
  points: [{
    positions: [0.5],
    time_from_start: {sec: 1, nanosec: 0}
  }]
}"
```

### 问题 3：Gazebo 崩溃或卡住

**解决方法**：

1. 停止所有 Gazebo 进程：
```bash
killall -9 gz ruby
```

2. 清理并重新启动：
```bash
cd ~/aperfect/carbot_ws
rm -rf build/dog2_description install/dog2_description
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
```

3. 重新启动测试

### 问题 4：机器人移动方向错误

如果机器人向后移动或向侧面移动：

**调整方法**：
- 修改 `forward_step_phase1()` 和 `forward_step_phase3()` 中的第一个关节角度
- 正值：向后摆动
- 负值：向前摆动

## 📈 下一步改进

### 1. 调整步态参数

修改以下参数以优化行走：

```python
# 在 forward_walk_demo.py 中
num_steps = 10  # 增加步数
time.sleep(0.8)  # 减少等待时间（加快步态）
```

### 2. 添加速度控制

创建一个可以接收速度命令的节点：

```python
# 订阅 /cmd_vel 话题
self.cmd_vel_sub = self.create_subscription(
    Twist,
    '/cmd_vel',
    self.cmd_vel_callback,
    10
)
```

### 3. 实现转向

添加转向功能：
- 左转：左侧腿步幅小于右侧腿
- 右转：右侧腿步幅小于左侧腿

### 4. 集成 CHAMP

如果需要更高级的步态规划：
1. 为 `dog2_champ_config` 创建 `package.xml`
2. 配置 CHAMP 参数文件
3. 使用 CHAMP 的步态生成器

参考：[QUICK_START_CHAMP.md](QUICK_START_CHAMP.md)

### 5. 实现 MPC + WBC

对于越障等高级功能：
1. 实现模型预测控制（MPC）
2. 实现全身控制（WBC）
3. 集成传感器反馈

## 📝 测试记录模板

记录你的测试结果：

```
测试日期：____________________
测试脚本：[ ] simple_walk_demo.py  [ ] forward_walk_demo.py

结果：
[ ] 机器人成功站立
[ ] 步态执行流畅
[ ] 机器人向前移动
[ ] 移动距离：_______ 米
[ ] 机器人保持稳定（未倒下）

问题：
_________________________________
_________________________________

改进建议：
_________________________________
_________________________________
```

## 🔗 相关文件

- `simple_walk_demo.py` - 基础动作演示
- `forward_walk_demo.py` - 前进行走演示
- `test_simple_walk.sh` - 自动化测试脚本
- `src/dog2_description/launch/dog2_fortress_with_control.launch.py` - 启动文件
- `DOG2_SIMPLE_WALK_TEST.md` - 简单测试指南
- `DOG2_WALKING_GUIDE.md` - 完整行走指南
- `QUICK_START_CHAMP.md` - CHAMP 集成指南

## 💡 提示

1. **首次测试建议使用 simple_walk_demo.py**，确保基本控制正常
2. **然后测试 forward_walk_demo.py**，观察实际移动效果
3. **在 Gazebo 中调整视角**，从侧面观察机器人的步态
4. **记录测试结果**，便于后续优化
5. **如果效果不理想**，先调整关节角度，再调整时间参数

## 🎯 成功标准

测试成功的标志：
- ✅ Gazebo 正常启动，无崩溃
- ✅ 控制器成功加载
- ✅ 机器人能够站立
- ✅ 机器人执行步态动作
- ✅ （forward_walk_demo）机器人向前移动至少 0.5 米
- ✅ 机器人在整个过程中保持稳定

祝测试顺利！🐕✨
