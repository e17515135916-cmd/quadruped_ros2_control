#!/usr/bin/env python3
"""
Fix rear leg orientation to make all four legs point downward.

The problem: Rear legs (3 & 4) have different hip_joint_xyz values that cause
the coordinate system to be flipped compared to front legs.

Solution: Make rear legs use the same hip_joint_xyz as front legs, but with
appropriate sign changes for left/right symmetry.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def fix_rear_leg_orientation():
    """Fix rear leg orientation in URDF."""
    
    urdf_path = Path("src/dog2_description/urdf/dog2.urdf.xacro")
    
    # Read the file
    with open(urdf_path, 'r') as f:
        content = f.read()
    
    print("Current rear leg configurations:")
    print("=" * 60)
    
    # Show current Leg 3 config
    if 'leg_num="3"' in content:
        leg3_start = content.find('<!-- Leg 3:')
        leg3_end = content.find('<!-- Leg 4:', leg3_start)
        leg3_section = content[leg3_start:leg3_end]
        print("\nLeg 3 (Rear Left):")
        if 'hip_joint_xyz="0.016' in leg3_section:
            print("  hip_joint_xyz: 0.016 0.0199 0.080 ❌ (WRONG - should be negative X)")
        if 'hip_axis="1 0 0"' in leg3_section:
            print("  hip_axis: 1 0 0 ✓")
    
    # Show current Leg 4 config
    if 'leg_num="4"' in content:
        leg4_start = content.find('<!-- Leg 4:')
        leg4_end = content.find('<!-- ============================================ -->', leg4_start)
        leg4_section = content[leg4_start:leg4_end]
        print("\nLeg 4 (Rear Right):")
        if 'hip_joint_xyz="-0.016' in leg4_section:
            print("  hip_joint_xyz: -0.016 0.0199 0.080 ✓ (Correct)")
        if 'hip_axis="1 0 0"' in leg4_section:
            print("  hip_axis: 1 0 0 ✓")
    
    print("\n" + "=" * 60)
    print("\nFIX STRATEGY:")
    print("=" * 60)
    print("Front legs (1 & 2) are correct - they point downward")
    print("Rear legs (3 & 4) need to match front leg coordinate system")
    print()
    print("Changes needed:")
    print("  Leg 3: hip_joint_xyz from '0.016' to '-0.016' (flip X sign)")
    print("  Leg 4: Already correct at '-0.016'")
    print()
    
    # Apply fix for Leg 3
    # Find and replace Leg 3's hip_joint_xyz
    old_leg3_line = '             hip_joint_xyz="0.016 0.0199 0.080"'
    new_leg3_line = '             hip_joint_xyz="-0.016 0.0199 0.080"'
    
    if old_leg3_line in content:
        content = content.replace(old_leg3_line, new_leg3_line)
        print("✓ Fixed Leg 3 hip_joint_xyz: 0.016 → -0.016")
    else:
        print("⚠ Could not find Leg 3 hip_joint_xyz to fix")
        return False
    
    # Write back
    with open(urdf_path, 'w') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✓ URDF file updated successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: ./view_robot_in_rviz.sh")
    print("2. Verify all four legs point downward")
    print("3. Use Joint State Publisher to test joint motion")
    
    return True

if __name__ == "__main__":
    success = fix_rear_leg_orientation()
    exit(0 if success else 1)
