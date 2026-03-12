# 集成测试指南

本文档描述如何运行任务14的集成测试：Gazebo仿真测试和导轨锁定验证。

## 概述

任务14包含两个主要测试：

### 14.3 Gazebo仿真测试
- 启动仿真环境
- 测试爬行步态
- 验证静态稳定性
- 测试速度命令响应
- **需求**: 2.1, 5.2, 6.1

### 14.4 导轨锁定验证
- 在仿真中监控导轨位置
- 验证整个运动过程中导轨保持0.0米
- 测试安全姿态切换时导轨不滑动
- **需求**: 1.3, 8.5, 8.6

## 前置条件

1. **ROS 2环境已设置**
   ```bash
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ```

2. **包已编译**
   ```bash
   colcon build --packages-select dog2_motion_control dog2_description
   ```

3. **Gazebo Fortress已安装**
   ```bash
   # 检查Gazebo版本
   gz sim --version
   ```

## 快速开始

### 方法1: 使用自动化脚本（推荐）

1. **启动Gazebo仿真**（终端1）
   ```bash
   ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
   ```

2. **运行集成测试**（终端2）
   ```bash
   cd src/dog2_motion_control/test
   ./run_integration_tests.sh
   ```

### 方法2: 手动运行单个测试

1. **启动Gazebo仿真**（终端1）
   ```bash
   ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
   ```

2. **运行Gazebo仿真测试**（终端2）
   ```bash
   cd src/dog2_motion_control/test
   python3 test_gazebo_simulation.py
   ```

3. **运行导轨锁定测试**（终端2）
   ```bash
   cd src/dog2_motion_control/test
   python3 test_rail_locking.py
   ```

## 测试详情

### 14.3 Gazebo仿真测试

#### 测试用例

1. **test_01_crawl_gait_execution**
   - 验证爬行步态能够正常执行
   - 检查关节命令正确发送
   - 验证步态周期正常
   - **预期结果**: 旋转关节有显著运动（>1度）

2. **test_02_static_stability**
   - 验证静态稳定性
   - 检查关节位置在合理范围内
   - **预期结果**: 所有关节位置在±π范围内

3. **test_03_velocity_command_response**
   - 测试不同速度命令的响应
   - 验证前进、侧移、旋转、停止命令
   - **预期结果**: 系统响应所有速度命令

4. **test_04_smooth_stop**
   - 验证平滑停止功能
   - 检查速度逐渐减小
   - **预期结果**: 停止过程平滑，无突然停止

#### 运行示例

```bash
$ python3 test_gazebo_simulation.py

=== 测试 14.3.1: 爬行步态执行 ===
发送速度命令: vx=0.05, vy=0.0, omega=0.0
  关节 leg1_j2 运动: 0.0° -> 5.2°
  关节 leg1_j3 运动: 45.0° -> 52.3°
✓ 爬行步态执行正常

=== 测试 14.3.2: 静态稳定性验证 ===
✓ 所有关节位置在合理范围内
✓ 静态稳定性基础检查通过

=== 测试 14.3.3: 速度命令响应 ===
测试速度命令: vx=0.05, vy=0.0, omega=0.0
  ✓ 系统响应速度命令
...
✓ 速度命令响应测试完成

=== 测试 14.3.4: 平滑停止 ===
发送前进命令，等待2秒...
发送停止命令
  初始速度指标: 0.1234
  最终速度指标: 0.0012
  ✓ 平滑停止过程完成
✓ 平滑停止测试完成
```

### 14.4 导轨锁定验证

#### 测试用例

1. **test_01_rail_locking_at_rest**
   - 验证静止时导轨锁定在0.0米
   - 检查导轨位置在±0.5mm阈值内
   - **预期结果**: 所有导轨偏差 < 0.5mm

2. **test_02_rail_locking_during_motion**
   - 验证运动过程中导轨保持锁定
   - 监控10秒运动过程
   - **预期结果**: 整个过程中导轨不滑动

3. **test_03_rail_locking_during_emergency**
   - 验证紧急停止时导轨锁定
   - 测试安全姿态切换
   - **预期结果**: 紧急停止过程中导轨不滑动

4. **test_04_rail_position_monitoring**
   - 验证导轨位置监控功能
   - 检查监控频率和覆盖范围
   - **预期结果**: 所有4个导轨被持续监控

#### 运行示例

```bash
$ python3 test_rail_locking.py

=== 测试 14.4.1: 静止时导轨锁定 ===
收集静止状态下的导轨位置（5秒）...

导轨位置偏差统计：
  ✓ leg1_j1: 最大偏差 = 0.123 mm (阈值: ±0.5 mm)
  ✓ leg2_j1: 最大偏差 = 0.089 mm (阈值: ±0.5 mm)
  ✓ leg3_j1: 最大偏差 = 0.156 mm (阈值: ±0.5 mm)
  ✓ leg4_j1: 最大偏差 = 0.201 mm (阈值: ±0.5 mm)

✓ 静止时所有导轨正确锁定在0.0米

=== 测试 14.4.2: 运动过程中导轨锁定 ===
发送前进命令...
监控运动过程中的导轨位置（10秒）...

运动过程中导轨位置偏差统计：
  ✓ leg1_j1: 最大偏差 = 0.234 mm (阈值: ±0.5 mm)
  ✓ leg2_j1: 最大偏差 = 0.312 mm (阈值: ±0.5 mm)
  ✓ leg3_j1: 最大偏差 = 0.278 mm (阈值: ±0.5 mm)
  ✓ leg4_j1: 最大偏差 = 0.401 mm (阈值: ±0.5 mm)

✓ 运动过程中所有导轨保持锁定

=== 测试 14.4.3: 紧急停止时导轨锁定 ===
发送前进命令...
触发紧急停止...
监控紧急停止过程中的导轨位置（5秒）...

紧急停止过程中导轨位置偏差统计：
  ✓ leg1_j1: 最大偏差 = 0.189 mm (阈值: ±0.5 mm)
  ✓ leg2_j1: 最大偏差 = 0.267 mm (阈值: ±0.5 mm)
  ✓ leg3_j1: 最大偏差 = 0.223 mm (阈值: ±0.5 mm)
  ✓ leg4_j1: 最大偏差 = 0.345 mm (阈值: ±0.5 mm)

✓ 紧急停止过程中所有导轨保持锁定

=== 测试 14.4.4: 导轨位置监控 ===
收集导轨位置数据（3秒）...

✓ 成功监控所有4个导轨
  采样数: 150
  采样率: 50.0 Hz

导轨位置统计：
  leg1_j1:
    平均: 0.012 mm
    标准差: 0.045 mm
    最大偏差: 0.123 mm
  leg2_j1:
    平均: -0.008 mm
    标准差: 0.038 mm
    最大偏差: 0.089 mm
  ...

✓ 导轨位置监控功能正常
```

## 故障排除

### 问题1: 未检测到Gazebo仿真

**症状**: 测试报告"未能接收到关节状态消息"

**解决方案**:
1. 确认Gazebo仿真正在运行
   ```bash
   ros2 topic list | grep joint_states
   ```
2. 检查控制器是否加载
   ```bash
   ros2 control list_controllers
   ```
3. 重启仿真并等待完全启动（约10秒）

### 问题2: 导轨滑动超出阈值

**症状**: 导轨位置偏差 > 0.5mm

**可能原因**:
1. 仿真物理参数不正确
2. 控制器增益不足
3. 仿真时间步长过大

**解决方案**:
1. 检查ros2_controllers.yaml中的PID参数
2. 增加导轨控制器的P增益
3. 调整Gazebo物理引擎参数

### 问题3: 关节运动不明显

**症状**: 测试报告"未检测到旋转关节运动"

**可能原因**:
1. 速度命令过小
2. 步态生成器未启动
3. 控制器未正确加载

**解决方案**:
1. 增加cmd_vel速度值
2. 检查spider_robot_controller日志
3. 验证所有控制器状态

### 问题4: 测试超时

**症状**: 测试在等待消息时超时

**解决方案**:
1. 增加超时时间（在测试代码中修改timeout参数）
2. 检查ROS 2网络连接
3. 确认话题名称正确

## 性能指标

### 预期性能

- **控制频率**: 50 Hz
- **导轨锁定精度**: ±0.5 mm
- **关节运动范围**: ±180°
- **速度命令响应时间**: < 1秒
- **平滑停止时间**: < 3秒

### 测试通过标准

1. **Gazebo仿真测试**:
   - 所有4个测试用例通过
   - 关节运动检测成功
   - 速度命令响应正常

2. **导轨锁定验证**:
   - 所有4个测试用例通过
   - 导轨偏差 < 0.5mm
   - 监控频率 > 40 Hz

## 测试数据收集

测试会自动收集以下数据：

1. **关节状态历史**
   - 位置、速度、力矩
   - 采样频率：50 Hz

2. **导轨位置历史**
   - 4个导轨的位置
   - 时间戳
   - 偏差统计

3. **性能指标**
   - 最大偏差
   - 平均偏差
   - 标准差

## 下一步

完成集成测试后，继续任务15：

- [ ] 15. 最终检查点
  - 确保所有测试通过
  - 验证系统在Gazebo中正常运行
  - 验证导轨始终锁定
  - 验证爬行步态静态稳定

## 参考

- 需求文档: `.kiro/specs/spider-robot-basic-motion/requirements.md`
- 设计文档: `.kiro/specs/spider-robot-basic-motion/design.md`
- 任务列表: `.kiro/specs/spider-robot-basic-motion/tasks.md`
- 启动文件: `launch/spider_gazebo_complete.launch.py`

## 联系

如有问题，请参考：
- ROS 2文档: https://docs.ros.org/
- Gazebo文档: https://gazebosim.org/docs
- 项目README: `src/dog2_motion_control/README.md`
