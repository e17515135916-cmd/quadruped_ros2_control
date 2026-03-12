# RViz 髋关节轴向验证指南

本指南说明如何使用 RViz 验证髋关节轴向从 Z 轴改为 X 轴的修改。

## 概述

髋关节（j11, j21, j31, j41）的旋转轴已从 Z 轴（`0 0 -1`）改为 X 轴（`1 0 0`）。
这意味着髋关节现在应该前后摆动，而不是左右摆动。

## 验证方法

### 方法 1：自动化验证（推荐）

运行自动化验证脚本，它会：
- 编译 xacro 文件
- 验证 URDF 有效性
- 检查髋关节轴向配置
- 验证视觉模型保持不变
- 生成详细的验证报告

```bash
python3 run_rviz_verification.py 1
```

验证报告将保存为 `rviz_verification_report_YYYYMMDD_HHMMSS.txt`

### 方法 2：手动 RViz 验证

启动 RViz 进行手动验证：

```bash
./start_hip_axis_rviz_verification.sh
```

或直接使用 ros2 launch：

```bash
source install/setup.bash
ros2 launch verify_hip_axis_rviz.py
```

#### 手动验证步骤

1. **启动 RViz**
   - RViz 窗口将打开
   - joint_state_publisher_gui 窗口也会打开

2. **配置 RViz 显示**
   - 如果 RobotModel 显示未自动添加：
     - 点击 "Add" 按钮
     - 选择 "RobotModel"
     - 点击 "OK"
   - 确保 Fixed Frame 设置为 "base_link" 或 "world"

3. **测试髋关节运动**
   - 在 joint_state_publisher_gui 窗口中找到以下滑块：
     - j11 (前左髋关节)
     - j21 (前右髋关节)
     - j31 (后左髋关节)
     - j41 (后右髋关节)
   - 移动每个滑块，观察机器人模型的变化

4. **验证预期行为**
   - ✓ 髋关节应该**前后摆动**（绕 X 轴旋转）
   - ✓ 视觉外观应该与修改前一致
   - ✓ 关节限位：±150° (±2.618 rad)

5. **对比之前的行为**
   - ✗ 之前髋关节**左右摆动**（绕 Z 轴旋转）

### 方法 3：完整验证（自动化 + 手动）

运行完整验证流程：

```bash
python3 run_rviz_verification.py 3
```

这将先运行自动化验证，然后启动 RViz 进行手动验证。

## 验证脚本说明

### 1. `verify_hip_axis_rviz.py`
RViz 启动脚本，加载修改后的机器人模型。

**功能：**
- 处理 xacro 文件生成 URDF
- 启动 robot_state_publisher
- 启动 joint_state_publisher_gui
- 启动 RViz2

### 2. `verify_visual_unchanged.py`
视觉模型验证脚本。

**功能：**
- 对比修改前后的 URDF
- 验证视觉网格文件未改变
- 验证视觉原点未改变
- 验证髋关节轴向已正确更新

### 3. `test_hip_axis_movement.py`
髋关节运动测试脚本（可选）。

**功能：**
- 通过 ROS 2 topic 发布关节状态
- 自动测试髋关节运动范围
- 验证关节控制正常工作

**使用方法：**
```bash
# 在另一个终端中，先启动 RViz
ros2 launch verify_hip_axis_rviz.py

# 然后在新终端中运行测试
source install/setup.bash
python3 test_hip_axis_movement.py
```

### 4. `run_rviz_verification.py`
综合验证脚本。

**功能：**
- 自动化整个验证流程
- 生成详细的验证报告
- 可选启动 RViz 手动验证

### 5. `start_hip_axis_rviz_verification.sh`
便捷启动脚本。

**功能：**
- 一键启动 RViz 验证
- 显示验证说明
- 自动设置 ROS 2 环境

## 验证清单

使用以下清单确保所有验证项目都已完成：

- [ ] Xacro 文件成功编译为 URDF
- [ ] URDF 通过 check_urdf 验证
- [ ] 髋关节 j11 轴向为 `1 0 0`
- [ ] 髋关节 j21 轴向为 `1 0 0`
- [ ] 髋关节 j31 轴向为 `1 0 0`
- [ ] 髋关节 j41 轴向为 `1 0 0`
- [ ] 视觉网格文件未改变
- [ ] 视觉原点未改变
- [ ] RViz 中髋关节前后摆动（X 轴）
- [ ] 视觉外观与修改前一致
- [ ] 关节限位正常工作

## 常见问题

### Q: RViz 启动失败
**A:** 确保已正确设置 ROS 2 环境：
```bash
source install/setup.bash
```

### Q: 看不到机器人模型
**A:** 
1. 检查 RViz 的 Fixed Frame 设置
2. 添加 RobotModel 显示
3. 确保 robot_state_publisher 正在运行

### Q: joint_state_publisher_gui 没有显示髋关节
**A:** 
1. 确认 URDF 中髋关节定义正确
2. 检查关节类型是否为 "revolute"
3. 查看终端输出的错误信息

### Q: 髋关节运动方向不对
**A:** 
1. 检查关节轴向是否为 `1 0 0`
2. 运行 `verify_visual_unchanged.py` 验证配置
3. 查看验证报告了解详情

## 验证需求映射

本验证流程满足以下需求：

- **需求 6.1**: RViz 中加载和控制机器人模型
- **需求 6.2**: 通过 joint_state_publisher 测试髋关节运动
- **需求 6.5**: 验证视觉外观保持不变
- **需求 2.3**: 确认视觉模型未改变

## 下一步

完成 RViz 验证后，继续进行 Gazebo 仿真验证（任务 6）。

## 相关文件

- `.kiro/specs/hip-joint-z-axis-reversion/requirements.md` - 需求文档
- `.kiro/specs/hip-joint-z-axis-reversion/design.md` - 设计文档
- `.kiro/specs/hip-joint-z-axis-reversion/tasks.md` - 任务列表
- `src/dog2_description/urdf/dog2.urdf.xacro` - 机器人描述文件

## 联系方式

如有问题，请查看任务文档或联系项目维护者。
