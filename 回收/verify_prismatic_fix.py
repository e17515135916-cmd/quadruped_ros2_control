#!/usr/bin/env python3
"""
Verify Prismatic Coordinate System Fix

This script verifies that the Prismatic joint RPY has been removed
and that the joint configuration is now CHAMP-compliant (orthogonal).
"""

import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation as R

def parse_urdf(urdf_file):
    """Parse URDF file and extract joint information."""
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    joints = {}
    for joint in root.findall('joint'):
        name = joint.get('name')
        joint_type = joint.get('type')
        
        origin = joint.find('origin')
        if origin is not None:
            xyz = [float(x) for x in origin.get('xyz', '0 0 0').split()]
            rpy = [float(x) for x in origin.get('rpy', '0 0 0').split()]
        else:
            xyz = [0, 0, 0]
            rpy = [0, 0, 0]
        
        axis = joint.find('axis')
        if axis is not None:
            axis_xyz = [float(x) for x in axis.get('xyz', '1 0 0').split()]
        else:
            axis_xyz = [1, 0, 0]
        
        parent = joint.find('parent')
        child = joint.find('child')
        
        joints[name] = {
            'type': joint_type,
            'xyz': np.array(xyz),
            'rpy': np.array(rpy),
            'axis': np.array(axis_xyz),
            'parent': parent.get('link') if parent is not None else None,
            'child': child.get('link') if child is not None else None
        }
    
    return joints

def verify_prismatic_rpy(joints):
    """Verify that all Prismatic joints have RPY = [0, 0, 0]."""
    print("\n" + "=" * 60)
    print("VERIFYING PRISMATIC JOINT RPY")
    print("=" * 60)
    
    prismatic_joints = {name: j for name, j in joints.items() if j['type'] == 'prismatic'}
    
    all_correct = True
    for name, joint in prismatic_joints.items():
        rpy = joint['rpy']
        is_zero = np.allclose(rpy, [0, 0, 0], atol=0.01)
        
        status = "✓ PASS" if is_zero else "✗ FAIL"
        print(f"\n{name}:")
        print(f"  rpy: {rpy}")
        print(f"  Status: {status}")
        
        if not is_zero:
            all_correct = False
    
    return all_correct

def calculate_joint_axis_in_world(joints, joint_name, parent_chain=None):
    """Calculate joint axis in world frame by traversing parent chain."""
    if parent_chain is None:
        parent_chain = []
    
    joint = joints[joint_name]
    parent_link = joint['parent']
    
    # Find parent joint
    parent_joint = None
    for name, j in joints.items():
        if j['child'] == parent_link:
            parent_joint = name
            break
    
    # Base case: reached base_link
    if parent_joint is None or parent_link == 'base_link':
        # Just use this joint's rotation
        R_joint = R.from_euler('xyz', joint['rpy'])
        axis_world = R_joint.as_matrix() @ joint['axis']
        return axis_world
    
    # Recursive case: accumulate rotations
    R_parent = R.from_euler('xyz', joints[parent_joint]['rpy'])
    R_joint = R.from_euler('xyz', joint['rpy'])
    R_total = R_parent * R_joint
    
    axis_world = R_total.as_matrix() @ joint['axis']
    return axis_world

def verify_orthogonality(joints):
    """Verify that HAA is orthogonal to HFE/KFE."""
    print("\n" + "=" * 60)
    print("VERIFYING JOINT ORTHOGONALITY")
    print("=" * 60)
    
    legs = ['lf', 'rf', 'lh', 'rh']
    all_orthogonal = True
    
    for leg in legs:
        print(f"\n{leg.upper()} Leg:")
        
        # Get joint names
        haa_name = f"{leg}_haa_joint"
        hfe_name = f"{leg}_hfe_joint"
        kfe_name = f"{leg}_kfe_joint"
        
        if haa_name not in joints or hfe_name not in joints or kfe_name not in joints:
            print(f"  ✗ Joints not found")
            all_orthogonal = False
            continue
        
        # Get joint axes
        haa_axis = joints[haa_name]['axis']
        hfe_axis = joints[hfe_name]['axis']
        kfe_axis = joints[kfe_name]['axis']
        
        print(f"  HAA axis: {haa_axis}")
        print(f"  HFE axis: {hfe_axis}")
        print(f"  KFE axis: {kfe_axis}")
        
        # Calculate dot products
        dot_haa_hfe = np.dot(haa_axis, hfe_axis)
        dot_haa_kfe = np.dot(haa_axis, kfe_axis)
        dot_hfe_kfe = np.dot(hfe_axis, kfe_axis)
        
        print(f"\n  Dot products:")
        print(f"    HAA · HFE = {dot_haa_hfe:.6f}")
        print(f"    HAA · KFE = {dot_haa_kfe:.6f}")
        print(f"    HFE · KFE = {dot_hfe_kfe:.6f}")
        
        # Check orthogonality
        haa_hfe_orth = abs(dot_haa_hfe) < 0.01
        haa_kfe_orth = abs(dot_haa_kfe) < 0.01
        hfe_kfe_parallel = abs(abs(dot_hfe_kfe) - 1.0) < 0.01
        
        print(f"\n  Verification:")
        print(f"    HAA ⊥ HFE: {'✓ PASS' if haa_hfe_orth else '✗ FAIL'}")
        print(f"    HAA ⊥ KFE: {'✓ PASS' if haa_kfe_orth else '✗ FAIL'}")
        print(f"    HFE ∥ KFE: {'✓ PASS' if hfe_kfe_parallel else '✗ FAIL'}")
        
        if not (haa_hfe_orth and haa_kfe_orth and hfe_kfe_parallel):
            all_orthogonal = False
    
    return all_orthogonal

def verify_joint_names(joints):
    """Verify that CHAMP-compliant joint names exist."""
    print("\n" + "=" * 60)
    print("VERIFYING CHAMP-COMPLIANT JOINT NAMES")
    print("=" * 60)
    
    expected_joints = []
    for leg in ['lf', 'rf', 'lh', 'rh']:
        expected_joints.extend([
            f"{leg}_haa_joint",
            f"{leg}_hfe_joint",
            f"{leg}_kfe_joint"
        ])
    
    all_found = True
    for joint_name in expected_joints:
        found = joint_name in joints
        status = "✓ FOUND" if found else "✗ MISSING"
        print(f"  {joint_name}: {status}")
        if not found:
            all_found = False
    
    return all_found

def main():
    """Main verification function."""
    print("\n" + "=" * 60)
    print("PRISMATIC COORDINATE SYSTEM FIX VERIFICATION")
    print("=" * 60)
    
    urdf_file = '/tmp/dog2_fixed.urdf'
    
    try:
        joints = parse_urdf(urdf_file)
    except Exception as e:
        print(f"\n✗ ERROR: Failed to parse URDF: {e}")
        return 1
    
    # Run verifications
    prismatic_ok = verify_prismatic_rpy(joints)
    names_ok = verify_joint_names(joints)
    orthogonal_ok = verify_orthogonality(joints)
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"\nPrismatic RPY removed: {'✓ PASS' if prismatic_ok else '✗ FAIL'}")
    print(f"CHAMP joint names: {'✓ PASS' if names_ok else '✗ FAIL'}")
    print(f"Joint orthogonality: {'✓ PASS' if orthogonal_ok else '✗ FAIL'}")
    
    if prismatic_ok and names_ok and orthogonal_ok:
        print(f"\n✓ ALL VERIFICATIONS PASSED!")
        print(f"The Prismatic coordinate system fix is successful.")
        return 0
    else:
        print(f"\n✗ SOME VERIFICATIONS FAILED")
        print(f"Please review the output above for details.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
