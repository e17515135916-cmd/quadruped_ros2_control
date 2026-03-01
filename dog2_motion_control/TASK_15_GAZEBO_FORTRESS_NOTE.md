# 任务15 - Gazebo Fortress配置说明

## 更新时间
2026-03-01

## Gazebo版本选择

用户明确要求使用**Gazebo Fortress**，所有Gazebo Classic相关文件已删除。

## 已创建的Fortress启动文件

### 1. spider_gazebo_complete.launch.py
完整的启动文件，包含所有功能：
- Gazebo Fortress仿真环境
- 机器人模型spawn
- ros2_control控制器
- 话题桥接
- 运动控制节点

### 2. spider_fortress_simple.launch.py
简化版启动文件，更容易调试：
- 使用ExecuteProcess直接调用gz命令
- 使用TimerAction控制启动顺序
- 明确的延迟时间确保组件按顺序启动

## 启动方法

### 推荐方法（最简单）
```bash
cd ~/aperfect/carbot_ws
bash start_fortress.sh
```

### 使用简化启动文件
```bash
ros2 launch dog2_motion_control spider_fortress_simple.launch.py
```

### 使用完整启动文件
```bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
```

## 启动顺序

1. **T=0s**: Gazebo Fortress启动
2. **T=3s**: 机器人spawn到仿真环境
3. **T=5s**: joint_state_broadcaster加载
4. **T=6s**: joint_trajectory_controller加载
5. **T=7s**: rail_position_controller加载
6. **T=8s**: spider_robot_controller启动

## 验证机器人是否正确加载

### 方法1: 查看Gazebo窗口
打开Gazebo窗口，应该能看到四足机器人模型

### 方法2: 检查ROS 2话题
```bash
# 应该能看到joint_states话题
ros2 topic list | grep joint_states

# 应该能看到关节数据
ros2 topic echo /joint_states
```

### 方法3: 检查Gazebo模型
```bash
gz model -l
# 应该看到 "dog2" 模型
```

## 常见问题

### 问题1: 机器人没有出现
**原因**: spawn命令可能失败

**解决**: 
1. 检查robot_description话题是否发布
2. 手动spawn测试
3. 查看启动日志中的错误信息

详见: `GAZEBO_FORTRESS_TROUBLESHOOTING.md`

### 问题2: Gazebo窗口是空的
**原因**: 可能是Gazebo还没完全启动就尝试spawn

**解决**: 
使用`spider_fortress_simple.launch.py`，它有更长的延迟时间

### 问题3: 控制器加载失败
**原因**: ros2_control插件可能没有正确加载

**解决**:
1. 检查URDF中的ros2_control标签
2. 手动加载控制器测试
3. 查看controller_manager日志

## 与dog2_description包的集成

dog2_description包中也有Fortress启动文件：
- `dog2_fortress_with_control.launch.py`
- `dog2_fortress_with_gui.launch.py`
- `gazebo_dog2_fortress.launch.py`

这些文件可以作为参考，但dog2_motion_control包的启动文件是专门为蜘蛛机器人运动控制设计的。

## 下一步

1. 测试启动文件，确保机器人正确显示
2. 如果有问题，参考故障排除文档
3. 验证控制器是否正确加载
4. 测试速度命令响应

## 文件清单

### 已创建
- ✅ `launch/spider_gazebo_complete.launch.py` - 完整启动文件
- ✅ `launch/spider_fortress_simple.launch.py` - 简化启动文件
- ✅ `start_fortress.sh` - 启动脚本
- ✅ `GAZEBO_FORTRESS_TROUBLESHOOTING.md` - 故障排除指南

### 已删除
- ❌ `launch/spider_gazebo_classic.launch.py` - Gazebo Classic启动文件（已删除）
- ❌ `start_spider_simulation.sh` - Classic启动脚本（已删除）

## 测试状态

- ✅ 启动文件已创建
- ⚠️ 需要在实际Gazebo Fortress环境中测试
- ⚠️ 需要验证机器人是否正确spawn
- ⚠️ 需要验证控制器是否正确加载

## 备注

由于Gazebo Fortress和Gazebo Classic的API差异较大，启动文件需要使用：
- `ros_gz_sim`包而不是`gazebo_ros`
- `gz sim`命令而不是`gazebo`命令
- 不同的话题桥接方式

所有这些差异已在新的启动文件中正确处理。
