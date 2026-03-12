#!/usr/bin/env python3
"""
Diagnose leg directions by checking the URDF joint configurations
"""

import xml.etree.ElementTree as ET

# Parse the generated URDF
tree = ET.parse('/tmp/current_dog2.urdf')
root = tree.getroot()

print("\n" + "="*70)
print("LEG DIRECTION DIAGNOSIS")
print("="*70)

for leg_num in [1, 2, 3, 4]:
    print(f"\n--- Leg {leg_num} ---")
    
    # Find j{leg_num}1 (hip joint)
    hip_joint_name = f"j{leg_num}1"
    for joint in root.findall(".//joint[@name='{}']".format(hip_joint_name)):
        origin = joint.find('origin')
        axis = joint.find('axis')
        if origin is not None:
            rpy = origin.get('rpy', '0 0 0')
            xyz = origin.get('xyz', '0 0 0')
            print(f"  Hip joint ({hip_joint_name}):")
            print(f"    Origin XYZ: {xyz}")
            print(f"    Origin RPY: {rpy}")
        if axis is not None:
            axis_xyz = axis.get('xyz', '0 0 0')
            print(f"    Axis: {axis_xyz}")
    
    # Find j{leg_num}11 (thigh joint - HFE)
    thigh_joint_name = f"j{leg_num}11"
    for joint in root.findall(".//joint[@name='{}']".format(thigh_joint_name)):
        origin = joint.find('origin')
        axis = joint.find('axis')
        if origin is not None:
            rpy = origin.get('rpy', '0 0 0')
            xyz = origin.get('xyz', '0 0 0')
            print(f"  Thigh joint ({thigh_joint_name}):")
            print(f"    Origin XYZ: {xyz}")
            print(f"    Origin RPY: {rpy}")
        if axis is not None:
            axis_xyz = axis.get('xyz', '0 0 0')
            print(f"    Axis: {axis_xyz}")

print("\n" + "="*70)
print("ANALYSIS:")
print("="*70)
print("For legs to point downward at zero angles:")
print("- Hip joint (j*1) should rotate about X-axis (1 0 0 or -1 0 0)")
print("- Thigh joint (j*11) origin Z should be POSITIVE for downward")
print("- All legs should have consistent configuration")
print("="*70 + "\n")
