#!/usr/bin/env python3
"""
Script to add hip_axis parameter to the leg macro definition

This ensures the macro accepts the hip_axis parameter that is being passed
in the leg instantiations.
"""

import re


def add_hip_axis_to_macro(file_path):
    """Add hip_axis parameter to leg macro if not present"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the macro definition line
    macro_pattern = r'(<xacro:macro name="leg" params="[^"]*foot_xyz[^"]*")'
    
    # Check if hip_axis is already in the params
    if 'hip_axis' in content.split('<xacro:macro name="leg"')[1].split('>')[0]:
        print("✓ hip_axis parameter already exists in macro definition")
        return True
    
    # Add hip_axis parameter before the closing quote
    def add_param(match):
        macro_def = match.group(1)
        # Add hip_axis parameter before the closing quote
        if macro_def.endswith('"'):
            return macro_def[:-1] + "\n                                 hip_axis:='1 0 0'\"" 
        return macro_def
    
    new_content = re.sub(macro_pattern, add_param, content)
    
    if new_content != content:
        # Create backup
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
        
        # Write modified content
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("✓ Added hip_axis parameter to macro definition")
        return True
    else:
        print("✗ Failed to modify macro definition")
        return False


if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else "src/dog2_description/urdf/dog2.urdf.xacro"
    add_hip_axis_to_macro(file_path)
