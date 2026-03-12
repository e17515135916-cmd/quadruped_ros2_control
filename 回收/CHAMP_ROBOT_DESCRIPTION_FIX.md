# CHAMP robot_description 参数修复

## 问题诊断

### 错误信息
```
[ERROR] [rclcpp]: Failed to parse urdf string
terminate called after throwing an instance of 'std::runtime_error'
what():  No links config file provided
[ERROR] [quadruped_controller_node-6]: process has died [pid 194672, exit code -11]
```

### 根本原因

当使用 `arguments` + `--params-file` 传递参数时，ROS 2 Launch 系统会：
1. 创建临时参数文件（`/tmp/launch_params_xxx`）
2. 这些临时文件会**覆盖** `parameters` 列表中的参数
3. 导致 `robot_description` 参数丢失
4. CHAMP 节点无法解析 URDF，崩溃

## 解决方案

### 核心思路
将 `robot_description` 也写入临时 YAML 文件，然后通过 `--params-file` 传递

### 实现方法

#### 修改前（错误）
```python
Node(
    package='champ_base',
    executable='quadruped_controller_node',
    name='quadruped_controller',
    parameters=[
        robot_description,  # ❌ 会被 arguments 中的临时文件覆盖
        {'gazebo': True, ...}
    ],
    arguments=[
        '--ros-args',
        '--params-file', gait_config,
        '--params-file', joints_config,
        '--params-file', links_config,
    ]
)
```

#### 修改后（正确）
```python
# 创建包含 robot_description 的临时参数文件
import yaml
robot_desc_temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
robot_desc_params = {
    '/**': {
        'ros__parameters': {
            'robot_description': robot_description_config.toxml(),
            'gazebo': True,
            'publish_joint_states': False,
            'publish_joint_control': True,
            'publish_foot_contacts': True,
            'joint_controller_topic': 'joint_trajectory_controller/joint_trajectory',
            'use_sim_time': True
        }
    }
}
yaml.dump(robot_desc_params, robot_desc_temp_file)
robot_desc_temp_file.close()
robot_desc_param_file = robot_desc_temp_file.name

Node(
    package='champ_base',
    executable='quadruped_controller_node',
    name='quadruped_controller',
    arguments=[
        '--ros-args',
        '--params-file', robot_desc_param_file,  # ✅ 包含 robot_description
        '--params-file', gait_config,
        '--params-file', joints_config,
        '--params-file', links_config,
    ]
)
```

### 关键点

1. **YAML 格式**：使用 `/**:` 命名空间和 `ros__parameters:` 前缀
2. **参数顺序**：`robot_desc_param_file` 必须在其他配置文件之前
3. **同时修复**：`quadruped_controller` 和 `state_estimation_node` 都需要修复

## 应用修复

### 自动修复
```bash
./final_test_champ.sh
```

这个脚本会：
1. 重新编译 dog2_champ_config
2. 清理残留进程
3. 提示你启动 Gazebo

### 手动步骤
```bash
# 1. 重新编译
colcon build --packages-select dog2_champ_config --symlink-install

# 2. 重新加载环境
source install/setup.bash

# 3. 清理进程
pkill -9 -f "gz sim"
pkill -9 -f "quadruped_controller"

# 4. 启动 Gazebo（新终端）
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

## 验证修复

### 成功标志
启动 Gazebo 后，约 5 秒应该看到：
```
[INFO] [quadruped_controller]: Quadruped controller started
```

**不应该看到**：
- ❌ `terminate called`
- ❌ `No links config file provided`
- ❌ `Failed to parse urdf string`
- ❌ `process has died`

### 验证脚本
```bash
# 等待 10 秒后运行
./quick_verify_champ.sh
```

期望输出：
```
✅ quadruped_controller 节点正在运行
✅ /cmd_vel 话题存在
✅ 关节轨迹话题存在
✅ joint_trajectory_controller 已激活
```

## 技术细节

### ROS 2 参数加载优先级

当同时使用 `parameters` 和 `arguments` 时：
1. Launch 系统先处理 `parameters` 列表
2. 然后处理 `arguments` 中的 `--params-file`
3. **后加载的参数会覆盖先加载的参数**

因此，`arguments` 中的临时文件会覆盖 `parameters` 列表。

### YAML 参数文件格式

CHAMP 期望的格式：
```yaml
/**:
  ros__parameters:
    robot_description: "<robot>...</robot>"
    gazebo: true
    links_map:
      base: base_link
      left_front:
        - lf_hip_link
        - lf_upper_leg_link
```

- `/**:` 表示全局命名空间（适用于所有节点）
- `ros__parameters:` 是 ROS 2 的标准参数前缀

## 相关文件

- `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py` - 主启动文件（已修复）
- `fix_robot_description_param.py` - 自动修复脚本
- `final_test_champ.sh` - 完整测试脚本
- `quick_verify_champ.sh` - 快速验证脚本

## 下一步

修复成功后：
1. 验证 CHAMP 节点正常运行
2. 测试键盘控制
3. 诊断为什么机器人不动（如果还不动）

## 参考

- ROS 2 Launch 参数文档: https://docs.ros.org/en/humble/How-To-Guides/Launch-file-different-formats.html
- ROS 2 参数 YAML 格式: https://docs.ros.org/en/humble/Concepts/About-ROS-2-Parameters.html
