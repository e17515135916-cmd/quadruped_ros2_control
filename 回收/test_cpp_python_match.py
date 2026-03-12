#!/usr/bin/env python3
"""
Test to verify C++ and Python implementations match
"""

import sys
import numpy as np
from pathlib import Path

# Add the dog2_kinematics module to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dog2_kinematics"))

from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# Test a simple case
leg_num = 1
geometry = create_dog2_leg_geometry(leg_num)
ik_solver = LegIK4DOF(geometry)

# Test forward kinematics
prismatic = 0.0
haa = 0.5
hfe = -0.5
kfe = -1.0

print("Testing Forward Kinematics:")
print(f"Input: prismatic={prismatic}, haa={haa}, hfe={hfe}, kfe={kfe}")

foot_pos = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
print(f"Foot position: {foot_pos}")

# Test inverse kinematics
print("\nTesting Inverse Kinematics:")
print(f"Target foot position: {foot_pos}")

ik_solution = ik_solver.solve(foot_pos, prismatic)
print(f"IK Solution valid: {ik_solution.valid}")
if ik_solution.valid:
    print(f"Joint angles: prismatic={ik_solution.prismatic:.4f}, haa={ik_solution.haa:.4f}, hfe={ik_solution.hfe:.4f}, kfe={ik_solution.kfe:.4f}")
    
    # Verify round-trip
    foot_pos_roundtrip = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    error = np.linalg.norm(foot_pos - foot_pos_roundtrip)
    print(f"Round-trip error: {error*1000:.4f}mm")
    
    if error < 0.001:
        print("✓ Round-trip test PASSED")
    else:
        print("✗ Round-trip test FAILED")
else:
    print(f"IK failed: {ik_solution.error_msg}")
