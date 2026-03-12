#!/usr/bin/env python3
"""
Verify that all four legs point downward in the dog-style configuration.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def verify_leg_configuration():
    """Verify all legs are configured to point downward."""
    
    urdf_path = Path("/tmp/dog2_test.urdf")
    
    if not urdf_path.exists():
        print("❌ URDF file not found. Run xacro first.")
        return False
    
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    
    print("=" * 70)
    print("DOG-STYLE LEG ORIENTATION VERIFICATION")
    print("=" * 70)
    
    all_correct = True
    
    for leg_num in [1, 2, 3, 4]:
        print(f"\n{'='*70}")
        print(f"Leg {leg_num} Configuration:")
        print(f"{'='*70}")
        
        # Check prismatic joint (j{leg_num})
        prismatic_joint = root.find(f".//joint[@name='j{leg_num}']")
        if prismatic_joint is not None:
            origin = prismatic_joint.find("origin")
            if origin is not None:
                rpy = origin.get("rpy", "0 0 0")
                print(f"  Prismatic joint (j{leg_num}) origin RPY: {rpy}")
                
                # Check if it has the old spider-style rotation
                if "-3.1416" in rpy or "3.1416" in rpy.split()[2]:
                    print(f"    ❌ WRONG: Has 180° Z rotation (spider-style)")
                    all_correct = False
                else:
                    print(f"    ✓ Correct: No 180° Z rotation")
        
        # Check hip joint (j{leg_num}1)
        hip_joint = root.find(f".//joint[@name='j{leg_num}1']")
        if hip_joint is not None:
            # Check axis
            axis = hip_joint.find("axis")
            if axis is not None:
                axis_xyz = axis.get("xyz", "")
                print(f"  Hip joint (j{leg_num}1) axis: {axis_xyz}")
                
                if "1 0 0" in axis_xyz or "-1 0 0" in axis_xyz:
                    print(f"    ✓ Correct: X-axis rotation (dog-style)")
                elif "0 0" in axis_xyz and ("1" in axis_xyz or "-1" in axis_xyz):
                    print(f"    ❌ WRONG: Z-axis rotation (spider-style)")
                    all_correct = False
            
            # Check origin
            origin = hip_joint.find("origin")
            if origin is not None:
                xyz = origin.get("xyz", "")
                rpy = origin.get("rpy", "0 0 0")
                print(f"  Hip joint (j{leg_num}1) origin XYZ: {xyz}")
                print(f"  Hip joint (j{leg_num}1) origin RPY: {rpy}")
                
                # Check Z coordinate (should be ~0.080 for cantilever)
                z_coord = float(xyz.split()[2])
                if abs(z_coord - 0.080) < 0.001:
                    print(f"    ✓ Correct: Z = {z_coord:.3f}m (cantilever height)")
                elif abs(z_coord - 0.055) < 0.001:
                    print(f"    ❌ WRONG: Z = {z_coord:.3f}m (old height, no cantilever)")
                    all_correct = False
                
                # Check for old spider-style RPY rotations
                if "1.5708" in rpy and rpy.count("1.5708") > 1:
                    print(f"    ⚠ Warning: Multiple 90° rotations detected")
    
    print(f"\n{'='*70}")
    if all_correct:
        print("✅ SUCCESS: All four legs are configured for dog-style (downward)")
        print("='*70}")
        print("\nAll legs should now point DOWNWARD when joint angles are zero.")
        print("Launch RViz to verify visually: ./view_robot_in_rviz.sh")
    else:
        print("❌ FAILURE: Some legs still have spider-style configuration")
        print("=" * 70)
        print("\nSome legs may still point outward instead of downward.")
    
    return all_correct

if __name__ == "__main__":
    success = verify_leg_configuration()
    exit(0 if success else 1)
