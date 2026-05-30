#!/usr/bin/env python3
"""
Property-Based Test: Complete Link Structure

Feature: ros2-control-joint-fix, Property 2: Complete Link Structure
Validates: Requirements 1.5, 3.1

This test verifies that for each leg prefix (lf/lh/rh/rf), the generated
URDF contains the 5 canonical links and their parent-child joint chain
matches the expected kinematic topology.
"""

from hypothesis import given, strategies as st, settings
from urdf_test_utils import generate_urdf_from_xacro, parse_urdf

LEG_PREFIXES = ["lf", "lh", "rh", "rf"]

EXPECTED_LINKS_PER_LEG = {
    p: {
        f"{p}_rail_link",
        f"{p}_coxa_link",
        f"{p}_femur_link",
        f"{p}_tibia_link",
        f"{p}_foot_link",
    }
    for p in LEG_PREFIXES
}

EXPECTED_JOINT_CHAIN = {
    p: [
        (f"{p}_rail_joint", f"{p}_leg_mount", f"{p}_rail_link"),
        (f"{p}_coxa_joint", f"{p}_coxa_axis_frame", f"{p}_coxa_drive_frame"),
        (f"{p}_femur_joint", f"{p}_femur_axis_frame", f"{p}_femur_drive_frame"),
        (f"{p}_tibia_joint", f"{p}_tibia_axis_frame", f"{p}_tibia_drive_frame"),
        (f"{p}_foot_fixed", f"{p}_tibia_link", f"{p}_foot_link"),
    ]
    for p in LEG_PREFIXES
}


def get_links_for_leg_prefix(root, leg_prefix):
    """Return the set of expected link names that actually exist in the URDF."""
    expected = EXPECTED_LINKS_PER_LEG[leg_prefix]
    found = set()
    for link in root.findall("link"):
        name = link.get("name")
        if name in expected:
            found.add(name)
    return found


@settings(max_examples=100)
@given(leg_prefix=st.sampled_from(LEG_PREFIXES))
def test_complete_link_structure_property(leg_prefix):
    """
    Property Test: Complete Link Structure

    For each leg prefix (lf/lh/rh/rf), the URDF must contain exactly the
    5 canonical links and their parent-child joint chain must match the
    expected kinematic topology.
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)

    expected_links = EXPECTED_LINKS_PER_LEG[leg_prefix]
    actual_links = get_links_for_leg_prefix(root, leg_prefix)

    missing = expected_links - actual_links
    assert len(missing) == 0, (
        f"Leg {leg_prefix} missing links: {missing}. "
        f"Expected: {expected_links}, found: {actual_links}"
    )
    assert len(actual_links) == 5, (
        f"Leg {leg_prefix} should have exactly 5 canonical links, "
        f"but found {len(actual_links)}: {actual_links}"
    )

    for joint_name, expected_parent, expected_child in EXPECTED_JOINT_CHAIN[leg_prefix]:
        joint = root.find(f".//joint[@name='{joint_name}']")
        assert joint is not None, (
            f"Joint '{joint_name}' not found in URDF for leg {leg_prefix}"
        )
        parent = joint.find("parent").get("link")
        child = joint.find("child").get("link")
        assert parent == expected_parent, (
            f"Joint '{joint_name}' parent is '{parent}', expected '{expected_parent}'"
        )
        assert child == expected_child, (
            f"Joint '{joint_name}' child is '{child}', expected '{expected_child}'"
        )


if __name__ == "__main__":
    print("Running property-based test: Complete Link Structure")
    print("=" * 70)
    try:
        test_complete_link_structure_property()
        print("\n✓ Property test PASSED: All legs have complete link structure")
        print("  Verified: Each leg (lf/lh/rh/rf) has 5 canonical links + correct joint chain")
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        exit(1)
