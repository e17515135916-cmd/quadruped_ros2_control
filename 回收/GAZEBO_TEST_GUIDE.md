# Dog2 Gazebo仿真测试指南

## 当前状态

✅ Gazebo仿真已成功启动！

## 启动的组件

1. **gzserver** - Gazebo物理仿真服务器
2. **gzclient** - Gazebo GUI客户端（可视化窗口）
3. **robot_state_publisher** - 发布机器人TF变换
4. **joint_state_publisher** - 发布关节状态
5. **Dog2机器人** - 已spawn到仿真环境中

## 在Gazebo中检查什么

### 1. 机器人可见性
- 打开Gazebo窗口
- 在左侧模型列表中应该看到 "dog2"
- 机器人应该在空中（高度0.5m）然后掉落到地面

### 2. 物理仿真稳定性
- 机器人掉落后是否稳定？
- 是否有异常抖动或爆炸？
- 关节是否正常工作？

### 3. 导轨行程测试
在新终端中运行以下命令来测试导轨：

```bash
# 测试j1（左前腿导轨，应该只能负方向移动）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j1'], position: [-0.1]}"

# 测试j2（右前腿导轨，应该只能正方向移动）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j2'], position: [0.1]}"

# 测试j3（左后腿导轨）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j3'], position: [-0.1]}"

# 测试j4（右后腿导轨）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j4'], position: [0.1]}"
```

### 4. 关节角度测试
测试髋关节和膝关节的新限制：

```bash
# 测试髋关节（±150° = ±2.618 rad）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j11'], position: [2.5]}"

# 测试膝关节（±160° = ±2.8 rad）
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['j111'], position: [2.7]}"
```

## 常见问题

### 机器人不可见
1. 检查Gazebo左侧模型列表是否有 "dog2"
2. 检查控制台错误信息
3. 检查mesh文件路径：`src/dog2_description/meshes/`

### 机器人爆炸或抖动
1. 惯性值可能有问题（但我们已经修复了）
2. 碰撞检测可能有问题
3. 初始位置太低导致穿模

### 关节不动
1. 检查ros2_control插件是否加载
2. 检查joint_state_publisher是否运行
3. 使用 `ros2 topic list` 查看可用话题

## 停止仿真

```bash
# 方法1：使用脚本
./stop_gazebo.sh

# 方法2：手动停止
pkill -9 gzserver
pkill -9 gzclient
```

## 重新启动

```bash
./start_gazebo_test.sh
```

## 下一步

如果Gazebo仿真稳定：
1. ✅ 测试导轨行程限制
2. ✅ 测试关节角度限制
3. 🔄 添加MPC控制器
4. 🔄 添加WBC控制器
5. 🔄 测试越障功能

## 文件位置

- Launch文件: `src/dog2_description/launch/gazebo_test.launch.py`
- 启动脚本: `start_gazebo_test.sh`
- URDF文件: `src/dog2_description/urdf/dog2.urdf`
- Xacro文件: `src/dog2_description/urdf/dog2.urdf.xacro`
