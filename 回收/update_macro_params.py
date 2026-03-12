#!/usr/bin/env python3
"""
Update leg macro parameters to include hip_axis and thigh_joint_rpy
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    lines = f.readlines()

# Find and update macro definition
for i, line in enumerate(lines):
    if '<xacro:macro name="leg"' in line:
        # Replace lines 100-108 with updated parameters
        new_params = '''  <xacro:macro name="leg" params="leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz
                                 prismatic_inertia_xyz:='-0.0159999123716776 0.000737036465389251 0.0261570925915838'
                                 hip_joint_rpy:='0 0 0'
                                 hip_joint_xyz:='-0.016 0.0199 0.080'
                                 knee_joint_xyz:='-0.0233 -0.0550.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'
                                 thigh_joint_rpy:='1.5708 1.5708 0'
                                 hip_axis:='1 0 0'
                                 foot_xyz:='-0.034 -0.299478 -0.12'">
'''
        # Find the end of params (line with ">")
        end_line = i
        for j in range(i, min(i+15, len(lines))):
            if '>"' in lines[j] or '">' in lines[j]:
                end_line = j
                break
        
        # Replace lines
        lines[i:end_line+1] = [new_params]
        print(f"✓ Updated macro parameters (lines {i+1} to {end_line+1})")
        break

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.writelines(lines)

print("✓ File updated")
