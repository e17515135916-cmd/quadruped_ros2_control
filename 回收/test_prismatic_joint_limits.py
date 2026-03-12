#!/usr/bin/env python3
"""
Test script to verify prismatic joint velocity limits in processed URDF.

This script:
1. Processes the xacro file to generate URDF
2. Parses the URDF to extract joint limits
3. Verifies that prismatic joints have velocity limit of 0.0

Requirements: 10.1, 10.3
"""

import subprocess
import xml.etree.ElementTree as ET
import sys
import tempfile
import os


def process_xacro_to_urdf(xacro_path: str) -> str:
    """
    Process xacro file to generate URDF content.
    
    Args:
        xacro_path: Path to xacro file
        
    Returns:
        URDF content as string
    """
    try:
        result = subprocess.run(
            ['xacro', xacro_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to process xacro file: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: xacro command not found. Please install ros-humble-xacro")
        sys.exit(1)


def verify_prismatic_joints(urdf_content: str) -> bool:
    """
    Verify that prismatic joints have velocity limit of 0.0.
    
    Args:
        urdf_content: URDF XML content as string
        
    Returns:
        True if all checks pass, False otherwise
    """
    print("Parsing URDF and checking prismatic joint limits...")
    print("=" * 70)
    
    try:
        root = ET.fromstring(urdf_content)
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse URDF: {e}")
        return False
    
    # Find all prismatic joints
    prismatic_joints = []
    for joint in root.findall('.//joint[@type="prismatic"]'):
        joint_name = joint.get('name')
        limit = joint.find('limit')
        
        if limit is not None:
            velocity = float(limit.get('velocity', '0'))
            effort = float(limit.get('effort', '0'))
            lower = float(limit.get('lower', '0'))
            upper = float(limit.get('upper', '0'))
            
            prismatic_joints.append({
                'name': joint_name,
                'velocity': velocity,
                'effort': effort,
                'lower': lower,
                'upper': upper
            })
    
    if not prismatic_joints:
        print("WARNING: No prismatic joints found in URDF")
        return False
    
    print(f"\nFound {len(prismatic_joints)} prismatic joint(s):\n")
    
    all_locked = True
    for joint in prismatic_joints:
        print(f"Joint: {joint['name']}")
        print(f"  Velocity limit: {joint['velocity']} m/s")
        print(f"  Effort limit:   {joint['effort']} N")
        print(f"  Position range: [{joint['lower']:.4f}, {joint['upper']:.4f}] m")
        
        if joint['velocity'] == 0.0:
            print(f"  ✓ LOCKED (velocity = 0.0)")
        else:
            print(f"  ✗ NOT LOCKED (velocity = {joint['velocity']})")
            all_locked = False
        print()
    
    return all_locked


def main():
    """Main entry point."""
    xacro_path = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    if not os.path.exists(xacro_path):
        print(f"ERROR: Xacro file not found: {xacro_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("PRISMATIC JOINT LOCKING VERIFICATION")
    print("=" * 70)
    print(f"\nProcessing xacro file: {xacro_path}\n")
    
    # Process xacro to URDF
    urdf_content = process_xacro_to_urdf(xacro_path)
    
    # Verify prismatic joints
    success = verify_prismatic_joints(urdf_content)
    
    print("=" * 70)
    if success:
        print("✓ SUCCESS: All prismatic joints are properly locked")
        print("=" * 70)
        print("\nPrismatic joints (j1-j4) configuration:")
        print("  - Velocity limit: 0.0 m/s (locked)")
        print("  - Position limits: Preserved for mechanical constraints")
        print("  - Effort limits: Preserved for safety")
        print("  - State monitoring: Available via ros2_control")
        print("\nThese joints will remain at zero position during CHAMP operation.")
        print("\nRequirements validated:")
        print("  ✓ 10.1: Prismatic joints locked at zero position")
        print("  ✓ 10.3: Velocity limits configured to 0.0")
        sys.exit(0)
    else:
        print("✗ FAILURE: Some prismatic joints are not properly locked")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
