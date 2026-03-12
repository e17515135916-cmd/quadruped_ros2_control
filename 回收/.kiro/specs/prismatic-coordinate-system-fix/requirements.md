# Requirements Document

## Introduction

本文档定义了修复 Dog2 四足机器人 Prismatic joint 坐标系问题的需求。根本问题是：Prismatic joint 的 `rpy="1.5708 0 0"` 旋转了整个腿部坐标系，导致 HAA、HFE、KFE 三个关节都在同一平面旋转，无法实现 CHAMP 框架要求的正交关节配置（HAA 垂直于 HFE/KFE 平面）。

真正的解决方案是：移除 Prismatic joint 的 RPY 旋转，重新设计整个腿部的坐标系，确保 HAA 关节能够垂直于 HFE/KFE 平面。

## Glossary

- **Prismatic_Joint**: 滑动副关节（j1, j2, j3, j4），当前配置为 `rpy="1.5708 0 0"`
- **Coordinate_System**: 坐标系，由 joint origin 的 xyz 和 rpy 定义
- **HAA**: Hip Abduction/Adduction，髋关节外展/内收，应绕 z 轴旋转
- **HFE**: Hip Flexion/Extension，髋关节前后摆动，应绕 x 轴旋转
- **KFE**: Knee Flexion/Extension，膝关节屈伸，应绕 x 轴旋转
- **Orthogonal_Joints**: 正交关节配置，HAA 的旋转轴垂直于 HFE/KFE 的旋转平面
- **CHAMP**: Champ Humanoid And Manipulation Platform，要求 HAA、HFE、KFE 正交配置

## Requirements

### Requirement 1: 移除 Prismatic Joint 的 RPY 旋转

**User Story:** 作为机器人工程师，我想移除 Prismatic joint 的 RPY 旋转，以便腿部坐标系不被预先旋转。

#### Acceptance Criteria

1. WHEN the URDF is parsed, THE Prismatic joints (j1, j2, j3, j4) SHALL have origin rpy="0 0 0"
2. WHEN the Prismatic joint is at zero position, THE child link coordinate system SHALL align with base_link coordinate system
3. WHEN the robot is visualized, THE Prismatic links SHALL maintain their correct visual orientation
4. THE Prismatic joint axis SHALL remain as "-1 0 0" (x-axis sliding)

### Requirement 2: 重新计算 HAA Joint 的 Origin

**User Story:** 作为机器人工程师，我想重新计算 HAA joint 的 origin，以便补偿移除 Prismatic RPY 后的坐标变换。

#### Acceptance Criteria

1. WHEN Prismatic RPY is removed, THE HAA joint origin xyz SHALL be recalculated to maintain physical geometry
2. WHEN Prismatic RPY is removed, THE HAA joint origin rpy SHALL be recalculated to achieve proper orientation
3. WHEN the robot is at zero position, THE HAA joint SHALL be in the same physical location as before
4. THE HAA joint axis SHALL be "0 0 1" (z-axis for abduction/adduction)
5. WHEN HAA rotates, THE leg SHALL move in abduction/adduction motion (left-right)

### Requirement 3: 重新计算 HFE Joint 的 Origin

**User Story:** 作为机器人工程师，我想重新计算 HFE joint 的 origin，以便在新坐标系下保持正确的几何关系。

#### Acceptance Criteria

1. WHEN Prismatic RPY is removed, THE HFE joint origin xyz SHALL be recalculated relative to HAA joint
2. WHEN Prismatic RPY is removed, THE HFE joint origin rpy SHALL be recalculated to achieve proper orientation
3. WHEN the robot is at zero position, THE HFE joint SHALL be in the same physical location as before
4. THE HFE joint axis SHALL be "1 0 0" or "-1 0 0" (x-axis for flexion/extension)
5. WHEN HFE rotates, THE leg SHALL move in flexion/extension motion (forward-backward)

### Requirement 4: 重新计算 KFE Joint 的 Origin

**User Story:** 作为机器人工程师，我想重新计算 KFE joint 的 origin，以便在新坐标系下保持正确的几何关系。

#### Acceptance Criteria

1. WHEN Prismatic RPY is removed, THE KFE joint origin xyz SHALL be recalculated relative to HFE joint
2. WHEN Prismatic RPY is removed, THE KFE joint origin rpy SHALL be recalculated if needed
3. WHEN the robot is at zero position, THE KFE joint SHALL be in the same physical location as before
4. THE KFE joint axis SHALL be "1 0 0" or "-1 0 0" (x-axis for knee flexion)
5. WHEN KFE rotates, THE shin SHALL fold correctly

### Requirement 5: 验证正交关节配置

**User Story:** 作为机器人工程师，我想验证 HAA 关节垂直于 HFE/KFE 平面，以便确认 CHAMP 框架兼容性。

#### Acceptance Criteria

1. WHEN HAA joint rotates, THE rotation axis SHALL be perpendicular to HFE rotation axis
2. WHEN HAA joint rotates, THE rotation axis SHALL be perpendicular to KFE rotation axis
3. WHEN HFE and KFE rotate, THEY SHALL rotate in the same plane (parallel axes)
4. WHEN measuring joint axes in world frame, THE HAA axis SHALL be orthogonal to HFE/KFE axes
5. THE dot product of HAA axis and HFE axis SHALL be approximately 0 (orthogonal)

### Requirement 6: 保持视觉和物理几何不变

**User Story:** 作为机器人工程师，我想在修改坐标系后保持机器人的视觉和物理几何不变，以便机器人外观和运动学保持一致。

#### Acceptance Criteria

1. WHEN the robot is at zero position, THE visual appearance SHALL match the original design
2. WHEN joints are at zero position, THE link positions in world frame SHALL match original positions
3. WHEN the robot is visualized in RViz, THE mesh orientations SHALL be correct
4. THE link inertial properties SHALL remain unchanged
5. THE collision geometries SHALL remain in correct positions

### Requirement 7: 更新所有四条腿

**User Story:** 作为机器人工程师，我想对所有四条腿应用相同的坐标系修复，以便保持机器人对称性。

#### Acceptance Criteria

1. WHEN the fix is applied, ALL four legs (lf, rf, lh, rh) SHALL have Prismatic rpy="0 0 0"
2. WHEN the fix is applied, ALL four legs SHALL have recalculated joint origins
3. WHEN the fix is applied, ALL four legs SHALL maintain their unique geometric parameters
4. THE front legs (lf, rf) SHALL use the same coordinate transformation
5. THE rear legs (lh, rh) SHALL use the same coordinate transformation (may differ from front)

### Requirement 8: 在 RViz 中验证

**User Story:** 作为机器人工程师，我想在 RViz 中验证修复后的坐标系，以便确认关节运动正确。

#### Acceptance Criteria

1. WHEN the robot is loaded in RViz, THE visual appearance SHALL be correct at zero position
2. WHEN HAA joint is moved, THE leg SHALL move in abduction/adduction (left-right)
3. WHEN HFE joint is moved, THE leg SHALL move in flexion/extension (forward-backward)
4. WHEN KFE joint is moved, THE shin SHALL fold correctly
5. WHEN all joints are moved, THE motions SHALL be independent and orthogonal

### Requirement 9: 保持 ROS 2 Control 配置

**User Story:** 作为机器人工程师，我想保持现有的 ROS 2 Control 配置，以便控制器无需修改。

#### Acceptance Criteria

1. WHEN the fix is applied, THE joint names SHALL remain unchanged (j1, j11, j111, etc.)
2. WHEN the fix is applied, THE ROS 2 Control configuration SHALL remain valid
3. WHEN the fix is applied, THE joint interfaces SHALL remain unchanged
4. THE joint limits SHALL remain unchanged
5. THE joint effort and velocity limits SHALL remain unchanged

### Requirement 10: 向后兼容性

**User Story:** 作为机器人工程师，我想确保修复后的 URDF 与现有代码兼容，以便最小化破坏性变更。

#### Acceptance Criteria

1. WHEN the fix is applied, THE joint names SHALL remain unchanged
2. WHEN the fix is applied, THE link names SHALL remain unchanged (except CHAMP naming)
3. WHEN the fix is applied, THE existing control scripts SHALL continue to work
4. WHEN the fix is applied, THE joint state messages SHALL have the same format
5. THE fix SHALL NOT require changes to existing kinematics code (except coordinate transforms)
