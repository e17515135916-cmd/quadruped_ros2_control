# 集成测试快速开始

## 一分钟快速开始

### 步骤1: 检查就绪状态
```bash
cd src/dog2_motion_control/test
./check_test_readiness.sh
```

### 步骤2: 启动Gazebo仿真（终端1）
```bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
```

### 步骤3: 运行测试（终端2）
```bash
cd src/dog2_motion_control/test
./run_integration_tests.sh
```

## 测试内容

### ✓ 任务 14.3: Gazebo仿真测试
- 爬行步态执行
- 静态稳定性验证
- 速度命令响应
- 平滑停止

### ✓ 任务 14.4: 导轨锁定验证
- 静止时导轨锁定
- 运动过程中导轨锁定
- 紧急停止时导轨锁定
- 导轨位置监控

## 预期结果

```
==========================================
测试总结
==========================================
[SUCCESS] ✓ 任务 14.3: Gazebo仿真测试 - 通过
[SUCCESS] ✓ 任务 14.4: 导轨锁定验证 - 通过

[SUCCESS] 所有集成测试通过！
```

## 单独运行测试

```bash
# 只运行Gazebo仿真测试
python3 test_gazebo_simulation.py

# 只运行导轨锁定验证
python3 test_rail_locking.py
```

## 故障排除

### 问题: 未检测到Gazebo仿真
**解决**: 确认Gazebo正在运行
```bash
ros2 topic list | grep joint_states
```

### 问题: 导轨滑动超出阈值
**解决**: 检查控制器参数
```bash
ros2 control list_controllers
```

### 问题: 测试超时
**解决**: 重启仿真并等待完全启动（约10秒）

## 详细文档

- [集成测试指南](../INTEGRATION_TEST_GUIDE.md) - 完整的测试说明
- [测试目录说明](README_INTEGRATION_TESTS.md) - 测试文件详情
- [任务完成总结](../TASK_14_INTEGRATION_TESTS_COMPLETION.md) - 实现细节

## 性能指标

| 指标 | 目标值 |
|------|--------|
| 导轨锁定精度 | ±0.5 mm |
| 控制频率 | 50 Hz |
| 关节运动检测 | >1° |
| 速度响应时间 | <1秒 |
| 平滑停止时间 | <3秒 |

## 需求覆盖

- ✓ 需求 1.3: 导轨锁定
- ✓ 需求 2.1: 爬行步态
- ✓ 需求 5.2: 速度命令响应
- ✓ 需求 5.4: 平滑停止
- ✓ 需求 6.1: 静态稳定性
- ✓ 需求 8.5: 导轨锁定持续性
- ✓ 需求 8.6: 导轨滑动检测

---

**提示**: 首次运行建议先执行 `./check_test_readiness.sh` 检查环境配置。
