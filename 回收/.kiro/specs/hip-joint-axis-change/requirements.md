# Requirements Document

## Introduction

This document specifies the requirements for changing the hip joint rotation axes (j11, j21, j31, j41) from z-axis rotation to x-axis rotation on the Dog2 quadruped robot. This modification will change the fundamental kinematics of the robot's hip joints.

## Glossary

- **Hip_Joint**: The revolute joints j11, j21, j31, j41 that connect the hip links (l11, l21, l31, l41) to the prismatic links (l1, l2, l3, l4)
- **URDF**: Unified Robot Description Format, the XML file format used to describe the robot's physical configuration
- **Rotation_Axis**: The axis about which a revolute joint rotates, specified in the joint's local coordinate frame
- **IK_Solver**: Inverse Kinematics solver that calculates joint angles from desired foot positions
- **FK_Solver**: Forward Kinematics solver that calculates foot positions from joint angles

## Requirements

### Requirement 1: Update Hip Joint Axis Definitions

**User Story:** As a robotics engineer, I want to change the hip joint rotation axes from z-axis to x-axis, so that the robot's hip joints rotate in a different plane.

#### Acceptance Criteria

1. WHEN the URDF is parsed, THE Hip_Joint j11 SHALL have axis definition "1 0 0"
2. WHEN the URDF is parsed, THE Hip_Joint j21 SHALL have axis definition "1 0 0"
3. WHEN the URDF is parsed, THE Hip_Joint j31 SHALL have axis definition "1 0 0"
4. WHEN the URDF is parsed, THE Hip_Joint j41 SHALL have axis definition "1 0 0"
5. WHEN the URDF is loaded in RViz or Gazebo, THE Hip_Joint SHALL rotate about the x-axis when commanded

### Requirement 2: Update Joint Origin Transformations

**User Story:** As a robotics engineer, I want the joint origin transformations to be updated consistently with the new rotation axis, so that the kinematic chain remains correct.

#### Acceptance Criteria

1. WHEN the rotation axis is changed, THE Hip_Joint origin RPY values SHALL be updated to maintain correct link orientations
2. WHEN the robot is visualized, THE Hip_Joint links SHALL be positioned correctly relative to their parent links
3. WHEN joint angles are zero, THE Hip_Joint child links SHALL be in their expected neutral positions

### Requirement 3: Maintain Joint Limits

**User Story:** As a robotics engineer, I want the joint limits to remain appropriate for the new rotation axis, so that the robot operates safely.

#### Acceptance Criteria

1. WHEN the rotation axis is changed, THE Hip_Joint SHALL maintain effort limits of 50 Nm
2. WHEN the rotation axis is changed, THE Hip_Joint SHALL maintain velocity limits of 20 rad/s
3. WHEN the rotation axis is changed, THE Hip_Joint position limits SHALL be reviewed and updated if necessary for the new rotation plane

### Requirement 4: Update Kinematics Solvers

**User Story:** As a robotics engineer, I want the IK and FK solvers to be updated for the new joint configuration, so that motion planning continues to work correctly.

#### Acceptance Criteria

1. WHEN the IK_Solver calculates joint angles, THE Hip_Joint angles SHALL correspond to x-axis rotations
2. WHEN the FK_Solver calculates foot positions, THE Hip_Joint angles SHALL be interpreted as x-axis rotations
3. WHEN a desired foot position is given, THE IK_Solver SHALL produce valid joint angles that achieve that position with the new joint configuration

### Requirement 5: Update Visual Mesh Orientation

**User Story:** As a robotics engineer, I want the visual mesh files to be rotated to match the new joint axis, so that the robot appears correctly oriented in visualization tools.

#### Acceptance Criteria

1. WHEN the joint axis is changed from z to x, THE Hip_Joint child link visual meshes SHALL be rotated to maintain correct visual appearance
2. WHEN the robot is viewed in RViz, THE Hip_Joint links SHALL appear in their correct orientations
3. WHEN the robot is viewed in Gazebo, THE Hip_Joint links SHALL appear in their correct orientations
4. WHEN joint angles are zero, THE Hip_Joint visual meshes SHALL show the links in their neutral positions
5. THE Hip_Joint visual mesh files (l11.STL, l21.STL, l31.STL, l41.STL) SHALL be rotated using Blender or the visual origin RPY SHALL be adjusted in URDF
6. WHERE mesh files are rotated, THE System SHALL create backup copies of original mesh files before modification

### Requirement 6: Update Collision Mesh Orientation

**User Story:** As a robotics engineer, I want the collision geometry to be updated consistently with visual meshes, so that collision detection continues to work properly.

#### Acceptance Criteria

1. WHEN the joint axis is changed, THE Hip_Joint collision meshes SHALL be rotated to match visual mesh orientations
2. WHEN the robot moves in simulation, THE Hip_Joint collision detection SHALL function correctly
3. WHEN links move through their range of motion, THE Hip_Joint SHALL not produce false collision detections
4. THE Hip_Joint collision mesh files SHALL be rotated or the collision origin SHALL be adjusted to match visual changes
5. WHERE collision meshes are modified, THE System SHALL maintain the same collision detection accuracy as before

### Requirement 7: Validate in Simulation

**User Story:** As a robotics engineer, I want to validate the changes in Gazebo simulation, so that I can verify the robot behaves correctly before physical implementation.

#### Acceptance Criteria

1. WHEN the robot is loaded in Gazebo, THE Hip_Joint SHALL be controllable via ROS 2 topics
2. WHEN joint commands are sent, THE Hip_Joint SHALL rotate about the x-axis as expected
3. WHEN the robot stands, THE Hip_Joint configuration SHALL support stable standing posture
4. WHEN the robot walks, THE Hip_Joint configuration SHALL support locomotion
5. WHEN viewed in RViz and Gazebo, THE Hip_Joint visual appearance SHALL match the physical joint motion
