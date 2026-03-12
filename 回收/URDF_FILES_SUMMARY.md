# Dog2 URDF 文件目录完整说明

## 📋 快速总结

`src/dog2_description/urdf/` 目录包含 **16 个文件**，用于描述 Dog2 四足机器人的结构、物理属性和控制配置。

---

## 🎯 核心文件（必须了解）

### 1. **dog2.urdf.xacro** ⭐⭐⭐
**这是最重要的源文件！**

- **作用**: 使用 Xacro 宏语言编写的参数化机器人描述模板
- **大小**: 16KB (510 行)
- **特点**:
  - 10 个可配置属性（关节限制、力矩、速度）
  - 支持参数化，易于维护
  - 包含完整的 ROS 2 Control 配置
  - 包含 Gazebo 插件配置（已修复控制器路径）
- **关节配置**:
  - Hip 关节: ±150° (±2.618 rad) - 用于障碍物跨越
  - Knee 关节: ±160° (±2.8 rad) - 支持双向折叠
  - Prismatic 关节: ±0.111 m - 滑动副
- **如何使用**: 
  ```bash
  # 修改此文件后，需要重新生成 URDF
  xacro dog2.urdf.xacro > dog2.urdf
  ```

### 2. **dog2.urdf**
**从 dog2.urdf.xacro 自动生成的最终文件**

- **作用**: 标准 URDF 格式，供 ROS 2 节点使用
- **大小**: 28KB (728 行)
- **结构**:
  - 18 个连杆（links）
  - 29 个关节（joints）
  - 包含惯性、碰撞、视觉信息
- **⚠️ 警告**: 不要手动编辑！应该编辑 `dog2.urdf.xacro` 然后重新生成
- **用途**: 
  - ROS 2 节点读取
  - Gazebo 仿真加载
  - RViz 可视化

---

## 🔧 专用版本文件

### 3. **dog2_gazebo.urdf**
**Gazebo 仿真专用优化版本**

- **大小**: 24KB (838 行)
- **优化内容**:
  - 简化碰撞几何（球体代替复杂网格）→ 提高仿真速度
  - 调整惯性参数 → 提高稳定性
  - 包含接触传感器（足端）
  - 包含 IMU 传感器（base_link）
  - 优化摩擦系数（μ1=1.5, μ2=1.5）
- **何时使用**: 需要在 Gazebo 中进行物理仿真时

### 4. **dog2_champ.urdf**
**CHAMP 四足控制器框架专用**

- **大小**: 36KB (984 行)
- **特点**:
  - 53 个关节（包含虚拟关节）
  - 22 个连杆
  - 为 CHAMP 控制算法优化
- **何时使用**: 使用 CHAMP 控制器进行步态规划时

### 5. **dog2_visual.urdf**
**纯可视化版本**

- **大小**: 36KB (1036 行)
- **特点**:
  - 完整的视觉网格
  - 53 个关节，22 个连杆
  - 不包含物理仿真参数
- **何时使用**: 只需要在 RViz 中显示机器人外观，不需要物理仿真

### 6. **dog2_fixed_prismatic.urdf**
**固定滑动副版本**

- **大小**: 36KB (980 行)
- **特点**: 滑动关节被固定或移除
- **何时使用**: 测试不带滑动副的运动学

### 7. **dog2_optimized_for_crossing.urdf**
**障碍物跨越优化版本**

- **大小**: 28KB (1111 行)
- **特点**:
  - 33 个关节
  - 针对跨越动作优化的关节限制
- **何时使用**: 进行障碍物跨越实验时

---

## 📊 辅助文件

### 8. **dog2.csv**
**机器人参数数据表**

- **大小**: 12KB (18 行)
- **内容**: 从 SolidWorks 导出的完整参数表
- **包含信息**:
  - 每个连杆的质心位置 (X, Y, Z)
  - 质心姿态 (Roll, Pitch, Yaw)
  - 质量
  - 惯性矩阵 (Ixx, Ixy, Ixz, Iyy, Iyz, Izz)
  - 视觉和碰撞几何信息
  - 关节类型、位置、轴向
  - 关节限制（effort, velocity, lower, upper）
  - 网格文件路径
  - 颜色信息
- **用途**: 
  - 参数导入/导出
  - 数据分析
  - 与 CAD 软件同步

### 9. **links.xacro**
**Xacro 宏定义库**

- **大小**: 8KB (165 行)
- **作用**: 包含可重用的连杆宏定义
- **用途**: 减少重复代码，提高可维护性

### 10. **simple.urdf**
**简化测试模型**

- **大小**: 4KB
- **状态**: 当前为空
- **用途**: 可能用于快速测试

---

## 💾 备份文件（共 6 个）

### 按时间顺序：

1. **dog2.urdf.backup** - 通用备份（无时间戳）
2. **dog2.urdf.backup_20260112_170119** - 2026-01-12 备份
3. **dog2.urdf.backup_xacro_migration** - Xacro 迁移前备份
4. **dog2.urdf.xacro.before_macro** - 引入宏之前的版本
5. **dog2.urdf.backup_20260126_171703** - 2026-01-26 备份（关节限制修改前）
6. **dog2_gazebo.urdf.old_backup** - Gazebo URDF 旧备份

**用途**: 版本控制，可以回滚到之前的配置

---

## 🔄 文件关系和工作流程

```
┌─────────────────────┐
│ dog2.urdf.xacro     │ ← 源文件（手动编辑）
│ (参数化模板)         │
└──────────┬──────────┘
           │ xacro 处理
           ↓
┌─────────────────────┐
│ dog2.urdf           │ ← 生成文件（自动生成）
│ (标准 URDF)         │
└──────────┬──────────┘
           │
           ├─→ ROS 2 节点
           ├─→ Gazebo 仿真
           └─→ RViz 可视化

专用版本（根据需要选择）:
├─→ dog2_gazebo.urdf (Gazebo 优化)
├─→ dog2_champ.urdf (CHAMP 控制器)
├─→ dog2_visual.urdf (纯可视化)
└─→ dog2_optimized_for_crossing.urdf (障碍物跨越)
```

---

## 📈 关键统计对比

| 文件名 | 大小 | 行数 | 关节数 | 连杆数 | 主要用途 |
|--------|------|------|--------|--------|----------|
| dog2.urdf.xacro | 16K | 510 | - | - | 源模板 ⭐ |
| dog2.urdf | 28K | 728 | 29 | 18 | 通用 |
| dog2_gazebo.urdf | 24K | 838 | 29 | 18 | Gazebo 仿真 |
| dog2_champ.urdf | 36K | 984 | 53 | 22 | CHAMP 控制 |
| dog2_visual.urdf | 36K | 1036 | 53 | 22 | 可视化 |
| dog2_optimized_for_crossing.urdf | 28K | 1111 | 33 | 18 | 障碍物跨越 |
| dog2_fixed_prismatic.urdf | 36K | 980 | 53 | 22 | 固定滑动副 |

---

## 🎯 使用场景指南

### 场景 1: 修改机器人参数
```bash
# 1. 编辑源文件
vim src/dog2_description/urdf/dog2.urdf.xacro

# 2. 重新生成 URDF
xacro src/dog2_description/urdf/dog2.urdf.xacro > src/dog2_description/urdf/dog2.urdf

# 3. 验证
check_urdf src/dog2_description/urdf/dog2.urdf

# 4. 验证关节限制
python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf
```

### 场景 2: Gazebo 仿真
```bash
# 使用 Gazebo 优化版本
ros2 launch dog2_description view_dog2_gazebo.launch.py
```

### 场景 3: RViz 可视化
```bash
# 使用标准版本或可视化版本
ros2 launch dog2_description view_dog2.launch.py
```

### 场景 4: CHAMP 控制器
```bash
# 使用 CHAMP 专用版本
ros2 launch dog2_champ_config bringup.launch.py
```

---

## ⚠️ 重要注意事项

### ❌ 不要做的事情：
1. **不要直接编辑 dog2.urdf** - 它是自动生成的，修改会被覆盖
2. **不要删除备份文件** - 它们是版本历史的重要记录
3. **不要混用不同版本** - 确保 launch 文件使用正确的 URDF 版本

### ✅ 应该做的事情：
1. **修改前创建备份** - 使用时间戳命名
2. **修改后验证** - 运行 check_urdf 和验证脚本
3. **保持同步** - 修改 .xacro 后立即重新生成 .urdf
4. **记录变更** - 在注释中说明修改原因

---

## 🔧 常用命令

```bash
# 生成 URDF
xacro src/dog2_description/urdf/dog2.urdf.xacro > src/dog2_description/urdf/dog2.urdf

# 验证 URDF 语法
check_urdf src/dog2_description/urdf/dog2.urdf

# 生成 URDF 树形图
urdf_to_graphiz src/dog2_description/urdf/dog2.urdf

# 验证关节限制
python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf

# 验证 Gazebo 控制配置
./scripts/verify_gazebo_control_config.sh

# 创建带时间戳的备份
cp src/dog2_description/urdf/dog2.urdf src/dog2_description/urdf/dog2.urdf.backup_$(date +%Y%m%d_%H%M%S)

# 查看文件差异
diff src/dog2_description/urdf/dog2.urdf src/dog2_description/urdf/dog2.urdf.backup
```

---

## 📚 相关文档

- `src/dog2_description/README_JOINT_LIMITS.md` - 关节限制详细说明
- `src/dog2_description/GAZEBO_CONTROL_FIX.md` - Gazebo 控制配置修复说明
- `src/dog2_description/urdf/README_URDF_FILES.md` - URDF 文件详细文档
- `.kiro/specs/urdf-xacro-joint-limits/` - 关节限制修改规范

---

**最后更新**: 2026-01-26  
**维护者**: Dog2 开发团队  
**状态**: ✅ 所有文件已验证，Gazebo 控制配置已修复
