#!/usr/bin/env python3
"""
Property-Based Test: Spherical Foot Geometry Integrity

Feature: dog2-spherical-foot, Property 1: 球形足端几何体完整性
Validates: Requirements 1.1, 1.2, 1.3

This test verifies that for any leg instantiation (leg_num 1-4), 
the foot link uses spherical geometry with radius 0.02m in both
visual and collision tags, and that the geometry is consistent.
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from hypothesis import given, strategies as st, settings


def generate_urdf_from_xacro():
    """Generate URDF from xacro file."""
    # Try multiple possible locations for the xacro file
    possible_paths = [
        Path(__file__).parent.parent / "urdf" / "dog2.urdf.xacro",  # Source location
        Path(__file__).parent.parent.parent.parent / "install" / "dog2_description" / "share" / "dog2_description" / "urdf" / "dog2.urdf.xacro",  # Install location
    ]
    
    xacro_path = None
    for path in possible_paths:
        if path.exists():
            xacro_path = path
            break
    
    if xacro_path is None:
        raise RuntimeError(f"Could not find dog2.urdf.xacro in any of: {possible_paths}")
    
    # Set up environment to find the package
    import os
    env = os.environ.copy()
    
    # Add the workspace to ROS package path
    workspace_root = Path(__file__).parent.parent.parent.parent
    install_path = workspace_root / "install"
    
    if install_path.exists():
        # Set AMENT_PREFIX_PATH to include install directory
        existing_path = env.get("AMENT_PREFIX_PATH", "")
        if existing_path:
            env["AMENT_PREFIX_PATH"] = f"{install_path}:{existing_path}"
        else:
            env["AMENT_PREFIX_PATH"] = str(install_path)
    
    try:
        result = subprocess.run(
            ["xacro", str(xacro_path)],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to generate URDF from xacro: {e.stderr}")


def parse_urdf(urdf_content):
    """Parse URDF XML content and return the root element."""
    return ET.fromstring(urdf_content)


@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_spherical_foot_geometry_property(leg_num):
    """
    Property Test: Spherical Foot Geometry Integrity
    
    For any leg instantiation (leg_num 1-4), the foot link should use
    spherical geometry with radius 0.02m in both visual and collision tags,
    and the geometry should be consistent between them.
    
    This property validates that:
    1. The foot link exists
    2. Visual geometry is a sphere with radius 0.02m
    3. Collision geometry is a sphere with radius 0.02m
    4. Visual and collision geometries are consistent
    5. Visual material color is grey (0.5, 0.5, 0.5, 1)
    """
    # Generate URDF from xacro
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    # Find the foot link
    # Naming pattern: l{leg_num}1111 generates:
    # Leg 1: l11111, Leg 2: l21111, Leg 3: l31111, Leg 4: l41111
    foot_link_name = f"l{leg_num}1111"
    
    foot_link = root.find(f".//link[@name='{foot_link_name}']")
    
    assert foot_link is not None, (
        f"Foot link '{foot_link_name}' not found in URDF"
    )
    
    # Check visual geometry
    visual = foot_link.find("visual")
    assert visual is not None, (
        f"Foot link '{foot_link_name}' has no visual element"
    )
    
    visual_geometry = visual.find("geometry")
    assert visual_geometry is not None, (
        f"Foot link '{foot_link_name}' visual has no geometry element"
    )
    
    visual_sphere = visual_geometry.find("sphere")
    assert visual_sphere is not None, (
        f"Foot link '{foot_link_name}' visual geometry is not a sphere. "
        f"Found: {[child.tag for child in visual_geometry]}"
    )
    
    visual_radius = float(visual_sphere.get("radius"))
    assert abs(visual_radius - 0.02) < 1e-6, (
        f"Foot link '{foot_link_name}' visual sphere radius is {visual_radius}, "
        f"expected 0.02"
    )
    
    # Check collision geometry
    collision = foot_link.find("collision")
    assert collision is not None, (
        f"Foot link '{foot_link_name}' has no collision element"
    )
    
    collision_geometry = collision.find("geometry")
    assert collision_geometry is not None, (
        f"Foot link '{foot_link_name}' collision has no geometry element"
    )
    
    collision_sphere = collision_geometry.find("sphere")
    assert collision_sphere is not None, (
        f"Foot link '{foot_link_name}' collision geometry is not a sphere. "
        f"Found: {[child.tag for child in collision_geometry]}"
    )
    
    collision_radius = float(collision_sphere.get("radius"))
    assert abs(collision_radius - 0.02) < 1e-6, (
        f"Foot link '{foot_link_name}' collision sphere radius is {collision_radius}, "
        f"expected 0.02"
    )
    
    # Verify visual and collision radii are consistent
    assert abs(visual_radius - collision_radius) < 1e-9, (
        f"Foot link '{foot_link_name}' visual and collision sphere radii are inconsistent: "
        f"visual={visual_radius}, collision={collision_radius}"
    )
    
    # Check visual material color (grey: 0.5, 0.5, 0.5, 1)
    material = visual.find("material")
    assert material is not None, (
        f"Foot link '{foot_link_name}' visual has no material element"
    )
    
    color = material.find("color")
    assert color is not None, (
        f"Foot link '{foot_link_name}' visual material has no color element"
    )
    
    rgba_str = color.get("rgba")
    assert rgba_str is not None, (
        f"Foot link '{foot_link_name}' visual material color has no rgba attribute"
    )
    
    rgba = [float(x) for x in rgba_str.split()]
    expected_rgba = [0.5, 0.5, 0.5, 1.0]
    
    for i, (actual, expected) in enumerate(zip(rgba, expected_rgba)):
        assert abs(actual - expected) < 1e-6, (
            f"Foot link '{foot_link_name}' visual material color component {i} is {actual}, "
            f"expected {expected}. Full RGBA: {rgba}"
        )


if __name__ == "__main__":
    # Run the property test for all legs
    print("Running property-based test: Spherical Foot Geometry Integrity")
    print("=" * 70)
    
    try:
        test_spherical_foot_geometry_property()
        print("\n✓ Property test PASSED: All foot links have spherical geometry")
        print("  Verified: Each foot link (1-4) uses sphere with radius 0.02m")
        print("  Verified: Visual and collision geometries are consistent")
        print("  Verified: Visual material is grey (0.5, 0.5, 0.5, 1)")
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        exit(1)
