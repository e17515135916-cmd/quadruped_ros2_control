#!/usr/bin/env python3
"""
Manually fix the Z coordinate of rear legs' thigh joints in URDF
"""

with open('/tmp/newest.urdf', 'r') as f:
    content = f.read()

# Fix j311 (Leg 3 thigh joint)
content = content.replace(
    '<origin rpy="0 1.5708 0" xyz="-0.0233 -0.055 -0.0254"/>',
    '<origin rpy="0 1.5708 0" xyz="-0.0233 -0.055 0.0274"/>',
    1  # Only replace first occurrence (j311)
)

# Fix j411 (Leg 4 thigh joint) - need to find the second occurrence
lines = content.split('\n')
j411_found = False
for i, line in enumerate(lines):
    if 'joint name="j411"' in line:
        j411_found = True
    if j411_found and '<origin rpy="0 1.5708 0" xyz="-0.0233 -0.055 -0.0254"/>' in line:
        lines[i] = line.replace('-0.0254', '0.0274')
        break

content = '\n'.join(lines)

with open('/tmp/manual_fixed.urdf', 'w') as f:
    f.write(content)

print("✓ Fixed rear legs' Z coordinates")
print("  j311: -0.0254 → 0.0274")
print("  j411: -0.0254 → 0.0274")
