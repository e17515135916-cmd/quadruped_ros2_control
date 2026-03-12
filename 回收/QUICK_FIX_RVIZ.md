# 快速修复：在 RViz2 中查看 Xacro

## ❌ 你遇到的错误

```
Package 'dog2_description' not found
```

## ✅ 解决方案

### 步骤 1: 切换到工作空间目录

```bash
cd /home/dell/aperfect/carbot_ws
```

**重要**: 你必须在工作空间根目录运行命令！

### 步骤 2: 编译工作空间

```bash
# Source ROS 2 环境
source /opt/ros/humble/setup.bash

# 编译 dog2_description 包
colcon build --packages-select dog2_description --symlink-install
```

### 步骤 3: Source 工作空间

```bash
source install/setup.bash
```

### 步骤 4: 验证包是否可用

```bash
ros2 pkg list | grep dog2_description
```

应该看到输出：`dog2_description`

### 步骤 5: 启动 RViz2

```bash
ros2 launch dog2_description view_dog2_xacro.launch.py
```

---

## 🚀 或者使用一键脚本（推荐）

脚本已经更新，会自动处理所有步骤：

```bash
cd /home/dell/aperfect/carbot_ws
./view_xacro_in_rviz.sh
```

---

## 📋 完整命令序列（复制粘贴）

```bash
# 1. 切换到工作空间
cd /home/dell/aperfect/carbot_ws

# 2. Source ROS 2
source /opt/ros/humble/setup.bash

# 3. 编译
colcon build --packages-select dog2_description --symlink-install

# 4. Source 工作空间
source install/setup.bash

# 5. 启动
ros2 launch dog2_description view_dog2_xacro.launch.py
```

---

## 🔍 常见问题

### Q: 为什么找不到包？

**A**: 因为你在 home 目录 (`~`) 运行命令，而不是在工作空间目录。

**错误示例**:
```bash
dell@dell-Precision-3680:~$ ros2 launch dog2_description view_dog2_xacro.launch.py
# ❌ 在 home 目录，找不到包
```

**正确示例**:
```bash
dell@dell-Precision-3680:~/aperfect/carbot_ws$ ros2 launch dog2_description view_dog2_xacro.launch.py
# ✅ 在工作空间目录
```

### Q: 编译失败怎么办？

**A**: 检查依赖是否安装：

```bash
# 安装依赖
sudo apt update
sudo apt install ros-humble-xacro
sudo apt install ros-humble-joint-state-publisher-gui
sudo apt install ros-humble-robot-state-publisher
sudo apt install ros-humble-rviz2

# 重新编译
cd /home/dell/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
```

### Q: Source 后还是找不到包？

**A**: 确保你在正确的终端 source 了环境：

```bash
# 每个新终端都需要 source
source /opt/ros/humble/setup.bash
source /home/dell/aperfect/carbot_ws/install/setup.bash

# 或者添加到 ~/.bashrc（一劳永逸）
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source /home/dell/aperfect/carbot_ws/install/setup.bash" >> ~/.bashrc
```

---

## 💡 最佳实践

### 方法 1: 使用脚本（最简单）

```bash
cd /home/dell/aperfect/carbot_ws
./view_xacro_in_rviz.sh
```

### 方法 2: 创建别名

在 `~/.bashrc` 中添加：

```bash
alias view_dog2='cd /home/dell/aperfect/carbot_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch dog2_description view_dog2_xacro.launch.py'
```

然后：
```bash
source ~/.bashrc
view_dog2  # 在任何目录都可以运行
```

---

## 🎯 验证清单

在启动前，确保：

- [ ] 在工作空间目录：`cd /home/dell/aperfect/carbot_ws`
- [ ] 已 source ROS 2：`source /opt/ros/humble/setup.bash`
- [ ] 已编译包：`colcon build --packages-select dog2_description`
- [ ] 已 source 工作空间：`source install/setup.bash`
- [ ] 包可用：`ros2 pkg list | grep dog2_description`

全部 ✅ 后再运行 launch 文件！

---

**最后更新**: 2026-01-26
