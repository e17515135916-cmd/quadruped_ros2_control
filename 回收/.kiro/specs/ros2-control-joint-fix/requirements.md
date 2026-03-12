# Requirements Document

## Introduction

This specification addresses the critical issue where the URDF is missing the fourth joint (ankle/foot joint) for each leg of the DOG2 quadruped robot. The ros2_control configuration correctly expects 4 joints per leg (j1, j11, j111, j1111), but the URDF only defines 3 joints. This prevents Gazebo from launching properly because the control system cannot find the missing joints.

## Glossary

- **URDF**: Unified Robot Description Format - XML format describing robot kinematics and dynamics
- **Prismatic_Joint**: Linear sliding joint (导轨关节) that moves along a single axis
- **Revolute_Joint**: Rotational joint that rotates around a single axis
- **HAA**: Hip Abduction/Adduction - 髋关节外展/内收 - controls lateral leg movement
- **HFE**: Hip Flexion/Extension - 髋关节前屈/后伸 - controls forward/backward leg swing
- **KFE**: Knee Flexion/Extension - 膝关节 - controls shin bending relative to thigh
- **ros2_control**: ROS 2 framework for robot control interfaces
- **Joint_State_Broadcaster**: Controller that publishes joint states to ROS topics
- **Effort_Controller**: Controller that commands joint torques/forces
- **Gazebo**: Physics simulation environment for robotics
- **Control_Configuration**: YAML file defining which joints are controlled and how
- **Leg_Macro**: Xacro macro template that generates leg structure for each of the 4 legs

## Requirements

### Requirement 1: Accurate Joint Inventory and Naming

**User Story:** As a robotics engineer, I want to verify the complete joint structure and correct naming of the DOG2 robot, so that I can identify missing joints and incorrect labels in the URDF.

#### Acceptance Criteria

1. WHEN analyzing the URDF file, THE System SHALL identify all currently defined joints for each leg
2. WHEN comparing with the control configuration, THE System SHALL identify that 4 joints are expected but only 3 are defined
3. THE System SHALL document the correct naming and function for all joints:
   - j1: Prismatic rail (直线导轨)
   - j11: HAA - Hip Abduction/Adduction (髋关节外展/内收)
   - j111: HFE - Hip Flexion/Extension (髋关节前屈/后伸)
   - j1111: KFE - Knee Flexion/Extension (膝关节) - MISSING
4. THE System SHALL identify that current j111 is incorrectly labeled as "Knee joint" when it should be "Hip flexion/extension"
5. THE System SHALL verify that link l${leg_num}1111 (foot/shin link) and joint j${leg_num}1111 (knee) are missing from the leg macro

### Requirement 2: Control Configuration Validation

**User Story:** As a control systems engineer, I want to validate that the ros2_controllers.yaml matches the URDF joint definitions, so that Gazebo can load the robot successfully.

#### Acceptance Criteria

1. WHEN comparing URDF and YAML configurations, THE System SHALL identify any joint names in YAML that do not exist in URDF
2. WHEN validating joint types, THE System SHALL confirm that prismatic joints are properly configured with position/effort interfaces
3. THE System SHALL verify that all joints in ros2_control block match joints in the controllers YAML file
4. IF non-existent joints are found in configuration, THEN THE System SHALL report them with their expected names

### Requirement 3: Add Missing Fourth Joint and Correct Labels

**User Story:** As a developer, I want to add the missing fourth joint (KFE knee) and fourth link (foot) to each leg in the URDF, and correct the joint labels, so that the robot structure matches the control configuration and physical reality.

#### Acceptance Criteria

1. WHEN updating the leg macro, THE System SHALL add a fourth link l${leg_num}1111 (foot/shin link) with appropriate inertial properties from the original dog2.urdf
2. WHEN adding the fourth joint, THE System SHALL create j${leg_num}1111 as a revolute joint (KFE - knee) connecting l${leg_num}111 (thigh) to l${leg_num}1111 (foot/shin)
3. THE System SHALL correct the comment for j${leg_num}11 from "Knee joint" to "Hip flexion/extension (HFE)"
4. THE System SHALL update the comment for j${leg_num}1111 to "Knee joint (KFE)"
5. THE System SHALL define appropriate joint limits, effort, and velocity for the knee joint based on the original dog2.urdf
6. THE System SHALL add visual and collision geometry for the foot link using the existing l${leg_num}1111.STL mesh files
7. THE System SHALL add Gazebo friction configuration for the foot link to prevent "ice skating"

### Requirement 4: Verify URDF ros2_control Block

**User Story:** As a robotics engineer, I want to ensure the URDF ros2_control block matches the controller configuration, so that the hardware interfaces are properly defined.

#### Acceptance Criteria

1. WHEN examining the URDF ros2_control block, THE System SHALL verify it contains entries for all joints in the controllers YAML
2. WHEN checking interface definitions, THE System SHALL confirm each joint has command_interface and state_interface entries
3. THE System SHALL verify that prismatic joints (j1, j2, j3, j4) have appropriate interfaces for linear motion
4. IF the ros2_control block contains non-existent joints, THEN THE System SHALL remove them

### Requirement 5: Gazebo Launch Validation

**User Story:** As a developer, I want to verify that Gazebo can successfully launch with the complete 4-joint leg structure, so that I can proceed with robot simulation and testing.

#### Acceptance Criteria

1. WHEN launching Gazebo with the updated URDF, THE System SHALL load without joint-related errors
2. WHEN the robot spawns in Gazebo, THE System SHALL display all 4 legs with correct 4-joint structure
3. THE Joint_State_Broadcaster SHALL publish states for all 16 joints (4 legs × 4 joints)
4. THE Effort_Controller SHALL accept commands for all 16 joints without errors

### Requirement 6: Documentation and Verification Script

**User Story:** As a team member, I want automated verification of URDF-controller consistency, so that future changes don't reintroduce this mismatch.

#### Acceptance Criteria

1. THE System SHALL provide a validation script that compares URDF joints with controller configuration
2. WHEN the validation script runs, THE System SHALL report any mismatches between URDF and YAML
3. THE System SHALL document the correct joint structure in a README file
4. THE System SHALL include examples of correct joint naming for each leg type
