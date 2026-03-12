#!/usr/bin/env python3
"""
Check the actual content of the xacro file for Leg 3 and 4
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Find Leg 3 section
leg3_start = content.find('Leg 3: Rear Left')
leg3_section = ""
if leg3_start != -1:
    leg3_section = content[leg3_start:leg3_start+500]
    print("=== Leg 3 Section ===")
    print(leg3_section)
    print()

# Find Leg 4 section  
leg4_start = content.find('Leg 4: Rear Right')
leg4_section = ""
if leg4_start != -1:
    leg4_section = content[leg4_start:leg4_start+500]
    print("=== Leg 4 Section ===")
    print(leg4_section)
    print()

# Check for origin_rpy in these sections
if leg3_section:
    if 'origin_rpy="1.5708 0 0"' in leg3_section:
        print("✓ Leg 3 has correct origin_rpy: 1.5708 0 0")
    elif 'origin_rpy="1.5708 0 -3.1416"' in leg3_section:
        print("✗ Leg 3 has WRONG origin_rpy: 1.5708 0 -3.1416")
    else:
        print("? Leg 3 origin_rpy not found in expected format")

if leg4_section:
    if 'origin_rpy="1.5708 0 0"' in leg4_section:
        print("✓ Leg 4 has correct origin_rpy: 1.5708 0 0")
    elif 'origin_rpy="1.5708 0 -3.1416"' in leg4_section:
        print("✗ Leg 4 has WRONG origin_rpy: 1.5708 0 -3.1416")
    else:
        print("? Leg 4 origin_rpy not found in expected format")
