#!/usr/bin/env python3
"""
Verification script for ROS 2 Control configuration update.
This script verifies that all joints have been correctly configured with CHAMP naming
and have all required interfaces (position, velocity, effort).
"""

import re
import sys

def verify_ros2_control():
    """Verify the ROS 2 Control configuration."""
    
    with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
        content = f.read()
    
    # Extract ros2_control section
    ros2_control_match = re.search(r'<ros2_control[^>]*>.*?</ros2_control>', content, re.DOTALL)
    if not ros2_control_match:
        print("✗ ERROR: No ros2_control section found")
        return False
    
    ros2_control_section = ros2_control_match.group(0)
    
    # Find all joint names
    joint_names = re.findall(r'<joint name="([^"]+)">', ros2_control_section)
    
    print("=" * 70)
    print("ROS 2 Control Configuration Verification")
    print("=" * 70)
    print()
    
    # Expected joints
    expected_prismatic = ['j1', 'j2', 'j3', 'j4']
    expected_haa = ['lf_haa_joint', 'rf_haa_joint', 'lh_haa_joint', 'rh_haa_joint']
    expected_hfe = ['lf_hfe_joint', 'rf_hfe_joint', 'lh_hfe_joint', 'rh_hfe_joint']
    expected_kfe = ['lf_kfe_joint', 'rf_kfe_joint', 'lh_kfe_joint', 'rh_kfe_joint']
    
    all_expected = expected_prismatic + expected_haa + expected_hfe + expected_kfe
    
    # Check if all expected joints are present
    print("Task 4.1: Prismatic Joint Configuration")
    print("-" * 70)
    all_prismatic_present = True
    for joint in expected_prismatic:
        present = joint in joint_names
        status = "✓" if present else "✗"
        print(f"  {status} {joint}: {'Present' if present else 'MISSING'}")
        if not present:
            all_prismatic_present = False
    
    if all_prismatic_present:
        print("  ✓ All prismatic joints (j1, j2, j3, j4) are present")
    else:
        print("  ✗ Some prismatic joints are missing")
    print()
    
    print("Task 4.2: HAA Joint Configuration")
    print("-" * 70)
    all_haa_present = True
    for joint in expected_haa:
        present = joint in joint_names
        status = "✓" if present else "✗"
        print(f"  {status} {joint}: {'Present' if present else 'MISSING'}")
        if not present:
            all_haa_present = False
    
    if all_haa_present:
        print("  ✓ All HAA joints renamed to CHAMP standard")
    else:
        print("  ✗ Some HAA joints are missing or not renamed")
    print()
    
    print("Task 4.3: HFE Joint Configuration")
    print("-" * 70)
    all_hfe_present = True
    for joint in expected_hfe:
        present = joint in joint_names
        status = "✓" if present else "✗"
        print(f"  {status} {joint}: {'Present' if present else 'MISSING'}")
        if not present:
            all_hfe_present = False
    
    if all_hfe_present:
        print("  ✓ All HFE joints renamed to CHAMP standard")
    else:
        print("  ✗ Some HFE joints are missing or not renamed")
    print()
    
    print("Task 4.4: KFE Joint Configuration")
    print("-" * 70)
    all_kfe_present = True
    for joint in expected_kfe:
        present = joint in joint_names
        status = "✓" if present else "✗"
        print(f"  {status} {joint}: {'Present' if present else 'MISSING'}")
        if not present:
            all_kfe_present = False
    
    if all_kfe_present:
        print("  ✓ All KFE joints renamed to CHAMP standard")
    else:
        print("  ✗ Some KFE joints are missing or not renamed")
    print()
    
    # Check interfaces for all joints
    print("Interface Verification (Requirements 9.1-9.5)")
    print("-" * 70)
    all_interfaces_correct = True
    
    for joint in all_expected:
        # Find the joint block
        joint_pattern = f'<joint name="{joint}">.*?</joint>'
        joint_match = re.search(joint_pattern, ros2_control_section, re.DOTALL)
        
        if not joint_match:
            print(f"  ✗ {joint}: Joint block not found")
            all_interfaces_correct = False
            continue
        
        joint_block = joint_match.group(0)
        
        # Check for required interfaces
        has_position_cmd = 'command_interface name="position"' in joint_block
        has_effort_cmd = 'command_interface name="effort"' in joint_block
        has_position_state = 'state_interface name="position"' in joint_block
        has_velocity_state = 'state_interface name="velocity"' in joint_block
        has_effort_state = 'state_interface name="effort"' in joint_block
        
        all_present = all([has_position_cmd, has_effort_cmd, has_position_state, 
                          has_velocity_state, has_effort_state])
        
        status = "✓" if all_present else "✗"
        
        if all_present:
            print(f"  {status} {joint}: All interfaces present (pos, vel, eff)")
        else:
            missing = []
            if not has_position_cmd: missing.append("pos_cmd")
            if not has_effort_cmd: missing.append("eff_cmd")
            if not has_position_state: missing.append("pos_state")
            if not has_velocity_state: missing.append("vel_state")
            if not has_effort_state: missing.append("eff_state")
            print(f"  {status} {joint}: Missing interfaces: {', '.join(missing)}")
            all_interfaces_correct = False
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    if all_prismatic_present and all_haa_present and all_hfe_present and all_kfe_present and all_interfaces_correct:
        print("✓ ALL TASKS COMPLETED SUCCESSFULLY")
        print()
        print("  ✓ Task 4.1: Prismatic joints (j1-j4) preserved with all interfaces")
        print("  ✓ Task 4.2: HAA joints renamed to CHAMP standard with all interfaces")
        print("  ✓ Task 4.3: HFE joints renamed to CHAMP standard with all interfaces")
        print("  ✓ Task 4.4: KFE joints renamed to CHAMP standard with all interfaces")
        print()
        print("Requirements validated:")
        print("  ✓ Requirement 9.1: Prismatic joints have position, velocity, effort interfaces")
        print("  ✓ Requirement 9.2: HAA joints have position, velocity, effort interfaces")
        print("  ✓ Requirement 9.3: HFE joints have position, velocity, effort interfaces")
        print("  ✓ Requirement 9.4: KFE joints have position, velocity, effort interfaces")
        print("  ✓ Requirement 9.5: All joints use CHAMP-compliant naming")
        return True
    else:
        print("✗ SOME TASKS INCOMPLETE OR FAILED")
        return False

if __name__ == "__main__":
    success = verify_ros2_control()
    sys.exit(0 if success else 1)
