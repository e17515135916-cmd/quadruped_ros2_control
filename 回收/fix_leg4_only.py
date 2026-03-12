#!/usr/bin/env python3
"""
Fix Leg 4 by finding and replacing specific parameters
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    lines = f.readlines()

in_leg4 = False
for i, line in enumerate(lines):
    if 'Leg 4: Rear Right' in line:
        in_leg4 = True
    elif in_leg4 and 'SECTION 4' in line:
        break
    elif in_leg4:
        # Fix origin_rpy
        if 'origin_rpy="1.5708 0 -3.1416"' in line:
            lines[i] = line.replace('origin_rpy="1.5708 0 -3.1416"', 'origin_rpy="1.5708 0 0"')
            print(f"✓ Fixed origin_rpy at line {i+1}")
        # Fix hip_joint_rpy
        elif 'hip_joint_rpy="3.1416 0 1.5708"' in line:
            lines[i] = line.replace('hip_joint_rpy="3.1416 0 1.5708"', 'hip_joint_rpy="0 0 0"')
            print(f"✓ Fixed hip_joint_rpy at line {i+1}")
        # Fix hip_joint_xyz
        elif 'hip_joint_xyz="0.0116 0.0199 0.055"' in line:
            lines[i] = line.replace('hip_joint_xyz="0.0116 0.0199 0.055"', 'hip_joint_xyz="-0.016 0.0199 0.080"')
            print(f"✓ Fixed hip_joint_xyz at line {i+1}")
        # Fix knee_joint_xyz
        elif 'knee_joint_xyz="-0.0233 -0.055 -0.0254"' in line:
            lines[i] = line.replace('knee_joint_xyz="-0.0233 -0.055 -0.0254"', 'knee_joint_xyz="-0.0233 -0.055 0.0274"')
            print(f"✓ Fixed knee_joint_xyz at line {i+1}")
        # Add hip_axis if not present
        elif 'foot_xyz=' in line and 'hip_axis=' not in ''.join(lines[max(0,i-15):i+1]):
            lines[i] = line.replace('foot_xyz=', 'thigh_joint_rpy="1.5708 1.5708 0"\n             hip_axis="1 0 0"\n             foot_xyz=')
            print(f"✓ Added thigh_joint_rpy and hip_axis at line {i+1}")

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.writelines(lines)

print("✓ Leg 4 fixed")
