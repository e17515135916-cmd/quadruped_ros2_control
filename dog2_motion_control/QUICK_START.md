# 快速启动指南

## 环境准备

### 1. Source ROS 2环境（如果还没有）
```bash
source /opt/ros/humble/setup.bash
```

### 2. 编译工作空间
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_motion_control --symlink-install
```

### 3. Source工作空间
```bash
source install/setup.bash
```

## 验证安装

### 快速验证
```bash
cd src/dog2_motion_control
bash verify_final_checkpoint.sh
```

预期输出：
```
==========================================
  蜘蛛机器人基础运动算法 - 最终检查点
==========================================

1. 核心模块检查
-------------------
✓ 运动学求解器模块
✓ 步态生成器模块
✓ 轨迹规划器模块
✓ 关节控制器模块
✓ 主控制器模块
✓ 配置加载器模块

...

✓ 所有检查通过！系统就绪。
```

## 运行测试

### 单元测试
```bash
cd ~/aperfect/carbot_ws/src/dog2_motion_control
python3 -m pytest test/ -v
```

### 特定测试
```bash
# 运动学测试
python3 -m pytest test/test_kinematics.py -v

# 步态生成器测试
python3 -m pytest test/test_gait_generator.py -v

# 系统集成测试
python3 -m pytest test/test_system_integration.py -v
```

## 启动Gazebo Fortress仿真

### 方法1: 使用启动脚本（最简单）
```bash
cd ~/aperfect/carbot_ws
bash start_fortress.sh
```

### 方法2: 使用ROS 2启动文件
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_motion_control spider_fortress_simple.launch.py
```

### 方法3: 使用完整启动文件
```bash
cd ~/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
```

**注意**: 
- 机器人将在Gazebo启动3秒后spawn
- 控制器将在5-8秒后加载
- 请耐心等待所有组件启动完成

## 控制机器人

### 发送速度命令

#### 前进
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.05, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" \
  --once
```

#### 后退
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: -0.05, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" \
  --once
```

#### 左转
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.2}}" \
  --once
```

#### 右转
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.2}}" \
  --once
```

#### 停止
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" \
  --once
```

## 监控系统

### 查看关节状态
```bash
ros2 topic echo /joint_states
```

### 监控导轨位置（验证锁定）
```bash
ros2 topic echo /joint_states | grep -A 20 "leg.*_j1"
```

预期：所有导轨关节（leg1_j1, leg2_j1, leg3_j1, leg4_j4）的位置应该接近0.0米。

### 查看调试信息
```bash
ros2 topic echo /spider_robot/debug_info
```

### 查看可用话题
```bash
ros2 topic list
```

### 查看控制器状态
```bash
ros2 control list_controllers
```

## 运行集成测试

### 前提条件
确保Gazebo仿真正在运行。

### 运行测试
```bash
cd ~/aperfect/carbot_ws/src/dog2_motion_control
source ../../install/setup.bash
bash test/run_integration_tests.sh
```

## 可视化

### 启动RViz
```bash
ros2 run rviz2 rviz2 -d src/dog2_motion_control/config/spider_robot.rviz
```

### RViz中查看
- 机器人模型
- TF坐标系
- 关节状态
- 脚部轨迹（如果发布）

## 常见问题

### Q1: 找不到包
```
Package 'dog2_motion_control' not found
```

**解决**:
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_motion_control
source install/setup.bash
```

### Q2: 导入错误
```
ModuleNotFoundError: No module named 'dog2_motion_control'
```

**解决**:
```bash
# 确保在正确的目录
cd ~/aperfect/carbot_ws

# 重新编译
colcon build --packages-select dog2_motion_control --symlink-install

# Source环境
source install/setup.bash
```

### Q3: Gazebo无法启动
```
[gazebo-1] process has died
```

**解决**:
```bash
# 检查Gazebo安装
gz sim --version

# 如果未安装，安装Gazebo Fortress
sudo apt install ros-humble-ros-gz
```

### Q4: 控制器未加载
```
Controller 'joint_trajectory_controller' not found
```

**解决**:
```bash
# 检查控制器配置
ros2 control list_controllers

# 如果未加载，手动加载
ros2 control load_controller joint_trajectory_controller
ros2 control set_controller_state joint_trajectory_controller active
```

### Q5: 机器人不动
**检查**:
1. Gazebo是否正在运行
2. 控制器是否激活
3. 是否发送了速度命令
4. 查看日志是否有错误

```bash
# 查看节点日志
ros2 node list
ros2 topic list
ros2 topic echo /cmd_vel
```

## 性能调优

### 调整步态参数
编辑配置文件：
```bash
nano src/dog2_motion_control/config/gait_params.yaml
```

关键参数：
- `stride_length`: 步长（米）
- `stride_height`: 步高（米）
- `cycle_time`: 步态周期（秒）
- `duty_factor`: 支撑相占比

### 调整控制频率
在`spider_robot_controller.py`中修改：
```python
self.control_timer = self.create_timer(0.02, self._timer_callback)  # 50Hz
```

## 调试技巧

### 启用调试模式
```bash
ros2 param set /spider_robot_controller debug_mode true
```

### 查看详细日志
```bash
ros2 run dog2_motion_control spider_robot_controller --ros-args --log-level debug
```

### 录制数据
```bash
ros2 bag record -a -o spider_robot_test
```

### 回放数据
```bash
ros2 bag play spider_robot_test
```

## 下一步

1. ✅ 验证系统安装
2. ✅ 运行单元测试
3. ✅ 启动Gazebo仿真
4. ✅ 测试速度命令
5. ✅ 验证导轨锁定
6. ✅ 观察爬行步态
7. 🔄 调整参数优化性能
8. 🔄 在实际硬件上测试

## 参考文档

- **需求文档**: `.kiro/specs/spider-robot-basic-motion/requirements.md`
- **设计文档**: `.kiro/specs/spider-robot-basic-motion/design.md`
- **任务列表**: `.kiro/specs/spider-robot-basic-motion/tasks.md`
- **最终报告**: `src/dog2_motion_control/FINAL_CHECKPOINT_REPORT.md`
- **项目总结**: `src/dog2_motion_control/FINAL_SUMMARY.md`

## 支持

如有问题，请查看：
1. 测试日志
2. ROS 2日志
3. Gazebo日志
4. 文档中的故障排除部分

---

**快速启动完成！祝使用愉快！** 🚀
