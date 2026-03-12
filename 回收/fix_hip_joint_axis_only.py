#!/usr/bin/env python3
"""
Fix only the hip joint axis (line 174) to use ${hip_axis}
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    lines = f.readlines()

# Find hip joint and replace its axis
in_hip_joint = False
for i, line in enumerate(lines):
    if 'Hip joint (j${leg_num}1)' in line:
        in_hip_joint = True
    elif in_hip_joint and '<axis xyz="-1 0 0"/>' in line:
        lines[i] = line.replace('<axis xyz="-1 0 0"/>', '<axis xyz="${hip_axis}"/>')
        print(f"✓ Fixed hip joint axis at line {i+1}")
        break

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.writelines(lines)

print("✓ File updated")
