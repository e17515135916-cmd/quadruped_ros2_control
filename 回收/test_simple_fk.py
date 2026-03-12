#!/usr/bin/env python3
"""
Simple test of forward kinematics
"""

import sys
import numpy as np
from pathlib import Path

# Add the dog2_kinematics module to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dog2_kinematics"))

from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# Test a simple case - all joints at zero
leg_num = 1
geometry = create_dog2_leg_geometry(leg_num)
ik_solver = LegIK4DOF(geometry)

print("Test 1: All joints at zero")
prismatic = 0.0
haa = 0.0
hfe = 0.0
kfe = 0.0

foot_pos = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
print(f"Foot position: {foot_pos}")
print(f"Expected: leg fully extended downward from HFE position")

# Calculate expected position manually
prismatic_pos = geometry.base_to_prismatic_offset.copy()
prismatic_pos[0] += prismatic
print(f"Prismatic pos: {prismatic_pos}")

haa_pos = prismatic_pos + geometry.prismatic_to_haa_offset
print(f"HAA pos: {haa_pos}")

# With HAA=0, no rotation
hfe_pos = haa_pos + geometry.haa_to_hfe_offset
print(f"HFE pos: {hfe_pos}")

# With HFE=0, KFE=0, leg extends in +X direction
total_length = geometry.thigh_length + geometry.shin_length
expected_foot = hfe_pos + np.array([total_length, 0, 0])
print(f"Expected foot pos: {expected_foot}")
print(f"Difference: {foot_pos - expected_foot}")

print("\n" + "="*60)
print("Test 2: HAA = 0.5 rad (rotation about Y-axis)")
haa = 0.5
foot_pos = ik_solver.forward_kinematics(0.0, haa, 0.0, 0.0)
print(f"Foot position: {foot_pos}")

# With Y-axis rotation, X and Z should change, Y should stay same
# Rotation matrix Ry(0.5):
# [cos(0.5)  0  sin(0.5)]   [total_length]   [total_length*cos(0.5)]
# [   0      1      0    ] * [     0      ] = [         0          ]
# [-sin(0.5) 0  cos(0.5)]   [     0      ]   [total_length*sin(0.5)]

expected_x = hfe_pos[0] + total_length * np.cos(0.5)
expected_y = hfe_pos[1]
expected_z = hfe_pos[2] + total_length * np.sin(0.5)
expected_foot = np.array([expected_x, expected_y, expected_z])
print(f"Expected foot pos: {expected_foot}")
print(f"Difference: {foot_pos - expected_foot}")
