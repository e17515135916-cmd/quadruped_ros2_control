# Design Document: Prismatic Coordinate System Fix

## Overview

本设计文档描述了如何修复 Dog2 四足机器人的 Prismatic joint 坐标系问题。根本问题是 Prismatic joint 的 `rpy="1.5708 0 0"` 旋转导致整个腿部坐标系被旋转 90°，使得 HAA、HFE、KFE 三个关节都在同一平面旋转，无法实现 CHAMP 框架要求的正交关节配置。

**核心解决方案**：
1. 移除 Prismatic joint 的 RPY 旋转（改为 `rpy="0 0 0"`）
2. 重新计算所有后续关节的 origin（xyz 和 rpy），以补偿坐标系变化
3. 确保 HAA 关节垂直于 HFE/KFE 平面

## Architecture

### 当前问题架构

```
base_link
  └─ j1 (prismatic, rpy="1.5708 0 0")  ← 这里旋转了坐标系！
      └─ l1
          └─ lf_haa_joint (axis="0 0 1", rpy="-1.5708 0 0")
              └─ lf_hip_link
                  └─ lf_hfe_joint (axis="-1 0 0", rpy="0 1.5708 0")
                      └─ lf_upper_leg_link
                          └─ lf_kfe_joint (axis="-1 0 0")
                              └─ lf_lower_leg_link
```

**问题分析**：
- Prismatic joint 的 `rpy="1.5708 0 0"` 将整个坐标系绕 x 轴旋转 90°
- 在旋转后的坐标系中：
  - 原 z 轴 → 新 -y 轴
  - 原 y 轴 → 新 z 轴
  - 原 x 轴 → 新 x 轴（不变）
- HAA 的 `axis="0 0 1"` 在旋转后的坐标系中实际指向 -y 方向（世界坐标系）
- HFE 的 `axis="-1 0 0"` 始终指向 -x 方向
- 结果：HAA 和 HFE 都在 xy 平面旋转，不正交！

### 目标架构

```
base_link
  └─ j1 (prismatic, rpy="0 0 0")  ← 移除旋转！
      └─ l1
          └─ lf_haa_joint (axis="0 0 1", rpy="NEW_RPY")  ← 重新计算
              └─ lf_hip_link
                  └─ lf_hfe_joint (axis="-1 0 0", rpy="NEW_RPY")  ← 重新计算
                      └─ lf_upper_leg_link
                          └─ lf_kfe_joint (axis="-1 0 0", rpy="NEW_RPY")  ← 重新计算
                              └─ lf_lower_leg_link
```

**目标**：
- HAA 的 `axis="0 0 1"` 在世界坐标系中指向 z 方向（垂直）
- HFE 的 `axis="-1 0 0"` 在世界坐标系中指向 -x 方向（前后）
- HAA 和 HFE 正交（垂直）

## Components and Interfaces

### 1. 坐标变换数学

#### 当前坐标变换链

对于 Leg 1（前左腿），当前的变换链为：

```
T_base_to_l1 = Trans(1.1026, -0.80953, 0.2649) * Rot_x(1.5708)
T_l1_to_hip = Trans(-0.016, 0.0199, 0.080) * Rot_x(-1.5708)
T_hip_to_thigh = Trans(-0.0233, -0.055, 0.0274) * Rot_y(1.5708)
T_thigh_to_shin = Trans(0, -0.15201, 0.12997)
```

其中 `Rot_x(1.5708)` 是问题根源。

#### 目标坐标变换链

移除 Prismatic 的 RPY 后：

```
T_base_to_l1 = Trans(1.1026, -0.80953, 0.2649)  ← 移除 Rot_x(1.5708)
T_l1_to_hip = Trans(NEW_XYZ) * Rot(NEW_RPY)     ← 需要重新计算
T_hip_to_thigh = Trans(NEW_XYZ) * Rot(NEW_RPY)  ← 需要重新计算
T_thigh_to_shin = Trans(NEW_XYZ) * Rot(NEW_RPY) ← 需要重新计算
```

#### 坐标变换计算方法

**步骤 1：计算当前世界坐标系中的关节位置**

使用当前 URDF，计算每个关节在世界坐标系中的位置和方向：

```python
import numpy as np
from scipy.spatial.transform import Rotation as R

# 当前配置
prismatic_xyz = np.array([1.1026, -0.80953, 0.2649])
prismatic_rpy = np.array([1.5708, 0, 0])

haa_xyz_local = np.array([-0.016, 0.0199, 0.080])
haa_rpy_local = np.array([-1.5708, 0, 0])

# 计算 HAA 在世界坐标系中的位置
R_prismatic = R.from_euler('xyz', prismatic_rpy)
haa_xyz_world = prismatic_xyz + R_prismatic.apply(haa_xyz_local)
haa_R_world = R_prismatic * R.from_euler('xyz', haa_rpy_local)
```

**步骤 2：在新坐标系中重新表达**

移除 Prismatic RPY 后，重新计算 HAA 的 origin：

```python
# 新配置：Prismatic rpy = [0, 0, 0]
prismatic_rpy_new = np.array([0, 0, 0])
R_prismatic_new = R.from_euler('xyz', prismatic_rpy_new)  # 单位矩阵

# HAA 在世界坐标系中的位置不变
# 但现在需要在新的 l1 坐标系中表达
haa_xyz_new = haa_xyz_world - prismatic_xyz  # 因为 R_prismatic_new 是单位矩阵
haa_R_new = haa_R_world  # 世界坐标系中的方向不变
haa_rpy_new = haa_R_new.as_euler('xyz')
```

### 2. 具体计算结果

#### Leg 1 (Front Left) 计算

**当前配置**：
```xml
<!-- Prismatic joint -->
<origin rpy="1.5708 0 0" xyz="1.1026 -0.80953 0.2649"/>

<!-- HAA joint -->
<origin rpy="-1.5708 0 0" xyz="-0.016 0.0199 0.080"/>

<!-- HFE joint -->
<origin rpy="0 1.5708 0" xyz="-0.0233 -0.055 0.0274"/>

<!-- KFE joint -->
<origin rpy="0 0 0" xyz="0 -0.15201 0.12997"/>
```

**计算步骤**：

1. **Prismatic joint 世界位置**：
   - xyz: (1.1026, -0.80953, 0.2649)
   - R = Rot_x(90°)

2. **HAA joint 在旧 l1 坐标系中**：
   - xyz_local: (-0.016, 0.0199, 0.080)
   - 在旧坐标系中（已旋转 90°）：
     - x_old → x_new
     - y_old → z_new
     - z_old → -y_new

3. **HAA joint 在世界坐标系中**：
   ```python
   # 旋转 xyz_local
   # Rot_x(90°) * [-0.016, 0.0199, 0.080]
   # = [-0.016, -0.080, 0.0199]
   
   haa_world = [1.1026, -0.80953, 0.2649] + [-0.016, -0.080, 0.0199]
             = [1.0866, -0.88953, 0.2848]
   ```

4. **HAA joint 在新 l1 坐标系中**（Prismatic rpy="0 0 0"）：
   ```python
   # 新 l1 坐标系与世界坐标系对齐
   haa_xyz_new = [1.0866, -0.88953, 0.2848] - [1.1026, -0.80953, 0.2649]
               = [-0.016, -0.080, 0.0199]
   ```

5. **HAA joint 的新 RPY**：
   ```python
   # 旧 HAA rpy: (-1.5708, 0, 0) 在旧坐标系中
   # 旧坐标系已经被 Rot_x(90°) 旋转
   # 总旋转 = Rot_x(90°) * Rot_x(-90°) = Identity
   # 但我们需要 HAA axis="0 0 1" 指向世界 z 轴
   
   # 新 HAA rpy 应该让 hip_link 正确定向
   # 需要补偿原来的 Rot_x(90°)
   haa_rpy_new = [0, 0, 0]  # 需要通过实验确定
   ```

**简化方法**：

由于坐标变换复杂，我们采用以下策略：

1. **保持 HAA joint xyz 不变**：`xyz="-0.016 0.0199 0.080"`
   - 但需要理解这是在新坐标系中的表达

2. **调整 HAA joint rpy**：
   - 原来：`rpy="-1.5708 0 0"` 用于抵消 Prismatic 的旋转
   - 现在：需要新的 rpy 来正确定向 hip_link
   - 由于移除了 Prismatic 的 Rot_x(90°)，hip_link 会旋转 90°
   - 新 rpy 应该是：`rpy="0 0 0"` 或需要补偿

3. **调整 HFE joint rpy**：
   - 原来：`rpy="0 1.5708 0"` 
   - 现在：需要考虑 HAA 坐标系的变化

### 3. 实用计算方法

**方法 1：坐标变换补偿**

```python
def calculate_new_origins():
    """
    计算移除 Prismatic RPY 后的新 joint origins
    """
    # 步骤 1：移除 Prismatic RPY
    prismatic_rpy_old = [1.5708, 0, 0]
    prismatic_rpy_new = [0, 0, 0]
    
    # 步骤 2：计算补偿旋转
    R_compensation = R.from_euler('xyz', prismatic_rpy_old)
    
    # 步骤 3：对每个子关节应用补偿
    # HAA joint
    haa_xyz_old = [-0.016, 0.0199, 0.080]
    haa_rpy_old = [-1.5708, 0, 0]
    
    # 在新坐标系中，xyz 需要反向旋转
    haa_xyz_new = R_compensation.apply(haa_xyz_old)
    
    # rpy 需要组合旋转
    R_haa_old = R.from_euler('xyz', haa_rpy_old)
    R_haa_new = R_compensation * R_haa_old
    haa_rpy_new = R_haa_new.as_euler('xyz')
    
    return {
        'haa_xyz': haa_xyz_new,
        'haa_rpy': haa_rpy_new
    }
```

**方法 2：RViz 实验验证**

1. 修改 Prismatic rpy 为 "0 0 0"
2. 在 RViz 中观察机器人姿态
3. 逐步调整 HAA、HFE、KFE 的 origin rpy
4. 直到视觉外观与原设计匹配
5. 验证关节运动方向正确

### 4. 预期结果

#### Leg 1 (Front Left) 新配置

```xml
<!-- Prismatic joint -->
<joint name="j1" type="prismatic">
  <origin rpy="0 0 0" xyz="1.1026 -0.80953 0.2649"/>
  <parent link="base_link"/>
  <child link="l1"/>
  <axis xyz="-1 0 0"/>
  <limit effort="100" lower="-0.111" upper="0.0" velocity="5"/>
</joint>

<!-- HAA joint -->
<joint name="lf_haa_joint" type="revolute">
  <origin rpy="0 0 0" xyz="-0.016 -0.080 0.0199"/>
  <parent link="l1"/>
  <child link="lf_hip_link"/>
  <axis xyz="0 0 1"/>
  <limit effort="50" lower="-0.785" upper="0.785" velocity="20"/>
</joint>

<!-- HFE joint -->
<joint name="lf_hfe_joint" type="revolute">
  <origin rpy="1.5708 0 0" xyz="-0.0233 -0.055 0.0274"/>
  <parent link="lf_hip_link"/>
  <child link="lf_upper_leg_link"/>
  <axis xyz="-1 0 0"/>
  <limit effort="50" lower="-2.618" upper="2.618" velocity="20"/>
</joint>

<!-- KFE joint -->
<joint name="lf_kfe_joint" type="revolute">
  <origin rpy="0 0 0" xyz="0 -0.15201 0.12997"/>
  <parent link="lf_upper_leg_link"/>
  <child link="lf_lower_leg_link"/>
  <axis xyz="-1 0 0"/>
  <limit effort="50" lower="-2.8" upper="0.0" velocity="20"/>
</joint>
```

**关键变化**：
1. Prismatic rpy: `1.5708 0 0` → `0 0 0`
2. HAA xyz: `-0.016 0.0199 0.080` → `-0.016 -0.080 0.0199` （坐标轴交换）
3. HAA rpy: `-1.5708 0 0` → `0 0 0` （移除补偿旋转）
4. HFE rpy: `0 1.5708 0` → `1.5708 0 0` （调整方向）

## Data Models

### 坐标变换数据结构

```python
from dataclasses import dataclass
from typing import Tuple
import numpy as np

@dataclass
class JointOrigin:
    """Joint origin configuration"""
    xyz: Tuple[float, float, float]
    rpy: Tuple[float, float, float]
    
    def to_transform_matrix(self) -> np.ndarray:
        """Convert to 4x4 transformation matrix"""
        from scipy.spatial.transform import Rotation as R
        
        T = np.eye(4)
        T[:3, :3] = R.from_euler('xyz', self.rpy).as_matrix()
        T[:3, 3] = self.xyz
        return T

@dataclass
class LegConfiguration:
    """Complete leg configuration"""
    leg_name: str  # "lf", "rf", "lh", "rh"
    
    # Prismatic joint
    prismatic_origin: JointOrigin
    prismatic_limits: Tuple[float, float]
    
    # HAA joint
    haa_origin: JointOrigin
    haa_axis: Tuple[float, float, float]
    haa_limits: Tuple[float, float]
    
    # HFE joint
    hfe_origin: JointOrigin
    hfe_axis: Tuple[float, float, float]
    hfe_limits: Tuple[float, float]
    
    # KFE joint
    kfe_origin: JointOrigin
    kfe_axis: Tuple[float, float, float]
    kfe_limits: Tuple[float, float]
```

### 四条腿的配置

```python
# Leg 1: Front Left
leg1_config = LegConfiguration(
    leg_name="lf",
    prismatic_origin=JointOrigin(
        xyz=(1.1026, -0.80953, 0.2649),
        rpy=(0, 0, 0)  # 移除旋转
    ),
    prismatic_limits=(-0.111, 0.0),
    haa_origin=JointOrigin(
        xyz=(-0.016, -0.080, 0.0199),  # 重新计算
        rpy=(0, 0, 0)  # 重新计算
    ),
    haa_axis=(0, 0, 1),
    haa_limits=(-0.785, 0.785),
    hfe_origin=JointOrigin(
        xyz=(-0.0233, -0.055, 0.0274),
        rpy=(1.5708, 0, 0)  # 重新计算
    ),
    hfe_axis=(-1, 0, 0),
    hfe_limits=(-2.618, 2.618),
    kfe_origin=JointOrigin(
        xyz=(0, -0.15201, 0.12997),
        rpy=(0, 0, 0)
    ),
    kfe_axis=(-1, 0, 0),
    kfe_limits=(-2.8, 0.0)
)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Prismatic RPY Removed
*For any* leg (lf, rf, lh, rh), the Prismatic joint SHALL have origin rpy=(0, 0, 0)

**Validates: Requirements 1.1**

### Property 2: HAA Axis in World Frame
*For any* leg at zero position, the HAA joint axis in world frame SHALL be approximately (0, 0, 1)

**Validates: Requirements 2.4, 5.1**

### Property 3: HFE Axis in World Frame
*For any* leg at zero position, the HFE joint axis in world frame SHALL be approximately (±1, 0, 0)

**Validates: Requirements 3.4, 5.2**

### Property 4: HAA and HFE Orthogonality
*For any* leg at zero position, the dot product of HAA axis and HFE axis in world frame SHALL be approximately 0

**Validates: Requirements 5.1, 5.2, 5.5**

### Property 5: HAA and KFE Orthogonality
*For any* leg at zero position, the dot product of HAA axis and KFE axis in world frame SHALL be approximately 0

**Validates: Requirements 5.1, 5.3, 5.5**

### Property 6: HFE and KFE Parallel
*For any* leg at zero position, the HFE axis and KFE axis in world frame SHALL be approximately parallel (dot product ≈ ±1)

**Validates: Requirements 5.3**

### Property 7: Joint Position Preservation
*For any* joint, the position in world frame at zero configuration SHALL match the original position within 1mm tolerance

**Validates: Requirements 2.3, 3.3, 4.3, 6.2**

### Property 8: Visual Geometry Preservation
*For any* link, the visual mesh position and orientation SHALL match the original design at zero configuration

**Validates: Requirements 6.1, 6.3**

### Property 9: HAA Motion Direction
*For any* leg, when HAA joint rotates positively, the leg SHALL move in abduction direction (away from body center)

**Validates: Requirements 2.5, 8.2**

### Property 10: HFE Motion Direction
*For any* leg, when HFE joint rotates positively, the leg SHALL move in flexion direction (forward for front legs, backward for rear legs)

**Validates: Requirements 3.5, 8.3**

### Property 11: KFE Motion Direction
*For any* leg, when KFE joint rotates negatively, the shin SHALL fold upward

**Validates: Requirements 4.5, 8.4**

### Property 12: Joint Names Unchanged
*For any* leg, the joint names SHALL remain as j1, j11, j111 (or lf_haa_joint, lf_hfe_joint, lf_kfe_joint)

**Validates: Requirements 9.1, 10.1**

### Property 13: Joint Limits Unchanged
*For any* joint, the position, effort, and velocity limits SHALL match the original configuration

**Validates: Requirements 9.4, 9.5**

## Error Handling

### Potential Issues

1. **坐标变换计算错误**
   - Check: 使用 RViz 验证零位姿态
   - Handle: 逐步调整 origin 参数
   - Recovery: 回退到备份配置

2. **关节轴向错误**
   - Check: 在 RViz 中测试每个关节的运动方向
   - Handle: 调整 axis 参数或 origin rpy
   - Recovery: 使用 TF tree 分析坐标系

3. **视觉几何错位**
   - Check: 对比修改前后的 RViz 显示
   - Handle: 调整 link visual origin
   - Recovery: 重新计算坐标变换

4. **碰撞几何错位**
   - Check: 在 Gazebo 中测试碰撞
   - Handle: 调整 collision origin
   - Recovery: 使用简化碰撞几何

## Testing Strategy

### Unit Tests

#### Test 1: Prismatic RPY Verification
- 解析 URDF
- 验证所有 Prismatic joints 的 rpy 为 (0, 0, 0)

#### Test 2: Joint Axis Verification
- 计算每个关节在世界坐标系中的轴向
- 验证 HAA axis ≈ (0, 0, 1)
- 验证 HFE axis ≈ (±1, 0, 0)
- 验证 KFE axis ≈ (±1, 0, 0)

#### Test 3: Orthogonality Verification
- 计算 HAA 和 HFE 轴向的点积
- 验证点积 ≈ 0（正交）

#### Test 4: Joint Position Verification
- 计算每个关节在世界坐标系中的位置
- 与原始配置对比
- 验证误差 < 1mm

### Property-Based Tests

#### Property Test 1: Prismatic RPY Removed
- 解析 URDF
- 验证所有 Prismatic joints 的 rpy = (0, 0, 0)
- **Feature: prismatic-coordinate-system-fix, Property 1: Prismatic RPY Removed**

#### Property Test 2: Joint Axes Orthogonality
- 对每条腿计算 HAA、HFE、KFE 在世界坐标系中的轴向
- 验证 HAA ⊥ HFE（点积 ≈ 0）
- 验证 HAA ⊥ KFE（点积 ≈ 0）
- 验证 HFE ∥ KFE（点积 ≈ ±1）
- **Feature: prismatic-coordinate-system-fix, Property 4-6: Joint orthogonality**

#### Property Test 3: Joint Position Preservation
- 对每条腿计算所有关节在世界坐标系中的位置
- 与原始配置对比
- 验证误差 < 1mm
- **Feature: prismatic-coordinate-system-fix, Property 7: Joint position preservation**

### Integration Tests

#### Test 1: RViz Visual Verification
- 加载修改后的 URDF 到 RViz
- 验证零位姿态与原设计匹配
- 使用 joint_state_publisher_gui 测试每个关节
- 验证运动方向正确

#### Test 2: TF Tree Analysis
- 发布 robot_description
- 使用 `ros2 run tf2_tools view_frames` 生成 TF tree
- 验证坐标系关系正确

#### Test 3: Motion Direction Verification
- 在 RViz 中逐个测试关节
- HAA: 验证左右摆动（abduction/adduction）
- HFE: 验证前后摆动（flexion/extension）
- KFE: 验证膝关节折叠

## Implementation Plan

### Phase 1: 坐标变换计算
1. 编写 Python 脚本计算新的 joint origins
2. 使用 scipy.spatial.transform 进行旋转计算
3. 生成所有四条腿的新配置

### Phase 2: URDF 修改
1. 备份当前 URDF
2. 修改 Prismatic joint rpy 为 "0 0 0"
3. 更新 HAA joint origin（xyz 和 rpy）
4. 更新 HFE joint origin（xyz 和 rpy）
5. 更新 KFE joint origin（如需要）

### Phase 3: RViz 验证
1. 加载修改后的 URDF
2. 验证零位姿态
3. 测试每个关节的运动方向
4. 调整 origin 参数直到正确

### Phase 4: 测试
1. 运行单元测试
2. 运行属性测试
3. 运行集成测试
4. 生成测试报告

### Phase 5: 文档
1. 记录坐标变换计算过程
2. 创建迁移指南
3. 更新机器人文档

## Dependencies

- Python 3.8+
- scipy (spatial.transform)
- numpy
- urdf_parser_py
- ROS 2 Humble
- RViz2

## Timeline Estimate

- Phase 1: 2 hours（坐标计算）
- Phase 2: 1 hour（URDF 修改）
- Phase 3: 2 hours（RViz 验证和调整）
- Phase 4: 1 hour（测试）
- Phase 5: 1 hour（文档）
- **Total**: 7 hours

## Risks and Mitigations

### Risk 1: 坐标变换计算错误
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: 使用 RViz 实时验证，逐步调整

### Risk 2: 视觉几何错位
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: 对比修改前后的 RViz 显示

### Risk 3: 破坏现有功能
- **Probability**: Low
- **Impact**: High
- **Mitigation**: 完整备份，保持向后兼容性

## Conclusion

本设计通过移除 Prismatic joint 的 RPY 旋转并重新计算所有后续关节的 origin，从根本上解决了坐标系问题。这将使 HAA 关节能够垂直于 HFE/KFE 平面，实现 CHAMP 框架要求的正交关节配置。

关键步骤是正确计算坐标变换，并通过 RViz 验证结果。通过系统的测试和验证，我们可以确保修改后的 URDF 保持机器人的物理几何和运动学特性。
