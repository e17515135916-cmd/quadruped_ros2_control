# RViz 测试快速指南

## 快速启动

### 1. 启动 RViz 可视化

```bash
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

这将启动：
- robot_state_publisher（发布机器人状态）
- joint_state_publisher_gui（关节控制 GUI）
- RViz2（3D 可视化）

### 2. 运行自动验证测试

在另一个终端：

```bash
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
python3 auto_verify_hip_visual.py
```

这将自动测试所有髋关节的旋转和视觉外观。

## 手动测试

### 使用 joint_state_publisher_gui

1. 在 RViz 启动后，会出现一个 GUI 窗口
2. 找到髋关节滑块：
   - j11（腿1髋关节）
   - j21（腿2髋关节）
   - j31（腿3髋关节）
   - j41（腿4髋关节）
3. 移动滑块观察关节旋转
4. 验证关节绕 x 轴旋转（前后方向）

### 在 RViz 中检查

1. **检查视觉网格**
   - 确保髋关节链接 (l11, l21, l31, l41) 方向正确
   - 零位置时链接应在中性位置

2. **检查关节旋转**
   - 正角度：从前方看逆时针旋转
   - 负角度：从前方看顺时针旋转
   - 旋转应平滑，无跳跃

3. **检查碰撞几何体**（可选）
   - 在 RViz 中启用 "Collision Enabled"
   - 验证碰撞网格与视觉网格对齐

## 验证清单

- [ ] URDF 加载无错误
- [ ] 所有髋关节链接正确显示
- [ ] 关节绕 x 轴旋转
- [ ] 视觉网格方向正确
- [ ] 零位置时链接在中性位置
- [ ] 关节运动平滑
- [ ] 碰撞网格与视觉网格对齐

## 测试脚本说明

### auto_verify_hip_visual.py

**功能**：
- 自动测试所有髋关节
- 测试单关节旋转
- 测试同步旋转
- 测试对角线运动
- 测试全范围扫描

**运行时间**：约 45 秒

**输出**：详细的测试报告和验证结果

### verify_hip_joint_visual.py

**功能**：
- 交互式测试
- 需要用户在每个步骤后按 Enter
- 适合详细检查每个关节

**运行时间**：取决于用户交互

### test_hip_joint_rviz.py

**功能**：
- 基本的关节旋转测试
- 简单快速

**运行时间**：约 25 秒

## 常见问题

### Q: RViz 启动失败
**A**: 检查是否已 source 环境：
```bash
source install/setup.bash
```

### Q: 看不到机器人
**A**: 
1. 检查 RViz 的 Fixed Frame 设置为 "world" 或 "base_link"
2. 点击 "Reset" 按钮重置视图
3. 确保 RobotModel 显示已启用

### Q: 关节不动
**A**: 
1. 确保 joint_state_publisher_gui 正在运行
2. 检查是否有其他节点在发布 /joint_states
3. 尝试重启 RViz

### Q: 视觉网格方向错误
**A**: 
1. 检查 URDF 中的 visual origin RPY 是否为 "0 0 1.5708"
2. 确保使用的是最新的 URDF 文件
3. 重新构建工作空间：`colcon build --packages-select dog2_description`

## 停止测试

```bash
# 停止 RViz
Ctrl+C

# 或者杀死所有相关进程
killall -9 robot_state_publisher joint_state_publisher_gui rviz2
```

## 下一步

完成 RViz 测试后，继续：
- **任务 10**: Gazebo 仿真测试
- **任务 11**: 站立姿态测试
- **任务 12**: 行走步态测试

## 相关文档

- 验证报告: `.kiro/specs/hip-joint-axis-change/RVIZ_VERIFICATION_REPORT.md`
- 需求文档: `.kiro/specs/hip-joint-axis-change/requirements.md`
- 设计文档: `.kiro/specs/hip-joint-axis-change/design.md`
- 任务列表: `.kiro/specs/hip-joint-axis-change/tasks.md`
