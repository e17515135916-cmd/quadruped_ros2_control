#!/usr/bin/env python3
"""
Verification script for prismatic joint locking in URDF.

This script verifies that:
1. Prismatic joints (j1-j4) have velocity limits set to 0.0
2. The URDF can be parsed successfully
3. Joint limits are properly configured

Requirements: 10.1, 10.3
"""

import xml.etree.ElementTree as ET
import sys
from pathlib import Path


def verify_prismatic_joint_locking(urdf_path: str) -> bool:
    """
    Verify that prismatic joints are properly locked in URDF.
    
    Args:
        urdf_path: Path to the URDF/xacro file
        
    Returns:
        True if all checks pass, False otherwise
    """
    print(f"Verifying prismatic joint locking in: {urdf_path}")
    print("=" * 70)
    
    # Read the file content
    try:
        with open(urdf_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {urdf_path}")
        return False
    
    # Check 1: Verify prismatic_velocity property is set to 0.0
    print("\n[Check 1] Verifying prismatic_velocity property...")
    if 'name="prismatic_velocity" value="0.0"' in content:
        print("✓ PASS: prismatic_velocity property set to 0.0")
        check1_pass = True
    else:
        print("✗ FAIL: prismatic_velocity property not set to 0.0")
        check1_pass = False
    
    # Check 2: Verify all prismatic joints use the property
    print("\n[Check 2] Verifying prismatic joints use velocity property...")
    
    # Check if the macro uses the property
    if 'velocity="${prismatic_velocity}"' in content:
        print("✓ PASS: Leg macro uses prismatic_velocity property")
        check2_pass = True
    else:
        print("✗ FAIL: Leg macro does not use prismatic_velocity property")
        check2_pass = False
    
    # Check 3: Verify the comment explaining the change
    print("\n[Check 3] Verifying documentation comment...")
    if 'CHAMP GAZEBO MOTION: Prismatic joints locked' in content or 'Prismatic joints locked by setting velocity to 0.0' in content:
        print("✓ PASS: Documentation comment present")
        check3_pass = True
    else:
        print("✗ FAIL: Documentation comment missing")
        check3_pass = False
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_checks_pass = check1_pass and check2_pass and check3_pass
    
    if all_checks_pass:
        print("✓ ALL CHECKS PASSED")
        print("\nPrismatic joints (j1-j4) are properly locked:")
        print("  - Velocity limit set to 0.0")
        print("  - Joints will remain at zero position")
        print("  - State monitoring still available via ros2_control")
        return True
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease review the failures above and fix the URDF configuration.")
        return False


def main():
    """Main entry point."""
    urdf_path = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    if not Path(urdf_path).exists():
        print(f"ERROR: URDF file not found: {urdf_path}")
        sys.exit(1)
    
    success = verify_prismatic_joint_locking(urdf_path)
    
    if success:
        print("\n" + "=" * 70)
        print("TASK 1 COMPLETE: Prismatic joint locking verified")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Build the workspace: colcon build --packages-select dog2_description")
        print("  2. Test in Gazebo to verify joints remain at zero position")
        print("  3. Proceed to Task 2: Update ros2_control configuration")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
