# Requirements Document

## Introduction

This document defines the requirements for fixing incorrect inertia positions in specific leg links of the Dog2 quadruped robot. The issue affects leg 3 (thigh and shin) and leg 4 (shin only), where the inertia origin positions do not match the actual center of mass of the physical components.

**Background**: The Dog2 robot uses a xacro macro to define all four legs with identical inertia parameters. However, due to manufacturing variations or design differences, legs 3 and 4 have different actual center of mass positions that require individual corrections.

## Glossary

- **Inertia_Origin**: The position (xyz) and orientation (rpy) of the center of mass relative to the link's coordinate frame
- **Thigh**: The upper leg segment (l311 for leg 3, l411 for leg 4)
- **Shin**: The lower leg segment (l3111 for leg 3, l4111 for leg 4)
- **Xacro_Macro**: A parameterized template in xacro that generates repeated URDF structures
- **Link**: A rigid body component in the URDF robot model
- **Center_of_Mass**: The point where the mass of an object is concentrated for physics calculations

## Requirements

### Requirement 1: Identify Correct Inertia Positions

**User Story:** As a robotics engineer, I want to determine the correct inertia origin positions for leg 3 and leg 4 links, so that the simulation accurately represents the physical robot's mass distribution.

#### Acceptance Criteria

1. WHEN analyzing the physical robot THEN THE System SHALL provide the actual center of mass coordinates for l311 (leg 3 thigh)
2. WHEN analyzing the physical robot THEN THE System SHALL provide the actual center of mass coordinates for l3111 (leg 3 shin)
3. WHEN analyzing the physical robot THEN THE System SHALL provide the actual center of mass coordinates for l4111 (leg 4 shin)
4. THE Documentation SHALL explain the method used to determine the correct inertia positions (CAD model, physical measurement, or estimation)
5. THE System SHALL compare current inertia positions with the corrected positions to quantify the error

### Requirement 2: Modify Xacro Macro to Support Per-Leg Inertia

**User Story:** As a URDF developer, I want to modify the leg macro to accept per-link inertia parameters, so that each leg can have individualized inertia configurations while maintaining code reusability.

#### Acceptance Criteria

1. WHEN the leg macro is invoked THEN THE Macro SHALL accept optional inertia override parameters for thigh and shin links
2. WHEN no override parameters are provided THEN THE Macro SHALL use default inertia values
3. WHEN override parameters are provided THEN THE Macro SHALL use the specified inertia values for that specific leg
4. THE Macro SHALL maintain backward compatibility with existing leg instantiations
5. THE Macro SHALL support overriding both inertia origin (xyz, rpy) and inertia tensor (ixx, ixy, ixz, iyy, iyz, izz)

### Requirement 3: Apply Corrected Inertia to Leg 3

**User Story:** As a simulation engineer, I want leg 3's thigh and shin to use corrected inertia parameters, so that the MPC and WBC controllers receive accurate dynamics information.

#### Acceptance Criteria

1. WHEN leg 3 is instantiated THEN THE l311_link SHALL use the corrected inertia origin position
2. WHEN leg 3 is instantiated THEN THE l3111_link SHALL use the corrected inertia origin position
3. WHEN the URDF is parsed THEN THE l311_inertia SHALL match the specified corrected values
4. WHEN the URDF is parsed THEN THE l3111_inertia SHALL match the specified corrected values
5. THE System SHALL preserve all other leg 3 parameters (mass, inertia tensor, visual, collision)

### Requirement 4: Apply Corrected Inertia to Leg 4

**User Story:** As a simulation engineer, I want leg 4's shin to use corrected inertia parameters, so that the robot's balance and dynamics are accurately simulated.

#### Acceptance Criteria

1. WHEN leg 4 is instantiated THEN THE l4111_link SHALL use the corrected inertia origin position
2. WHEN the URDF is parsed THEN THE l4111_inertia SHALL match the specified corrected values
3. THE System SHALL preserve leg 4's thigh (l411) inertia as default (no correction needed)
4. THE System SHALL preserve all other leg 4 parameters (mass, inertia tensor, visual, collision)

### Requirement 5: Validate Corrected Inertia

**User Story:** As a quality assurance engineer, I want to verify that the corrected inertia parameters are physically valid, so that the simulation remains stable and accurate.

#### Acceptance Criteria

1. WHEN validating inertia parameters THEN THE System SHALL verify that the inertia tensor is positive definite
2. WHEN validating inertia parameters THEN THE System SHALL verify that the inertia origin is within reasonable bounds of the link geometry
3. WHEN running Gazebo simulation THEN THE Robot SHALL remain stable without numerical explosions
4. WHEN comparing with legs 1 and 2 THEN THE Corrected_Inertia SHALL have similar magnitude (within 50% difference)
5. THE System SHALL provide a validation script to check inertia parameter correctness

### Requirement 6: Document Inertia Corrections

**User Story:** As a developer, I want clear documentation of the inertia corrections, so that I understand why specific legs have different parameters and can maintain the URDF in the future.

#### Acceptance Criteria

1. WHEN viewing the xacro file THEN THE File SHALL contain comments explaining why legs 3 and 4 have custom inertia
2. WHEN viewing the xacro file THEN THE Comments SHALL document the source of the corrected inertia values
3. WHEN viewing the xacro file THEN THE Comments SHALL explain which links are affected (l311, l3111, l4111)
4. THE Documentation SHALL include before/after comparison of inertia positions
5. THE Documentation SHALL explain the impact on simulation accuracy

### Requirement 7: Preserve Legs 1 and 2 Inertia

**User Story:** As a system integrator, I want legs 1 and 2 to maintain their current inertia parameters, so that only the problematic legs are modified.

#### Acceptance Criteria

1. WHEN legs 1 and 2 are instantiated THEN THE System SHALL use default macro inertia parameters
2. WHEN comparing before and after URDF THEN THE l111_and_l211_inertia SHALL remain unchanged
3. WHEN comparing before and after URDF THEN THE l1111_and_l2111_inertia SHALL remain unchanged
4. THE System SHALL not modify any leg 1 or leg 2 link parameters
5. THE Validation SHALL confirm legs 1 and 2 are unaffected by the changes

### Requirement 8: Test Corrected URDF in Simulation

**User Story:** As a robotics engineer, I want to test the corrected URDF in Gazebo simulation, so that I can verify the corrections improve simulation accuracy.

#### Acceptance Criteria

1. WHEN loading the corrected URDF in Gazebo THEN THE Robot SHALL load without errors
2. WHEN running MPC controller THEN THE Controller SHALL compute valid control commands
3. WHEN running WBC controller THEN THE Controller SHALL compute valid joint torques
4. WHEN the robot stands THEN THE Robot SHALL maintain stable balance
5. WHEN the robot walks THEN THE Gait SHALL be smooth without unexpected oscillations
