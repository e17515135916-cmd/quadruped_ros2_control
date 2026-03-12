#!/usr/bin/env python3
"""
Verify that hip joints (j11, j21, j31, j41) have axis [1, 0, 0]
Requirements: 1.1, 1.2, 1.3, 1.4
"""

import sys
from urdf_parser_py.urdf import URDF


def verify_hip_axis(urdf_file):
    """Parse URDF and verify hip joint axes"""
    print(f"Parsing URDF file: {urdf_file}")
    
    try:
        robot = URDF.from_xml_file(urdf_file)
    except Exception as e:
        print(f"ERROR: Failed to parse URDF: {e}")
        return False
    
    print(f"Robot name: {robot.name}")
    print(f"Total joints: {len(robot.joints)}")
    
    # Hip joints to verify
    hip_joints = ['j11', 'j21', 'j31', 'j41']
    expected_axis = [1.0, 0.0, 0.0]
    
    all_passed = True
    
    for joint_name in hip_joints:
        # Find the joint
        joint = None
        for j in robot.joints:
            if j.name == joint_name:
                joint = j
                break
        
        if joint is None:
            print(f"ERROR: Joint {joint_name} not found in URDF")
            all_passed = False
            continue
        
        # Check axis
        if joint.axis is None:
            print(f"ERROR: Joint {joint_name} has no axis defined")
            all_passed = False
            continue
        
        actual_axis = list(joint.axis)
        print(f"Joint {joint_name}: axis = {actual_axis}")
        
        # Compare with expected axis
        if actual_axis != expected_axis:
            print(f"  FAIL: Expected {expected_axis}, got {actual_axis}")
            all_passed = False
        else:
            print(f"  PASS: Axis is correct [1, 0, 0]")
    
    return all_passed


if __name__ == "__main__":
    urdf_file = "/tmp/dog2_test.urdf"
    
    if len(sys.argv) > 1:
        urdf_file = sys.argv[1]
    
    print("=" * 60)
    print("Hip Joint Axis Verification")
    print("=" * 60)
    
    success = verify_hip_axis(urdf_file)
    
    print("=" * 60)
    if success:
        print("RESULT: All hip joints have correct axis [1, 0, 0]")
        sys.exit(0)
    else:
        print("RESULT: Some hip joints have incorrect axis")
        sys.exit(1)
