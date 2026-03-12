# Requirements Document

## Introduction

本文档定义了将 Dog2 四足机器人的髋关节（j11, j21, j31, j41）从 z 轴旋转改为 x 轴旋转的需求。此修改将改变髋关节的运动学配置，使其绕 x 轴旋转（前后摆动），而不改变视觉模型和其他部分。

## Glossary

- **Hip_Joint**: 髋关节 j11, j21, j31, j41，连接髋部连杆（l11, l21, l31, l41）到滑动连杆（l1, l2, l3, l4）的旋转关节
- **URDF**: Unified Robot Description Format，用于描述机器人物理配置的 XML 文件格式
- **Rotation_Axis**: 旋转轴，指定旋转关节绕哪个轴旋转，在关节的局部坐标系中定义
- **Xacro**: XML Macro，ROS 中用于参数化 URDF 的宏语言

## Requirements

### Requirement 1: 更新髋关节轴定义为 x 轴

**User Story:** 作为机器人工程师，我想将髋关节的旋转轴从 z 轴改为 x 轴，以便机器人的髋关节可以前后摆动。

#### Acceptance Criteria

1. WHEN the URDF is parsed, THE Hip_Joint j11 SHALL have axis definition "1 0 0"
2. WHEN the URDF is parsed, THE Hip_Joint j21 SHALL have axis definition "1 0 0"
3. WHEN the URDF is parsed, THE Hip_Joint j31 SHALL have axis definition "1 0 0"
4. WHEN the URDF is parsed, THE Hip_Joint j41 SHALL have axis definition "1 0 0"
5. WHEN the URDF is loaded in RViz or Gazebo, THE Hip_Joint SHALL rotate about the x-axis when commanded

### Requirement 2: 保持视觉模型不变

**User Story:** 作为机器人工程师，我想在修改关节轴时保持视觉模型不变，以便只改变运动学配置而不影响外观。

#### Acceptance Criteria

1. WHEN the rotation axis is changed, THE Hip_Joint visual meshes SHALL remain unchanged
2. WHEN the rotation axis is changed, THE Hip_Joint visual origin SHALL remain unchanged
3. WHEN the robot is visualized in RViz, THE Hip_Joint links SHALL appear in the same visual orientation as before
4. THE Hip_Joint visual mesh files (l11.STL, l21.STL, l31.STL, l41.STL) SHALL NOT be modified

### Requirement 3: 保持碰撞模型不变

**User Story:** 作为机器人工程师，我想在修改关节轴时保持碰撞模型不变，以便碰撞检测继续正常工作。

#### Acceptance Criteria

1. WHEN the rotation axis is changed, THE Hip_Joint collision geometry SHALL remain unchanged
2. WHEN the rotation axis is changed, THE Hip_Joint collision origin SHALL remain unchanged
3. WHEN the robot moves in simulation, THE Hip_Joint collision detection SHALL function correctly

### Requirement 4: 保持关节限位

**User Story:** 作为机器人工程师，我想保持关节限位不变，以便机器人在新的旋转轴配置下安全运行。

#### Acceptance Criteria

1. WHEN the rotation axis is changed, THE Hip_Joint SHALL maintain effort limits of 50 Nm
2. WHEN the rotation axis is changed, THE Hip_Joint SHALL maintain velocity limits of 20 rad/s
3. WHEN the rotation axis is changed, THE Hip_Joint position limits SHALL remain ±150° (±2.618 rad)

### Requirement 5: 仅修改 Xacro 宏参数

**User Story:** 作为机器人工程师，我想通过修改 Xacro 宏参数来改变关节轴，以便实现最小化的代码修改。

#### Acceptance Criteria

1. WHEN implementing the change, THE System SHALL only modify the `hip_axis` parameter in leg macro instantiations
2. WHEN implementing the change, THE System SHALL change `hip_axis` from "0 0 -1" to "1 0 0" for all four legs
3. WHEN implementing the change, THE System SHALL NOT modify any other parameters in the URDF
4. THE System SHALL maintain the existing leg macro structure and all other joint definitions

### Requirement 6: 在 RViz 和 Gazebo 中验证

**User Story:** 作为机器人工程师，我想在 RViz 和 Gazebo 中验证修改，以便确认机器人在新配置下正确运行。

#### Acceptance Criteria

1. WHEN the robot is loaded in RViz, THE Hip_Joint SHALL be controllable via joint_state_publisher
2. WHEN joint commands are sent in RViz, THE Hip_Joint SHALL rotate about the x-axis as expected
3. WHEN the robot is loaded in Gazebo, THE Hip_Joint SHALL be controllable via ROS 2 topics
4. WHEN joint commands are sent in Gazebo, THE Hip_Joint SHALL rotate about the x-axis as expected
5. WHEN viewed in RViz and Gazebo, THE Hip_Joint visual appearance SHALL remain unchanged from before
