# 控制器激活完整指南

## 当前状态

根据用户提供的日志：
```
joint_trajectory_controller joint_trajectory_controller/JointTrajectoryController  inactive
joint_state_broadcaster     joint_state_broadcaster/JointStateBroadcaster          active
```

**问题**：`joint_trajectory_controller` 已加载但处于 `inactive` 状态，需要激活才能控制机器人。

## 解决方案

### 步骤 1：确认 Gazebo 正在运行

在一个终端中，Gazebo 应该已经启动：
```bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

等待约 7 秒让所有节点完全启动。

### 步骤 2：激活控制器

在**另一个终端**中运行：

```bash
./activate_controller.sh
```

这个脚本会：
1. 激活 `joint_trajectory_controller`
2. 验证激活状态
3. 显示下一步操作

### 步骤 3：测试键盘控制

激活成功后，运行：

```bash
./start_keyboard_control.sh
```

然后按 **W** 键，机器人应该开始向前移动！

## 预期输出

### 激活前
```
joint_trajectory_controller joint_trajectory_controller/JointTrajectoryController  inactive
joint_state_broadcaster     joint_state_broadcaster/JointStateBroadcaster          active
```

### 激活后
```
joint_trajectory_controller joint_trajectory_controller/JointTrajectoryController  active
joint_state_broadcaster     joint_state_broadcaster/JointStateBroadcaster          active
```

## 故障排除

### 问题 1：激活失败

**错误信息**：
```
Error activating controller, check controller_manager logs
```

**解决方法**：
1. 检查 Gazebo 终端的日志，查找错误信息
2. 确认硬件接口已加载：
   ```bash
   ros2 control list_hardware_interfaces
   ```
   应该看到 16 个接口（4 个滑动副 + 12 个腿部关节）

3. 如果硬件接口不完整，重启 Gazebo

### 问题 2：控制器激活但机器人不动

**可能原因**：
1. CHAMP quadruped_controller 未发布命令
2. 关节轨迹话题连接有问题

**检查方法**：
```bash
# 检查 CHAMP 是否在发布轨迹
ros2 topic echo /joint_trajectory_controller/joint_trajectory --once

# 检查 /cmd_vel 是否有订阅者
ros2 topic info /cmd_vel
```

### 问题 3：控制器配置错误

**检查控制器配置**：
```bash
ros2 control list_controllers
ros2 param get /controller_manager joint_trajectory_controller.joints
```

应该看到 12 个 CHAMP 关节名称：
- lf_haa_joint, lf_hfe_joint, lf_kfe_joint
- rf_haa_joint, rf_hfe_joint, rf_kfe_joint
- lh_haa_joint, lh_hfe_joint, lh_kfe_joint
- rh_haa_joint, rh_hfe_joint, rh_kfe_joint

## 自动激活（可选）

如果希望启动时自动激活控制器，可以修改启动文件：

编辑 `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py`，在 spawner 参数中添加 `--activate`：

```python
joint_trajectory_controller = TimerAction(
    period=4.0,
    actions=[
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_trajectory_controller', '--activate'],  # 添加这个
            output='screen',
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        )
    ]
)
```

然后重新编译：
```bash
colcon build --packages-select dog2_champ_config --symlink-install
```

## 快速测试流程

```bash
# 终端 1：启动 Gazebo
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

# 等待 7 秒...

# 终端 2：激活控制器
./activate_controller.sh

# 终端 2：测试键盘控制
./start_keyboard_control.sh

# 按 W 键 - 机器人应该移动！
```

## 成功标志

当一切正常时，你应该看到：
1. ✅ 两个控制器都是 `active` 状态
2. ✅ 按 W 键后，终端显示 "向前 ⬆️"
3. ✅ Gazebo 中机器人开始移动
4. ✅ 腿部关节有运动

## 下一步

一旦机器人能够移动，Task 7.1 就完成了！可以继续测试其他功能：
- A/D 键：左右平移
- Q/E 键：左右转向
- S 键：后退
- 空格：停止
