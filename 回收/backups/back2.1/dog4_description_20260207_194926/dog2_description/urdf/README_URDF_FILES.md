# Dog2 URDF 目录文件说明

本目录包含 Dog2 四足机器人的各种 URDF（统一机器人描述格式）文件。以下是每个文件的详细说明。

## 📁 主要工作文件

### 1. **dog2.urdf.xacro** ⭐ (主源文件)
- **大小**: 16K (510 行)
- **类型**: Xacro 模板文件
- **用途**: **这是主要的源文件**，使用 Xacro 宏语言编写
- **特点**:
  - 包含 10 个可配置属性（关节限制、力矩、速度等）
  - 支持参数化配置
  - 包含完整的 ROS 2 Control 配置
  - 包含 Gazebo 插件配置
- **关节限制**:
  - Hip 关节: ±150° (±2.618 rad)
  - Knee 关节: ±160° (±2.8 rad)
  - Prismatic 关节: ±0.111 m
- **生成命令**: `xacro dog2.urdf.xacro > dog2.urdf`
- **状态**: ✅ 最新，已修复 Gazebo 控制器配置

### 2. **dog2.urdf** (生成文件)
- **大小**: 28K (728 行)
- **类型**: 标准 URDF 文件
- **用途**: 从 `dog2.urdf.xacro` 自动生成的最终 URDF 文件
- **特点**:
  - 包含 18 个连杆（links）
  - 包含 29 个关节（joints）
  - 包含完整的惯性、碰撞、视觉信息
  - 包含 ROS 2 Control 和 Gazebo 配置
- **警告**: ⚠️ 不要手动编辑此文件！应该编辑 `dog2.urdf.xacro` 然后重新生成
- **状态**: ✅ 最新，已包含控制器配置路径

---

## 📁 专用版本文件

### 3. **dog2_gazebo.urdf**
- **大小**: 24K (838 行)
- **用途**: 专门为 Gazebo 仿真优化的版本
- **特点**:
  - 简化的碰撞几何（使用球体代替复杂网格）
  - 调整的惯性参数以提高仿真稳定性
  - 包含接触传感器配置
  - 包含 IMU 传感器
  - 摩擦系数优化
- **关节数**: 29 个关节
- **连杆数**: 18 个连杆
- **使用场景**: Gazebo 物理仿真

### 4. **dog2_champ.urdf**
- **大小**: 36K (984 行)
- **用途**: 为 CHAMP 四足控制器框架配置的版本
- **特点**:
  - 包含 CHAMP 特定的关节配置
  - 更多的关节（53 个）和连杆（22 个）
  - 可能包含额外的虚拟关节用于控制
- **使用场景**: 与 CHAMP 控制器集成

### 5. **dog2_visual.urdf**
- **大小**: 36K (1036 行)
- **用途**: 专门用于可视化的版本
- **特点**:
  - 包含完整的视觉网格
  - 53 个关节，22 个连杆
  - 可能包含更详细的视觉元素
- **使用场景**: RViz 可视化，不用于物理仿真

### 6. **dog2_fixed_prismatic.urdf**
- **大小**: 36K (980 行)
- **用途**: 固定滑动副（prismatic joint）的版本
- **特点**:
  - 滑动关节可能被固定或移除
  - 53 个关节，22 个连杆
- **使用场景**: 测试不带滑动副的运动

### 7. **dog2_optimized_for_crossing.urdf**
- **大小**: 28K (1111 行)
- **用途**: 为障碍物跨越优化的版本
- **特点**:
  - 可能包含特殊的关节限制配置
  - 针对跨越动作优化的参数
  - 33 个关节，18 个连杆
- **使用场景**: 障碍物跨越实验

---

## 📁 辅助文件

### 8. **links.xacro**
- **大小**: 8K (165 行)
- **类型**: Xacro 宏定义文件
- **用途**: 包含可重用的连杆宏定义
- **特点**: 可能定义了腿部结构的宏，用于减少重复代码

### 9. **dog2.csv**
- **大小**: 12K (18 行)
- **类型**: CSV 数据文件
- **用途**: 可能包含关节参数、DH 参数或其他机器人参数
- **使用场景**: 参数导入/导出，数据分析

### 10. **simple.urdf**
- **大小**: 4K (空文件)
- **用途**: 可能是简化的测试模型
- **状态**: 当前为空

---

## 📁 备份文件

### 11. **dog2.urdf.backup**
- **日期**: 未标注
- **用途**: 通用备份

### 12. **dog2.urdf.backup_20260112_170119**
- **日期**: 2026-01-12 17:01:19
- **用途**: 时间戳备份

### 13. **dog2.urdf.backup_20260126_171703**
- **日期**: 2026-01-26 17:17:03
- **用途**: 最近的备份（关节限制修改前）

### 14. **dog2.urdf.backup_xacro_migration**
- **用途**: Xacro 迁移前的备份
- **说明**: 从纯 URDF 迁移到 Xacro 之前的版本

### 15. **dog2.urdf.xacro.before_macro**
- **大小**: 28K (1076 行)
- **用途**: 引入宏之前的 Xacro 版本
- **说明**: 重构为使用宏之前的版本

### 16. **dog2_gazebo.urdf.old_backup**
- **用途**: Gazebo URDF 的旧备份

---

## 🔄 文件关系图

```
dog2.urdf.xacro (源文件)
    ↓ (xacro 处理)
dog2.urdf (生成文件)
    ↓ (用于)
├── ROS 2 节点
├── Gazebo 仿真
└── RViz 可视化

dog2_gazebo.urdf ← 专门为 Gazebo 优化
dog2_champ.urdf ← 专门为 CHAMP 控制器
dog2_visual.urdf ← 专门为可视化
dog2_optimized_for_crossing.urdf ← 专门为障碍物跨越
```

---

## 📊 关键统计

| 文件 | 关节数 | 连杆数 | 用途 |
|------|--------|--------|------|
| dog2.urdf.xacro | - | - | 源模板 |
| dog2.urdf | 29 | 18 | 通用 |
| dog2_gazebo.urdf | 29 | 18 | Gazebo |
| dog2_champ.urdf | 53 | 22 | CHAMP |
| dog2_visual.urdf | 53 | 22 | 可视化 |
| dog2_optimized_for_crossing.urdf | 33 | 18 | 跨越 |

---

## 🎯 使用建议

### 开发工作流程：
1. **修改参数**: 编辑 `dog2.urdf.xacro`
2. **生成 URDF**: 运行 `xacro dog2.urdf.xacro > dog2.urdf`
3. **验证**: 运行 `check_urdf dog2.urdf`
4. **测试**: 在 RViz 或 Gazebo 中测试

### 选择合适的文件：
- **一般开发**: 使用 `dog2.urdf.xacro` 和 `dog2.urdf`
- **Gazebo 仿真**: 使用 `dog2_gazebo.urdf`（如果需要优化的物理参数）
- **CHAMP 控制**: 使用 `dog2_champ.urdf`
- **纯可视化**: 使用 `dog2_visual.urdf`
- **障碍物跨越**: 使用 `dog2_optimized_for_crossing.urdf`

---

## ⚠️ 重要提示

1. **不要直接编辑生成的文件**: `dog2.urdf` 是自动生成的，修改会被覆盖
2. **保持备份**: 重要修改前创建带时间戳的备份
3. **验证修改**: 每次修改后运行验证脚本
4. **同步更新**: 如果修改了 `dog2.urdf.xacro`，记得重新生成 `dog2.urdf`

---

## 🔧 相关命令

```bash
# 生成 URDF
xacro src/dog2_description/urdf/dog2.urdf.xacro > src/dog2_description/urdf/dog2.urdf

# 验证 URDF
check_urdf src/dog2_description/urdf/dog2.urdf

# 查看 URDF 树结构
urdf_to_graphiz src/dog2_description/urdf/dog2.urdf

# 验证关节限制
python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf

# 验证 Gazebo 控制配置
./scripts/verify_gazebo_control_config.sh
```

---

**最后更新**: 2026-01-26
**维护者**: Dog2 开发团队
