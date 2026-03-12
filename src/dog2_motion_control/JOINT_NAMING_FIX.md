# 关节命名修复文档

## 问题描述

在初始实现中，`joint_controller.py` 使用了错误的关节命名规则：
- ❌ 错误：`leg1_j1`, `leg1_j2`, `leg1_j3`, `leg1_j4`
- ❌ 错误：`leg2_j1`, `leg2_j2`, `leg2_j3`, `leg2_j4`
- 等等...

这与URDF文件（`dog2.urdf.xacro`）中定义的真实关节名称完全不符，会导致ros2_control报错：`Joint names mismatch`。

## URDF中的真实关节命名

根据 `dog2.urdf.xacro` 文件，真实的关节命名规则为：

### 导轨关节（Prismatic Joints）
- `j1` - Leg 1 (前左) 的导轨
- `j2` - Leg 2 (前右) 的导轨
- `j3` - Leg 3 (后左) 的导轨
- `j4` - Leg 4 (后右) 的导轨

### 旋转关节（Revolute Joints）
格式：`{prefix}_{joint_type}_joint`

其中：
- `prefix` 为腿部前缀：
  - `lf` = Left Front (前左, Leg 1)
  - `rf` = Right Front (前右, Leg 2)
  - `lh` = Left Hind (后左, Leg 3)
  - `rh` = Right Hind (后右, Leg 4)

- `joint_type` 为关节类型：
  - `haa` = Hip Abduction/Adduction (髋关节外展/内收)
  - `hfe` = Hip Flexion/Extension (髋关节屈伸)
  - `kfe` = Knee Flexion/Extension (膝关节屈伸)

### 完整的16个关节名称（按顺序）

```
1.  j1              (Leg 1 导轨)
2.  lf_haa_joint    (Leg 1 HAA)
3.  lf_hfe_joint    (Leg 1 HFE)
4.  lf_kfe_joint    (Leg 1 KFE)
5.  j2              (Leg 2 导轨)
6.  rf_haa_joint    (Leg 2 HAA)
7.  rf_hfe_joint    (Leg 2 HFE)
8.  rf_kfe_joint    (Leg 2 KFE)
9.  j3              (Leg 3 导轨)
10. lh_haa_joint    (Leg 3 HAA)
11. lh_hfe_joint    (Leg 3 HFE)
12. lh_kfe_joint    (Leg 3 KFE)
13. j4              (Leg 4 导轨)
14. rh_haa_joint    (Leg 4 HAA)
15. rh_hfe_joint    (Leg 4 HFE)
16. rh_kfe_joint    (Leg 4 KFE)
```

## 解决方案

### 1. 创建关节命名模块

创建了 `joint_names.py` 模块，提供：
- 腿部编号到URDF前缀的映射
- 辅助函数生成正确的关节名称
- 预定义的所有关节名称列表

### 2. 更新 joint_controller.py

修改了以下方法：
- `send_joint_commands()` - 使用正确的关节名称发送命令
- `monitor_rail_positions()` - 使用正确的导轨关节名称监控

### 3. 添加测试

创建了 `test_joint_names.py`，包含10个测试用例：
- 验证腿部前缀映射
- 验证关节名称生成函数
- **关键测试**：`test_urdf_consistency()` - 确保生成的名称与URDF完全一致

## 使用方法

### 在代码中使用

```python
from dog2_motion_control.joint_names import (
    get_rail_joint_name,
    get_revolute_joint_name,
    get_all_joint_names,
    get_leg_joint_names
)

# 获取导轨关节名称
rail_joint = get_rail_joint_name(1)  # 返回 'j1'

# 获取旋转关节名称
haa_joint = get_revolute_joint_name(1, 'haa')  # 返回 'lf_haa_joint'

# 获取所有关节名称
all_joints = get_all_joint_names()  # 返回16个关节名称的列表

# 获取某条腿的所有关节
leg1_joints = get_leg_joint_names(1)
# 返回：{
#     'rail': 'j1',
#     'haa': 'lf_haa_joint',
#     'hfe': 'lf_hfe_joint',
#     'kfe': 'lf_kfe_joint'
# }
```

### 运行测试

```bash
# 测试关节命名模块
pytest src/dog2_motion_control/test/test_joint_names.py -v

# 运行所有测试
pytest src/dog2_motion_control/test/ -v
```

## 验证结果

✅ 所有10个测试通过
✅ 包构建成功
✅ 关节名称与URDF完全一致

## 影响范围

此修复影响以下模块：
- ✅ `joint_controller.py` - 已修复
- ⚠️ `kinematics_solver.py` - 需要在实现时使用正确的关节名称
- ⚠️ `gait_generator.py` - 需要在实现时使用正确的腿部标识
- ⚠️ 其他未来模块 - 应使用 `joint_names.py` 中的函数

## 注意事项

1. **始终使用 joint_names 模块**：不要硬编码关节名称
2. **腿部标识统一**：在内部使用leg_num (1-4)，对外使用URDF前缀 (lf, rf, lh, rh)
3. **测试覆盖**：任何涉及关节名称的代码都应该有测试验证

## 参考

- URDF文件：`src/dog2_description/urdf/dog2.urdf.xacro`
- 关节命名模块：`src/dog2_motion_control/dog2_motion_control/joint_names.py`
- 测试文件：`src/dog2_motion_control/test/test_joint_names.py`
