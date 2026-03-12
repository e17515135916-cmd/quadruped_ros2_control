# Dog2 Motion Control

蜘蛛机器人基础运动控制系统，实现爬行步态和静态稳定行走。

## 功能特性

- **静态稳定步态**: 爬行步态确保至少三条腿始终着地
- **16通道控制**: 4个直线导轨（锁定） + 12个旋转关节
- **运动学求解**: 3-DOF逆运动学和正运动学
- **轨迹规划**: 平滑的关节轨迹生成
- **ROS 2集成**: 完整的ROS 2接口支持

## 安装

### 依赖项

```bash
# 安装Python依赖
pip3 install -r requirements.txt
```

### 构建

```bash
# 在ROS 2工作空间根目录
colcon build --packages-select dog2_motion_control
source install/setup.bash
```

## 使用方法

### 启动控制器

```bash
ros2 launch dog2_motion_control spider_controller.launch.py
```

### 发送速度命令

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest test/test_kinematics.py

# 运行属性测试
pytest test/test_properties.py
```

## 架构

```
dog2_motion_control/
├── spider_robot_controller.py  # 主控制器
├── kinematics_solver.py        # 运动学求解器
├── gait_generator.py           # 步态生成器
├── trajectory_planner.py       # 轨迹规划器
└── joint_controller.py         # 关节控制器
```

## 配置

步态参数配置文件位于 `config/gait_params.yaml`。

主要参数：
- `stride_length`: 步长（米）
- `stride_height`: 步高（米）
- `cycle_time`: 步态周期（秒）
- `duty_factor`: 支撑相占比

## 开发

参考设计文档：`.kiro/specs/spider-robot-basic-motion/design.md`

## 许可证

Apache-2.0
