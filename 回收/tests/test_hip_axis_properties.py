#!/usr/bin/env python3
"""
Property-based tests for hip joint axis verification
Feature: hip-joint-z-axis-reversion
"""

import pytest
from hypothesis import given, strategies as st, settings
from urdf_parser_py.urdf import URDF
import subprocess
import tempfile
import os


# Path to the xacro file
XACRO_FILE = "src/dog2_description/urdf/dog2.urdf.xacro"


def compile_urdf():
    """Compile xacro to URDF"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as f:
        urdf_path = f.name
    
    try:
        result = subprocess.run(
            ['xacro', XACRO_FILE],
            capture_output=True,
            text=True,
            check=True
        )
        with open(urdf_path, 'w') as f:
            f.write(result.stdout)
        return urdf_path
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to compile xacro: {e.stderr}")


def parse_urdf(urdf_file):
    """Parse URDF file"""
    try:
        return URDF.from_xml_file(urdf_file)
    except Exception as e:
        pytest.fail(f"Failed to parse URDF: {e}")


@settings(max_examples=100)
@given(st.just(None))  # Deterministic test, but run 100 times for consistency
def test_property_hip_axis_configuration_consistency(dummy):
    """
    Property 1: Hip Axis Configuration Consistency
    
    For any leg instantiation (leg 1, 2, 3, 4), the hip_axis parameter 
    SHALL be set to "1 0 0"
    
    Feature: hip-joint-z-axis-reversion, Property 1: Hip Axis Configuration Consistency
    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """
    # Compile URDF
    urdf_file = compile_urdf()
    
    try:
        # Parse URDF
        robot = parse_urdf(urdf_file)
        
        # Hip joints to verify
        hip_joints = ['j11', 'j21', 'j31', 'j41']
        expected_axis = [1.0, 0.0, 0.0]
        
        # Verify each hip joint
        for joint_name in hip_joints:
            # Find the joint
            joint = None
            for j in robot.joints:
                if j.name == joint_name:
                    joint = j
                    break
            
            assert joint is not None, f"Joint {joint_name} not found in URDF"
            assert joint.axis is not None, f"Joint {joint_name} has no axis defined"
            
            actual_axis = list(joint.axis)
            assert actual_axis == expected_axis, \
                f"Joint {joint_name}: expected axis {expected_axis}, got {actual_axis}"
    
    finally:
        # Clean up temporary file
        if os.path.exists(urdf_file):
            os.unlink(urdf_file)


@settings(max_examples=100)
@given(st.just(None))  # Deterministic test, but run 100 times for consistency
def test_property_visual_model_preservation(dummy):
    """
    Property 3: Visual Model Preservation
    
    For any hip link (l11, l21, l31, l41), the visual mesh filename and 
    visual origin SHALL remain unchanged after the axis modification
    
    Feature: hip-joint-z-axis-reversion, Property 3: Visual Model Preservation
    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    # Compile URDF
    urdf_file = compile_urdf()
    
    try:
        # Parse URDF
        robot = parse_urdf(urdf_file)
        
        # Hip links to verify
        hip_links = ['l11', 'l21', 'l31', 'l41']
        expected_meshes = {
            'l11': 'package://dog2_description/meshes/l11.STL',
            'l21': 'package://dog2_description/meshes/l21.STL',
            'l31': 'package://dog2_description/meshes/l31.STL',
            'l41': 'package://dog2_description/meshes/l41.STL'
        }
        
        # Verify each hip link
        for link_name in hip_links:
            # Find the link
            link = None
            for l in robot.links:
                if l.name == link_name:
                    link = l
                    break
            
            assert link is not None, f"Link {link_name} not found in URDF"
            assert link.visual is not None, f"Link {link_name} has no visual element"
            assert link.visual.geometry is not None, f"Link {link_name} has no visual geometry"
            
            # Check mesh filename (geometry is the Mesh object itself)
            actual_mesh = link.visual.geometry.filename
            expected_mesh = expected_meshes[link_name]
            assert actual_mesh == expected_mesh, \
                f"Link {link_name}: expected mesh {expected_mesh}, got {actual_mesh}"
            
            # Visual origin should exist (we're not checking specific values, 
            # just that it exists and hasn't been removed)
            assert link.visual.origin is not None, \
                f"Link {link_name}: visual origin should exist"
    
    finally:
        # Clean up temporary file
        if os.path.exists(urdf_file):
            os.unlink(urdf_file)


@settings(max_examples=100)
@given(st.just(None))  # Deterministic test, but run 100 times for consistency
def test_property_collision_model_preservation(dummy):
    """
    Property 4: Collision Model Preservation
    
    For any hip link (l11, l21, l31, l41), the collision geometry and 
    collision origin SHALL remain unchanged after the axis modification
    
    Feature: hip-joint-z-axis-reversion, Property 4: Collision Model Preservation
    Validates: Requirements 3.1, 3.2, 3.3
    """
    # Compile URDF
    urdf_file = compile_urdf()
    
    try:
        # Parse URDF
        robot = parse_urdf(urdf_file)
        
        # Hip links to verify
        hip_links = ['l11', 'l21', 'l31', 'l41']
        expected_meshes = {
            'l11': 'package://dog2_description/meshes/collision/l11_collision.STL',
            'l21': 'package://dog2_description/meshes/collision/l21_collision.STL',
            'l31': 'package://dog2_description/meshes/collision/l31_collision.STL',
            'l41': 'package://dog2_description/meshes/collision/l41_collision.STL'
        }
        
        # Verify each hip link
        for link_name in hip_links:
            # Find the link
            link = None
            for l in robot.links:
                if l.name == link_name:
                    link = l
                    break
            
            assert link is not None, f"Link {link_name} not found in URDF"
            assert link.collision is not None, f"Link {link_name} has no collision element"
            assert link.collision.geometry is not None, f"Link {link_name} has no collision geometry"
            
            # Check collision mesh filename (geometry is the Mesh object itself)
            actual_mesh = link.collision.geometry.filename
            expected_mesh = expected_meshes[link_name]
            assert actual_mesh == expected_mesh, \
                f"Link {link_name}: expected collision mesh {expected_mesh}, got {actual_mesh}"
            
            # Collision origin should exist
            assert link.collision.origin is not None, \
                f"Link {link_name}: collision origin should exist"
    
    finally:
        # Clean up temporary file
        if os.path.exists(urdf_file):
            os.unlink(urdf_file)


@settings(max_examples=100)
@given(st.just(None))  # Deterministic test, but run 100 times for consistency
def test_property_joint_limits_preservation(dummy):
    """
    Property 5: Joint Limits Preservation
    
    For any hip joint (j11, j21, j31, j41), the effort, velocity, and 
    position limits SHALL remain unchanged after the axis modification
    
    Feature: hip-joint-z-axis-reversion, Property 5: Joint Limits Preservation
    Validates: Requirements 4.1, 4.2, 4.3
    """
    # Compile URDF
    urdf_file = compile_urdf()
    
    try:
        # Parse URDF
        robot = parse_urdf(urdf_file)
        
        # Hip joints to verify
        hip_joints = ['j11', 'j21', 'j31', 'j41']
        
        # Expected limits (from requirements)
        expected_effort = 50.0
        expected_velocity = 20.0
        expected_lower = -2.618  # -150 degrees
        expected_upper = 2.618   # +150 degrees
        
        # Verify each hip joint
        for joint_name in hip_joints:
            # Find the joint
            joint = None
            for j in robot.joints:
                if j.name == joint_name:
                    joint = j
                    break
            
            assert joint is not None, f"Joint {joint_name} not found in URDF"
            assert joint.limit is not None, f"Joint {joint_name} has no limit defined"
            
            # Check effort limit
            assert joint.limit.effort == expected_effort, \
                f"Joint {joint_name}: expected effort {expected_effort}, got {joint.limit.effort}"
            
            # Check velocity limit
            assert joint.limit.velocity == expected_velocity, \
                f"Joint {joint_name}: expected velocity {expected_velocity}, got {joint.limit.velocity}"
            
            # Check position limits (with small tolerance for floating point)
            assert abs(joint.limit.lower - expected_lower) < 0.001, \
                f"Joint {joint_name}: expected lower limit {expected_lower}, got {joint.limit.lower}"
            
            assert abs(joint.limit.upper - expected_upper) < 0.001, \
                f"Joint {joint_name}: expected upper limit {expected_upper}, got {joint.limit.upper}"
    
    finally:
        # Clean up temporary file
        if os.path.exists(urdf_file):
            os.unlink(urdf_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
