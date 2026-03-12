# Requirements Document

## Introduction

This document specifies the requirements for converting the Dog2 robot's URDF from hardcoded continuous joints to a parameterized Xacro-based system with realistic joint limits. The current URDF uses `continuous` joint types for hip and knee joints, which allows 360° unlimited rotation - physically impossible for real robots and problematic for MPC/WBC solvers. This refactoring will introduce Xacro parameters to manage joint limits centrally, ensuring consistency across all four legs and enabling easy tuning for obstacle-crossing experiments.

## Glossary

- **URDF**: Unified Robot Description Format - XML format for describing robot kinematics and dynamics
- **Xacro**: XML Macros - a macro language for URDF that enables parameterization and code reuse
- **Continuous Joint**: A joint type that allows unlimited rotation (360° and beyond)
- **Revolute Joint**: A joint type with defined angular limits (lower and upper bounds)
- **Hip Joint**: The proximal leg joint connecting the body to the thigh (J11, J21, J31, J41)
- **Knee Joint**: The distal leg joint connecting the thigh to the shin (J111, J211, J311, J411)
- **MPC**: Model Predictive Control - the high-level controller that plans trajectories
- **WBC**: Whole Body Control - the low-level controller that computes joint torques
- **Elbow Configuration**: Knee bent backward (negative angle, shin behind thigh)
- **Knee Configuration**: Knee bent forward (positive angle, shin in front of thigh)
- **Morphing**: The reconfiguration process where legs transition between elbow and knee configurations
- **Dog2_System**: The complete robot system including URDF, controllers, and simulation

## Requirements

### Requirement 1: Xacro Parameter Definition

**User Story:** As a robotics engineer, I want joint limits defined as Xacro parameters at the top of the file, so that I can adjust all joint limits from a single location without editing multiple joint definitions.

#### Acceptance Criteria

1. THE Dog2_System SHALL define hip joint limits as Xacro properties (hip_lower_limit, hip_upper_limit)
2. THE Dog2_System SHALL define knee joint limits as Xacro properties (knee_lower_limit, knee_upper_limit)
3. THE Dog2_System SHALL define joint effort limits as Xacro properties (hip_effort, knee_effort)
4. THE Dog2_System SHALL define joint velocity limits as Xacro properties (hip_velocity, knee_velocity)
5. THE Dog2_System SHALL place all parameter definitions in a dedicated properties section at the beginning of the Xacro file

### Requirement 2: Hip Joint Configuration

**User Story:** As a motion planner, I want hip joints to support ±150° range of motion, so that the robot can perform leg lifting (>0.25m), forward swing (+90°), backward swing (-90°), and extreme retraction (±150°) required for obstacle crossing.

#### Acceptance Criteria

1. WHEN a hip joint is defined, THE Dog2_System SHALL set the joint type to "revolute"
2. WHEN a hip joint is defined, THE Dog2_System SHALL set the lower limit to -2.618 radians (-150°)
3. WHEN a hip joint is defined, THE Dog2_System SHALL set the upper limit to +2.618 radians (+150°)
4. THE Dog2_System SHALL apply these limits to all four hip joints (j11, j21, j31, j41)
5. WHEN hip limits are referenced, THE Dog2_System SHALL use Xacro property substitution (${hip_lower_limit}, ${hip_upper_limit})

### Requirement 3: Knee Joint Configuration

**User Story:** As a morphing controller, I want knee joints to support ±160° range with bidirectional folding, so that the robot can transition between elbow configuration (shin behind thigh) and knee configuration (shin in front of thigh) through the 0° singularity point.

#### Acceptance Criteria

1. WHEN a knee joint is defined, THE Dog2_System SHALL set the joint type to "revolute"
2. WHEN a knee joint is defined, THE Dog2_System SHALL set the lower limit to -2.8 radians (-160°)
3. WHEN a knee joint is defined, THE Dog2_System SHALL set the upper limit to +2.8 radians (+160°)
4. THE Dog2_System SHALL apply these limits to all four knee joints (j111, j211, j311, j411)
5. WHEN knee limits are referenced, THE Dog2_System SHALL use Xacro property substitution (${knee_lower_limit}, ${knee_upper_limit})
6. THE Dog2_System SHALL ensure the range includes 0° (straight leg) as a valid configuration

### Requirement 4: Xacro Macro for Leg Definition

**User Story:** As a developer, I want a reusable Xacro macro for leg definitions, so that all four legs are guaranteed to have identical joint configurations and I can avoid copy-paste errors.

#### Acceptance Criteria

1. THE Dog2_System SHALL define a Xacro macro named "leg" that accepts parameters (leg_name, parent_link, origin_xyz, origin_rpy)
2. WHEN the leg macro is invoked, THE Dog2_System SHALL generate all links and joints for one complete leg
3. WHEN the leg macro defines joints, THE Dog2_System SHALL reference the global joint limit parameters
4. THE Dog2_System SHALL invoke the leg macro exactly four times (once per leg)
5. WHEN generating joint names, THE Dog2_System SHALL use the leg_name parameter to ensure unique naming (e.g., j11, j21, j31, j41)

### Requirement 5: Backward Compatibility

**User Story:** As a system integrator, I want the Xacro file to generate a URDF compatible with existing launch files and controllers, so that I don't need to modify other parts of the system.

#### Acceptance Criteria

1. WHEN the Xacro file is processed, THE Dog2_System SHALL generate a URDF with the same link names as the original
2. WHEN the Xacro file is processed, THE Dog2_System SHALL generate a URDF with the same joint names as the original
3. WHEN the Xacro file is processed, THE Dog2_System SHALL preserve all transmission definitions
4. WHEN the Xacro file is processed, THE Dog2_System SHALL preserve all Gazebo plugin configurations
5. THE Dog2_System SHALL maintain the same coordinate frames and transformations as the original URDF

### Requirement 6: Documentation and Comments

**User Story:** As a future maintainer, I want clear documentation in the Xacro file explaining the joint limit choices, so that I understand the physical reasoning and can make informed adjustments.

#### Acceptance Criteria

1. THE Dog2_System SHALL include comments explaining the hip joint range rationale (0°=vertical, +90°=forward, -90°=backward, ±150°=extreme)
2. THE Dog2_System SHALL include comments explaining the knee joint range rationale (0°=straight, -160°=elbow, +160°=knee)
3. THE Dog2_System SHALL include comments documenting the relationship between joint limits and obstacle-crossing phases
4. THE Dog2_System SHALL include comments warning about the 0° singularity in knee joints
5. THE Dog2_System SHALL include a header comment documenting the file purpose and parameter modification instructions

### Requirement 7: Build System Integration

**User Story:** As a developer, I want the build system to automatically convert Xacro to URDF, so that I can work with Xacro source files and have URDF generated on demand.

#### Acceptance Criteria

1. WHEN the package is built, THE Dog2_System SHALL process the Xacro file to generate dog2.urdf
2. WHEN Xacro parameters are modified, THE Dog2_System SHALL regenerate the URDF on the next build
3. THE Dog2_System SHALL report Xacro processing errors clearly during the build process
4. THE Dog2_System SHALL preserve the generated URDF in the urdf/ directory
5. WHEN launch files reference the robot description, THE Dog2_System SHALL use the generated URDF file

### Requirement 8: Validation and Testing

**User Story:** As a quality assurance engineer, I want automated validation that the generated URDF has correct joint limits, so that I can catch configuration errors before runtime.

#### Acceptance Criteria

1. WHEN the URDF is generated, THE Dog2_System SHALL validate that all hip joints have type="revolute"
2. WHEN the URDF is generated, THE Dog2_System SHALL validate that all knee joints have type="revolute"
3. WHEN the URDF is generated, THE Dog2_System SHALL validate that no joints have type="continuous"
4. WHEN the URDF is generated, THE Dog2_System SHALL validate that all four legs have identical joint limit values
5. THE Dog2_System SHALL provide a validation script that checks joint limit consistency across all legs
