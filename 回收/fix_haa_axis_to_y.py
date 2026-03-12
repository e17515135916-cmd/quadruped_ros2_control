#!/usr/bin/env python3
"""
Fix HAA joint axis to Y-axis (0 1 0) for CHAMP compliance

CHAMP standard:
- HAA (Hip Abduction/Adduction): Y-axis rotation
- HFE (Hip Flexion/Extension): X-axis rotation  
- KFE (Knee Flexion/Extension): X-axis rotation
"""

import re

def fix_haa_axis(xacro_file):
    with open(xacro_file, 'r') as f:
        content = f.read()
    
    # Find the HAA joint definition and change axis from "-1 0 0" to "0 1 0"
    # Pattern: <axis xyz="-1 0 0"/> within the HAA joint definition
    
    # First, let's find the HAA joint section
    pattern = r'(<joint name="\$\{prefix\}_haa_joint"[^>]*>.*?<axis xyz=")(-1 0 0)(")'
    replacement = r'\g<1>0 1 0\g<3>'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also update the comment
    content = content.replace(
        'Changed rotation axis to z-axis for CHAMP compliance',
        'Changed rotation axis to Y-axis for CHAMP compliance'
    )
    
    with open(xacro_file, 'w') as f:
        f.write(content)
    
    print("✅ Fixed HAA joint axis to Y-axis (0 1 0)")
    print("   CHAMP standard: HAA=Y-axis, HFE=X-axis, KFE=X-axis")

if __name__ == "__main__":
    fix_haa_axis("src/dog2_description/urdf/dog2.urdf.xacro")
