# Dog2 导轨控制器配置说明

## 问题说明

Dog2 机器人每条腿有 4 个自由度，包括 1 个移动关节（导轨）和 3 个旋转关节。为了正确控制机器人，需要：

1. **ros2_controllers.yaml** - 定义控制器配置
2. **启动文件** - **spawn 控制器**（这是关键！）

**仅修改 YAML 不够，必须在启动文件中 spawn 控制器！**

## ✅ 已完成的配置

### 1. ros2_controllers.yaml

文件位置：`src/dog2_description/config/ros2_controllers.yaml`

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    rail_position_controller:  # 导轨控制器
      type: forward_command_controller/ForwardCommandController

joint_trajectory_controller:
  ros__parameters:
    joints:
      # 只控制 12 个旋转关节（每条腿 3 个）
      - j11    # 腿 1: HAA
      - j111   # 腿 1: HFE
      - j1111  # 腿 1: KFE
      - j21    # 腿 2: HAA
      - j211   # 腿 2: HFE
      - j2111  # 腿 2: KFE
      - j31    # 腿 3: HAA
      - j311   # 腿 3: HFE
      - j3111  # 腿 3: KFE
      - j41    # 腿 4: HAA
      - j411   # 腿 4: HFE
      - j4111  # 腿 4: KFE

rail_position_controller:
  ros__parameters:
    joints:
      # 控制 4 个移动关节（导轨）
      - j1   # 腿 1: 移动关节
      - j2   # 腿 2: 移动关节
      - j3   # 腿 3: 移动关节
      - j4   # 腿 4: 移动关节
    interface_name: position
```

### 2. 启动文件更新

#### dog2_fortress_with_control.launch.py

已添加 `rail_position_controller` 的 spawner：

```python
# 加载 Joint State Broadcaster
load_joint_state_broadcaster = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['joint_state_broadcaster'],
    output='screen'
)

# 加载 Joint Trajectory Controller（控制 3 个旋转关节）
load_joint_trajectory_controller = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['joint_trajectory_controller'],
    output='screen'
)

# 加载 Rail Position Controller（控制 4 个移动关节，锁定导轨）
load_rail_position_controller = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['rail_position_controller'],
    output='screen'
)

return LaunchDescription([
    # ...
    RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[
                load_joint_state_broadcaster,
                load_joint_trajectory_controller,
                load_rail_position_controller,  # ✅ 添加导轨控制器
            ],
        )
    ),
])
```

#### dog2_fortress_auto_stand.launch.py

同样已添加 `rail_position_controller` 的 spawner。

## 🔒 锁定导轨位置

### 方法 1：使用 lock_rails.py 脚本

```bash
# 终端 1：启动 Gazebo
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_description dog2_fortress_with_control.launch.py

# 终端 2：锁定导轨
cd ~/aperfect/carbot_ws
source install/setup.bash
python3 lock_rails.py
```

这会将所有 4 个移动关节设置为 0 位置。

### 方法 2：手动发布命令

```bash
# 锁定所有导轨在零位
ros2 topic pub --once /rail_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, 0.0, 0.0, 0.0]}"

# 或者设置特定位置（例如腿 1 向后 0.05m）
ros2 topic pub --once /rail_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [-0.05, 0.0, 0.0, 0.0]}"
```

### 方法 3：在代码中控制

```python
from std_msgs.msg import Float64MultiArray

# 创建发布者
rail_publisher = self.create_publisher(
    Float64MultiArray,
    '/rail_position_controller/commands',
    10
)

# 发送导轨位置命令
msg = Float64MultiArray()
msg.data = [0.0, 0.0, 0.0, 0.0]  # 所有导轨在零位
rail_publisher.publish(msg)
```

## 📊 验证控制器加载

### 检查控制器状态

```bash
ros2 control list_controllers
```

应该看到：

```
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
joint_trajectory_controller[joint_trajectory_controller/JointTrajectoryController] active
rail_position_controller[forward_command_controller/ForwardCommandController] active
```

### 检查话题

```bash
# 查看所有控制器话题
ros2 topic list | grep controller

# 应该看到：
# /joint_state_broadcaster/...
# /joint_trajectory_controller/...
# /rail_position_controller/commands  ← 导轨控制话题
```

### 监控导轨位置

```bash
# 监控关节状态
ros2 topic echo /joint_states

# 查看 j1, j2, j3, j4 的位置
```

## 🎯 控制策略

### 策略 1：锁定导轨（推荐用于初始测试）

将所有移动关节锁定在零位，只控制旋转关节：

```python
# 启动时锁定导轨
rail_msg = Float64MultiArray()
rail_msg.data = [0.0, 0.0, 0.0, 0.0]
rail_publisher.publish(rail_msg)

# 然后只控制旋转关节
traj_msg = JointTrajectory()
traj_msg.joint_names = ['j11', 'j111', 'j1111', 'j21', 'j211', 'j2111', ...]
traj_msg.points = [...]
trajectory_publisher.publish(traj_msg)
```

### 策略 2：协调控制（用于高级运动）

同时控制移动关节和旋转关节：

```python
# 使用逆运动学求解器
from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# 求解每条腿的关节角度
ik_solver = LegIK4DOF(create_dog2_leg_geometry(1))
solution = ik_solver.solve_with_optimization(foot_position)

# 分别发送命令
# 1. 移动关节
rail_msg = Float64MultiArray()
rail_msg.data = [
    solution_leg1.prismatic,
    solution_leg2.prismatic,
    solution_leg3.prismatic,
    solution_leg4.prismatic
]
rail_publisher.publish(rail_msg)

# 2. 旋转关节
traj_msg = JointTrajectory()
traj_msg.joint_names = ['j11', 'j111', 'j1111', ...]
traj_msg.points = [...]
trajectory_publisher.publish(traj_msg)
```

## 🔧 故障排除

### 问题 1：rail_position_controller 未加载

**症状**：
```bash
ros2 control list_controllers
# 没有看到 rail_position_controller
```

**解决方法**：
1. 检查启动文件是否包含 spawner
2. 重新编译并启动：
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
ros2 launch dog2_description dog2_fortress_with_control.launch.py
```

### 问题 2：话题不存在

**症状**：
```bash
ros2 topic list | grep rail_position_controller
# 没有输出
```

**解决方法**：
- 确认控制器已加载（见问题 1）
- 检查 YAML 配置是否正确

### 问题 3：导轨不响应命令

**症状**：
发送命令后导轨位置不变

**解决方法**：
1. 检查关节限位（URDF）
2. 确认命令值在允许范围内：
   - 腿 1: -0.111 ~ 0.0
   - 腿 2: 0.0 ~ 0.111
   - 腿 3: -0.111 ~ 0.0
   - 腿 4: 0.0 ~ 0.111

## 📝 完整测试流程

### 测试 1：验证控制器加载

```bash
# 终端 1：启动 Gazebo
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
ros2 launch dog2_description dog2_fortress_with_control.launch.py

# 终端 2：检查控制器
ros2 control list_controllers

# 应该看到 3 个控制器都是 active
```

### 测试 2：锁定导轨

```bash
# 终端 2（继续）
python3 lock_rails.py

# 检查关节状态
ros2 topic echo /joint_states --once | grep -A 20 "name: \[j1"
```

### 测试 3：站立测试

```bash
# 终端 2（继续）
python3 quick_stand.py

# 机器人应该站立起来，导轨保持在零位
```

### 测试 4：行走测试

```bash
# 终端 2（继续）
python3 forward_walk_demo.py

# 机器人应该向前行走，导轨保持锁定
```

## 📚 相关文件

- `src/dog2_description/config/ros2_controllers.yaml` - 控制器配置
- `src/dog2_description/launch/dog2_fortress_with_control.launch.py` - 启动文件
- `lock_rails.py` - 导轨锁定脚本
- `DOG2_4DOF_KINEMATICS.md` - 4-DOF 运动学文档
- `DOG2_4DOF_SUMMARY.md` - 4-DOF 快速总结

## ✅ 总结

1. **YAML 配置** ✅ - 已定义 `rail_position_controller`
2. **启动文件** ✅ - 已添加 spawner
3. **锁定脚本** ✅ - 已创建 `lock_rails.py`
4. **测试流程** ✅ - 已提供完整测试步骤

**关键点**：
- 必须在启动文件中 spawn 控制器
- 导轨控制器和轨迹控制器是独立的
- 可以选择锁定导轨或协调控制
- 总共 16 个关节：4 个移动 + 12 个旋转

现在启动即可锁定导轨！🔒✨
