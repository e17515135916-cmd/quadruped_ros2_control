# Gazebo Fortress 故障排除指南

## 问题1: 机器人没有出现在Gazebo中

### 症状
- Gazebo窗口打开了
- 但是看不到机器人模型

### 可能原因和解决方案

#### 原因1: robot_description话题没有发布
**检查**:
```bash
ros2 topic list | grep robot_description
ros2 topic echo /robot_description --once
```

**解决**:
确保robot_state_publisher节点正在运行：
```bash
ros2 node list | grep robot_state_publisher
```

#### 原因2: spawn命令失败
**检查日志**:
启动文件的输出中查找spawn相关的错误信息

**手动spawn测试**:
```bash
# 在一个终端启动Gazebo
gz sim -r empty.sdf

# 在另一个终端
source install/setup.bash
ros2 run ros_gz_sim create -topic /robot_description -name dog2 -z 0.5
```

#### 原因3: URDF/SDF转换问题
**检查URDF**:
```bash
# 查看生成的URDF
ros2 topic echo /robot_description --once > /tmp/robot.urdf
cat /tmp/robot.urdf
```

**验证URDF**:
```bash
check_urdf /tmp/robot.urdf
```

## 问题2: Gazebo启动失败

### 症状
- 命令执行后没有窗口打开
- 或者窗口闪退

### 解决方案

#### 检查Gazebo安装
```bash
gz sim --version
```

应该看到类似输出：
```
Gazebo Sim, version 6.x.x
```

#### 安装/重新安装Gazebo Fortress
```bash
sudo apt update
sudo apt install ros-humble-ros-gz
```

#### 检查图形驱动
```bash
glxinfo | grep "OpenGL version"
```

## 问题3: 控制器加载失败

### 症状
- 机器人出现了但不动
- 控制器spawner报错

### 解决方案

#### 检查控制器配置
```bash
# 查看可用的控制器
ros2 control list_controllers

# 查看控制器管理器
ros2 control list_hardware_interfaces
```

#### 手动加载控制器
```bash
# 加载joint_state_broadcaster
ros2 run controller_manager spawner joint_state_broadcaster

# 加载joint_trajectory_controller
ros2 run controller_manager spawner joint_trajectory_controller

# 加载rail_position_controller
ros2 run controller_manager spawner rail_position_controller
```

## 问题4: 话题桥接问题

### 症状
- ROS 2话题中看不到Gazebo的数据
- /joint_states话题没有数据

### 解决方案

#### 检查桥接节点
```bash
ros2 node list | grep bridge
```

#### 手动启动桥接
```bash
# 桥接joint_states
ros2 run ros_gz_bridge parameter_bridge \
  /world/empty/model/dog2/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model \
  --ros-args -r /world/empty/model/dog2/joint_state:=/joint_states

# 桥接clock
ros2 run ros_gz_bridge parameter_bridge \
  /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock
```

## 问题5: 机器人掉落或穿模

### 症状
- 机器人spawn后立即掉落
- 或者部分穿过地面

### 解决方案

#### 调整spawn高度
在启动文件中修改z坐标：
```python
'-z', '1.0',  # 增加高度
```

#### 检查碰撞模型
确保URDF中有正确的collision标签

## 问题6: 性能问题

### 症状
- Gazebo运行很慢
- Real Time Factor < 1.0

### 解决方案

#### 降低物理引擎更新频率
在world文件中调整：
```xml
<physics type="ode">
  <max_step_size>0.01</max_step_size>
  <real_time_factor>1.0</real_time_factor>
</physics>
```

#### 简化模型
- 减少mesh的复杂度
- 使用简单的碰撞几何体

## 调试技巧

### 1. 查看所有ROS 2话题
```bash
ros2 topic list
```

### 2. 查看Gazebo话题
```bash
gz topic -l
```

### 3. 查看TF树
```bash
ros2 run tf2_tools view_frames
evince frames.pdf
```

### 4. 录制和回放
```bash
# 录制
ros2 bag record -a

# 回放
ros2 bag play <bag_file>
```

### 5. 查看日志
```bash
# ROS 2日志
ros2 run rqt_console rqt_console

# Gazebo日志
gz log -i
```

## 常用命令

### 启动Gazebo（无GUI）
```bash
gz sim -r -s empty.sdf
```

### 列出Gazebo中的模型
```bash
gz model -l
```

### 查看模型信息
```bash
gz model -m dog2 -i
```

### 暂停/恢复仿真
```bash
gz service -s /world/empty/control --reqtype gz.msgs.WorldControl \
  --reptype gz.msgs.Boolean --timeout 3000 \
  --req 'pause: true'
```

## 获取帮助

如果以上方法都无法解决问题：

1. 检查ROS 2和Gazebo版本兼容性
2. 查看GitHub issues
3. 在ROS Answers上提问
4. 查看Gazebo官方文档

## 参考资源

- [Gazebo Fortress文档](https://gazebosim.org/docs/fortress)
- [ros_gz包文档](https://github.com/gazebosim/ros_gz)
- [ROS 2 Control文档](https://control.ros.org/)
