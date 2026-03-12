# Implementation Plan: Hip Joint Axis Change

## Overview

This plan implements the change of hip joint rotation axes (j11, j21, j31, j41) from z-axis to x-axis rotation. The implementation follows a careful approach with backups, incremental changes, and thorough testing at each step.

## Tasks

- [x] 1. Create backup system and backup current files
  - Create backup script for URDF and mesh files
  - Execute backup of `dog2.urdf.xacro`
  - Execute backup of hip link mesh files (l11.STL, l21.STL, l31.STL, l41.STL)
  - Execute backup of hip collision meshes
  - Verify all backups are created successfully
  - _Requirements: 5.6_

- [x] 2. Update URDF joint axis definitions
  - [x] 2.1 Modify hip joint axis in leg macro
    - Change `<axis xyz="0 0 -1"/>` to `<axis xyz="1 0 0"/>` in j${leg_num}1 joint definition
    - Update URDF comments to document the change
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 2.2 Write unit test for joint axis verification
    - Parse URDF and extract j11, j21, j31, j41 axis definitions
    - Assert each joint has axis (1, 0, 0)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Update visual mesh orientations in URDF
  - [x] 3.1 Add visual origin RPY to hip links
    - Add `<origin rpy="0 0 1.5708" xyz="0 0 0"/>` to l${leg_num}1 visual elements
    - Apply to all four hip links (l11, l21, l31, l41)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 3.2 Write unit test for visual origin verification
    - Parse URDF and extract visual origins for hip links
    - Assert RPY values are correctly set
    - _Requirements: 5.1_

- [x] 4. Update collision mesh orientations in URDF
  - [x] 4.1 Add collision origin RPY to hip links
    - Add `<origin rpy="0 0 1.5708" xyz="0 0 0"/>` to l${leg_num}1 collision elements
    - Apply to all four hip links
    - Ensure collision RPY matches visual RPY
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 4.2 Write unit test for visual-collision alignment
    - **Property 2: Visual-Collision Alignment**
    - **Validates: Requirements 5.1, 6.1**
    - Parse URDF and extract visual and collision origins
    - Assert RPY values match for each hip link
    - _Requirements: 6.1_

- [x] 5. Checkpoint - Verify URDF changes
  - Build URDF and check for parsing errors
  - Run unit tests for joint axis and origins
  - Ensure all tests pass, ask the user if questions arise

- [x] 6. Update Python kinematics solver
  - [x] 6.1 Update HAA calculation for x-axis rotation
    - Modify `solve()` method in `leg_ik_4dof.py`
    - Change HAA calculation from `atan2(z, y)` to appropriate formula for x-axis
    - Update coordinate transformations
    - _Requirements: 4.1, 4.2_
  
  - [x] 6.2 Update forward kinematics for x-axis rotation
    - Modify `forward_kinematics()` method
    - Update rotation matrices and transformations
    - _Requirements: 4.2_
  
  - [x] 6.3 Write property test for kinematics round-trip
    - **Property 3: Kinematics Round-Trip Consistency**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - Generate random valid foot positions
    - Compute IK then FK
    - Assert foot position error < 1mm
    - Run with minimum 100 iterations
    - _Requirements: 4.3_

- [x] 7. Update C++ kinematics solver
  - [x] 7.1 Update HAA calculation in C++ implementation
    - Modify `solve()` method in `leg_ik_4dof.cpp`
    - Match Python implementation changes
    - _Requirements: 4.1, 4.2_
  
  - [x] 7.2 Update forward kinematics in C++ implementation
    - Modify `forwardKinematics()` method
    - Match Python implementation changes
    - _Requirements: 4.2_
  
  - [x] 7.3 Update C++ header file
    - Update documentation in `leg_ik_4dof.hpp`
    - Add comments about x-axis rotation
    - _Requirements: 4.1_

- [x] 8. Checkpoint - Test kinematics solvers
  - Run Python kinematics tests
  - Run C++ kinematics tests (if available)
  - Verify round-trip property test passes
  - Ensure all tests pass, ask the user if questions arise

- [x] 9. Test in RViz visualization
  - [x] 9.1 Launch RViz with updated URDF
    - Use `ros2 launch dog2_description view_robot.launch.py` or `./view_robot_in_rviz.sh`
    - Verify URDF loads without errors
    - _Requirements: 5.2, 7.5_
  
  - [x] 9.2 Verify visual appearance
    - Check hip links (l11, l21, l31, l41) appear correctly oriented
    - Command joints through range of motion using joint_state_publisher_gui
    - Verify rotation is about x-axis
    - _Requirements: 5.2, 5.3, 5.4_

- [-] 10. Test in Gazebo simulation
  - [x] 10.1 Launch Gazebo with updated URDF
    - Use `./start_gazebo_with_dog2.sh` or `./start_dog2_gui.sh`
    - Verify robot loads without errors
    - _Requirements: 7.1, 7.5_
  
  - [ ] 10.2 Test joint controllability
    - Send position commands to j11, j21, j31, j41 via ROS 2 topics
    - Verify joints rotate about x-axis
    - Check joint limits are respected
    - _Requirements: 7.1, 7.2_
  
  - [ ] 10.3 Verify collision detection
    - Move joints through range of motion
    - Check for false collision detections
    - Verify collision meshes are correctly oriented
    - _Requirements: 6.2, 6.3_

- [ ] 11. Test standing posture
  - [ ] 11.1 Command robot to standing posture
    - Use `./quick_stand.py` or `./stand_up_dog2.py`
    - Verify robot stands stably with new joint configuration
    - Check all joints are within limits
    - _Requirements: 7.3_

- [ ] 12. Test walking gait
  - [ ] 12.1 Execute simple walking gait
    - Use `./simple_walk_demo.py` or `./forward_walk_demo.py`
    - Verify locomotion works with new joint configuration
    - Monitor for kinematic issues
    - _Requirements: 7.4_

- [ ] 13. Final checkpoint and documentation
  - Run all unit tests and verify they pass
  - Run all property tests and verify they pass: `python tests/test_kinematics_roundtrip_property.py`
  - Update DOG2_4DOF_KINEMATICS.md to reflect x-axis rotation
  - Create summary document of changes made
  - Ensure all tests pass, ask the user if questions arise

- [ ] 14. Create rollback script (if needed)
  - Verify backup files exist in `backups/hip_joint_axis_change_latest/`
  - Document rollback procedure if issues arise
  - _Requirements: 5.6_

## Notes

- Tasks marked with completed checkboxes [x] have been implemented
- Remaining tasks focus on validation and testing in simulation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases

## Implementation Status

**Completed:**
- ✅ Task 1: Backup system created
- ✅ Task 2: URDF joint axis changed from z-axis to x-axis
- ✅ Task 3: Visual mesh orientations updated with RPY rotation
- ✅ Task 4: Collision mesh orientations updated to match visual
- ✅ Task 5: URDF changes verified
- ✅ Task 6: Python kinematics solver updated for x-axis rotation
- ✅ Task 7: C++ kinematics solver updated for x-axis rotation
- ✅ Task 8: Kinematics property tests passing

**Remaining:**
- ⏳ Task 9: RViz visualization testing
- ⏳ Task 10: Gazebo simulation testing
- ⏳ Task 11: Standing posture testing
- ⏳ Task 12: Walking gait testing
- ⏳ Task 13: Final documentation
- ⏳ Task 14: Rollback script (if needed)

## Critical Warnings

⚠️ **Before starting**: Ensure you have backups of all files (Task 1)

⚠️ **Coordinate system change**: The x-axis rotation fundamentally changes how the hip joints move. Carefully review kinematics calculations.

⚠️ **Visual verification**: Always visually inspect the robot in RViz and Gazebo after changes to ensure meshes are correctly oriented.

⚠️ **Testing order**: Follow the task order - test URDF changes before kinematics, test kinematics before simulation, test standing before walking.
