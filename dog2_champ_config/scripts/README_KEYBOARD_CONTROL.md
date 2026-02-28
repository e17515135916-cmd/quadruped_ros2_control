# Dog2 键盘控制脚本使用说明

## 概述

`dog2_keyboard_control.py` 是一个用于通过键盘控制 Dog2 四足机器人的遥操作脚本。

## 功能特性

- ✅ 实时键盘输入控制
- ✅ 支持前进/后退、左右平移、原地旋转
- ✅ 发布速度命令到 `/cmd_vel` 话题
- ✅ 终端实时显示当前命令
- ✅ 紧急停止功能

## 按键说明

| 按键 | 功能 | 速度参数 |
|------|------|----------|
| W/w | 向前移动 | linear.x = +0.3 m/s |
| S/s | 向后移动 | linear.x = -0.3 m/s |
| A/a | 向左平移 | linear.y = +0.2 m/s |
| D/d | 向右平移 | linear.y = -0.2 m/s |
| Q/q | 左转 | angular.z = +0.5 rad/s |
| E/e | 右转 | angular.z = -0.5 rad/s |
| 空格 | 停止所有运动 | 所有速度 = 0 |
| X/x | 退出程序 | 退出并停止机器人 |

## 使用方法

### 前提条件

1. 确保 Gazebo Fortress 和 CHAMP 系统已启动：
```bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

2. 等待系统完全启动（约7秒）

### 启动键盘控制

在新的终端中运行：

```bash
# 方法1：直接运行脚本
./src/dog2_champ_config/scripts/dog2_keyboard_control.py

# 方法2：使用 python3
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py

# 方法3：使用 ros2 run（如果已安装）
ros2 run dog2_champ_config dog2_keyboard_control.py
```

### 操作示例

1. **向前行走**：按 `W` 键，机器人开始向前移动
2. **停止**：按 `空格` 键，机器人立即停止
3. **左转**：按 `Q` 键，机器人原地左转
4. **退出**：按 `X` 键，程序退出并停止机器人

## 速度参数调整

如需调整速度参数，编辑脚本中的以下变量：

```python
self.linear_speed = 0.3    # 前进/后退速度 (m/s)
self.angular_speed = 0.5   # 旋转速度 (rad/s)
self.lateral_speed = 0.2   # 侧向移动速度 (m/s)
```

### 推荐速度范围

- **linear_speed**: 0.1 - 0.5 m/s（根据设计文档，最大为 0.5 m/s）
- **angular_speed**: 0.2 - 1.0 rad/s（根据设计文档，最大为 1.0 rad/s）
- **lateral_speed**: 0.1 - 0.3 m/s（根据设计文档，最大为 0.3 m/s）

## 故障排除

### 问题：按键无响应

**解决方案**：
1. 确保终端窗口处于活动状态（点击终端窗口）
2. 检查 `/cmd_vel` 话题是否正常：
```bash
ros2 topic echo /cmd_vel
```

### 问题：机器人不移动

**解决方案**：
1. 检查 CHAMP 控制器是否运行：
```bash
ros2 node list | grep quadruped_controller
```

2. 检查关节控制器是否加载：
```bash
ros2 control list_controllers
```

### 问题：程序无法启动

**解决方案**：
1. 确保脚本有执行权限：
```bash
chmod +x src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

2. 检查 ROS 2 环境是否正确配置：
```bash
source install/setup.bash
```

## 技术细节

### 发布的消息类型

```python
geometry_msgs/Twist:
  linear:
    x: float64  # 前进/后退速度
    y: float64  # 左右平移速度
    z: float64  # 未使用（始终为0）
  angular:
    x: float64  # 未使用（始终为0）
    y: float64  # 未使用（始终为0）
    z: float64  # 旋转速度
```

### 话题信息

- **话题名称**: `/cmd_vel`
- **消息类型**: `geometry_msgs/msg/Twist`
- **发布频率**: 按键触发（非周期性）

## 安全注意事项

⚠️ **重要提示**：

1. 在使用前确保机器人周围有足够的空间
2. 随时准备按 `空格` 键紧急停止
3. 首次使用时建议使用较低的速度参数
4. 在 Gazebo 仿真中测试后再部署到真实硬件

## 相关文档

- [CHAMP Gazebo Motion 需求文档](../../.kiro/specs/champ-gazebo-motion/requirements.md)
- [CHAMP Gazebo Motion 设计文档](../../.kiro/specs/champ-gazebo-motion/design.md)
- [快速启动指南](../../../QUICK_START_GAZEBO_FORTRESS.md)

## 验证需求

该脚本满足以下需求（来自 requirements.md）：

- ✅ 需求 7.1: 提供键盘遥操作脚本
- ✅ 需求 7.2: W 键向前移动
- ✅ 需求 7.3: S 键向后移动
- ✅ 需求 7.4: A 键向左移动
- ✅ 需求 7.5: D 键向右移动
- ✅ 需求 7.6: Q 键左转
- ✅ 需求 7.7: E 键右转
- ✅ 需求 7.8: 空格键停止
- ✅ 需求 7.9: 在终端显示当前速度命令

## 版本历史

- v1.0 (2026-01-21): 初始版本，实现所有基本功能
