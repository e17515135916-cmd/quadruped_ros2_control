#!/usr/bin/env python3
"""
Fix the leg macro parameters to add hip_axis and remove old parameters.
"""

from pathlib import Path
import re

def fix_macro_parameters():
    """Fix macro parameter list."""
    
    urdf_path = Path("src/dog2_description/urdf/dog2.urdf.xacro")
    
    with open(urdf_path, 'r') as f:
        content = f.read()
    
    print("Fixing macro parameters...")
    print("=" * 70)
    
    # Find the macro definition
    macro_pattern = r'<xacro:macro name="leg" params="[^"]*">'
    
    match = re.search(macro_pattern, content, re.DOTALL)
    if not match:
        print("❌ Could not find macro definition")
        return False
    
    old_macro = match.group(0)
    print(f"\nOld macro definition found (length: {len(old_macro)} chars)")
    
    # Create new macro definition
    new_macro = '''<xacro:macro name="leg" params="leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz
                                 hip_joint_rpy:='0 0 0'
                                 hip_joint_xyz:='-0.016 0.0199 0.080'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_joint_rpy:='1.5708 1.5708 0'
                                 hip_axis:='1 0 0'">'''
    
    # Replace
    content = content.replace(old_macro, new_macro)
    
    print("\n✓ Macro parameters updated:")
    print("  • Removed: prismatic_inertia_xyz")
    print("  • Removed: thigh_collision_rpy")
    print("  • Removed: foot_xyz")
    print("  • Added: hip_axis (default: '1 0 0')")
    print("  • Changed hip_joint_rpy default: '0 0 1.5708' → '0 0 0'")
    print("  • Added: thigh_joint_rpy (default: '1.5708 1.5708 0')")
    
    # Write back
    with open(urdf_path, 'w') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("✓ File updated successfully!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = fix_macro_parameters()
    exit(0 if success else 1)
