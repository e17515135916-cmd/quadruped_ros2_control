#!/usr/bin/env python3
"""
Verification script for hip_axis modification

This script verifies that all four legs have hip_axis="1 0 0" in the URDF xacro file.
Requirements: 1.1, 1.2, 1.3, 1.4, 5.2
"""

from lxml import etree
import sys


def verify_hip_axis(xacro_file_path):
    """
    Verify that all four legs have hip_axis="1 0 0"
    
    Args:
        xacro_file_path: Path to the dog2.urdf.xacro file
        
    Returns:
        bool: True if all legs have correct hip_axis, False otherwise
    """
    try:
        # Parse the XML file
        parser = etree.XMLParser(remove_blank_text=False, strip_cdata=False)
        tree = etree.parse(xacro_file_path, parser)
        root = tree.getroot()
        
        print("=" * 60)
        print("Hip Axis Verification")
        print("=" * 60)
        print(f"File: {xacro_file_path}\n")
        
        # Find all xacro:leg elements
        leg_elements = []
        for elem in root.iter('{http://www.ros.org/wiki/xacro}leg'):
            leg_num = elem.get('leg_num')
            if leg_num in ['1', '2', '3', '4']:
                leg_elements.append(elem)
        
        if not leg_elements:
            # Try without namespace
            for elem in root.iter():
                if elem.tag.endswith('leg') and 'leg' in elem.tag:
                    leg_num = elem.get('leg_num')
                    if leg_num in ['1', '2', '3', '4']:
                        leg_elements.append(elem)
        
        if len(leg_elements) != 4:
            print(f"❌ Error: Expected 4 leg instantiations, found {len(leg_elements)}")
            return False
        
        # Check each leg's hip_axis parameter
        all_correct = True
        expected_value = "1 0 0"
        
        for leg_elem in sorted(leg_elements, key=lambda e: e.get('leg_num')):
            leg_num = leg_elem.get('leg_num')
            hip_axis = leg_elem.get('hip_axis')
            
            if hip_axis == expected_value:
                print(f"✓ Leg {leg_num}: hip_axis = \"{hip_axis}\" ✓")
            else:
                print(f"✗ Leg {leg_num}: hip_axis = \"{hip_axis}\" (expected \"{expected_value}\") ✗")
                all_correct = False
        
        print("\n" + "=" * 60)
        if all_correct:
            print("✓ VERIFICATION PASSED: All legs have correct hip_axis")
            print("=" * 60)
            print("\nRequirements validated:")
            print("  - 1.1: j11 has axis definition '1 0 0' ✓")
            print("  - 1.2: j21 has axis definition '1 0 0' ✓")
            print("  - 1.3: j31 has axis definition '1 0 0' ✓")
            print("  - 1.4: j41 has axis definition '1 0 0' ✓")
            print("  - 5.2: hip_axis changed from '0 0 -1' to '1 0 0' ✓")
            return True
        else:
            print("✗ VERIFICATION FAILED: Some legs have incorrect hip_axis")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


def main():
    """Main function"""
    xacro_path = sys.argv[1] if len(sys.argv) > 1 else "src/dog2_description/urdf/dog2.urdf.xacro"
    
    success = verify_hip_axis(xacro_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
