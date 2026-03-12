# Implementation Plan: Gazebo Fortress Migration

## Overview

This plan guides the migration from Gazebo Classic to Gazebo Fortress through incremental, testable steps. Each task builds on previous work, with checkpoints to ensure stability before proceeding.

## Tasks

- [x] 1. Create installation script for Gazebo Fortress
  - Create `scripts/install_gazebo_fortress.sh` bash script
  - Add Gazebo Fortress repository configuration
  - Install gz-fortress, ros-humble-ros-gz-sim, ros-humble-ros-gz-bridge packages
  - Add verification checks for gz command and libign_ros2_control-system.so
  - Include error handling for missing dependencies
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 1.1 Write unit tests for installation verification
  - Test gz command availability check
  - Test package installation verification
  - Test plugin file existence check
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Create URDF migration script
  - [x] 2.1 Implement backup functionality
    - Create `scripts/migrate_urdf_to_fortress.py` Python script
    - Implement timestamped backup creation for URDF files
    - Create backup directory structure
    - _Requirements: 2.3_

  - [ ]* 2.2 Write property test for plugin reference replacement
    - **Property 1: Plugin Reference Replacement**
    - **Validates: Requirements 2.1**

  - [x] 2.3 Implement plugin reference replacement
    - Replace `gazebo_ros2_control/GazeboSystem` with `ign_ros2_control/IgnitionSystem`
    - Replace `libgazebo_ros2_control.so` with `libign_ros2_control-system.so`
    - Use XML parsing to ensure correct replacements
    - _Requirements: 2.1_

  - [ ]* 2.4 Write property test for ros2_control configuration preservation
    - **Property 2: ros2_control Configuration Preservation**
    - **Validates: Requirements 2.2, 2.4**

  - [x] 2.5 Implement configuration validation
    - Parse ros2_control section before and after migration
    - Verify joint names, command interfaces, and state interfaces are preserved
    - Add validation error reporting
    - _Requirements: 2.2, 2.4_

  - [x] 2.6 Add xacro processing validation
    - Run xacro command on migrated files
    - Check for processing errors
    - Report validation results
    - _Requirements: 2.5_

- [x] 3. Checkpoint - Verify URDF migration
  - Run migration script on dog2.urdf.xacro
  - Verify backup was created
  - Verify xacro processing succeeds
  - Ensure all tests pass, ask the user if questions arise

- [x] 4. Create launch file migration script
  - [x] 4.1 Implement launch file backup
    - Create `scripts/migrate_launch_to_fortress.py` Python script
    - Implement backup functionality for launch files
    - _Requirements: 3.1_

  - [ ]* 4.2 Write property test for launch import replacement
    - **Property 3: Launch Import Replacement**
    - **Validates: Requirements 3.1**

  - [x] 4.3 Implement import statement replacement
    - Replace `gazebo_ros` imports with `ros_gz_sim` imports
    - Update `get_package_share_directory('gazebo_ros')` calls
    - Handle various import styles (from X import Y, import X)
    - _Requirements: 3.1_

  - [ ]* 4.4 Write property test for node type replacement
    - **Property 5: Node Type Replacement**
    - **Validates: Requirements 3.2**

  - [x] 4.5 Implement node type replacement
    - Replace `gazebo.launch.py` with `gz_sim.launch.py`
    - Replace `gzserver`/`gzclient` with `GzServer` equivalents
    - Update ExecuteProcess commands
    - _Requirements: 3.2_

  - [ ]* 4.6 Write property test for spawner configuration preservation
    - **Property 4: Spawner Configuration Preservation**
    - **Validates: Requirements 3.4**

  - [x] 4.7 Implement spawner node migration
    - Replace `gazebo_ros/spawn_entity.py` with `ros_gz_sim/create`
    - Preserve entity name and topic arguments
    - Update argument format if needed
    - _Requirements: 3.4_

  - [x] 4.8 Add Python syntax validation
    - Run Python syntax checker on migrated files
    - Report any syntax errors
    - _Requirements: 3.1_

- [x] 5. Checkpoint - Verify launch file migration
  - Run migration script on all launch files
  - Verify backups were created
  - Verify Python syntax is valid
  - Ensure all tests pass, ask the user if questions arise

- [ ] 6. Create migration verification tests
  - [ ] 6.1 Write simulation startup test
    - Test that Gazebo Fortress launches without errors
    - Verify gz process is running
    - Check for GUI crash indicators
    - _Requirements: 4.1_

  - [ ] 6.2 Write robot spawning test
    - Test that dog2 model spawns correctly
    - Verify all links are present in simulation
    - Check model geometry is correct
    - _Requirements: 4.2_

  - [ ] 6.3 Write ros2_control connectivity test
    - Test that controller_manager connects to plugin
    - Verify hardware interfaces are available
    - Check joint command/state topics exist
    - _Requirements: 4.3, 4.4, 3.5_

  - [ ] 6.4 Write joint control test
    - Send joint position commands
    - Verify joint states update correctly
    - Test all 12 joints (4 legs × 3 joints)
    - _Requirements: 4.3, 4.4_

- [x] 7. Create migration documentation
  - Create `GAZEBO_FORTRESS_MIGRATION.md` documentation file
  - Document all file changes with before/after examples
  - Include rollback instructions
  - Document gz command usage
  - List behavioral differences from Gazebo Classic
  - Add troubleshooting section with common errors
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8. Execute migration on dog2 project
  - [ ] 8.1 Create full project backup
    - Backup entire src/dog2_description directory
    - Create backup timestamp and README
    - _Requirements: 2.3_

  - [ ] 8.2 Run installation script
    - Execute `scripts/install_gazebo_fortress.sh`
    - Verify installation success
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 8.3 Migrate URDF files
    - Run `scripts/migrate_urdf_to_fortress.py` on dog2.urdf.xacro
    - Verify migration success
    - Test xacro processing
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ] 8.4 Migrate launch files
    - Run `scripts/migrate_launch_to_fortress.py` on all launch files
    - Verify migration success
    - Check Python syntax
    - _Requirements: 3.1, 3.2, 3.4_

  - [ ] 8.5 Update world files if needed
    - Check world file SDF format compatibility
    - Convert to Gazebo Fortress SDF if necessary
    - _Requirements: 3.3_

- [-] 9. Final verification and testing
  - [x] 9.1 Test simulation startup
    - Launch Gazebo Fortress with dog2 model
    - Verify no GUI crashes
    - Monitor for 5 minutes of stable operation
    - _Requirements: 4.1_

  - [x] 9.2 Test ros2_control functionality
    - Start controller_manager
    - Load joint controllers
    - Send test commands to all joints
    - Verify joint states are published
    - _Requirements: 4.3, 4.4, 3.5_

  - [ ] 9.3 Run existing test scripts
    - Execute existing dog2 test scripts
    - Compare behavior to Gazebo Classic baseline
    - Document any differences
    - _Requirements: 4.5_

  - [ ] 9.4 Performance comparison
    - Measure simulation real-time factor
    - Compare to Gazebo Classic performance
    - Document any performance changes
    - _Requirements: 4.2_

- [x] 10. Final checkpoint - Complete migration
  - Verify all tests pass
  - Confirm no GUI crashes
  - Ensure ros2_control works correctly
  - Update project README with Gazebo Fortress instructions
  - Ask the user if questions arise or if rollback is needed

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Backup creation is mandatory before any file modifications
- Rollback instructions are available in the design document
