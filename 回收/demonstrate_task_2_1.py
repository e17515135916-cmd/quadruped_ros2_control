#!/usr/bin/env python3
"""
Demonstration script for Task 2.1: Read and parse xacro file

This script demonstrates that the HipAxisModifier class can:
1. Use lxml to parse XML
2. Locate four leg instantiation statements

Requirements: 5.1, 5.2
"""

from fix_hip_axis import HipAxisModifier

def main():
    print("=" * 70)
    print("Task 2.1 Demonstration: Read and Parse Xacro File")
    print("=" * 70)
    print()
    
    # Initialize the modifier
    xacro_path = "src/dog2_description/urdf/dog2.urdf.xacro"
    modifier = HipAxisModifier(xacro_path)
    
    # Requirement 5.1: Use lxml to parse XML
    print("✓ Requirement 5.1: Using lxml to parse XML")
    if not modifier.read_and_parse():
        print("✗ Failed to parse file")
        return 1
    print(f"  Successfully parsed: {xacro_path}")
    print(f"  Parser: lxml.etree")
    print(f"  Root element: {modifier.root.tag}")
    print()
    
    # Requirement 5.2: Locate four leg instantiation statements
    print("✓ Requirement 5.2: Locating four leg instantiation statements")
    leg_elements = modifier.find_leg_instantiations()
    
    if len(leg_elements) != 4:
        print(f"✗ Expected 4 legs, found {len(leg_elements)}")
        return 1
    
    print(f"  Found {len(leg_elements)} leg instantiations:")
    for elem in leg_elements:
        leg_num = elem.get('leg_num')
        num_attrs = len(elem.attrib)
        print(f"    - Leg {leg_num}: {num_attrs} attributes")
    print()
    
    print("=" * 70)
    print("✓ Task 2.1 COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✓ Script can read and parse xacro files using lxml")
    print("  ✓ Script can locate all four leg instantiation statements")
    print("  ✓ Ready for Task 2.2: Implement hip_axis parameter replacement")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
