#!/usr/bin/env python3
"""
Clean up leg instantiations by removing old parameters.
"""

from pathlib import Path
import re

def clean_leg_instantiations():
    """Remove old parameters from leg instantiations."""
    
    urdf_path = Path("src/dog2_description/urdf/dog2.urdf.xacro")
    
    with open(urdf_path, 'r') as f:
        lines = f.readlines()
    
    print("Cleaning leg instantiations...")
    print("=" * 70)
    
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        # Skip lines with old parameters
        if any(param in line for param in ['prismatic_inertia_xyz=', 'foot_xyz=', 'thigh_collision_rpy=']):
            print(f"  ✗ Removing: {line.strip()[:60]}...")
            removed_count += 1
            continue
        cleaned_lines.append(line)
    
    # Write back
    with open(urdf_path, 'w') as f:
        f.writelines(cleaned_lines)
    
    print(f"\n✓ Removed {removed_count} lines with old parameters")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = clean_leg_instantiations()
    exit(0 if success else 1)
