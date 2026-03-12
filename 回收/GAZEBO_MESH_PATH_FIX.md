# Gazebo Mesh 路径问题修复说明

## 问题描述

Gazebo 启动时出现大量 `Failed to find mesh file` 错误，导致：
- 机器人模型在 Gazebo 中不显示或不可见
- gzserver 崩溃（Exit code -11）
- 控制台满屏红色报错信息

## 根本原因

**路径解析不匹配：**
- **ROS 2 (URDF)** 使用：`package://dog2_description/meshes/...`
- **Gazebo** 期望：`model://` 路径或通过 `GAZEBO_MODEL_PATH` 环境变量查找
- **问题**：Gazebo 不知道如何解析 `package://` 协议，也不知道 `dog2_description` 包在哪里

## 解决方案

在 Launch 文件中添加环境变量设置，告诉 Gazebo 在哪里找模型文件。

### 修改的文件

`src/dog2_description/launch/gazebo_dog2_final.launch.py`

### 关键修改

1. **导入 SetEnvironmentVariable**：
```python
from launch.actions import SetEnvironmentVariable
```

2. **设置 GAZEBO_MODEL_PATH**：
```python
# 获取包的父目录（包含所有 ROS 2 包）
gazebo_model_path = os.path.join(pkg_dog2_description, '..')
if 'GAZEBO_MODEL_PATH' in os.environ:
    gazebo_model_path = os.environ['GAZEBO_MODEL_PATH'] + ':' + gazebo_model_path

set_gazebo_model_path = SetEnvironmentVariable(
    name='GAZEBO_MODEL_PATH',
    value=gazebo_model_path
)
```

3. **设置 GAZEBO_RESOURCE_PATH**：
```python
gazebo_resource_path = pkg_dog2_description
if 'GAZEBO_RESOURCE_PATH' in os.environ:
    gazebo_resource_path = os.environ['GAZEBO_RESOURCE_PATH'] + ':' + gazebo_resource_path

set_gazebo_resource_path = SetEnvironmentVariable(
    name='GAZEBO_RESOURCE_PATH',
    value=gazebo_resource_path
)
```

4. **在 LaunchDescription 中首先设置环境变量**：
```python
return LaunchDescription([
    # 首先设置环境变量（在启动 Gazebo 之前）
    set_gazebo_model_path,
    set_gazebo_resource_path,
    # ... 其他启动项
])
```

## 工作原理

1. **GAZEBO_MODEL_PATH**：告诉 Gazebo 在哪些目录中查找模型包
   - 设置为包的父目录，这样 Gazebo 可以找到 `dog2_description` 包
   - 保留现有的环境变量值（如果有）

2. **GAZEBO_RESOURCE_PATH**：告诉 Gazebo 在哪里查找资源文件（如 meshes）
   - 设置为 `dog2_description` 包的路径
   - 这样 Gazebo 可以直接访问 `meshes/` 目录

3. **路径解析**：
   - URDF 中的 `package://dog2_description/meshes/base_link.STL`
   - Gazebo 通过 `GAZEBO_MODEL_PATH` 找到 `dog2_description` 包
   - 然后访问 `meshes/base_link.STL` 文件

## 测试方法

### 方法 1：使用测试脚本
```bash
./test_gazebo_mesh_fix.sh
```

### 方法 2：手动启动
```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_description gazebo_dog2_final.launch.py
```

## 预期结果

✅ **成功标志：**
- Gazebo 窗口正常打开
- 机器人模型完整显示（所有腿部和身体部件可见）
- 控制台没有 `Failed to find mesh file` 错误
- gzserver 稳定运行，不崩溃

❌ **如果仍有问题：**
1. 检查 meshes 文件是否存在：
   ```bash
   ls -la src/dog2_description/meshes/
   ```

2. 验证包是否正确安装：
   ```bash
   ros2 pkg prefix dog2_description
   ```

3. 检查环境变量是否正确设置（在 launch 文件运行时）：
   ```bash
   echo $GAZEBO_MODEL_PATH
   echo $GAZEBO_RESOURCE_PATH
   ```

## 相关文件

- **Launch 文件**：`src/dog2_description/launch/gazebo_dog2_final.launch.py`
- **URDF 文件**：`src/dog2_description/urdf/dog2.urdf.xacro`
- **Mesh 文件**：`src/dog2_description/meshes/*.STL`
- **测试脚本**：`test_gazebo_mesh_fix.sh`

## 技术要点

这个修复方法适用于所有使用 `package://` 路径引用资源的 ROS 2 + Gazebo 项目。关键是：

1. **在 Launch 文件中设置环境变量**（不是在 shell 中）
2. **在启动 Gazebo 之前设置**（顺序很重要）
3. **保留现有环境变量**（使用 `:` 连接）

## 日期

修复日期：2026-01-27
