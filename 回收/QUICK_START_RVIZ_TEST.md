# RViz 集成测试快速开始指南

## 文件位置
所有测试文件位于工作空间目录：
```
/home/dell/aperfect/carbot_ws/
```

## 使用步骤

### 1. 进入工作空间目录
```bash
cd ~/aperfect/carbot_ws
```

### 2. 运行自动化测试
```bash
python3 test_champ_rviz_integration.py 1
```

这将：
- 编译 URDF
- 验证关节配置
- 检查轴向设置
- 生成测试报告

### 3. 启动 RViz 手动验证（可选）
```bash
./start_champ_rviz_test.sh
```

或者：
```bash
python3 test_champ_rviz_integration.py 2
```

### 4. 运行完整测试（自动化 + 手动）
```bash
python3 test_champ_rviz_integration.py 3
```

## 测试文件说明

- `test_champ_rviz_integration.py` - 自动化测试脚本
- `launch_champ_rviz_test.py` - RViz launch 文件
- `start_champ_rviz_test.sh` - 启动脚本
- `CHAMP_RVIZ_INTEGRATION_TEST_SUMMARY.md` - 详细文档

## 预期结果

自动化测试应该显示：
```
✓ 所有自动化测试通过
CHAMP 兼容关节配置验证成功
```

## 手动验证要点

在 RViz 中验证：
1. ✓ 滑动副关节 (j1-j4) 可控制
2. ✓ HAA 关节绕 z 轴旋转（外展/内收）
3. ✓ HFE 关节绕 x 轴旋转（前后摆动）
4. ✓ KFE 关节绕 x 轴旋转（膝关节屈伸）
5. ✓ 视觉外观正确

## 故障排除

### 问题：找不到文件
**解决方案**：确保在正确的目录
```bash
cd ~/aperfect/carbot_ws
ls test_champ_rviz_integration.py  # 应该能看到文件
```

### 问题：ROS 2 环境未设置
**解决方案**：
```bash
source /opt/ros/humble/setup.bash  # 或您的 ROS 版本
source install/setup.bash
```

### 问题：工作空间未构建
**解决方案**：
```bash
colcon build
source install/setup.bash
```

## 查看测试报告

测试完成后，查看生成的报告：
```bash
cat champ_rviz_integration_report_*.txt
```

或查看总结文档：
```bash
cat CHAMP_RVIZ_INTEGRATION_TEST_SUMMARY.md
```
