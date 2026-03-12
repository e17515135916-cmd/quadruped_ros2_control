#!/usr/bin/env python3
"""
Apply Prismatic Coordinate System Fix to URDF

This script modifies the dog2.urdf.xacro file to:
1. Remove Prismatic joint RPY rotation (set to "0 0 0")
2. Update HAA, HFE, KFE joint origins to compensate
3. Update ROS 2 Control joint names to CHAMP standard
"""

import re
import sys
from pathlib import Path

def apply_fix(urdf_file):
    """Apply the Prismatic coordinate system fix."""
    
    print(f"Reading {urdf_file}...")
    with open(urdf_file, 'r') as f:
        content = f.read()
    
    # Backup
    backup_file = str(urdf_file) + '.backup_before_fix'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"Created backup: {backup_file}")
    
    # Fix 1: Update Leg 1 (Front Left) instantiation
    print("\nFixing Leg 1 (Front Left)...")
    content = re.sub(
        r'<!-- Leg 1: Front Left -->\s*<xacro:leg prefix="lf".*?haa_axis="0 0 1"/>',
        '''<!-- Leg 1: Front Left -->
  <xacro:leg prefix="lf"
             leg_num="1" 
             origin_xyz="1.1026 -0.80953 0.2649" 
             origin_rpy="0 0 0" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             hip_joint_xyz="-0.016 -0.08 0.0199"
             hip_joint_rpy="0 0 0"
             thigh_joint_rpy="1.5708 0 0"
             haa_axis="0 0 1"/>''',
        content,
        flags=re.DOTALL
    )
    
    # Fix 2: Update Leg 2 (Front Right) instantiation
    print("Fixing Leg 2 (Front Right)...")
    content = re.sub(
        r'<!-- Leg 2: Front Right -->\s*<xacro:leg prefix="rf".*?haa_axis="0 0 1"/>',
        '''<!-- Leg 2: Front Right -->
  <xacro:leg prefix="rf"
             leg_num="2" 
             origin_xyz="1.3491 -0.80953 0.2649" 
             origin_rpy="0 0 0" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             hip_joint_xyz="-0.016 -0.08 0.0199"
             hip_joint_rpy="0 0 0"
             thigh_joint_rpy="1.5708 0 0"
             haa_axis="0 0 1"/>''',
        content,
        flags=re.DOTALL
    )
    
    # Fix 3: Update Leg 3 (Rear Left) instantiation
    print("Fixing Leg 3 (Rear Left)...")
    content = re.sub(
        r'<!-- Leg 3: Rear Left.*?-->\s*<xacro:leg prefix="lh".*?haa_axis="0 0 1"/>',
        '''<!-- Leg 3: Rear Left (with inertia corrections for mirrored geometry) -->
  <xacro:leg prefix="lh"
             leg_num="3" 
             origin_xyz="1.3491 -0.68953 0.2649" 
             origin_rpy="0 0 0" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg3_shin_inertia_xyz}"
             hip_joint_xyz="0.016 -0.08 0.0199"
             hip_joint_rpy="0 0 0"
             knee_joint_xyz="-0.0233 -0.055 0.0274"
             thigh_joint_rpy="1.5708 0 0"
             haa_axis="0 0 1"/>''',
        content,
        flags=re.DOTALL
    )
    
    # Fix 4: Update Leg 4 (Rear Right) instantiation
    print("Fixing Leg 4 (Rear Right)...")
    content = re.sub(
        r'<!-- Leg 4: Rear Right.*?-->\s*<xacro:leg prefix="rh".*?haa_axis="0 0 1"/>',
        '''<!-- Leg 4: Rear Right (with inertia corrections for mirrored geometry) -->
  <xacro:leg prefix="rh"
             leg_num="4" 
             origin_xyz="1.1071 -0.68953 0.2649" 
             origin_rpy="0 0 0" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg4_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg4_shin_inertia_xyz}"
             hip_joint_xyz="-0.016 -0.08 0.0199"
             hip_joint_rpy="0 0 0"
             knee_joint_xyz="-0.0233 -0.055 0.0274"
             thigh_visual_rpy="0 0 0"
             thigh_joint_rpy="1.5708 0 0"
             haa_axis="0 0 1"/>''',
        content,
        flags=re.DOTALL
    )
    
    # Fix 5: Update ROS 2 Control joint names
    print("Fixing ROS 2 Control joint names...")
    
    # Replace j11 -> lf_haa_joint
    content = content.replace('<joint name="j11">', '<joint name="lf_haa_joint">')
    content = content.replace('<joint name="j111">', '<joint name="lf_hfe_joint">')
    content = content.replace('<joint name="j1111">', '<joint name="lf_kfe_joint">')
    
    # Replace j21 -> rf_haa_joint
    content = content.replace('<joint name="j21">', '<joint name="rf_haa_joint">')
    content = content.replace('<joint name="j211">', '<joint name="rf_hfe_joint">')
    content = content.replace('<joint name="j2111">', '<joint name="rf_kfe_joint">')
    
    # Replace j31 -> lh_haa_joint
    content = content.replace('<joint name="j31">', '<joint name="lh_haa_joint">')
    content = content.replace('<joint name="j311">', '<joint name="lh_hfe_joint">')
    content = content.replace('<joint name="j3111">', '<joint name="lh_kfe_joint">')
    
    # Replace j41 -> rh_haa_joint
    content = content.replace('<joint name="j41">', '<joint name="rh_haa_joint">')
    content = content.replace('<joint name="j411">', '<joint name="rh_hfe_joint">')
    content = content.replace('<joint name="j4111">', '<joint name="rh_kfe_joint">')
    
    # Write modified content
    print(f"\nWriting modified file to {urdf_file}...")
    with open(urdf_file, 'w') as f:
        f.write(content)
    
    print("\n✓ Fix applied successfully!")
    print("\nSummary of changes:")
    print("1. Prismatic joint RPY: 1.5708 0 0 → 0 0 0")
    print("2. HAA joint xyz: -0.016 0.0199 0.080 → -0.016 -0.08 0.0199")
    print("3. HAA joint rpy: -1.5708 0 0 → 0 0 0")
    print("4. HFE joint rpy: 0 1.5708 0 → 1.5708 0 0")
    print("5. ROS 2 Control: j11→lf_haa_joint, j111→lf_hfe_joint, etc.")
    
    return 0

def main():
    urdf_file = Path('src/dog2_description/urdf/dog2.urdf.xacro')
    
    if not urdf_file.exists():
        print(f"Error: {urdf_file} not found!")
        return 1
    
    return apply_fix(urdf_file)

if __name__ == "__main__":
    sys.exit(main())
