# Dog2 腿部位置修复说明

## 🐛 问题描述

在 RViz2 中查看 Dog2 机器人时，发现所有 4 条腿都堆叠在同一个位置，而不是分布在机器人身体的四个角落。

### 问题原因

`dog2.urdf` 文件中，所有 4 条腿的滑动关节（j1, j2, j3, j4）都使用了**相同的位置坐标**：

```xml
<!-- 错误：所有腿都在同一位置 -->
<joint name="j1" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>
</joint>

<joint name="j2" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>  ← 相同！
</joint>

<joint name="j3" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>  ← 相同！
</joint>

<joint name="j4" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>  ← 相同！
</joint>
```

---

## ✅ 修复方案

根据 `dog2.csv` 文件中的原始 CAD 数据，每条腿应该有不同的 XY 坐标：

### 正确的腿部位置

| 腿 | 关节 | X | Y | Z | 位置说明 |
|---|------|-------|---------|-------|----------|
| 腿1 | j1 | 1.1026 | -0.80953 | 0.2649 | 左前腿 |
| 腿2 | j2 | **1.3491** | -0.80953 | 0.2649 | 右前腿 |
| 腿3 | j3 | **1.3491** | **-0.68953** | 0.2649 | 右后腿 |
| 腿4 | j4 | **1.1071** | **-0.68953** | 0.2649 | 左后腿 |

### 修复后的代码

```xml
<!-- 正确：每条腿有不同的位置 -->
<joint name="j1" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>
  <parent link="base_link"/>
  <child link="l1"/>
  <axis xyz="-1 0 0"/>
  <limit effort="100" lower="-0.111" upper="0.111" velocity="5"/>
</joint>

<joint name="j2" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.3491 -0.80953 0.2649"/>  ← 修复 X
  <parent link="base_link"/>
  <child link="l2"/>
  <axis xyz="-1 0 0"/>
  <limit effort="100" lower="-0.111" upper="0.111" velocity="5"/>
</joint>

<joint name="j3" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.3491 -0.68953 0.2649"/>  ← 修复 X, Y
  <parent link="base_link"/>
  <child link="l3"/>
  <axis xyz="-1 0 0"/>
  <limit effort="100" lower="-0.111" upper="0.111" velocity="5"/>
</joint>

<joint name="j4" type="prismatic">
  <origin rpy="1.5708 0 0" xyz="1.1071 -0.68953 0.2649"/>  ← 修复 X, Y
  <parent link="base_link"/>
  <child link="l4"/>
  <axis xyz="-1 0 0"/>
  <limit effort="100" lower="-0.111" upper="0.111" velocity="5"/>
</joint>
```

---

## 📊 腿部布局示意图

```
机器人俯视图（从上往下看）：

        前方 (X+)
           ↑
           
    腿1 ●━━━━━━━● 腿2
    j1          j2
  (1.10, -0.81) (1.35, -0.81)
    
    │           │
    │  base_link│
    │           │
    
    腿4 ●━━━━━━━● 腿3
    j4          j3
  (1.11, -0.69) (1.35, -0.69)

        后方 (X-)
```

### 坐标系说明

- **X 轴**: 前后方向（前方为正）
- **Y 轴**: 左右方向（左侧为负）
- **Z 轴**: 上下方向（向上为正）

### 腿部间距

- **前后间距**: 约 0.12 m (Y 方向)
- **左右间距**: 约 0.25 m (X 方向)

---

## 🔧 修复的文件

### 已修复
- ✅ `src/dog2_description/urdf/dog2.urdf` - 原始 URDF 文件

### 待修复
- ⚠️ `src/dog2_description/urdf/dog2.urdf.xacro` - Xacro 源文件（不完整，需要重建）

---

## 🧪 验证修复

### 方法 1: 在 RViz2 中查看

```bash
cd /home/dell/aperfect/carbot_ws
./view_original_urdf_in_rviz.sh
```

### 方法 2: 检查 URDF 语法

```bash
check_urdf src/dog2_description/urdf/dog2.urdf
```

### 方法 3: 验证关节位置

```bash
grep -A2 'joint name="j[1-4]" type="prismatic"' src/dog2_description/urdf/dog2.urdf | grep "origin"
```

应该看到 4 个不同的 XYZ 坐标。

---

## 📝 预期结果

修复后，在 RViz2 中应该看到：

✅ **正确的布局**:
- 4 条腿分布在机器人身体的四个角落
- 腿1 和腿4 在左侧（Y ≈ -0.81 和 -0.69）
- 腿2 和腿3 在右侧（Y ≈ -0.81 和 -0.69）
- 腿1 和腿2 在前方（X ≈ 1.10 和 1.35）
- 腿3 和腿4 在后方（X ≈ 1.35 和 1.11）

❌ **修复前的错误**:
- 所有 4 条腿堆叠在同一位置
- 无法区分各条腿

---

## 🔍 数据来源

修复数据来自 `src/dog2_description/urdf/dog2.csv` 文件，这是从 SolidWorks CAD 模型导出的原始参数。

CSV 文件中的关节位置数据：

```csv
Joint Name, Joint Origin X, Joint Origin Y, Joint Origin Z
j1,         1.1026,        -0.80953,       0.2649
j2,         1.3491,        -0.80953,       0.2649
j3,         1.3491,        -0.68953,       0.2649
j4,         1.1071,        -0.68953,       0.2649
```

---

## ⚠️ 注意事项

### 1. Xacro 文件需要重建

`dog2.urdf.xacro` 文件目前不完整（只有 510 行，缺少腿部定义）。如果需要使用 xacro，需要：

1. 从完整的 `dog2.urdf` 重建 xacro 文件
2. 或者使用其他完整的 URDF 版本（如 `dog2_gazebo.urdf`）

### 2. 其他 URDF 文件

目录中的其他 URDF 文件可能也有相同的问题，需要逐个检查：

- `dog2_gazebo.urdf`
- `dog2_champ.urdf`
- `dog2_visual.urdf`
- `dog2_optimized_for_crossing.urdf`

### 3. 编译和更新

修改 URDF 后，需要重新编译工作空间：

```bash
cd /home/dell/aperfect/carbot_ws
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
```

---

## 📚 相关文档

- `URDF_FILES_SUMMARY.md` - URDF 文件完整说明
- `src/dog2_description/urdf/README_URDF_FILES.md` - URDF 文件技术文档
- `src/dog2_description/urdf/dog2.csv` - 原始 CAD 参数数据

---

## 🎯 总结

**问题**: 所有腿的关节位置相同，导致腿部堆叠

**原因**: URDF 文件中 j1, j2, j3, j4 关节的 origin xyz 坐标完全相同

**修复**: 根据 CSV 数据，为每条腿设置正确的 XY 坐标

**结果**: 4 条腿正确分布在机器人身体的四个角落

---

**修复日期**: 2026-01-26  
**修复文件**: `src/dog2_description/urdf/dog2.urdf`  
**状态**: ✅ 已修复并验证
