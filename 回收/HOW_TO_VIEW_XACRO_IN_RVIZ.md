# 如何在 RViz2 中查看 Xacro URDF 文件

本指南说明如何在 RViz2 中直接查看 `dog2.urdf.xacro` 文件。

---

## 🚀 快速启动（推荐）

### 方法 1: 使用便捷脚本

```bash
# 在工作空间根目录运行
./view_xacro_in_rviz.sh
```

这个脚本会：
- ✅ 自动检查环境
- ✅ 自动 source ROS 2 和工作空间
- ✅ 直接从 xacro 加载模型
- ✅ 启动 RViz2 和关节控制 GUI

---

## 📋 手动启动方法

### 方法 2: 使用 ROS 2 Launch

```bash
# 1. Source 环境
source /opt/ros/humble/setup.bash
source install/setup.bash

# 2. 启动 launch 文件
ros2 launch dog2_description view_dog2_xacro.launch.py
```

### 方法 3: 使用 xacro 命令行

```bash
# 1. 先将 xacro 转换为 URDF（临时）
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_temp.urdf

# 2. 启动 robot_state_publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat /tmp/dog2_temp.urdf)"

# 3. 在另一个终端启动 joint_state_publisher_gui
ros2 run joint_state_publisher_gui joint_state_publisher_gui

# 4. 在第三个终端启动 RViz2
ros2 run rviz2 rviz2 -d src/dog2_description/rviz/dog2.rviz
```

---

## 🎮 使用 RViz2

### 启动后你会看到：

1. **RViz2 窗口** - 显示 Dog2 机器人的 3D 模型
2. **Joint State Publisher GUI** - 关节控制滑块

### 关节控制：

在 Joint State Publisher GUI 中，你可以手动调整以下关节：

#### 滑动关节（Prismatic）：
- `j1`, `j2`, `j3`, `j4` - 范围: ±0.111 m

#### 髋关节（Hip）：
- `j11`, `j21`, `j31`, `j41` - 范围: ±150° (±2.618 rad)

#### 膝关节（Knee）：
- `j111`, `j211`, `j311`, `j411` - 范围: ±160° (±2.8 rad)

### RViz2 显示设置：

1. **Fixed Frame**: 设置为 `world` 或 `base_link`
2. **RobotModel**: 应该已经自动添加
3. **TF**: 可以添加 TF 显示来查看坐标系

---

## 🔧 常见问题

### Q1: 提示找不到 xacro 命令
```bash
# 安装 xacro
sudo apt install ros-humble-xacro
```

### Q2: 提示找不到 joint_state_publisher_gui
```bash
# 安装 joint_state_publisher_gui
sudo apt install ros-humble-joint-state-publisher-gui
```

### Q3: RViz2 中看不到机器人
**检查项**:
1. 确保 Fixed Frame 设置正确（通常是 `world` 或 `base_link`）
2. 检查 RobotModel 显示是否启用
3. 查看终端是否有错误信息
4. 尝试重置 RViz2 视图（View → Reset）

### Q4: 关节滑块不显示
**解决方法**:
1. 确保 `joint_state_publisher_gui` 正在运行
2. 检查是否有关节状态话题发布：
   ```bash
   ros2 topic list | grep joint
   ros2 topic echo /joint_states
   ```

### Q5: 修改 xacro 后看不到变化
**解决方法**:
1. 重启 launch 文件（xacro 会自动重新处理）
2. 或者手动重新生成 URDF：
   ```bash
   xacro src/dog2_description/urdf/dog2.urdf.xacro > src/dog2_description/urdf/dog2.urdf
   ```

---

## 📊 验证 Xacro 文件

在查看之前，建议先验证 xacro 文件：

```bash
# 1. 检查 xacro 语法
xacro --check-order src/dog2_description/urdf/dog2.urdf.xacro

# 2. 生成 URDF 并验证
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/test.urdf
check_urdf /tmp/test.urdf

# 3. 验证关节限制
python3 scripts/validate_urdf_limits.py /tmp/test.urdf
```

---

## 🎯 查看不同版本的 URDF

如果你想查看其他版本的 URDF 文件：

### 查看 Gazebo 优化版本：
```bash
ros2 launch dog2_description view_dog2_gazebo.launch.py
```

### 查看标准 URDF 版本：
```bash
ros2 launch dog2_description view_dog2.launch.py
```

### 查看可视化版本：
```bash
# 需要修改 launch 文件指向 dog2_visual.urdf
```

---

## 📝 Launch 文件说明

### view_dog2_xacro.launch.py

这个 launch 文件的特点：

1. **直接处理 xacro**: 使用 `Command(['xacro ', xacro_file])` 在运行时处理
2. **实时更新**: 修改 xacro 后重启 launch 即可看到变化
3. **完整功能**: 包含 robot_state_publisher、joint_state_publisher_gui 和 RViz2

**关键代码**:
```python
robot_description_content = ParameterValue(
    Command(['xacro ', xacro_file]),
    value_type=str
)
```

这行代码确保每次启动时都会重新处理 xacro 文件。

---

## 🔄 工作流程

### 开发流程：

1. **编辑 xacro 文件**
   ```bash
   vim src/dog2_description/urdf/dog2.urdf.xacro
   ```

2. **在 RViz2 中查看**
   ```bash
   ./view_xacro_in_rviz.sh
   ```

3. **调整关节查看效果**
   - 使用 Joint State Publisher GUI 滑块

4. **满意后生成最终 URDF**
   ```bash
   xacro src/dog2_description/urdf/dog2.urdf.xacro > src/dog2_description/urdf/dog2.urdf
   ```

5. **验证**
   ```bash
   python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf
   ```

---

## 🎨 RViz2 配置技巧

### 推荐的显示设置：

1. **Grid** - 显示地面网格
2. **TF** - 显示坐标系变换
3. **RobotModel** - 显示机器人模型
4. **Axes** - 在每个连杆显示坐标轴

### 保存自定义配置：

```bash
# 在 RViz2 中: File → Save Config As
# 保存到: src/dog2_description/rviz/dog2_custom.rviz
```

---

## 📚 相关文档

- `URDF_FILES_SUMMARY.md` - URDF 文件完整说明
- `src/dog2_description/README_JOINT_LIMITS.md` - 关节限制详细说明
- `src/dog2_description/urdf/README_URDF_FILES.md` - URDF 文件技术文档

---

## 🆘 获取帮助

如果遇到问题：

1. 查看终端错误信息
2. 检查 ROS 2 话题：`ros2 topic list`
3. 检查节点状态：`ros2 node list`
4. 查看 TF 树：`ros2 run tf2_tools view_frames`

---

**最后更新**: 2026-01-26  
**维护者**: Dog2 开发团队
