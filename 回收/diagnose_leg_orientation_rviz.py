#!/usr/bin/env python3
"""
Diagnose leg orientation in RViz by analyzing the generated URDF.
This script checks if all legs point downward when joint angles are zero.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess

def generate_urdf():
    """Generate URDF from xacro."""
    print("Generating URDF from xacro...")
    result = subprocess.run(
        ["xacro", "src/dog2_description/urdf/dog2.urdf.xacro"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error generating URDF: {result.stderr}")
        return None
    
    return result.stdout

def analyze_leg_configuration(urdf_content):
    """Analyze leg configuration from URDF."""
    
    root = ET.fromstring(urdf_content)
    
    print("\n" + "=" * 70)
    print("LEG ORIENTATION ANALYSIS")
    print("=" * 70)
    
    results = {}
    
    for leg_num in [1, 2, 3, 4]:
        print(f"\n{'='*70}")
        print(f"Leg {leg_num}:")
        print(f"{'='*70}")
        
        leg_data = {}
        
        # Check hip joint
        hip_joint = root.find(f".//joint[@name='j{leg_num}1']")
        if hip_joint is not None:
            axis = hip_joint.find("axis")
            origin = hip_joint.find("origin")
            
            if axis is not None:
                axis_xyz = axis.get("xyz", "")
                leg_data['hip_axis'] = axis_xyz
                print(f"  Hip joint axis: {axis_xyz}")
                
                # Check if X-axis rotation
                if "1 0 0" in axis_xyz or "-1 0 0" in axis_xyz:
                    print(f"    ✓ X-axis rotation (dog-style)")
                    leg_data['axis_correct'] = True
                else:
                    print(f"    ❌ Not X-axis rotation")
                    leg_data['axis_correct'] = False
            
            if origin is not None:
                xyz = origin.get("xyz", "")
                rpy = origin.get("rpy", "0 0 0")
                leg_data['hip_origin_xyz'] = xyz
                leg_data['hip_origin_rpy'] = rpy
                
                print(f"  Hip joint origin XYZ: {xyz}")
                print(f"  Hip joint origin RPY: {rpy}")
                
                # Check Z coordinate
                try:
                    z_coord = float(xyz.split()[2])
                    if abs(z_coord - 0.080) < 0.001:
                        print(f"    ✓ Z = {z_coord:.3f}m (cantilever height)")
                        leg_data['z_correct'] = True
                    else:
                        print(f"    ⚠ Z = {z_coord:.3f}m (expected 0.080m)")
                        leg_data['z_correct'] = False
                except:
                    leg_data['z_correct'] = False
        
        # Check prismatic joint origin
        prismatic_joint = root.find(f".//joint[@name='j{leg_num}']")
        if prismatic_joint is not None:
            origin = prismatic_joint.find("origin")
            if origin is not None:
                rpy = origin.get("rpy", "0 0 0")
                leg_data['prismatic_rpy'] = rpy
                print(f"  Prismatic joint RPY: {rpy}")
                
                # Check for spider-style 180° Z rotation
                if "-3.1416" in rpy or (rpy.split()[2] != "0" and "3.1416" in rpy.split()[2]):
                    print(f"    ❌ Has 180° Z rotation (spider-style)")
                    leg_data['prismatic_correct'] = False
                else:
                    print(f"    ✓ No 180° Z rotation")
                    leg_data['prismatic_correct'] = True
        
        results[leg_num] = leg_data
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    all_correct = True
    for leg_num, data in results.items():
        status = "✓" if data.get('axis_correct') and data.get('z_correct') and data.get('prismatic_correct') else "❌"
        print(f"  Leg {leg_num}: {status}")
        if not (data.get('axis_correct') and data.get('z_correct') and data.get('prismatic_correct')):
            all_correct = False
    
    print(f"\n{'='*70}")
    if all_correct:
        print("✅ ALL LEGS CONFIGURED CORRECTLY FOR DOG-STYLE")
        print("   All four legs should point DOWNWARD in RViz")
    else:
        print("❌ SOME LEGS HAVE INCORRECT CONFIGURATION")
        print("   Some legs may point in wrong direction")
    print(f"{'='*70}\n")
    
    return all_correct

if __name__ == "__main__":
    urdf_content = generate_urdf()
    if urdf_content:
        analyze_leg_configuration(urdf_content)
