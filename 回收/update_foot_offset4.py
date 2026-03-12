#!/usr/bin/env python3
"""Script to update foot joint offset in dog2.urdf.xacro"""

# Read the file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Replace the offset
old_offset = 'xyz="0 -0.27 -0.13"'
new_offset = 'xyz="0 -0.29 -0.13"'

if old_offset in content:
    content = content.replace(old_offset, new_offset)
    print(f"Replaced '{old_offset}' with '{new_offset}'")
else:
    print(f"Warning: '{old_offset}' not found in file")

# Write back to file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("File updated successfully")
