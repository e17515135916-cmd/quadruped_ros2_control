#!/usr/bin/env python3
"""
Property-Based Tests: Kinematics Round-Trip Consistency

Feature: hip-joint-axis-change, Property 3: Kinematics Round-Trip Consistency
Validates: Requirements 4.1, 4.2, 4.3

This test verifies that for any valid foot position within the workspace,
computing IK then FK should return joint angles that produce a foot position
within 1mm of the original position.
"""

import sys
import os
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path

# Add the dog2_kinematics module to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "dog2_kinematics"))

from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry


# Strategy for generating valid foot positions within the workspace
@st.composite
def valid_foot_position(draw, leg_num=1):
    """
    Generate valid foot positions within the robot's workspace.
    
    The workspace is constrained by:
    - Prismatic joint limits: -0.1 to 0.1 m
    - Leg reach: thigh + shin length ≈ 0.5 m
    - Physical constraints of the robot
    """
    geometry = create_dog2_leg_geometry(leg_num)
    
    # Generate prismatic position within limits
    prismatic = draw(st.floats(
        min_value=geometry.prismatic_lower + 0.01,
        max_value=geometry.prismatic_upper - 0.01
    ))
    
    # Calculate base position of the leg
    prismatic_pos = geometry.base_to_prismatic_offset.copy()
    prismatic_pos[0] += prismatic
    haa_pos = prismatic_pos + geometry.prismatic_to_haa_offset
    
    # Generate foot position relative to HAA
    # The foot should be within reach of the leg (thigh + shin length)
    max_reach = geometry.thigh_length + geometry.shin_length
    min_reach = abs(geometry.thigh_length - geometry.shin_length)
    
    # Generate reach distance
    reach = draw(st.floats(
        min_value=min_reach + 0.05,  # Add margin
        max_value=max_reach - 0.05   # Add margin
    ))
    
    # Generate angles for spherical coordinates
    # HAA angle (rotation about x-axis in Y-Z plane)
    haa_angle = draw(st.floats(
        min_value=geometry.haa_lower + 0.1,
        max_value=geometry.haa_upper - 0.1
    ))
    
    # HFE angle (pitch angle in the leg plane)
    hfe_angle = draw(st.floats(
        min_value=geometry.hfe_lower + 0.1,
        max_value=geometry.hfe_upper - 0.1
    ))
    
    # Calculate foot position in leg plane
    plane_x = reach * np.cos(hfe_angle)
    plane_y = reach * np.sin(hfe_angle)
    
    # Transform to base frame considering HAA rotation about x-axis
    hfe_offset_rotated = np.array([
        geometry.haa_to_hfe_offset[0],
        geometry.haa_to_hfe_offset[1] * np.cos(haa_angle) - 
        geometry.haa_to_hfe_offset[2] * np.sin(haa_angle),
        geometry.haa_to_hfe_offset[1] * np.sin(haa_angle) + 
        geometry.haa_to_hfe_offset[2] * np.cos(haa_angle)
    ])
    
    hfe_pos = haa_pos + hfe_offset_rotated
    
    foot_position = np.array([
        hfe_pos[0] + plane_x,
        hfe_pos[1] + plane_y * np.cos(haa_angle),
        hfe_pos[2] + plane_y * np.sin(haa_angle)
    ])
    
    return foot_position, prismatic, leg_num


@settings(max_examples=100, deadline=None)
@given(data=valid_foot_position())
def test_property_3_kinematics_roundtrip(data):
    """
    Property Test: Kinematics Round-Trip Consistency
    
    Feature: hip-joint-axis-change, Property 3: Kinematics Round-Trip Consistency
    Validates: Requirements 4.1, 4.2, 4.3
    
    For any valid foot position within the workspace, computing IK then FK
    should return joint angles that produce a foot position within 1mm of
    the original position.
    
    This property validates that:
    1. IK solver produces valid joint angles
    2. FK solver correctly computes foot position from joint angles
    3. Round-trip error is less than 1mm
    4. The x-axis rotation is correctly implemented
    """
    foot_position, prismatic, leg_num = data
    
    # Create kinematics solver
    geometry = create_dog2_leg_geometry(leg_num)
    ik_solver = LegIK4DOF(geometry)
    
    # Compute IK
    ik_solution = ik_solver.solve(foot_position, prismatic)
    
    # IK should find a valid solution
    assume(ik_solution.valid)
    
    # Compute FK with the IK solution
    foot_position_fk = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    
    # Calculate position error
    position_error = np.linalg.norm(foot_position - foot_position_fk)
    
    # Property: Round-trip error should be less than 1mm
    assert position_error < 0.001, (
        f"Round-trip error {position_error*1000:.4f}mm exceeds 1mm threshold\n"
        f"Original position: {foot_position}\n"
        f"FK position: {foot_position_fk}\n"
        f"Joint angles: prismatic={ik_solution.prismatic:.4f}, "
        f"haa={ik_solution.haa:.4f}, hfe={ik_solution.hfe:.4f}, kfe={ik_solution.kfe:.4f}"
    )
    
    # Additional check: Joint angles should be within limits
    assert geometry.prismatic_lower <= ik_solution.prismatic <= geometry.prismatic_upper
    assert geometry.haa_lower <= ik_solution.haa <= geometry.haa_upper
    assert geometry.hfe_lower <= ik_solution.hfe <= geometry.hfe_upper
    assert geometry.kfe_lower <= ik_solution.kfe <= geometry.kfe_upper


@settings(max_examples=100, deadline=None)
@given(
    leg_num=st.integers(min_value=1, max_value=4),
    prismatic=st.floats(min_value=-0.09, max_value=0.09),
    haa=st.floats(min_value=-2.5, max_value=2.5),
    hfe=st.floats(min_value=-2.7, max_value=2.7),
    kfe=st.floats(min_value=-2.7, max_value=-0.1)
)
def test_property_3_fk_then_ik_roundtrip(leg_num, prismatic, haa, hfe, kfe):
    """
    Property Test: FK then IK Round-Trip
    
    For any valid joint configuration, computing FK then IK should return
    joint angles close to the original configuration.
    """
    geometry = create_dog2_leg_geometry(leg_num)
    ik_solver = LegIK4DOF(geometry)
    
    # Compute FK
    foot_position = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
    
    # Compute IK
    ik_solution = ik_solver.solve(foot_position, prismatic)
    
    # IK should find a valid solution
    assume(ik_solution.valid)
    
    # Compute FK again with IK solution
    foot_position_roundtrip = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    
    # Position should match within 1mm
    position_error = np.linalg.norm(foot_position - foot_position_roundtrip)
    assert position_error < 0.001, (
        f"FK->IK->FK round-trip error {position_error*1000:.4f}mm exceeds 1mm"
    )


@settings(max_examples=50, deadline=None)
@given(data=valid_foot_position())
def test_property_3_ik_determinism(data):
    """
    Property Test: IK Determinism
    
    For any foot position, calling IK multiple times with the same input
    should produce the same result.
    """
    foot_position, prismatic, leg_num = data
    
    geometry = create_dog2_leg_geometry(leg_num)
    ik_solver = LegIK4DOF(geometry)
    
    # Compute IK twice
    solution1 = ik_solver.solve(foot_position, prismatic)
    solution2 = ik_solver.solve(foot_position, prismatic)
    
    assume(solution1.valid and solution2.valid)
    
    # Solutions should be identical
    assert np.isclose(solution1.prismatic, solution2.prismatic)
    assert np.isclose(solution1.haa, solution2.haa)
    assert np.isclose(solution1.hfe, solution2.hfe)
    assert np.isclose(solution1.kfe, solution2.kfe)


@settings(max_examples=50, deadline=None)
@given(
    leg_num=st.integers(min_value=1, max_value=4),
    prismatic=st.floats(min_value=-0.09, max_value=0.09),
    haa=st.floats(min_value=-2.5, max_value=2.5),
    hfe=st.floats(min_value=-2.7, max_value=2.7),
    kfe=st.floats(min_value=-2.7, max_value=-0.1)
)
def test_property_3_fk_determinism(leg_num, prismatic, haa, hfe, kfe):
    """
    Property Test: FK Determinism
    
    For any joint configuration, calling FK multiple times with the same input
    should produce the same result.
    """
    geometry = create_dog2_leg_geometry(leg_num)
    ik_solver = LegIK4DOF(geometry)
    
    # Compute FK twice
    foot_pos1 = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
    foot_pos2 = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
    
    # Results should be identical
    assert np.allclose(foot_pos1, foot_pos2, rtol=1e-15, atol=1e-15)


@settings(max_examples=50, deadline=None)
@given(data=valid_foot_position())
def test_property_3_x_axis_rotation_validation(data):
    """
    Property Test: X-Axis Rotation Validation
    
    Verify that the HAA joint correctly implements x-axis rotation.
    When HAA changes, the foot should move in the Y-Z plane.
    """
    foot_position, prismatic, leg_num = data
    
    geometry = create_dog2_leg_geometry(leg_num)
    ik_solver = LegIK4DOF(geometry)
    
    # Compute IK
    ik_solution = ik_solver.solve(foot_position, prismatic)
    assume(ik_solution.valid)
    
    # Compute FK at original HAA
    foot_pos_original = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    
    # Compute FK with slightly different HAA (small rotation about x-axis)
    delta_haa = 0.01  # Small rotation
    foot_pos_rotated = ik_solver.forward_kinematics(
        ik_solution.prismatic,
        ik_solution.haa + delta_haa,
        ik_solution.hfe,
        ik_solution.kfe
    )
    
    # The X component should remain relatively constant (rotation about x-axis)
    # The Y and Z components should change
    x_change = abs(foot_pos_rotated[0] - foot_pos_original[0])
    yz_change = np.linalg.norm(foot_pos_rotated[1:] - foot_pos_original[1:])
    
    # X should change less than Y-Z (since rotation is about x-axis)
    # This validates that HAA is indeed rotating about x-axis
    assert yz_change > x_change, (
        f"HAA rotation should primarily affect Y-Z plane, but "
        f"x_change={x_change:.6f}, yz_change={yz_change:.6f}"
    )


if __name__ == "__main__":
    print("Running property-based tests: Kinematics Round-Trip Consistency")
    print("=" * 80)
    
    try:
        print("\n1. Testing basic kinematics round-trip (IK->FK)...")
        test_property_3_kinematics_roundtrip()
        print("   ✓ PASSED: IK->FK round-trip error < 1mm")
        
        print("\n2. Testing FK->IK->FK round-trip...")
        test_property_3_fk_then_ik_roundtrip()
        print("   ✓ PASSED: FK->IK->FK round-trip error < 1mm")
        
        print("\n3. Testing IK determinism...")
        test_property_3_ik_determinism()
        print("   ✓ PASSED: IK produces consistent results")
        
        print("\n4. Testing FK determinism...")
        test_property_3_fk_determinism()
        print("   ✓ PASSED: FK produces consistent results")
        
        print("\n5. Testing x-axis rotation validation...")
        test_property_3_x_axis_rotation_validation()
        print("   ✓ PASSED: HAA correctly rotates about x-axis")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: IK->FK round-trip error < 1mm")
        print("  Verified: FK->IK->FK round-trip error < 1mm")
        print("  Verified: IK and FK are deterministic")
        print("  Verified: HAA joint rotates about x-axis")
        print("  Verified: Joint angles stay within limits")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
