# Dog2 简单行走测试指南

## 概述

这个测试使用直接的关节轨迹控制来实现机器狗的基本行走，不依赖 CHAMP 框架。

## 测试内容

`simple_walk_demo.py` 脚本会执行以下动作序列：

1. **站立姿态** - 机器狗站立起来
2. **对角步态演示** - 模拟 trot 步态（对角线腿同时抬起）
   - 抬起前左腿和后右腿
   - 抬起前右腿和后左腿
   - 循环 3 次
3. **回到站立** - 返回站立姿态
4. **单腿抬起演示** - 依次抬起每条腿
5. **完成** - 保持站立姿态

## 快速开始

### 方法 1：使用自动化脚本（推荐）

```bash
# 终端 1：启动 Gazebo 和控制器
cd ~/aperfect/carbot_ws
./test_simple_walk.sh

# 等待 Gazebo 完全启动后，在终端 2 运行：
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 simple_walk_demo.py
```

### 方法 2：手动步骤

#### 终端 1：启动 Gazebo Fortress + 控制器

```bash
cd ~/aperfect/carbot_ws

# 编译 dog2_description 包
colcon build --packages-select dog2_description --symlink-install

# 加载环境
source install/setup.bash

# 启动 Gazebo 和控制器
ros2 launch dog2_description dog2_fortress_with_control.launch.py
```

#### 终端 2：运行行走演示

等待 Gazebo 完全启动并且控制器加载完成后：

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 simple_walk_demo.py
```

## 验证步骤

### 1. 检查 Gazebo 是否正常启动

在终端 1 中，你应该看到：

```
[INFO] [robot_state_publisher]: Robot initialized
[INFO] [spawner-joint_state_broadcaster]: Loaded joint_state_broadcaster
[INFO] [spawner-joint_trajectory_controller]: Loaded joint_trajectory_controller
```

### 2. 检查控制器是否加载

```bash
# 在新终端中运行
ros2 control list_controllers
```

应该看到：

```
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active
```

### 3. 检查关节状态

```bash
ros2 topic echo /joint_states --once
```

应该看到 16 个关节的状态信息。

### 4. 观察行走演示

运行 `simple_walk_demo.py` 后，在终端 2 中你应该看到：

```
🐕 Dog2 简单行走演示启动
等待 2 秒...

=== 阶段 1: 站立 ===
📍 站立姿态

=== 阶段 2: 对角步态演示 ===
  步态循环 1/3
📍 抬起前左腿和后右腿
📍 抬起前右腿和后左腿
  步态循环 2/3
...

=== ✅ 演示完成 ===
机器狗保持站立姿态
```

在 Gazebo GUI 中，你应该看到机器狗执行相应的动作。

## 关节命名

Dog2 机器狗有 16 个关节（4 条腿 × 4 个关节）：

- **腿 1（前左）**: j1, j11, j111, j1111
- **腿 2（前右）**: j2, j21, j211, j2111
- **腿 3（后左）**: j3, j31, j311, j3111
- **腿 4（后右）**: j4, j41, j411, j4111

每条腿的关节顺序：
1. 髋关节（横向摆动）
2. 髋关节（纵向摆动）
3. 膝关节（大腿）
4. 踝关节（小腿）

## 故障排除

### 问题 1：找不到启动文件

```
Package 'dog2_description' not found
```

**解决方法**：
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
```

### 问题 2：控制器未加载

```
[ERROR] [controller_manager]: Could not load controller
```

**解决方法**：
- 确保 Gazebo 完全启动
- 检查 `src/dog2_description/config/ros2_controllers.yaml` 配置
- 重启 Gazebo

### 问题 3：机器人倒下

如果机器人在演示过程中倒下，可能是：
- 关节角度设置不合适
- 重力设置问题
- 碰撞检测问题

**解决方法**：
- 调整 `simple_walk_demo.py` 中的关节角度
- 检查 URDF 中的惯性参数

### 问题 4：机器人不动

**检查步骤**：

1. 确认控制器已加载：
```bash
ros2 control list_controllers
```

2. 确认话题存在：
```bash
ros2 topic list | grep joint_trajectory
```

3. 手动发送测试命令：
```bash
ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['j1', 'j11', 'j111', 'j1111', 'j2', 'j21', 'j211', 'j2111', 'j3', 'j31', 'j311', 'j3111', 'j4', 'j41', 'j411', 'j4111'],
  points: [{
    positions: [0.0, 0.4, -1.0, 0.5, 0.0, 0.4, -1.0, 0.5, 0.0, 0.4, -1.0, 0.5, 0.0, 0.4, -1.0, 0.5],
    time_from_start: {sec: 2, nanosec: 0}
  }]
}"
```

## 下一步

### 选项 A：继续使用简单控制

如果这个演示工作正常，你可以：
1. 修改 `simple_walk_demo.py` 添加更多步态
2. 实现前进、后退、转向功能
3. 添加速度控制

### 选项 B：集成 CHAMP 框架

如果需要更高级的步态规划，可以：
1. 为 `dog2_champ_config` 创建 `package.xml`
2. 配置 CHAMP 参数
3. 使用 CHAMP 的步态生成器

### 选项 C：实现 MPC + WBC

对于越障等高级功能：
1. 实现模型预测控制（MPC）
2. 实现全身控制（WBC）
3. 集成传感器反馈

## 相关文件

- `simple_walk_demo.py` - 行走演示脚本
- `src/dog2_description/launch/dog2_fortress_with_control.launch.py` - 完整启动文件
- `src/dog2_description/launch/gazebo_fortress_gui.launch.py` - GUI 启动文件
- `src/dog2_description/config/ros2_controllers.yaml` - 控制器配置
- `test_simple_walk.sh` - 自动化测试脚本

## 参考资料

- [DOG2_WALKING_GUIDE.md](DOG2_WALKING_GUIDE.md) - 完整的行走实现指南
- [QUICK_START_CHAMP.md](QUICK_START_CHAMP.md) - CHAMP 快速开始指南
- [GAZEBO_FORTRESS_MIGRATION.md](GAZEBO_FORTRESS_MIGRATION.md) - Gazebo Fortress 迁移文档
