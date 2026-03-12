# 🚀 Dog2 键盘控制 - 从这里开始

## ⚠️ 重要：使用前必须 Source 环境

在运行任何命令之前，**必须先 source ROS 2 环境**！

---

## 📋 方法一：使用自动脚本（推荐，已包含 source）

这些脚本会自动 source 环境，最简单！

### 步骤 1：启动 Gazebo 仿真

在终端 1 中：

```bash
cd ~/aperfect/carbot_ws
./quick_start_keyboard_control.sh
```

脚本会自动：
- ✅ Source ROS 2 Humble 环境
- ✅ Source 工作空间环境
- ✅ 检查编译状态
- ✅ 启动 Gazebo + CHAMP 系统

### 步骤 2：启动键盘控制

等待约 7 秒后，在终端 2 中：

```bash
cd ~/aperfect/carbot_ws
./start_keyboard_control.sh
```

脚本会自动：
- ✅ Source ROS 2 Humble 环境
- ✅ Source 工作空间环境
- ✅ 检查系统状态
- ✅ 启动键盘控制

### 步骤 3：控制机器人

按 **W** 键，机器人就会向前走！

---

## 📋 方法二：手动启动（需要手动 source）

如果你想手动控制每一步：

### 步骤 0：Source 环境（必须！）

**在每个新终端中都要执行：**

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### 步骤 1：启动 Gazebo 仿真

在终端 1 中：

```bash
# 先 source 环境（如果还没做）
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# 启动系统
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

### 步骤 2：启动键盘控制

等待约 7 秒后，在终端 2 中：

```bash
# 先 source 环境（必须！）
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# 启动键盘控制
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

---

## 🔍 为什么必须 Source 环境？

### Source 的作用

```bash
source /opt/ros/humble/setup.bash    # 加载 ROS 2 系统环境
source install/setup.bash             # 加载你的工作空间环境
```

这两个命令会：
1. 设置 ROS 2 的环境变量（`ROS_DISTRO`, `AMENT_PREFIX_PATH` 等）
2. 添加 ROS 2 命令到 PATH（`ros2`, `colcon` 等）
3. 加载你编译的包（`dog2_champ_config`, `dog2_description` 等）
4. 设置 Python 路径，让 ROS 2 能找到你的包

### 如果不 Source 会怎样？

❌ **错误示例：**

```bash
# 没有 source 环境
cd ~/aperfect/carbot_ws
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

**结果：**
```
bash: ros2: command not found
```

或者：

```
Package 'dog2_champ_config' not found
```

---

## ✅ 验证环境是否正确 Source

运行以下命令检查：

```bash
# 检查 ROS 2 环境
echo $ROS_DISTRO
# 应该输出: humble

# 检查 ros2 命令
which ros2
# 应该输出: /opt/ros/humble/bin/ros2

# 检查工作空间包
ros2 pkg list | grep dog2
# 应该看到: dog2_champ_config, dog2_description 等
```

如果这些命令都正常，说明环境已正确 source！

---

## 🎮 键盘控制说明

| 按键 | 功能 |
|------|------|
| W | 向前 |
| S | 向后 |
| A | 向左 |
| D | 向右 |
| Q | 左转 |
| E | 右转 |
| 空格 | 停止 |
| X | 退出 |

---

## 🔧 常见问题

### Q1: 提示 "ros2: command not found"

**原因：** 没有 source ROS 2 环境

**解决：**
```bash
source /opt/ros/humble/setup.bash
```

### Q2: 提示 "Package 'dog2_champ_config' not found"

**原因：** 没有 source 工作空间环境

**解决：**
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
```

### Q3: 提示 "install/setup.bash: No such file or directory"

**原因：** 工作空间还没编译

**解决：**
```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select dog2_champ_config dog2_description champ_base champ_msgs
source install/setup.bash
```

### Q4: 每次都要 source 吗？

**是的！** 每个新终端都需要 source。

**可选：添加到 ~/.bashrc 自动 source**

编辑 `~/.bashrc`：

```bash
nano ~/.bashrc
```

在文件末尾添加：

```bash
# ROS 2 Humble
source /opt/ros/humble/setup.bash

# Dog2 工作空间（根据你的实际路径修改）
source ~/aperfect/carbot_ws/install/setup.bash
```

保存后，重新加载：

```bash
source ~/.bashrc
```

**注意：** 如果你有多个 ROS 2 工作空间，不建议自动 source，因为可能会冲突。

---

## 📚 相关文档

- `KEYBOARD_CONTROL_QUICK_START.md` - 详细启动指南
- `SYSTEM_READINESS_CHECK.md` - 系统就绪检查
- `src/dog2_champ_config/scripts/README_KEYBOARD_CONTROL.md` - 键盘控制详细说明

---

## 🎯 快速命令参考卡

### 使用自动脚本（推荐）

```bash
# 终端 1
cd ~/aperfect/carbot_ws
./quick_start_keyboard_control.sh

# 终端 2（等待 7 秒）
cd ~/aperfect/carbot_ws
./start_keyboard_control.sh
```

### 手动启动

```bash
# 终端 1
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

# 终端 2
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
```

---

## ✅ 准备好了吗？

如果你已经：
- ✅ 理解了 source 环境的重要性
- ✅ 知道如何 source 环境
- ✅ 选择了启动方法（自动脚本或手动）

那就开始吧！🚀

```bash
cd ~/aperfect/carbot_ws
./quick_start_keyboard_control.sh
```

祝你使用愉快！
