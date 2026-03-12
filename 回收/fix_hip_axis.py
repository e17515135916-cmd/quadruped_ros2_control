#!/usr/bin/env python3
"""
Script to modify hip_axis parameter in dog2.urdf.xacro

This script changes the hip_axis parameter from "0 0 -1" to "1 0 0" for all four legs.
It uses lxml to parse and modify the XML file while preserving formatting.

Requirements: 5.1, 5.2, 1.1, 1.2, 1.3, 1.4
"""

import os
import sys
from datetime import datetime
from lxml import etree
import shutil


class HipAxisModifier:
    """Class to handle hip_axis parameter modification in xacro files"""
    
    def __init__(self, xacro_file_path):
        """
        Initialize the modifier with the xacro file path
        
        Args:
            xacro_file_path: Path to the dog2.urdf.xacro file
        """
        self.xacro_file_path = xacro_file_path
        self.tree = None
        self.root = None
        self.namespace = {'xacro': 'http://www.ros.org/wiki/xacro'}
        
    def read_and_parse(self):
        """
        Read and parse the xacro file using lxml
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(self.xacro_file_path):
                print(f"Error: File not found: {self.xacro_file_path}")
                return False
            
            # Parse the XML file
            parser = etree.XMLParser(remove_blank_text=False, strip_cdata=False)
            self.tree = etree.parse(self.xacro_file_path, parser)
            self.root = self.tree.getroot()
            
            print(f"Successfully parsed: {self.xacro_file_path}")
            return True
            
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False
    
    def find_leg_instantiations(self):
        """
        Find all four leg instantiation elements in the xacro file
        
        Returns:
            list: List of leg elements with their leg_num attribute
        """
        leg_elements = []
        
        try:
            # Find all xacro:leg elements (try both with and without namespace)
            # First try with namespace
            for elem in self.root.iter('{http://www.ros.org/wiki/xacro}leg'):
                leg_num = elem.get('leg_num')
                if leg_num in ['1', '2', '3', '4']:
                    leg_elements.append(elem)
                    print(f"Found leg instantiation: leg_num={leg_num}")
            
            # If no elements found, try without namespace (in case of different parsing)
            if not leg_elements:
                for elem in self.root.iter():
                    if elem.tag.endswith('leg') and 'leg' in elem.tag:
                        leg_num = elem.get('leg_num')
                        if leg_num in ['1', '2', '3', '4']:
                            leg_elements.append(elem)
                            print(f"Found leg instantiation: leg_num={leg_num}")
            
            if len(leg_elements) != 4:
                print(f"Warning: Expected 4 leg instantiations, found {len(leg_elements)}")
            
            return leg_elements
            
        except Exception as e:
            print(f"Error finding leg instantiations: {e}")
            return []
    
    def modify_hip_axis(self, leg_elements, old_value="0 0 -1", new_value="1 0 0"):
        """
        Modify the hip_axis parameter for all leg elements
        
        Args:
            leg_elements: List of leg elements to modify
            old_value: Expected old value of hip_axis (default: "0 0 -1")
            new_value: New value for hip_axis (default: "1 0 0")
            
        Returns:
            dict: Dictionary with modification results for each leg
        """
        results = {}
        
        for leg_elem in leg_elements:
            leg_num = leg_elem.get('leg_num')
            current_value = leg_elem.get('hip_axis')
            
            if current_value is None:
                # hip_axis parameter doesn't exist, add it
                leg_elem.set('hip_axis', new_value)
                results[leg_num] = {
                    'status': 'added',
                    'old_value': None,
                    'new_value': new_value,
                    'message': f'Added hip_axis parameter with value "{new_value}"'
                }
                print(f"Leg {leg_num}: {results[leg_num]['message']}")
                continue
            
            # Modify the value
            leg_elem.set('hip_axis', new_value)
            
            results[leg_num] = {
                'status': 'modified',
                'old_value': current_value,
                'new_value': new_value,
                'message': f'Changed hip_axis from "{current_value}" to "{new_value}"'
            }
            print(f"Leg {leg_num}: {results[leg_num]['message']}")
        
        return results
    
    def write_file(self, backup=True):
        """
        Write the modified content back to the file
        
        Args:
            backup: Whether to create a backup before writing (default: True)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup if requested
            if backup:
                backup_path = self.create_backup()
                if backup_path:
                    print(f"Backup created: {backup_path}")
            
            # Get original file permissions
            original_stat = os.stat(self.xacro_file_path)
            
            # Write the modified tree to file
            self.tree.write(
                self.xacro_file_path,
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True
            )
            
            # Restore original permissions
            os.chmod(self.xacro_file_path, original_stat.st_mode)
            
            print(f"Successfully wrote modified file: {self.xacro_file_path}")
            return True
            
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    def create_backup(self):
        """
        Create a timestamped backup of the original file
        
        Returns:
            str: Path to backup file, or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.xacro_file_path}.backup_{timestamp}"
            
            shutil.copy2(self.xacro_file_path, backup_path)
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None


def main():
    """Main function to execute the hip_axis modification"""
    
    # Default path to xacro file
    default_path = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    # Allow custom path from command line
    xacro_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    print("=" * 60)
    print("Hip Axis Modifier Script")
    print("=" * 60)
    print(f"Target file: {xacro_path}")
    print()
    
    # Create modifier instance
    modifier = HipAxisModifier(xacro_path)
    
    # Step 1: Read and parse the file
    print("Step 1: Reading and parsing xacro file...")
    if not modifier.read_and_parse():
        print("Failed to read and parse file. Exiting.")
        return 1
    print()
    
    # Step 2: Find leg instantiations
    print("Step 2: Finding leg instantiations...")
    leg_elements = modifier.find_leg_instantiations()
    if not leg_elements:
        print("No leg instantiations found. Exiting.")
        return 1
    print()
    
    # Step 3: Modify hip_axis parameters
    print("Step 3: Modifying hip_axis parameters...")
    results = modifier.modify_hip_axis(leg_elements)
    print()
    
    # Step 4: Write modified file
    print("Step 4: Writing modified file...")
    if not modifier.write_file(backup=True):
        print("Failed to write file. Exiting.")
        return 1
    print()
    
    # Print summary
    print("=" * 60)
    print("Modification Summary:")
    print("=" * 60)
    for leg_num, result in sorted(results.items()):
        print(f"Leg {leg_num}: {result['status']}")
        if result['status'] in ['modified', 'added']:
            if result['old_value']:
                print(f"  Old value: {result['old_value']}")
            print(f"  New value: {result['new_value']}")
    print()
    
    print("Hip axis modification completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
