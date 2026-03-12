# Base_link 碰撞模型中心对齐修复

## 问题描述

当对 base_link 的碰撞模型应用 `scale="0.95 0.95 0.95"` 后，碰撞模型的位置发生了偏移，与视觉模型不再对齐。

## 根本原因

当一个 STL mesh 被缩放时：
- 缩放是相对于 mesh **自身坐标系的原点** (0,0,0) 进行的
- 如果 mesh 的几何中心不在 (0,0,0)，缩放会导致整个模型向原点收缩
- 这会产生一个位置偏移

### 数学原理

假设：
- mesh 的几何中心在 `C = (Cx, Cy, Cz)`
- 缩放因子为 `s`（例如 0.95）

缩放后：
- mesh 的几何中心会移动到 `s * C`
- 产生的偏移量为 `offset = C * (1 - s)`

要保持中心位置不变，需要在 `<origin>` 中补偿这个偏移。

## 解决方案

### 步骤 1: 计算 base_link_collision.STL 的几何中心

```python
import numpy as np
from stl import mesh as stl_mesh

mesh = stl_mesh.Mesh.from_file("src/dog2_description/meshes/collision/base_link_collision.STL")
vertices = mesh.vectors.reshape(-1, 3)
center = vertices.mean(axis=0)
```

**结果：**
```
几何中心: (1.175155, -0.748214, 0.304559)
```

### 步骤 2: 计算偏移补偿

```python
scale = 0.95
offset = center * (1 - scale)
```

**结果：**
```
偏移量: (0.058758, -0.037411, 0.015228)
```

### 步骤 3: 更新 URDF collision origin

**修改前：**
```xml
<collision>
  <origin xyz="0 0 0" rpy="0 0 0" />
  <geometry>
    <mesh filename="package://dog2_description/meshes/collision/base_link_collision.STL" scale="0.95 0.95 0.95" />
  </geometry>
</collision>
```

**修改后：**
```xml
<collision>
  <origin xyz="0.058758 -0.037411 0.015228" rpy="0 0 0" />
  <geometry>
    <mesh filename="package://dog2_description/meshes/collision/base_link_collision.STL" scale="0.95 0.95 0.95" />
  </geometry>
</collision>
```

## 实现脚本

创建了 `scripts/fix_base_collision_offset.py` 来自动计算和应用偏移补偿。

## 最终配置

### base_link
- **碰撞 scale**: 0.95 (缩小 5%)
- **碰撞 origin**: (0.058758, -0.037411, 0.015228)
- **效果**: 碰撞模型与视觉模型完美对齐

### 腿部部件
- **碰撞 scale**: 0.8 (缩小 20%)
- **碰撞 origin**: 保持不变（因为腿部 mesh 的几何中心接近原点）
- **效果**: 在关节处创造间隙，防止重叠

## 验证方法

1. 编译：
```bash
colcon build --packages-select dog2_description --symlink-install
source install/setup.bash
```

2. 在 RViz 中查看：
```bash
ros2 launch dog2_description view_dog2.launch.py
```

3. 在 RViz 中启用 "Collision Enabled" 选项，检查：
   - base_link 的碰撞模型（半透明）应该与视觉模型（实体）完美重合
   - 腿部的碰撞模型应该比视觉模型小一圈（20% 缩小）

## 相关文件

- `scripts/fix_base_collision_offset.py` - 自动计算和应用偏移补偿
- `scripts/add_scale_to_collisions.py` - 添加 scale 参数
- `src/dog2_description/urdf/dog2.urdf.xacro` - 主 URDF 文件

## 日期

2026-01-29
