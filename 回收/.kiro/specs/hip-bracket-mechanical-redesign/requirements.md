# Requirements Document

## Introduction

This document specifies the requirements for redesigning the white hip bracket (l11, l21, l31, l41) mechanical structure to change the servo mounting orientation from vertical (Z-axis rotation) to horizontal (X-axis rotation). This is a physical mechanical redesign that requires modifying the 3D mesh files to change the robot from "spider-style" (legs extending outward) to "dog-style" (legs extending downward).

## Glossary

- **Hip_Bracket**: The white support structure links (l11, l21, l31, l41) that mount the servo motors
- **Servo_Mounting_Interface**: The physical mounting surface and screw holes where the servo motor attaches to the bracket
- **Vertical_Mounting**: Current configuration where servo is mounted on a vertical surface, causing Z-axis rotation
- **Horizontal_Mounting**: Target configuration where servo is mounted on a horizontal platform, causing X-axis rotation
- **Cantilever_Platform**: A horizontal extension from the bracket that provides the mounting surface for the servo
- **Servo_Flange**: The mounting flange on the servo motor with screw holes
- **Spider_Style**: Current leg configuration where legs extend outward from body (Z-axis hip rotation)
- **Dog_Style**: Target leg configuration where legs extend downward from body (X-axis hip rotation)

## Requirements

### Requirement 1: Redesign Servo Mounting Interface

**User Story:** As a robotics engineer, I want to redesign the white hip bracket to mount the servo horizontally instead of vertically, so that the hip joint rotates about the X-axis instead of the Z-axis.

#### Acceptance Criteria

1. THE Hip_Bracket SHALL have a horizontal Cantilever_Platform extending from the main body
2. THE Cantilever_Platform SHALL be parallel to the ground plane when the robot is in neutral position
3. THE Cantilever_Platform SHALL have screw holes that align with the Servo_Flange after 90-degree rotation
4. WHEN the servo is mounted on the Cantilever_Platform, THE servo output shaft SHALL be aligned with the X-axis
5. THE Cantilever_Platform SHALL be structurally strong enough to support the servo weight and torque loads

### Requirement 2: Maintain Mechanical Compatibility

**User Story:** As a robotics engineer, I want the redesigned bracket to maintain compatibility with existing components, so that I don't need to redesign the entire leg assembly.

#### Acceptance Criteria

1. THE Hip_Bracket SHALL maintain the same mounting interface to the prismatic link (l1, l2, l3, l4)
2. THE Hip_Bracket SHALL maintain the same output interface to the thigh link (l11, l21, l31, l41)
3. THE Hip_Bracket dimensions SHALL fit within the robot's physical envelope
4. THE Hip_Bracket mass SHALL remain within ±20% of the original mass (0.25 kg)
5. WHERE possible, THE Hip_Bracket SHALL reuse existing fastener sizes and types

### Requirement 3: Update 3D Mesh Files

**User Story:** As a robotics engineer, I want the 3D mesh files to be updated with the new bracket design, so that the robot appears correctly in simulation and can be manufactured.

#### Acceptance Criteria

1. THE System SHALL create new STL mesh files for l11.STL, l21.STL, l31.STL, l41.STL
2. THE System SHALL create backup copies of original mesh files before modification
3. THE new mesh files SHALL be compatible with ROS 2 URDF format
4. THE new mesh files SHALL have correct scale (meters) and origin alignment
5. THE new mesh files SHALL be optimized for simulation (reasonable polygon count)

### Requirement 4: Update Collision Meshes

**User Story:** As a robotics engineer, I want the collision meshes to match the new bracket geometry, so that collision detection works correctly in simulation.

#### Acceptance Criteria

1. THE System SHALL create new collision mesh files for l11_collision.STL, l21_collision.STL, l31_collision.STL, l41_collision.STL
2. THE collision meshes SHALL be simplified versions of the visual meshes
3. THE collision meshes SHALL accurately represent the outer envelope of the bracket
4. WHEN the robot moves, THE collision detection SHALL not produce false positives
5. THE collision meshes SHALL have significantly fewer polygons than visual meshes for performance

### Requirement 5: Adjust Joint Origin Positions

**User Story:** As a robotics engineer, I want the joint origin positions to be updated to match the new bracket geometry, so that the kinematic chain remains correct.

#### Acceptance Criteria

1. WHEN the bracket geometry changes, THE joint origin XYZ positions SHALL be updated in URDF
2. THE joint origin positions SHALL place the rotation axis at the correct physical location
3. WHEN joint angles are zero, THE robot SHALL be in a neutral standing position
4. THE kinematic chain SHALL maintain correct link lengths and offsets
5. THE updated joint origins SHALL not cause link interpenetration

### Requirement 6: Validate Mechanical Design

**User Story:** As a robotics engineer, I want to validate the mechanical design before manufacturing, so that I can ensure it will work correctly.

#### Acceptance Criteria

1. THE Cantilever_Platform SHALL support minimum 5 Nm torque without excessive deflection
2. THE bracket SHALL have no stress concentrations exceeding material yield strength
3. THE bracket SHALL be manufacturable using available 3D printing or CNC methods
4. THE servo mounting SHALL provide adequate clearance for servo body and wiring
5. THE bracket SHALL not interfere with adjacent leg assemblies during full range of motion

### Requirement 7: Update URDF Configuration

**User Story:** As a robotics engineer, I want the URDF to be updated with the new mesh files and joint positions, so that simulation reflects the new design.

#### Acceptance Criteria

1. THE URDF SHALL reference the new mesh files for l11, l21, l31, l41
2. THE URDF SHALL reference the new collision mesh files
3. THE URDF SHALL have updated joint origin XYZ positions
4. THE URDF visual origin RPY SHALL be adjusted if needed for correct orientation
5. THE URDF SHALL parse without errors in ROS 2

### Requirement 8: Validate in Simulation

**User Story:** As a robotics engineer, I want to validate the redesigned bracket in simulation, so that I can verify it works before physical implementation.

#### Acceptance Criteria

1. WHEN the robot is loaded in RViz, THE Hip_Bracket SHALL appear correctly oriented
2. WHEN the robot is loaded in Gazebo, THE Hip_Bracket SHALL appear correctly oriented
3. WHEN hip joints are commanded, THE rotation SHALL be about the X-axis
4. WHEN the robot stands, THE legs SHALL extend downward (dog-style) not outward (spider-style)
5. WHEN the robot walks, THE new bracket configuration SHALL support locomotion

### Requirement 9: Document Design Concept

**User Story:** As a robotics engineer, I want to document the mechanical design concept, so that it can be implemented in the future if needed.

#### Acceptance Criteria

1. THE System SHALL document the key design changes in the bracket geometry
2. THE System SHALL document the cantilever platform dimensions and orientation
3. THE System SHALL document the expected improvements in robot kinematics
4. THE System SHALL provide visual comparisons between spider-style and dog-style configurations
5. THE System SHALL document any limitations or trade-offs of the new design

