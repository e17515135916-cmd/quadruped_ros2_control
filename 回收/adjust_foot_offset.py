#!/usr/bin/env python3
"""
Adjust foot joint offset in dog2.urdf.xacro
"""

import re

# Read the URDF file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Current offset: xyz="0 -0.27 -0.13"
# New offset: xyz="0 -0.31 -0.13" (move down more)
old_pattern = r'<origin rpy="0 0 0" xyz="0 -0\.27 -0\.13"/>'
new_pattern = '<origin rpy="0 0 0" xyz="0 -0.31 -0.13"/>'

if old_pattern in content or re.search(old_pattern, content):
    content = re.sub(old_pattern, new_pattern, content)
    print("✓ Updated foot joint offset from -0.27 to -0.31")
else:
    print("✗ Could not find the exact pattern to replace")
    print("Searching for similar patterns...")
    # Try a more flexible pattern
    pattern = r'<origin rpy="0 0 0" xyz="0 -0\.\d+ -0\.13"/>'
    matches = re.findall(pattern, content)
    if matches:
        print(f"Found matches: {matches}")
        # Replace the first match (should be the foot joint)
        content = re.sub(pattern, new_pattern, content, count=1)
        print("✓ Updated foot joint offset")

# Write back
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("Done!")
