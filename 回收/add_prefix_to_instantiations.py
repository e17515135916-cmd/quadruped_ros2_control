#!/usr/bin/env python3
"""
Add prefix parameter to all leg macro instantiations
"""

import re

def add_prefix_to_instantiations(xacro_file):
    with open(xacro_file, 'r') as f:
        content = f.read()
    
    # Define the mapping of leg numbers to prefixes
    leg_prefixes = {
        '1': 'lf',  # Front Left
        '2': 'rf',  # Front Right
        '3': 'lh',  # Rear Left (hind)
        '4': 'rh',  # Rear Right (hind)
    }
    
    # For each leg, add the prefix parameter
    for leg_num, prefix in leg_prefixes.items():
        # Pattern to match: <xacro:leg leg_num="X"
        # Replace with: <xacro:leg prefix="XX" leg_num="X"
        pattern = rf'(<xacro:leg )leg_num="{leg_num}"'
        replacement = rf'\1prefix="{prefix}" leg_num="{leg_num}"'
        content = re.sub(pattern, replacement, content)
        print(f"✅ Added prefix='{prefix}' to leg {leg_num}")
    
    with open(xacro_file, 'w') as f:
        f.write(content)
    
    print("\n✅ All leg instantiations updated with prefix parameter")

if __name__ == "__main__":
    add_prefix_to_instantiations("src/dog2_description/urdf/dog2.urdf.xacro")
