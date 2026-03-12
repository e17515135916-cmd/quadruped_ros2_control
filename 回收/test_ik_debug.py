#!/usr/bin/env python3
"""
Debug IK calculation
"""

import sys
import numpy as np
from pathlib import Path

# Add the dog2_kinematics module to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dog2_kinematics"))

from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# Test with a known good configuration
leg_num = 1
geometry = create_dog2_leg_geometry(leg_num)
ik_solver = LegIK4DOF(geometry)

# Start with FK to get a known good foot position
prismatic_in = 0.0
haa_in = 0.0
hfe_in = -0.5
kfe_in = -1.0

print("Forward Kinematics:")
print(f"Input joints: prismatic={prismatic_in}, haa={haa_in}, hfe={hfe_in}, kfe={kfe_in}")

foot_pos = ik_solver.forward_kinematics(prismatic_in, haa_in, hfe_in, kfe_in)
print(f"Foot position: {foot_pos}")

print("\n" + "="*60)
print("Inverse Kinematics:")
print(f"Target foot position: {foot_pos}")

# Now solve IK
ik_solution = ik_solver.solve(foot_pos, prismatic_in)

print(f"IK valid: {ik_solution.valid}")
if ik_solution.valid:
    print(f"IK joints: prismatic={ik_solution.prismatic:.4f}, haa={ik_solution.haa:.4f}, hfe={ik_solution.hfe:.4f}, kfe={ik_solution.kfe:.4f}")
    
    # Check if joints match
    print(f"\nJoint differences:")
    print(f"  prismatic: {abs(ik_solution.prismatic - prismatic_in):.6f}")
    print(f"  haa: {abs(ik_solution.haa - haa_in):.6f}")
    print(f"  hfe: {abs(ik_solution.hfe - hfe_in):.6f}")
    print(f"  kfe: {abs(ik_solution.kfe - kfe_in):.6f}")
    
    # Verify with FK
    foot_pos_check = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    error = np.linalg.norm(foot_pos - foot_pos_check)
    print(f"\nRound-trip error: {error*1000:.4f}mm")
else:
    print(f"IK failed: {ik_solution.error_msg}")

# Try with HAA = 0.5
print("\n" + "="*60)
print("Test with HAA = 0.5:")
haa_in = 0.5
foot_pos = ik_solver.forward_kinematics(prismatic_in, haa_in, hfe_in, kfe_in)
print(f"Foot position: {foot_pos}")

ik_solution = ik_solver.solve(foot_pos, prismatic_in)
print(f"IK valid: {ik_solution.valid}")
if ik_solution.valid:
    print(f"IK joints: prismatic={ik_solution.prismatic:.4f}, haa={ik_solution.haa:.4f}, hfe={ik_solution.hfe:.4f}, kfe={ik_solution.kfe:.4f}")
    print(f"Expected haa: {haa_in:.4f}")
    
    foot_pos_check = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    error = np.linalg.norm(foot_pos - foot_pos_check)
    print(f"Round-trip error: {error*1000:.4f}mm")
else:
    print(f"IK failed: {ik_solution.error_msg}")
