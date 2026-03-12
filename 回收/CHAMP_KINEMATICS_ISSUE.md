# CHAMP 运动学问题 - 快速诊断指南

## 🚨 问题现象

- ✅ CHAMP `quadruped_controller` 节点启动成功
- ✅ `/cmd_vel` 话题存在
- ✅ `/joint_trajectory_controller/joint_trajectory` 话题存在
- ❌ **机器人不动**

## 🎯 根本原因

**CHAMP 找不到它需要的关节** → 关节名称不匹配或配置错误

## 🔍 快速诊断（3 步）

### 1️⃣ 检查实际关节名称
```bash
ros2 topic echo /joint_states --once
```

**期望看到**：
- `lf_haa_joint, lf_hfe_joint, lf_kfe_joint` (左前腿)
- `rf_haa_joint, rf_hfe_joint, rf_kfe_joint` (右前腿)
- `lh_haa_joint, lh_hfe_joint, lh_kfe_joint` (左后腿)
- `rh_haa_joint, rh_hfe_joint, rh_kfe_joint` (右后腿)
- `j1, j2, j3, j4` (导轨，可以忽略)

### 2️⃣ 运行自动诊断
```bash
python3 diagnose_champ_kinematics.py
```

**期望输出**：
```
✅ 所有 CHAMP 关节都存在！
✅ 关节名称匹配正确！
```

**如果看到**：
```
❌ CHAMP 找不到以下关节
```
→ 继续第 3 步

### 3️⃣ 自动修复
```bash
python3 fix_champ_kinematics.py
colcon build --packages-select dog2_champ_config --symlink-install
./clean_and_restart.sh
```

## 🚀 完整测试流程（一键执行）

```bash
./final_test_champ.sh
```

然后按照屏幕提示在 3 个终端中操作：
1. **终端 1**：启动 Gazebo + CHAMP
2. **终端 2**：运行诊断工具
3. **终端 3**：测试键盘控制

## 📊 诊断结果解读

### 情况 A：关节名称不匹配
**症状**：
```
❌ CHAMP 找不到以下关节:
   - lf_haa_joint
   - lf_hfe_joint
   ...
```

**原因**：配置文件中的关节名称与 URDF 不一致

**解决**：
```bash
python3 fix_champ_kinematics.py
colcon build --packages-select dog2_champ_config --symlink-install
```

### 情况 B：关节存在但不发布轨迹
**症状**：
```
✅ 所有 CHAMP 关节都存在！
⚠️  未收到轨迹命令
```

**原因**：CHAMP 没有收到 `/cmd_vel` 或运动学计算失败

**调试**：
1. 检查 `/cmd_vel`：
   ```bash
   ros2 topic echo /cmd_vel
   ```
2. 手动发送命令：
   ```bash
   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
     "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once
   ```
3. 查看 CHAMP 终端输出，寻找错误信息

### 情况 C：发布轨迹但机器人不动
**症状**：
```
✅ 所有 CHAMP 关节都存在！
✅ 收到轨迹命令！
```
但机器人仍然不动

**原因**：控制器或 Gazebo 插件问题

**调试**：
1. 检查控制器状态：
   ```bash
   ros2 control list_controllers
   ```
   应该看到：`joint_trajectory_controller [active]`

2. 测试直接控制（绕过 CHAMP）：
   ```bash
   ./test_direct_control.sh
   ```

3. 如果直接控制有效 → CHAMP 配置问题
4. 如果直接控制无效 → Gazebo/控制器问题

## 🛠️ 工具脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `diagnose_champ_kinematics.py` | 诊断关节名称匹配 | 机器人不动时首先运行 |
| `fix_champ_kinematics.py` | 自动修复配置 | 关节名称不匹配时 |
| `verify_champ_kinematics_fix.py` | 验证配置正确性 | 修复后验证 |
| `final_test_champ.sh` | 完整测试流程 | 一键测试所有功能 |
| `clean_and_restart.sh` | 清理并重启 | 重启系统前 |
| `start_keyboard_control.sh` | 启动键盘控制 | 测试机器人移动 |
| `test_direct_control.sh` | 直接控制测试 | 绕过 CHAMP 测试 |

## 📝 配置文件位置

| 文件 | 路径 | 作用 |
|------|------|------|
| 关节配置 | `src/dog2_champ_config/config/joints/joints.yaml` | 定义 CHAMP 使用的关节名称 |
| 链接配置 | `src/dog2_champ_config/config/links/links.yaml` | 定义 CHAMP 使用的链接名称 |
| 步态配置 | `src/dog2_champ_config/config/gait/gait.yaml` | 定义步态参数 |
| 控制器配置 | `src/dog2_description/config/ros2_controllers.yaml` | 定义 ros2_control 控制器 |
| URDF | `src/dog2_description/urdf/dog2.urdf.xacro` | 机器人描述文件 |

## 🎯 关键检查点

### ✅ 配置正确的标志
- [ ] 关节配置包含 12 个关节（每条腿 3 个）
- [ ] 关节顺序：HAA → HFE → KFE
- [ ] 关节名称与 URDF 完全一致
- [ ] 链接配置包含 4 个链接（每条腿）
- [ ] base 链接是 `base_link`

### ✅ 系统运行正常的标志
- [ ] CHAMP 启动时显示 `Successfully parsed urdf file`
- [ ] `ros2 control list_controllers` 显示控制器 `active`
- [ ] 诊断工具显示 `所有 CHAMP 关节都存在`
- [ ] 发送 `/cmd_vel` 后收到轨迹命令
- [ ] 机器人在 Gazebo 中移动

## 🆘 常见错误

### 错误 1：`Error document empty`
**原因**：URDF 文件路径错误或 `robot_description` 参数未设置

**解决**：使用正确的启动命令
```bash
ros2 launch dog2_champ_config champ.launch.py \
  use_sim_time:=true \
  description_path:=/home/dell/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf
```

### 错误 2：`Failed to parse urdf string`
**原因**：URDF 语法错误

**解决**：检查 URDF 文件
```bash
check_urdf src/dog2_description/urdf/dog2.urdf
```

### 错误 3：`No links config file provided`
**原因**：`links.yaml` 未正确加载

**解决**：检查文件是否存在并重新编译
```bash
ls -la src/dog2_champ_config/config/links/links.yaml
colcon build --packages-select dog2_champ_config --symlink-install
```

## 📚 详细文档

- `CHAMP_KINEMATICS_ROOT_CAUSE.md` - 根本原因详细分析
- `CHAMP_KINEMATICS_FIX_SUMMARY.md` - 修复总结
- `CHAMP修复快速指南.md` - 快速参考
- `ALTERNATIVE_SOLUTION.md` - 备选方案

## 🚀 立即开始

```bash
# 一键测试
./final_test_champ.sh

# 或者手动诊断
python3 diagnose_champ_kinematics.py
```

---

**记住**：关节名称必须完全匹配！使用诊断工具可以快速定位问题。
