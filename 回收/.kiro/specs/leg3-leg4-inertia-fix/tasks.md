# Implementation Plan: Leg 3 and Leg 4 Inertia Position Corrections

## Overview

This implementation plan modifies the Dog2 robot's xacro file to support per-leg inertia corrections for legs 3 and 4, while maintaining backward compatibility and preserving legs 1 and 2 unchanged.

## Tasks

- [x] 1. Determine correct inertia positions
  - Analyze CAD models or physical measurements to obtain accurate center of mass positions
  - Document the method used (CAD analysis, physical measurement, or estimation)
  - Record corrected xyz coordinates for l311, l3111, and l4111
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Backup current xacro file
  - Create timestamped backup of dog2.urdf.xacro
  - Verify backup file is readable and complete
  - _Requirements: 6.1_

- [ ] 3. Add inertia override properties to xacro file
  - [x] 3.1 Define default inertia properties
    - Add `default_thigh_inertia_xyz` property with current thigh inertia origin
    - Add `default_shin_inertia_xyz` property with current shin inertia origin
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Define leg 3 inertia correction properties
    - Add `leg3_thigh_inertia_xyz` property with corrected value
    - Add `leg3_thigh_inertia_rpy` property (typically "0 0 0")
    - Add `leg3_shin_inertia_xyz` property with corrected value
    - Add `leg3_shin_inertia_rpy` property (typically "0 0 0")
    - Add comments documenting the source of corrected values
    - _Requirements: 3.1, 3.2, 6.2, 6.3_

  - [x] 3.3 Define leg 4 inertia correction properties
    - Add `leg4_shin_inertia_xyz` property with corrected value
    - Add `leg4_shin_inertia_rpy` property (typically "0 0 0")
    - Add comments documenting the source of corrected values
    - _Requirements: 4.1, 6.2, 6.3_

- [ ] 4. Modify leg macro to support inertia overrides
  - [x] 4.1 Add optional parameters to macro signature
    - Add `thigh_inertia_xyz` parameter with default value `${default_thigh_inertia_xyz}`
    - Add `shin_inertia_xyz` parameter with default value `${default_shin_inertia_xyz}`
    - Use xacro's `:=` syntax for default parameter values
    - _Requirements: 2.1, 2.2, 2.4_

  - [x] 4.2 Update thigh link (l${leg_num}11) inertial definition
    - Replace hardcoded xyz value with `${thigh_inertia_xyz}` parameter
    - Preserve all other inertial properties (mass, inertia tensor)
    - _Requirements: 2.3, 2.5_

  - [x] 4.3 Update shin link (l${leg_num}111) inertial definition
    - Replace hardcoded xyz value with `${shin_inertia_xyz}` parameter
    - Preserve all other inertial properties (mass, inertia tensor)
    - _Requirements: 2.3, 2.5_

- [ ] 5. Update leg instantiations
  - [x] 5.1 Verify legs 1 and 2 use defaults
    - Ensure leg 1 instantiation does not specify inertia override parameters
    - Ensure leg 2 instantiation does not specify inertia override parameters
    - _Requirements: 7.1, 7.4_

  - [x] 5.2 Add inertia overrides to leg 3 instantiation
    - Add `thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"` parameter
    - Add `shin_inertia_xyz="${leg3_shin_inertia_xyz}"` parameter
    - _Requirements: 3.1, 3.2_

  - [x] 5.3 Add inertia override to leg 4 instantiation
    - Add `shin_inertia_xyz="${leg4_shin_inertia_xyz}"` parameter
    - Do not add thigh override (leg 4 thigh uses default)
    - _Requirements: 4.1, 4.3_

- [ ] 6. Generate and validate URDF
  - [x] 6.1 Generate URDF from modified xacro
    - Run `xacro dog2.urdf.xacro > dog2_test.urdf`
    - Verify xacro processing completes without errors
    - _Requirements: 8.1_

  - [ ] 6.2 Validate XML syntax
    - Run `check_urdf dog2_test.urdf`
    - Verify no syntax errors are reported
    - _Requirements: 5.1, 8.1_

  - [ ] 6.3 Extract and verify inertia values
    - Parse generated URDF to extract inertia origins for all leg links
    - Verify l311 uses leg3_thigh_inertia_xyz
    - Verify l3111 uses leg3_shin_inertia_xyz
    - Verify l4111 uses leg4_shin_inertia_xyz
    - Verify l411 uses default_thigh_inertia_xyz
    - Verify l111, l211, l1111, l2111 use default values
    - _Requirements: 3.3, 3.4, 4.2, 7.2, 7.3_

- [ ] 7. Checkpoint - Verify generated URDF correctness
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Create validation script
  - [ ] 8.1 Write Python script to compare inertia values
    - Parse original and modified URDF files
    - Extract inertia origins for all leg links
    - Compare values and report differences
    - Highlight which links changed and which remained the same
    - _Requirements: 1.5, 5.5_

  - [ ] 8.2 Write unit tests for validation script
    - Test URDF parsing functionality
    - Test inertia extraction for various link types
    - Test comparison logic with known inputs
    - _Requirements: 5.5_

- [ ] 9. Test in RViz
  - [x] 9.1 Launch RViz with modified URDF
    - Run `ros2 launch dog2_description view_dog2_xacro.launch.py`
    - Verify robot model loads without errors
    - Visually inspect leg positions and orientations
    - _Requirements: 8.1_

  - [ ] 9.2 Check for visual anomalies
    - Verify all links are properly connected
    - Check that legs appear in correct positions
    - Ensure no links are displaced or rotated unexpectedly
    - _Requirements: 5.2_

- [ ] 10. Test in Gazebo simulation
  - [ ] 10.1 Launch Gazebo with modified URDF
    - Run `ros2 launch dog2_description gazebo_dog2.launch.py`
    - Verify robot model loads without errors
    - Check Gazebo console for warnings or errors
    - _Requirements: 8.1, 8.2_

  - [ ] 10.2 Test robot stability
    - Let robot settle under gravity
    - Verify robot maintains stable standing pose
    - Check for unexpected oscillations or instability
    - _Requirements: 5.3, 8.4_

  - [ ] 10.3 Test with MPC controller
    - Launch MPC controller node
    - Verify controller initializes successfully
    - Send simple velocity commands
    - Verify robot responds appropriately
    - _Requirements: 8.3_

  - [ ] 10.4 Test with WBC controller
    - Launch WBC controller node
    - Verify controller initializes successfully
    - Check joint torque computations are valid
    - _Requirements: 8.3_

  - [ ] 10.5 Test walking gait
    - Command robot to walk forward
    - Verify gait is smooth without unexpected oscillations
    - Compare with original URDF behavior
    - _Requirements: 8.5_

- [ ] 11. Checkpoint - Ensure simulation tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Document changes
  - [ ] 12.1 Add inline comments to xacro file
    - Document why legs 3 and 4 have custom inertia
    - Explain the source of corrected values
    - List affected links (l311, l3111, l4111)
    - _Requirements: 6.1, 6.3_

  - [ ] 12.2 Create before/after comparison document
    - Document original inertia positions
    - Document corrected inertia positions
    - Calculate and document position differences
    - Explain expected impact on simulation
    - _Requirements: 6.4, 6.5_

  - [ ] 12.3 Update README or documentation
    - Explain the inertia correction feature
    - Provide instructions for future modifications
    - Document validation procedures
    - _Requirements: 6.1, 6.5_

- [ ] 13. Final validation
  - [ ] 13.1 Run complete validation suite
    - Execute validation script
    - Verify all inertia corrections are applied
    - Verify legs 1 and 2 are unchanged
    - Check for any unexpected modifications
    - _Requirements: 5.5, 7.5_

  - [ ] 13.2 Run property-based tests
    - Test inertia override application (Property 1)
    - Test default inertia preservation (Property 2)
    - Test legs 1 and 2 unchanged (Property 3)
    - Test leg 3 corrections applied (Properties 4, 5)
    - Test leg 4 corrections applied (Properties 6, 7)
    - Test XML validity (Property 8)
    - Test inertia tensor validity (Property 9)
    - Test Gazebo load success (Property 10)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 13.3 Final simulation test
    - Run complete simulation with all controllers
    - Verify stable operation over extended period
    - Compare performance with original URDF
    - Document any improvements or issues
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 14. Replace original URDF
  - Verify all tests pass
  - Replace dog2.urdf with corrected version
  - Update any launch files if necessary
  - Commit changes to version control
  - _Requirements: 8.1_

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The most critical task is determining the correct inertia positions (Task 1) - all other tasks depend on this
- Backup (Task 2) is essential before making any modifications
- Testing in both RViz and Gazebo ensures visual and physical correctness
