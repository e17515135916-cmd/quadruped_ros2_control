# Joint State Publisher GUI 显示旧关节名称问题 - 解决指南

## 问题描述
joint_state_publisher_gui 显示的是旧的关节名称（j11, j111 等），而不是新的 CHAMP 命名（lf_haa_joint, lf_hfe_joint 等）。

## 诊断结果
✅ URDF 文件中的关节名称已正确更新为 CHAMP 命名  
❌ 但 GUI 仍显示旧名称

## 原因分析
1. **使用了旧的 launch 文件** - 旧的 launch 文件可能加载了缓存的 URDF
2. **ROS 2 环境未更新** - 需要重新 source 环境
3. **robot_state_publisher 使用了旧配置** - 需要重启节点

## 解决步骤

### 步骤 1: 关闭所有 ROS 2 节点
```bash
# 按 Ctrl+C 关闭所有正在运行的 RViz 和 ROS 2 节点
```

### 步骤 2: 重新构建和 source 环境
```bash
cd ~/aperfect/carbot_ws

# 重新构建
colcon build --packages-select dog2_description

# 重新 source 环境
source install/setup.bash
```

### 步骤 3: 使用正确的 launch 文件
**重要**: 必须使用新创建的 launch 文件，不要使用旧的 launch 文件！

```bash
# 方法 1: 使用提供的脚本（推荐）
./start_champ_rviz_test.sh

# 方法 2: 直接使用 launch 文件
ros2 launch launch_champ_rviz_test.py

# 方法 3: 使用测试工具
python3 test_champ_rviz_integration.py 2
```

**不要使用以下旧的 launch 文件**:
- ❌ `view_dog2_simple.launch.py`
- ❌ `view_dog2.launch.py`
- ❌ 其他旧的 launch 文件

### 步骤 4: 验证关节名称
启动后，在 joint_state_publisher_gui 中应该看到：

**滑动副关节**:
- j1
- j2
- j3
- j4

**CHAMP 旋转关节**:
- lf_haa_joint (前左 HAA)
- lf_hfe_joint (前左 HFE)
- lf_kfe_joint (前左 KFE)
- rf_haa_joint (前右 HAA)
- rf_hfe_joint (前右 HFE)
- rf_kfe_joint (前右 KFE)
- lh_haa_joint (后左 HAA)
- lh_hfe_joint (后左 HFE)
- lh_kfe_joint (后左 KFE)
- rh_haa_joint (后右 HAA)
- rh_hfe_joint (后右 HFE)
- rh_kfe_joint (后右 KFE)

## 快速修复脚本

如果上述步骤不起作用，运行快速修复脚本：

```bash
./fix_joint_names_display.sh
```

然后重新启动 RViz：
```bash
./start_champ_rviz_test.sh
```

## 验证 URDF 正确性

运行诊断脚本确认 URDF 中的关节名称：
```bash
python3 diagnose_joint_names.py
```

应该看到：
```
✓ URDF 中的关节名称正确 (使用 CHAMP 命名)
```

## 常见问题

### Q: 为什么我看到的还是旧名称？
A: 可能原因：
1. 使用了旧的 launch 文件
2. ROS 2 环境未更新
3. 有多个 ROS 2 节点在运行

**解决**: 关闭所有节点，重新 source 环境，使用新的 launch 文件

### Q: 如何确认使用的是哪个 launch 文件？
A: 检查终端输出，应该看到：
```
ros2 launch launch_champ_rviz_test.py
```

### Q: 新旧关节名称对照表
| 旧名称 | 新名称 | 功能 |
|--------|--------|------|
| j11 | lf_haa_joint | 前左髋关节外展/内收 |
| j111 | lf_hfe_joint | 前左髋关节前后摆动 |
| j1111 | lf_kfe_joint | 前左膝关节 |
| j21 | rf_haa_joint | 前右髋关节外展/内收 |
| j211 | rf_hfe_joint | 前右髋关节前后摆动 |
| j2111 | rf_kfe_joint | 前右膝关节 |
| j31 | lh_haa_joint | 后左髋关节外展/内收 |
| j311 | lh_hfe_joint | 后左髋关节前后摆动 |
| j3111 | lh_kfe_joint | 后左膝关节 |
| j41 | rh_haa_joint | 后右髋关节外展/内收 |
| j411 | rh_hfe_joint | 后右髋关节前后摆动 |
| j4111 | rh_kfe_joint | 后右膝关节 |

## 完整的重启流程

如果问题持续存在，执行完整重启：

```bash
# 1. 关闭所有 ROS 2 进程
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui

# 2. 清理构建
cd ~/aperfect/carbot_ws
rm -rf build/ install/ log/

# 3. 重新构建
colcon build

# 4. Source 环境
source install/setup.bash

# 5. 启动 RViz
./start_champ_rviz_test.sh
```

## 成功标志

当一切正常时，您应该看到：
1. ✅ joint_state_publisher_gui 显示 CHAMP 关节名称
2. ✅ 可以控制所有 16 个关节（4 个滑动副 + 12 个旋转关节）
3. ✅ HAA 关节绕 z 轴旋转
4. ✅ HFE 和 KFE 关节绕 x 轴旋转

## 需要帮助？

如果问题仍然存在，请提供：
1. 使用的 launch 命令
2. joint_state_publisher_gui 中显示的关节名称列表
3. `python3 diagnose_joint_names.py` 的输出
