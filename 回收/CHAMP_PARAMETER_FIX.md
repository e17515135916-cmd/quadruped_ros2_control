# CHAMP 参数传递修复说明

## 问题描述

CHAMP `quadruped_controller_node` 节点无法启动，报错：
```
terminate called after throwing an instance of 'std::runtime_error'
what():  No links config file provided
```

## 根本原因

CHAMP 节点无法正确读取配置文件参数。原因是：

1. **参数传递方式不正确**：将配置文件路径作为 `parameters` 列表传递，但 CHAMP 期望通过 `--params-file` 参数读取
2. **robot_description 缺失**：CHAMP 需要 `robot_description` 参数来解析 URDF

## 解决方案

修改 `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py` 中的 CHAMP 节点定义：

### 修改前
```python
parameters=[
    robot_description,
    gait_config,      # ❌ 错误：作为参数传递
    joints_config,    # ❌ 错误：作为参数传递
    links_config,     # ❌ 错误：作为参数传递
    {
        'gazebo': True,
        ...
    }
],
```

### 修改后
```python
parameters=[
    robot_description,  # ✅ 正确：robot_description 作为参数
    {
        'gazebo': True,
        ...
    }
],
arguments=[
    '--ros-args',
    '--params-file', gait_config,    # ✅ 正确：使用 --params-file
    '--params-file', joints_config,  # ✅ 正确：使用 --params-file
    '--params-file', links_config,   # ✅ 正确：使用 --params-file
],
```

## 应用修复

### 方法 1：自动修复（推荐）
```bash
# 1. 运行测试脚本（会自动编译）
./test_champ_fix.sh

# 2. 在另一个终端启动 Gazebo
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py

# 3. 等待 7 秒后验证
ros2 node list | grep quadruped
```

### 方法 2：手动步骤
```bash
# 1. 修复已自动完成（fix_champ_launch_params.py）

# 2. 重新编译
colcon build --packages-select dog2_champ_config --symlink-install

# 3. 重新加载环境
source install/setup.bash

# 4. 清理残留进程
./clean_and_restart.sh

# 5. 启动 Gazebo
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

## 验证修复

### 1. 检查 CHAMP 节点是否启动
```bash
ros2 node list | grep quadruped
```
期望输出：`/quadruped_controller`

### 2. 检查 /cmd_vel 话题
```bash
ros2 topic list | grep cmd_vel
```
期望输出：`/cmd_vel`

### 3. 测试键盘控制
```bash
./start_keyboard_control.sh
```
按 W 键，机器人应该向前移动

## 技术细节

### ROS 2 参数传递方式

ROS 2 节点有两种方式接收参数：

1. **parameters 列表**：用于传递简单的键值对参数
   ```python
   parameters=[
       {'param_name': 'value'},
       robot_description,  # 字典类型
   ]
   ```

2. **arguments + --params-file**：用于从 YAML 文件加载参数
   ```python
   arguments=[
       '--ros-args',
       '--params-file', '/path/to/config.yaml',
   ]
   ```

### CHAMP 配置文件格式

CHAMP 的配置文件使用特殊的命名空间格式：
```yaml
/**:
  ros__parameters:
    links_map:
      base: base_link
      left_front:
        - lf_hip_link
        - lf_upper_leg_link
        ...
```

这种格式需要通过 `--params-file` 加载，而不能直接作为 Python 字典传递。

## 相关文件

- `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py` - 主启动文件（已修复）
- `src/dog2_champ_config/config/gait/gait.yaml` - 步态配置
- `src/dog2_champ_config/config/joints/joints.yaml` - 关节映射
- `src/dog2_champ_config/config/links/links.yaml` - 连杆映射
- `fix_champ_launch_params.py` - 自动修复脚本
- `test_champ_fix.sh` - 测试脚本

## 下一步

修复完成后，继续 Task 7.1 的验证：
1. ✅ 键盘控制脚本已完成
2. ✅ CHAMP 节点参数传递已修复
3. ⏳ 等待验证机器人是否能响应键盘命令

## 参考

- ROS 2 Launch 文档: https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html
- CHAMP 文档: https://github.com/chvmp/champ
