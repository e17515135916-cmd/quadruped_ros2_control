#!/usr/bin/env python3
"""
Unit tests for hip_axis modifier script

Tests file reading, parameter location, and parameter replacement functionality.
Requirements: 1.1, 1.2, 1.3, 1.4
"""

import pytest
import os
import tempfile
import shutil
from lxml import etree
import sys

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fix_hip_axis import HipAxisModifier


# Sample xacro content for testing
SAMPLE_XACRO = """<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog2">
  <xacro:macro name="leg" params="leg_num hip_axis:='0 0 -1'">
    <joint name="j${leg_num}1" type="revolute">
      <axis xyz="${hip_axis}"/>
    </joint>
  </xacro:macro>
  
  <xacro:leg leg_num="1" hip_axis="0 0 -1"/>
  <xacro:leg leg_num="2" hip_axis="0 0 -1"/>
  <xacro:leg leg_num="3" hip_axis="0 0 -1"/>
  <xacro:leg leg_num="4" hip_axis="0 0 -1"/>
</robot>
"""


class TestHipAxisModifier:
    """Test suite for HipAxisModifier class"""
    
    @pytest.fixture
    def temp_xacro_file(self):
        """Create a temporary xacro file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xacro', delete=False) as f:
            f.write(SAMPLE_XACRO)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Also cleanup any backup files
        backup_pattern = f"{temp_path}.backup_"
        for file in os.listdir(os.path.dirname(temp_path)):
            if file.startswith(os.path.basename(temp_path)) and '.backup_' in file:
                os.remove(os.path.join(os.path.dirname(temp_path), file))
    
    def test_file_reading(self, temp_xacro_file):
        """Test 1: Verify file reading functionality"""
        modifier = HipAxisModifier(temp_xacro_file)
        
        # Should successfully read and parse the file
        assert modifier.read_and_parse() == True
        assert modifier.tree is not None
        assert modifier.root is not None
        
        # Root element should be 'robot'
        assert modifier.root.tag == 'robot'
    
    def test_file_not_found(self):
        """Test 2: Verify error handling for non-existent file"""
        modifier = HipAxisModifier("/nonexistent/path/file.xacro")
        
        # Should fail gracefully
        assert modifier.read_and_parse() == False
    
    def test_find_leg_instantiations(self, temp_xacro_file):
        """Test 3: Verify finding all four leg instantiations"""
        modifier = HipAxisModifier(temp_xacro_file)
        modifier.read_and_parse()
        
        leg_elements = modifier.find_leg_instantiations()
        
        # Should find exactly 4 leg elements
        assert len(leg_elements) == 4
        
        # Should have leg_num 1, 2, 3, 4
        leg_nums = [elem.get('leg_num') for elem in leg_elements]
        assert sorted(leg_nums) == ['1', '2', '3', '4']
    
    def test_parameter_location(self, temp_xacro_file):
        """Test 4: Verify locating hip_axis parameter in each leg"""
        modifier = HipAxisModifier(temp_xacro_file)
        modifier.read_and_parse()
        leg_elements = modifier.find_leg_instantiations()
        
        # Each leg should have hip_axis parameter
        for leg_elem in leg_elements:
            hip_axis = leg_elem.get('hip_axis')
            assert hip_axis is not None
            assert hip_axis == "0 0 -1"
    
    def test_parameter_replacement(self, temp_xacro_file):
        """Test 5: Verify parameter replacement functionality"""
        modifier = HipAxisModifier(temp_xacro_file)
        modifier.read_and_parse()
        leg_elements = modifier.find_leg_instantiations()
        
        # Modify hip_axis parameters
        results = modifier.modify_hip_axis(leg_elements, old_value="0 0 -1", new_value="1 0 0")
        
        # Should have results for all 4 legs
        assert len(results) == 4
        
        # All legs should be modified successfully
        for leg_num in ['1', '2', '3', '4']:
            assert leg_num in results
            assert results[leg_num]['status'] == 'modified'
            assert results[leg_num]['old_value'] == "0 0 -1"
            assert results[leg_num]['new_value'] == "1 0 0"
        
        # Verify the actual elements were modified
        for leg_elem in leg_elements:
            assert leg_elem.get('hip_axis') == "1 0 0"
    
    def test_backup_creation(self, temp_xacro_file):
        """Test 6: Verify backup file creation"""
        modifier = HipAxisModifier(temp_xacro_file)
        
        backup_path = modifier.create_backup()
        
        # Backup should be created
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert backup_path.startswith(temp_xacro_file)
        assert '.backup_' in backup_path
        
        # Backup content should match original
        with open(temp_xacro_file, 'r') as f1, open(backup_path, 'r') as f2:
            assert f1.read() == f2.read()
        
        # Cleanup backup
        os.remove(backup_path)
    
    def test_file_writing(self, temp_xacro_file):
        """Test 7: Verify file writing preserves structure"""
        modifier = HipAxisModifier(temp_xacro_file)
        modifier.read_and_parse()
        leg_elements = modifier.find_leg_instantiations()
        modifier.modify_hip_axis(leg_elements)
        
        # Write the file
        assert modifier.write_file(backup=True) == True
        
        # Verify backup was created
        backup_files = [f for f in os.listdir(os.path.dirname(temp_xacro_file)) 
                       if f.startswith(os.path.basename(temp_xacro_file)) and '.backup_' in f]
        assert len(backup_files) > 0
        
        # Re-parse the written file to verify changes
        modifier2 = HipAxisModifier(temp_xacro_file)
        modifier2.read_and_parse()
        leg_elements2 = modifier2.find_leg_instantiations()
        
        # All legs should have new hip_axis value
        for leg_elem in leg_elements2:
            assert leg_elem.get('hip_axis') == "1 0 0"
    
    def test_file_permissions_preserved(self, temp_xacro_file):
        """Test 8: Verify file permissions are preserved after writing"""
        # Set specific permissions
        os.chmod(temp_xacro_file, 0o644)
        original_mode = os.stat(temp_xacro_file).st_mode
        
        modifier = HipAxisModifier(temp_xacro_file)
        modifier.read_and_parse()
        leg_elements = modifier.find_leg_instantiations()
        modifier.modify_hip_axis(leg_elements)
        modifier.write_file(backup=False)
        
        # Permissions should be preserved
        new_mode = os.stat(temp_xacro_file).st_mode
        assert original_mode == new_mode
    
    def test_missing_hip_axis_parameter(self):
        """Test 9: Verify handling of missing hip_axis parameter"""
        # Create xacro without hip_axis parameter
        xacro_no_param = """<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog2">
  <xacro:leg leg_num="1"/>
</robot>
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xacro', delete=False) as f:
            f.write(xacro_no_param)
            temp_path = f.name
        
        try:
            modifier = HipAxisModifier(temp_path)
            modifier.read_and_parse()
            leg_elements = modifier.find_leg_instantiations()
            results = modifier.modify_hip_axis(leg_elements)
            
            # Should add the parameter when it's missing
            assert '1' in results
            assert results['1']['status'] == 'added'
            assert results['1']['new_value'] == '1 0 0'
            assert results['1']['old_value'] is None
        finally:
            os.remove(temp_path)
    
    def test_end_to_end_modification(self, temp_xacro_file):
        """Test 10: End-to-end modification workflow"""
        modifier = HipAxisModifier(temp_xacro_file)
        
        # Complete workflow
        assert modifier.read_and_parse() == True
        leg_elements = modifier.find_leg_instantiations()
        assert len(leg_elements) == 4
        
        results = modifier.modify_hip_axis(leg_elements)
        assert all(r['status'] == 'modified' for r in results.values())
        
        assert modifier.write_file(backup=True) == True
        
        # Verify final result
        modifier2 = HipAxisModifier(temp_xacro_file)
        modifier2.read_and_parse()
        leg_elements2 = modifier2.find_leg_instantiations()
        
        for leg_elem in leg_elements2:
            assert leg_elem.get('hip_axis') == "1 0 0"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
