#!/usr/bin/env python3
"""
Property-Based Test: Thigh Collision Primitive Usage

Feature: gazebo-collision-mesh-fixes, Property 1: 碰撞原语使用
Validates: Requirements 1.1

This test verifies that for any leg instantiation (leg_num 1-4), 
the thigh link (l${leg_num}11) uses collision primitives (cylinder or box)
instead of mesh geometry, while preserving the STL mesh for visual display.
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
def test_thigh_collision_primitive_property(leg_num):
    """
    Property Test: Thigh Collision Primitive Usage
    
    For any leg instantiation (leg_num 1-4), the thigh link should use
    collision primitives (cylinder or box) instead of mesh geometry.
    
    This property validates that:
    1. The thigh link exists
    2. Collision geometry is a cylinder or box (not mesh)
    3. Visual geometry still uses STL mesh (preserved for display)
    4. No scale attribute is present in collision geometry
    """
    # Generate URDF from xacro
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    # Find the thigh link
    # Naming pattern: l{leg_num}11
    thigh_link_name = f"l{leg_num}11"
    
    thigh_link = root.find(f".//link[@name='{thigh_link_name}']")
    
    assert thigh_link is not None, (
        f"Thigh link '{thigh_link_name}' not found in URDF"
    )
    
    # Check collision geometry
    collision = thigh_link.find("collision")
    assert collision is not None, (
        f"Thigh link '{thigh_link_name}' has no collision element"
    )
    
    collision_geometry = collision.find("geometry")
    assert collision_geometry is not None, (
        f"Thigh link '{thigh_link_name}' collision has no geometry element"
    )
    
    # Check that collision uses primitive (cylinder or box), not mesh
    collision_cylinder = collision_geometry.find("cylinder")
    collision_box = collision_geometry.find("box")
    collision_mesh = collision_geometry.find("mesh")
    
    has_primitive = (collision_cylinder is not None) or (collision_box is not None)
    
    assert has_primitive, (
        f"Thigh link '{thigh_link_name}' collision geometry is not a primitive. "
        f"Expected cylinder or box, but found: {[child.tag for child in collision_geometry]}"
    )
    
    assert collision_mesh is None, (
        f"Thigh link '{thigh_link_name}' collision geometry should not use mesh. "
        f"Found mesh element in collision geometry."
    )
    
    # If mesh somehow exists, verify no scale attribute
    if collision_mesh is not None:
        scale_attr = collision_mesh.get("scale")
        assert scale_attr is None, (
            f"Thigh link '{thigh_link_name}' collision mesh should not have scale attribute. "
            f"Found scale='{scale_attr}'"
        )
    
    # Check visual geometry (should still use STL mesh)
    visual = thigh_link.find("visual")
    assert visual is not None, (
        f"Thigh link '{thigh_link_name}' has no visual element"
    )
    
    visual_geometry = visual.find("geometry")
    assert visual_geometry is not None, (
        f"Thigh link '{thigh_link_name}' visual has no geometry element"
    )
    
    visual_mesh = visual_geometry.find("mesh")
    assert visual_mesh is not None, (
        f"Thigh link '{thigh_link_name}' visual geometry should use mesh. "
        f"Expected mesh, but found: {[child.tag for child in visual_geometry]}"
    )
    
    # Verify visual mesh filename ends with .STL
    mesh_filename = visual_mesh.get("filename")
    assert mesh_filename is not None, (
        f"Thigh link '{thigh_link_name}' visual mesh has no filename attribute"
    )
    
    assert mesh_filename.endswith(".STL") or mesh_filename.endswith(".stl"), (
        f"Thigh link '{thigh_link_name}' visual mesh filename should end with .STL. "
        f"Found: '{mesh_filename}'"
    )


if __name__ == "__main__":
    # Run the property test for all legs
    print("Running property-based test: Thigh Collision Primitive Usage")
    print("=" * 70)
    
    try:
        test_thigh_collision_primitive_property()
        print("\n✓ Property test PASSED: All thigh links use collision primitives")
        print("  Verified: Each thigh link (1-4) uses cylinder or box for collision")
        print("  Verified: Visual geometry still uses STL mesh")
        print("  Verified: No scale attribute in collision geometry")
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        exit(1)
