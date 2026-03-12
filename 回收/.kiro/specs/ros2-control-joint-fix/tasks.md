# Implementation Plan: ros2-control-joint-fix

## Overview

This implementation plan adds the missing fourth joint (KFE knee joint) and fourth link (foot/shin) to each leg in the DOG2 robot's URDF xacro file. The plan follows an incremental approach: first adding the missing components to the leg macro, then verifying the generated URDF, and finally testing in Gazebo.

## Tasks

- [x] 1. Prepare inertial properties for the fourth link
  - Extract inertial properties from original dog2.urdf for all 4 legs
  - Create xacro properties for foot inertia (legs 1-4)
  - Verify X-coordinate mirroring for rear legs (legs 3, 4)
  - _Requirements: 3.1, 3.7_

- [x] 2. Add fourth link to leg macro
  - [x] 2.1 Add l${leg_num}1111 link definition after l${leg_num}111
    - Include inertial properties using parameterized foot_inertia_xyz
    - Add visual geometry referencing l${leg_num}1111.STL mesh
    - Add collision geometry referencing l${leg_num}1111.STL mesh
    - _Requirements: 3.1, 3.6_

  - [x] 2.2 Write property test for link structure completeness
    - **Property 2: Complete Link Structure**
    - **Validates: Requirements 1.5, 3.1**

- [ ] 3. Add fourth joint to leg macro
  - [ ] 3.1 Add j${leg_num}1111 joint definition after j${leg_num}111 joint
    - Set type to "revolute"
    - Set parent to l${leg_num}111 (thigh)
    - Set child to l${leg_num}1111 (foot/shin)
    - Set origin to xyz="0 -0.15201 0.12997" rpy="0 0 0"
    - Set axis to xyz="-1 0 0"
    - Set limits: effort="50" lower="-2.8" upper="0.0" velocity="20"
    - Add comment: "Knee joint (KFE)"
    - _Requirements: 3.2, 3.5_

  - [ ]* 3.2 Write property test for joint structure completeness
    - **Property 1: Complete Joint Structure**
    - **Validates: Requirements 1.2, 1.3**

  - [ ]* 3.3 Write property test for joint-link connectivity
    - **Property 3: Joint-Link Connectivity**
    - **Validates: Requirements 3.2**

- [ ] 4. Add Gazebo friction configuration
  - [ ] 4.1 Add Gazebo reference block for l${leg_num}1111
    - Set mu1="1.0" and mu2="1.0" (friction coefficients)
    - Set kp="1000000.0" (contact stiffness)
    - Set kd="100.0" (contact damping)
    - Set minDepth="0.001" and maxVel="0.1"
    - Set material="Gazebo/Grey"
    - _Requirements: 3.7_

  - [ ]* 4.2 Write property test for Gazebo friction configuration
    - **Property 8: Gazebo Friction Configuration**
    - **Validates: Requirements 3.7**

- [ ] 5. Update leg macro instantiations
  - [ ] 5.1 Add foot_inertia_xyz parameter to all 4 leg instantiations
    - Leg 1: Use leg12_foot_inertia_xyz (positive X)
    - Leg 2: Use leg12_foot_inertia_xyz (positive X)
    - Leg 3: Use leg3_foot_inertia_xyz (negative X)
    - Leg 4: Use leg4_foot_inertia_xyz (negative X)
    - _Requirements: 3.1_

  - [ ]* 5.2 Write property test for inertial mirroring
    - **Property 7: Inertial Property Mirroring**
    - **Validates: Requirements 3.1**

- [ ] 6. Correct joint comments and labels
  - [ ] 6.1 Update comment for j${leg_num}11 joint
    - Change from "Knee joint (j${leg_num}11)" to "Hip flexion/extension (HFE)"
    - _Requirements: 3.3_

  - [ ] 6.2 Verify all joint comments are accurate
    - j${leg_num}: "Prismatic joint" or "Rail joint"
    - j${leg_num}1: "Hip joint" or "Hip abduction/adduction (HAA)"
    - j${leg_num}11: "Hip flexion/extension (HFE)"
    - j${leg_num}111: "Knee joint (KFE)"
    - _Requirements: 1.3, 3.4_

- [ ] 7. Checkpoint - Verify xacro file syntax
  - Run xacro processing to check for syntax errors
  - Ensure all macro parameters are correctly defined
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Generate and validate URDF
  - [ ] 8.1 Generate URDF from updated xacro file
    - Run: `xacro src/dog2_description/urdf/dog2.urdf.xacro > generated_urdf.xml`
    - _Requirements: 5.1_

  - [ ]* 8.2 Write unit test to verify joint count
    - Parse generated URDF
    - Count total joints (should be 16: 4 legs × 4 joints)
    - _Requirements: 1.2_

  - [ ]* 8.3 Write unit test to verify link count
    - Parse generated URDF
    - Count total links (should be 21: 1 base + 4 legs × 5 links)
    - _Requirements: 1.5_

  - [ ]* 8.4 Write property test for mesh file existence
    - **Property 6: Mesh File Existence**
    - **Validates: Requirements 3.6**

- [ ] 9. Verify ros2_control configuration
  - [ ]* 9.1 Write property test for ros2_control consistency
    - **Property 4: ros2_control Consistency**
    - **Validates: Requirements 4.1, 4.2**

  - [ ]* 9.2 Write property test for controller configuration consistency
    - **Property 5: Controller Configuration Consistency**
    - **Validates: Requirements 2.1, 2.3**

  - [ ]* 9.3 Write property test for prismatic joint interfaces
    - **Property 2 (from design): Prismatic Joint Interfaces**
    - **Validates: Requirements 2.2, 4.3**

- [ ] 10. Create validation script
  - [ ] 10.1 Create Python script to validate URDF structure
    - Parse URDF XML
    - Validate joint count (16 expected)
    - Validate link count (21 expected)
    - Validate joint-link connectivity
    - Compare URDF joints with ros2_control block
    - Compare URDF joints with ros2_controllers.yaml
    - Report any mismatches or missing elements
    - _Requirements: 6.1, 6.2_

  - [ ]* 10.2 Write unit tests for validation script
    - Test with valid URDF (should pass)
    - Test with missing joints (should report errors)
    - Test with mismatched configurations (should report mismatches)
    - _Requirements: 6.2_

- [ ] 11. Checkpoint - Run validation script
  - Execute validation script on generated URDF
  - Verify all checks pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Integration testing with Gazebo
  - [ ]* 12.1 Test Gazebo launch
    - Launch Gazebo with updated URDF
    - Verify robot loads without joint-related errors
    - Verify all 4 legs are visible with correct structure
    - _Requirements: 5.1, 5.2_

  - [ ]* 12.2 Test joint state broadcaster
    - Verify joint_state_broadcaster publishes states for all 16 joints
    - Check that all joint names are correct
    - _Requirements: 5.3_

  - [ ]* 12.3 Test effort controller
    - Send effort commands to all 16 joints
    - Verify commands are accepted without errors
    - Verify joints respond to commands
    - _Requirements: 5.4_

- [ ] 13. Final checkpoint - Complete system verification
  - Ensure all tests pass
  - Verify Gazebo simulation runs smoothly
  - Verify no "ice skating" behavior (friction working correctly)
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The validation script provides automated consistency checking
- Integration tests verify the complete system works in Gazebo
