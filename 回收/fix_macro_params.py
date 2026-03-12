#!/usr/bin/env python3
"""
Fix the macro parameters to include haa_axis
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Find and replace the macro definition
old_macro = '''  <xacro:macro name="leg" params="prefix leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz
                                 prismatic_inertia_xyz:='-0.0159999123716776 0.000737036465389251 0.0261570925915838'
                                 hip_joint_rpy:='0 0 1.5708'
                                 hip_joint_xyz:='-0.016 0.0199 0.055'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'
                                 foot_xyz:='-0.034 -0.299478 -0.12'">'''

new_macro = '''  <xacro:macro name="leg" params="prefix leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz
                                 prismatic_inertia_xyz:='-0.0159999123716776 0.000737036465389251 0.0261570925915838'
                                 hip_joint_rpy:='0 0 1.5708'
                                 hip_joint_xyz:='-0.016 0.0199 0.055'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'
                                 foot_xyz:='-0.034 -0.299478 -0.12'
                                 haa_axis:='0 0 1'">'''

if old_macro in content:
    content = content.replace(old_macro, new_macro)
    print("Successfully added haa_axis parameter to macro")
else:
    print("Warning: Could not find exact macro definition")
    print("Trying alternative approach...")
    
    # Try to find the macro line and add the parameter
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'foot_xyz:=' in line and 'xacro:macro name="leg"' in '\n'.join(lines[max(0,i-10):i+1]):
            # Found the line with foot_xyz, add haa_axis after it
            if not 'haa_axis' in line:
                lines[i] = line.rstrip('>') + '\n                                 haa_axis:=\'0 0 1\'>'
                print(f"Added haa_axis parameter at line {i}")
                break
    content = '\n'.join(lines)

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("Done!")
