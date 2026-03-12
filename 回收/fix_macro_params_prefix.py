#!/usr/bin/env python3
"""
Fix the leg macro parameters to include 'prefix' parameter
"""

import re

def fix_macro_params(xacro_file):
    with open(xacro_file, 'r') as f:
        content = f.read()
    
    # Find the macro definition line and add 'prefix' as the first parameter
    # The pattern matches the macro definition across multiple lines
    pattern = r'(<xacro:macro name="leg" params=")leg_num'
    replacement = r'\1prefix leg_num'
    
    content = re.sub(pattern, replacement, content)
    
    with open(xacro_file, 'w') as f:
        f.write(content)
    
    print("✅ Added 'prefix' parameter to leg macro definition")

if __name__ == "__main__":
    fix_macro_params("src/dog2_description/urdf/dog2.urdf.xacro")
