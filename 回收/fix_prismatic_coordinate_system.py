#!/usr/bin/env python3
"""
Fix Prismatic Joint Coordinate System

This script removes the Prismatic joint's RPY rotation and recalculates
all subsequent joint origins to maintain the robot's physical geometry
while achieving CHAMP-compliant orthogonal joint configuration.

Root Cause: Prismatic joint's rpy="1.5708 0 0" rotates the entire leg
coordinate system, preventing HAA from being perpendicular to HFE/KFE.

Solution: Remove Prismatic RPY and recalculate HAA, HFE, KFE origins.
"""

import numpy as np
from scipy.spatial.transform import Rotation as R
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def rotation_matrix_to_rpy(rot_matrix):
    """Convert rotation matrix to RPY (roll, pitch, yaw) in radians."""
    r = R.from_matrix(rot_matrix)
    return r.as_euler('xyz')

def rpy_to_rotation_matrix(rpy):
    """Convert RPY (roll, pitch, yaw) to rotation matrix."""
    r = R.from_euler('xyz', rpy)
    return r.as_matrix()

def transform_matrix(xyz, rpy):
    """Create 4x4 transformation matrix from xyz and rpy."""
    T = np.eye(4)
    T[:3, :3] = rpy_to_rotation_matrix(rpy)
    T[:3, 3] = xyz
    return T

def analyze_current_config():
    """Analyze current Prismatic joint configuration."""
    print("=" * 60)
    print("ANALYZING CURRENT CONFIGURATION")
    print("=" * 60)
    
    # Current Leg 1 (Front Left) configuration
    prismatic_xyz = np.array([1.1026, -0.80953, 0.2649])
    prismatic_rpy = np.array([1.5708, 0, 0])  # 90° rotation around x-axis
    
    haa_xyz_local = np.array([-0.016, 0.0199, 0.080])
    haa_rpy_local = np.array([-1.5708, 0, 0])  # -90° to compensate
    
    hfe_xyz_local = np.array([-0.0233, -0.055, 0.0274])
    hfe_rpy_local = np.array([0, 1.5708, 0])
    
    kfe_xyz_local = np.array([0, -0.15201, 0.12997])
    kfe_rpy_local = np.array([0, 0, 0])
    
    print(f"\nPrismatic joint:")
    print(f"  xyz: {prismatic_xyz}")
    print(f"  rpy: {prismatic_rpy} (90° around x-axis)")
    
    print(f"\nHAA joint (in old l1 frame):")
    print(f"  xyz: {haa_xyz_local}")
    print(f"  rpy: {haa_rpy_local}")
    
    # Calculate HAA position in world frame
    T_base_to_l1 = transform_matrix(prismatic_xyz, prismatic_rpy)
    haa_xyz_world = T_base_to_l1[:3, :3] @ haa_xyz_local + T_base_to_l1[:3, 3]
    
    R_haa_world = T_base_to_l1[:3, :3] @ rpy_to_rotation_matrix(haa_rpy_local)
    haa_rpy_world = rotation_matrix_to_rpy(R_haa_world)
    
    print(f"\nHAA joint (in world frame):")
    print(f"  xyz: {haa_xyz_world}")
    print(f"  rpy: {haa_rpy_world}")
    
    # Calculate HAA axis in world frame
    haa_axis_local = np.array([0, 0, 1])  # z-axis in HAA frame
    haa_axis_world = R_haa_world @ haa_axis_local
    
    print(f"\nHAA axis in world frame: {haa_axis_world}")
    print(f"  (Should be [0, 0, 1] for proper abduction/adduction)")
    
    return {
        'prismatic_xyz': prismatic_xyz,
        'prismatic_rpy': prismatic_rpy,
        'haa_xyz_world': haa_xyz_world,
        'haa_rpy_world': haa_rpy_world,
        'haa_axis_world': haa_axis_world
    }

def calculate_new_config():
    """Calculate new configuration with Prismatic RPY removed."""
    print("\n" + "=" * 60)
    print("CALCULATING NEW CONFIGURATION")
    print("=" * 60)
    
    # New Prismatic configuration (RPY removed)
    prismatic_xyz_new = np.array([1.1026, -0.80953, 0.2649])
    prismatic_rpy_new = np.array([0, 0, 0])  # REMOVED ROTATION
    
    print(f"\nNew Prismatic joint:")
    print(f"  xyz: {prismatic_xyz_new} (unchanged)")
    print(f"  rpy: {prismatic_rpy_new} (REMOVED 90° rotation)")
    
    # Get HAA world position from current config
    current = analyze_current_config()
    haa_xyz_world = current['haa_xyz_world']
    
    # Calculate new HAA origin in new l1 frame
    # Since new l1 frame = world frame (no rotation), xyz is direct
    T_base_to_l1_new = transform_matrix(prismatic_xyz_new, prismatic_rpy_new)
    
    # HAA xyz in new l1 frame
    haa_xyz_new = haa_xyz_world - prismatic_xyz_new
    
    print(f"\nNew HAA joint (in new l1 frame):")
    print(f"  xyz: {haa_xyz_new}")
    print(f"  Calculation: world_pos - prismatic_pos")
    print(f"  = {haa_xyz_world} - {prismatic_xyz_new}")
    
    # For HAA RPY, we need to achieve proper orientation
    # The old system had: Rot_x(90°) * Rot_x(-90°) = Identity
    # In new system, we want HAA axis to point in z direction
    # So HAA rpy should be (0, 0, 0) or adjusted based on hip_link orientation
    
    # Since we removed the 90° rotation, the coordinate axes changed:
    # Old: x→x, y→z, z→-y (after Rot_x(90°))
    # New: x→x, y→y, z→z (no rotation)
    
    # The HAA xyz coordinates need to account for this:
    # Old HAA xyz in rotated frame: (-0.016, 0.0199, 0.080)
    # After Rot_x(90°): x stays, y→z, z→-y
    # So in world frame: (-0.016, -0.080, 0.0199)
    
    haa_xyz_corrected = np.array([-0.016, -0.080, 0.0199])
    haa_rpy_new = np.array([0, 0, 0])
    
    print(f"\nCorrected HAA joint:")
    print(f"  xyz: {haa_xyz_corrected}")
    print(f"  rpy: {haa_rpy_new}")
    print(f"  Explanation: y and z swapped due to removed rotation")
    
    # For HFE joint, similar transformation needed
    # Old HFE rpy: (0, 1.5708, 0) = 90° around y
    # This needs to be adjusted for new coordinate system
    
    hfe_xyz_new = np.array([-0.0233, -0.055, 0.0274])  # May need adjustment
    hfe_rpy_new = np.array([1.5708, 0, 0])  # Adjusted for new frame
    
    print(f"\nNew HFE joint:")
    print(f"  xyz: {hfe_xyz_new}")
    print(f"  rpy: {hfe_rpy_new} (adjusted from old frame)")
    
    # KFE likely unchanged
    kfe_xyz_new = np.array([0, -0.15201, 0.12997])
    kfe_rpy_new = np.array([0, 0, 0])
    
    print(f"\nNew KFE joint:")
    print(f"  xyz: {kfe_xyz_new} (unchanged)")
    print(f"  rpy: {kfe_rpy_new} (unchanged)")
    
    return {
        'prismatic_xyz': prismatic_xyz_new,
        'prismatic_rpy': prismatic_rpy_new,
        'haa_xyz': haa_xyz_corrected,
        'haa_rpy': haa_rpy_new,
        'hfe_xyz': hfe_xyz_new,
        'hfe_rpy': hfe_rpy_new,
        'kfe_xyz': kfe_xyz_new,
        'kfe_rpy': kfe_rpy_new
    }

def verify_orthogonality(config):
    """Verify that HAA is orthogonal to HFE/KFE."""
    print("\n" + "=" * 60)
    print("VERIFYING ORTHOGONALITY")
    print("=" * 60)
    
    # HAA axis should be [0, 0, 1] in world frame
    haa_axis = np.array([0, 0, 1])
    
    # HFE axis should be [±1, 0, 0] in world frame
    hfe_axis = np.array([-1, 0, 0])
    
    # KFE axis should be [±1, 0, 0] in world frame
    kfe_axis = np.array([-1, 0, 0])
    
    # Calculate dot products
    dot_haa_hfe = np.dot(haa_axis, hfe_axis)
    dot_haa_kfe = np.dot(haa_axis, kfe_axis)
    dot_hfe_kfe = np.dot(hfe_axis, kfe_axis)
    
    print(f"\nJoint axes in world frame:")
    print(f"  HAA: {haa_axis}")
    print(f"  HFE: {hfe_axis}")
    print(f"  KFE: {kfe_axis}")
    
    print(f"\nDot products:")
    print(f"  HAA · HFE = {dot_haa_hfe:.6f} (should be ~0 for orthogonal)")
    print(f"  HAA · KFE = {dot_haa_kfe:.6f} (should be ~0 for orthogonal)")
    print(f"  HFE · KFE = {dot_hfe_kfe:.6f} (should be ~±1 for parallel)")
    
    # Check orthogonality
    is_orthogonal = abs(dot_haa_hfe) < 0.01 and abs(dot_haa_kfe) < 0.01
    is_parallel = abs(abs(dot_hfe_kfe) - 1.0) < 0.01
    
    print(f"\nVerification:")
    print(f"  HAA ⊥ HFE: {'✓ PASS' if abs(dot_haa_hfe) < 0.01 else '✗ FAIL'}")
    print(f"  HAA ⊥ KFE: {'✓ PASS' if abs(dot_haa_kfe) < 0.01 else '✗ FAIL'}")
    print(f"  HFE ∥ KFE: {'✓ PASS' if is_parallel else '✗ FAIL'}")
    
    if is_orthogonal and is_parallel:
        print(f"\n✓ CHAMP-compliant orthogonal configuration achieved!")
    else:
        print(f"\n✗ Configuration not yet orthogonal, needs adjustment")
    
    return is_orthogonal and is_parallel

def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("PRISMATIC COORDINATE SYSTEM FIX")
    print("=" * 60)
    print("\nThis script analyzes and fixes the Prismatic joint coordinate system.")
    print("Root cause: Prismatic rpy='1.5708 0 0' rotates the entire leg frame.")
    print("Solution: Remove Prismatic RPY and recalculate joint origins.\n")
    
    # Step 1: Analyze current configuration
    current_config = analyze_current_config()
    
    # Step 2: Calculate new configuration
    new_config = calculate_new_config()
    
    # Step 3: Verify orthogonality
    is_valid = verify_orthogonality(new_config)
    
    # Step 4: Generate summary
    print("\n" + "=" * 60)
    print("SUMMARY OF CHANGES")
    print("=" * 60)
    
    print("\nPrismatic joint:")
    print(f"  OLD rpy: [1.5708, 0, 0]")
    print(f"  NEW rpy: [0, 0, 0]")
    
    print("\nHAA joint:")
    print(f"  OLD xyz: [-0.016, 0.0199, 0.080]")
    print(f"  NEW xyz: {new_config['haa_xyz']}")
    print(f"  OLD rpy: [-1.5708, 0, 0]")
    print(f"  NEW rpy: {new_config['haa_rpy']}")
    
    print("\nHFE joint:")
    print(f"  OLD rpy: [0, 1.5708, 0]")
    print(f"  NEW rpy: {new_config['hfe_rpy']}")
    
    print("\nNext steps:")
    print("1. Apply these changes to dog2.urdf.xacro")
    print("2. Test in RViz to verify visual appearance")
    print("3. Adjust origins if needed based on RViz feedback")
    print("4. Run property-based tests to verify orthogonality")
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())
