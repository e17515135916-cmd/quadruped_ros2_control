#!/usr/bin/env python3
"""
Property-Based Test: Complete Link Structure

Feature: ros2-control-joint-fix, Property 2: Complete Link Structure
Validates: Requirements 1.5, 3.1

This test verifies that for any leg instantiation (leg_num 1-4), 
the generated URDF contains exactly 5 links with the correct naming pattern:
- l${leg_num} (rail link)
- l${leg_num}1 (hip link)
- l${leg_num}11 (thigh link)
- l${leg_num}111 (shin link)
- l${leg_num}1111 (foot link)
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


def get_links_for_leg(root, leg_num):
    """
    Extract all links for a specific leg from the URDF.
    
    Args:
        root: XML root element of the URDF
        leg_num: Leg number (1-4)
    
    Returns:
        Set of link names for the specified leg
    """
    # Build expected link names based on the actual naming convention
    # The naming pattern is: l{leg_num} followed by 0-4 ones
    # For leg 1: l1, l11, l111, l1111, l11111
    # For leg 2: l2, l21, l211, l2111, l21111
    # For leg 3: l3, l31, l311, l3111, l31111
    # For leg 4: l4, l41, l411, l4111, l41111
    expected_patterns = [
        f"l{leg_num}",       # rail link
        f"l{leg_num}1",      # hip link
        f"l{leg_num}11",     # thigh link
        f"l{leg_num}111",    # shin link
        f"l{leg_num}1111",   # foot link
    ]
    
    found_links = set()
    for link in root.findall("link"):
        link_name = link.get("name")
        if link_name in expected_patterns:
            found_links.add(link_name)
    
    return found_links


@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_complete_link_structure_property(leg_num):
    """
    Property Test: Complete Link Structure
    
    For any leg instantiation (leg_num 1-4), the generated URDF should contain
    exactly 5 links with the correct naming pattern.
    
    This property validates that:
    1. All 5 links exist for each leg
    2. Link naming follows the correct pattern
    3. No links are missing from the kinematic chain
    """
    # Generate URDF from xacro
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    # Expected links for this leg
    expected_links = {
        f"l{leg_num}",      # rail link
        f"l{leg_num}1",     # hip link
        f"l{leg_num}11",    # thigh link
        f"l{leg_num}111",   # shin link
        f"l{leg_num}1111",  # foot link
    }
    
    # Get actual links for this leg
    actual_links = get_links_for_leg(root, leg_num)
    
    # Verify all expected links are present
    missing_links = expected_links - actual_links
    extra_links = actual_links - expected_links
    
    assert len(missing_links) == 0, (
        f"Leg {leg_num} is missing links: {missing_links}. "
        f"Expected 5 links: {expected_links}, but found: {actual_links}"
    )
    
    assert len(extra_links) == 0, (
        f"Leg {leg_num} has unexpected extra links: {extra_links}. "
        f"Expected exactly: {expected_links}, but found: {actual_links}"
    )
    
    assert len(actual_links) == 5, (
        f"Leg {leg_num} should have exactly 5 links, but has {len(actual_links)}: {actual_links}"
    )


if __name__ == "__main__":
    # Run the property test for all legs
    print("Running property-based test: Complete Link Structure")
    print("=" * 70)
    
    try:
        test_complete_link_structure_property()
        print("\n✓ Property test PASSED: All legs have complete link structure")
        print("  Verified: Each leg (1-4) has exactly 5 links with correct naming")
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        exit(1)
