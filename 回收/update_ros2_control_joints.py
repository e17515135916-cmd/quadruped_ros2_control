#!/usr/bin/env python3
"""
Update ROS 2 Control joint names to CHAMP-compliant names
"""

import re

# Read the file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Define the joint name mappings
joint_mappings = {
    'j11': 'lf_haa_joint',
    'j111': 'lf_hfe_joint',
    'j1111': 'lf_kfe_joint',
    'j21': 'rf_haa_joint',
    'j211': 'rf_hfe_joint',
    'j2111': 'rf_kfe_joint',
    'j31': 'lh_haa_joint',
    'j311': 'lh_hfe_joint',
    'j3111': 'lh_kfe_joint',
    'j41': 'rh_haa_joint',
    'j411': 'rh_hfe_joint',
    'j4111': 'rh_kfe_joint',
}

# Find the ros2_control section
ros2_control_start = content.find('<ros2_control name="GazeboSystem"')
ros2_control_end = content.find('</ros2_control>', ros2_control_start) + len('</ros2_control>')

if ros2_control_start == -1 or ros2_control_end == -1:
    print("Error: Could not find ros2_control section")
    exit(1)

# Extract the ros2_control section
ros2_control_section = content[ros2_control_start:ros2_control_end]

# Replace joint names in the ros2_control section
# Sort by length (longest first) to avoid partial replacements
for old_name in sorted(joint_mappings.keys(), key=len, reverse=True):
    new_name = joint_mappings[old_name]
    # Replace in joint name attributes
    ros2_control_section = ros2_control_section.replace(f'name="{old_name}"', f'name="{new_name}"')

# Update comment labels
ros2_control_section = ros2_control_section.replace('<!-- Leg 1 Joints -->', '<!-- Leg 1 Joints (Front Left) -->')
ros2_control_section = ros2_control_section.replace('<!-- Leg 2 Joints -->', '<!-- Leg 2 Joints (Front Right) -->')
ros2_control_section = ros2_control_section.replace('<!-- Leg 3 Joints -->', '<!-- Leg 3 Joints (Rear Left) -->')
ros2_control_section = ros2_control_section.replace('<!-- Leg 4 Joints -->', '<!-- Leg 4 Joints (Rear Right) -->')

# Reconstruct the file
new_content = content[:ros2_control_start] + ros2_control_section + content[ros2_control_end:]

# Write the updated content
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(new_content)

print("Successfully updated ROS 2 Control joint names")
print("\nUpdated mappings:")
for old, new in sorted(joint_mappings.items()):
    print(f"  {old} -> {new}")
