#!/usr/bin/env python3
"""
Update ROS 2 Control configuration to add effort interfaces to all joints.
This script adds effort command and state interfaces to all joints in the ros2_control section.
"""

import re
import sys

def update_ros2_control_section(content):
    """
    Add effort interfaces to all joints in the ros2_control section.
    """
    # Pattern to match joint definitions that are missing effort interfaces
    # Match joint blocks that have position and velocity but not effort
    pattern = r'(<joint name="[^"]+">)\s*(<command_interface name="position"/>)\s*(<state_interface name="position"/>)\s*(<state_interface name="velocity"/>)\s*(</joint>)'
    
    # Replacement adds effort interfaces
    replacement = r'\1\n      \2\n      <command_interface name="effort"/>\n      \3\n      \4\n      <state_interface name="effort"/>\n    \5'
    
    updated_content = re.sub(pattern, replacement, content)
    
    return updated_content

def main():
    urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    # Read the file
    with open(urdf_file, 'r') as f:
        content = f.read()
    
    # Update the ros2_control section
    updated_content = update_ros2_control_section(content)
    
    # Write back
    with open(urdf_file, 'w') as f:
        f.write(updated_content)
    
    print("✓ Updated ROS 2 Control configuration")
    print("  - Added effort command interface to all joints")
    print("  - Added effort state interface to all joints")
    print("  - Prismatic joints (j1, j2, j3, j4) now have position, velocity, effort interfaces")
    print("  - HAA joints (lf_haa_joint, rf_haa_joint, lh_haa_joint, rh_haa_joint) now have position, velocity, effort interfaces")
    print("  - HFE joints (lf_hfe_joint, rf_hfe_joint, lh_hfe_joint, rh_hfe_joint) now have position, velocity, effort interfaces")
    print("  - KFE joints (lf_kfe_joint, rf_kfe_joint, lh_kfe_joint, rh_kfe_joint) now have position, velocity, effort interfaces")

if __name__ == "__main__":
    main()
