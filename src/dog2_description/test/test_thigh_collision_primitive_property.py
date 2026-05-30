#!/usr/bin/env python3
"""
Property-Based Test: Femur Collision Geometry Integrity

Feature: gazebo-collision-mesh-fixes, Property 1: 碰撞几何体完整性
Validates: Requirements 1.1

This test verifies that for each leg prefix (lf/lh/rh/rf), the femur link
({prefix}_femur_link) has at least one valid collision and one valid visual
geometry element.  Mesh collision filenames must reference existing files
under package://dog2_description/.
"""

from hypothesis import given, strategies as st, settings
from urdf_test_utils import generate_urdf_from_xacro, parse_urdf, resolve_package_uri

LEG_PREFIXES = ["lf", "lh", "rh", "rf"]


@settings(max_examples=100)
@given(leg_prefix=st.sampled_from(LEG_PREFIXES))
def test_femur_collision_geometry_property(leg_prefix):
    """
    Property Test: Femur Collision Geometry Integrity

    For each leg prefix, {prefix}_femur_link must have:
    1. At least one collision element with a valid geometry.
    2. At least one visual element with a valid geometry.
    3. If collision geometry is a mesh, its filename must resolve to an
       existing local file under package://dog2_description/.
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)

    femur_name = f"{leg_prefix}_femur_link"
    femur_link = root.find(f".//link[@name='{femur_name}']")
    assert femur_link is not None, f"Femur link '{femur_name}' not found in URDF"

    # --- collision ---
    collisions = femur_link.findall("collision")
    assert len(collisions) > 0, f"Femur link '{femur_name}' has no collision elements"

    valid_collision = False
    for col in collisions:
        geom = col.find("geometry")
        assert geom is not None, (
            f"Femur link '{femur_name}' collision has no geometry element"
        )
        children = list(geom)
        assert len(children) > 0, (
            f"Femur link '{femur_name}' collision geometry is empty"
        )
        child = children[0]
        if child.tag == "mesh":
            filename = child.get("filename")
            assert filename is not None, (
                f"Femur link '{femur_name}' collision mesh has no filename"
            )
            assert filename.startswith("package://dog2_description/"), (
                f"Femur link '{femur_name}' collision mesh filename '{filename}' "
                f"does not use package://dog2_description/"
            )
            resolved = resolve_package_uri(filename)
            assert resolved is not None, (
                f"Femur link '{femur_name}' collision mesh '{filename}' "
                f"could not be resolved to a local file"
            )
            assert resolved.exists(), (
                f"Femur link '{femur_name}' collision mesh file not found: {resolved}"
            )
        valid_collision = True

    assert valid_collision, (
        f"Femur link '{femur_name}' has no valid collision geometry"
    )

    # --- visual ---
    visuals = femur_link.findall("visual")
    assert len(visuals) > 0, f"Femur link '{femur_name}' has no visual elements"

    for vis in visuals:
        geom = vis.find("geometry")
        assert geom is not None, (
            f"Femur link '{femur_name}' visual has no geometry element"
        )
        children = list(geom)
        assert len(children) > 0, (
            f"Femur link '{femur_name}' visual geometry is empty"
        )


if __name__ == "__main__":
    print("Running property-based test: Femur Collision Geometry Integrity")
    print("=" * 70)
    try:
        test_femur_collision_geometry_property()
        print("\n✓ Property test PASSED: All femur links have valid collision & visual geometry")
        print("  Verified: Each femur link has collision and visual geometry")
        print("  Verified: Mesh filenames reference existing files under dog2_description")
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        exit(1)
