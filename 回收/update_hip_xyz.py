#!/usr/bin/env python3
"""Update hip_xyz values from 0.055 to 0.080"""

# Read the file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Replace all occurrences of hip_xyz with 0.055 to 0.080
content = content.replace("hip_xyz:='-0.016 0.0199 0.055'", "hip_xyz:='-0.016 0.0199 0.080'")
content = content.replace('hip_xyz="0.016 0.0199 0.055"', 'hip_xyz="0.016 0.0199 0.080"')
content = content.replace('hip_xyz="0.0116 0.0199 0.055"', 'hip_xyz="0.0116 0.0199 0.080"')
content = content.replace('hip_xyz="-0.016 0.0199 0.055"', 'hip_xyz="-0.016 0.0199 0.080"')

# Write back
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("Updated all hip_xyz values from 0.055 to 0.080")
