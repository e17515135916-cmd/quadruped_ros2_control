#!/usr/bin/env python3
"""
Post-process generated URDF to fix rear legs' thigh joint Z coordinates
This is a workaround for xacro's coordinate transformation issue
"""

import sys
import re

def fix_urdf(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Pattern to match j311 and j411 thigh joints with negative Z
    # We need to change -0.0254 to 0.0274 for rear legs
    
    # Split into lines for easier processing
    lines = content.split('\n')
    
    in_j311 = False
    in_j411 = False
    
    for i, line in enumerate(lines):
        # Detect j311 joint
        if 'joint name="j311"' in line:
            in_j311 = True
            in_j411 = False
        # Detect j411 joint
        elif 'joint name="j411"' in line:
            in_j411 = True
            in_j311 = False
        # Detect end of joint
        elif '</joint>' in line:
            in_j311 = False
            in_j411 = False
        
        # Fix origin line if we're in j311 or j411
        if (in_j311 or in_j411) and '<origin' in line and 'xyz=' in line:
            # Replace -0.0254 with 0.0274
            if '-0.0254' in line or '-0.0274' in line:
                lines[i] = re.sub(r'-0\.02[57]4', '0.0274', line)
                joint_name = 'j311' if in_j311 else 'j411'
                print(f"  Fixed {joint_name}: Z coordinate → 0.0274")
    
    content = '\n'.join(lines)
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print("✓ URDF post-processing complete")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 post_process_urdf.py <input_urdf> <output_urdf>")
        sys.exit(1)
    
    fix_urdf(sys.argv[1], sys.argv[2])
