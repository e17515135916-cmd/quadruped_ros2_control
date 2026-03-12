# 快速激活控制器

## 正确的命令

```bash
# 激活控制器（使用 'active' 而不是 'start'）
./activate_controller.sh
```

或者手动运行：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 control set_controller_state joint_trajectory_controller active
```

## 验证

```bash
ros2 control list_controllers
```

应该看到：
```
joint_trajectory_controller joint_trajectory_controller/JointTrajectoryController  active
joint_state_broadcaster     joint_state_broadcaster/JointStateBroadcaster          active
```

## 测试键盘控制

```bash
./start_keyboard_control.sh
```

按 **W** 键，机器人应该移动！
