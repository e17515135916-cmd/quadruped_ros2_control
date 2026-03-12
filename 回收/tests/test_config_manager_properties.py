#!/usr/bin/env python3
"""
Property-Based Tests: ConfigManager Configuration Loading Robustness

Feature: presentation-visualization-system, Property 19: Configuration Loading Robustness
Validates: Requirements 9.1

This test verifies that for any valid YAML configuration file, the ConfigManager
should successfully load all sections without raising exceptions, and all required
fields should have non-null values.
"""

import tempfile
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings
from presentation_viz import ConfigManager


# Strategy for generating valid color codes
@st.composite
def valid_color_code(draw):
    """Generate valid hex color codes."""
    color_type = draw(st.sampled_from(['hex3', 'hex6', 'rgb']))
    
    if color_type == 'hex3':
        # 3-digit hex color
        hex_chars = '0123456789abcdef'
        color = '#' + ''.join(draw(st.lists(st.sampled_from(hex_chars), min_size=3, max_size=3)))
        return color
    elif color_type == 'hex6':
        # 6-digit hex color
        hex_chars = '0123456789abcdef'
        color = '#' + ''.join(draw(st.lists(st.sampled_from(hex_chars), min_size=6, max_size=6)))
        return color
    else:
        # RGB format
        r = draw(st.integers(min_value=0, max_value=255))
        g = draw(st.integers(min_value=0, max_value=255))
        b = draw(st.integers(min_value=0, max_value=255))
        return f'rgb({r}, {g}, {b})'


# Strategy for generating valid configuration dictionaries
@st.composite
def valid_config_dict(draw):
    """Generate valid configuration dictionaries with various combinations of fields."""
    config = {}
    
    # Randomly include style section
    if draw(st.booleans()):
        style = {}
        
        # Randomly include various style fields
        if draw(st.booleans()):
            style['color_scheme'] = draw(st.sampled_from(['dark_tech', 'light_professional', 'custom']))
        
        if draw(st.booleans()):
            style['background_color'] = draw(valid_color_code())
        
        if draw(st.booleans()):
            style['primary_color'] = draw(valid_color_code())
        
        if draw(st.booleans()):
            style['secondary_color'] = draw(valid_color_code())
        
        if draw(st.booleans()):
            style['font_family'] = draw(st.sampled_from(['Arial', 'Helvetica', 'Times New Roman', 'Courier']))
        
        if draw(st.booleans()):
            style['font_size_title'] = draw(st.integers(min_value=8, max_value=72))
        
        if draw(st.booleans()):
            style['font_size_label'] = draw(st.integers(min_value=6, max_value=48))
        
        if draw(st.booleans()):
            style['dpi'] = draw(st.integers(min_value=72, max_value=600))
        
        if style:  # Only add if not empty
            config['style'] = style
    
    # Randomly include data_sources section
    if draw(st.booleans()):
        data_sources = {}
        
        if draw(st.booleans()):
            data_sources['urdf_path'] = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
        
        if draw(st.booleans()):
            data_sources['joint_states_topic'] = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
        
        if draw(st.booleans()):
            data_sources['imu_topic'] = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
        
        if draw(st.booleans()):
            data_sources['odom_topic'] = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
        
        if data_sources:  # Only add if not empty
            config['data_sources'] = data_sources
    
    # Randomly include output section
    if draw(st.booleans()):
        output = {}
        
        if draw(st.booleans()):
            output['directory'] = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
        
        if draw(st.booleans()):
            output['format'] = draw(st.sampled_from(['png', 'jpg', 'jpeg', 'svg', 'pdf']))
        
        if draw(st.booleans()):
            output['preview_enabled'] = draw(st.booleans())
        
        if output:  # Only add if not empty
            config['output'] = output
    
    # Randomly include module-specific sections
    if draw(st.booleans()):
        config['kinematic_diagram'] = {
            'view': draw(st.sampled_from(['side', 'top', 'front'])),
            'show_coordinate_frames': draw(st.booleans())
        }
    
    if draw(st.booleans()):
        config['workspace_analysis'] = {
            'leg_id': draw(st.sampled_from(['FL', 'FR', 'RL', 'RR'])),
            'rail_extension': draw(st.floats(min_value=0.0, max_value=0.5)),
            'resolution': draw(st.integers(min_value=10, max_value=200))
        }
    
    return config


@settings(max_examples=100)
@given(config_data=valid_config_dict())
def test_property_19_configuration_loading_robustness(config_data):
    """
    Property Test: Configuration Loading Robustness
    
    Feature: presentation-visualization-system, Property 19: Configuration Loading Robustness
    Validates: Requirements 9.1
    
    For any valid YAML configuration file, the ConfigManager should successfully
    load all sections without raising exceptions, and all required fields should
    have non-null values.
    
    This property validates that:
    1. ConfigManager can load any valid YAML configuration without exceptions
    2. All required default fields remain accessible after loading
    3. User-provided values are correctly merged with defaults
    4. The system remains functional even with partial configurations
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Write the generated config to a file
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Attempt to load the configuration - should not raise exceptions
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager failed to load valid YAML configuration: {e}\n"
                f"Configuration data: {config_data}"
            )
        
        # Verify all required sections are accessible (should have defaults if not provided)
        style = config_manager.get_style()
        assert style is not None, "Style configuration should never be None"
        assert isinstance(style, dict), "Style configuration should be a dictionary"
        
        data_sources = config_manager.get_data_sources()
        assert data_sources is not None, "Data sources configuration should never be None"
        assert isinstance(data_sources, dict), "Data sources configuration should be a dictionary"
        
        output = config_manager.get_output_config()
        assert output is not None, "Output configuration should never be None"
        assert isinstance(output, dict), "Output configuration should be a dictionary"
        
        # Verify all required fields have non-null values (from defaults or user config)
        # Style required fields
        assert 'color_scheme' in style, "color_scheme should always be present"
        assert style['color_scheme'] is not None, "color_scheme should not be None"
        
        assert 'background_color' in style, "background_color should always be present"
        assert style['background_color'] is not None, "background_color should not be None"
        
        assert 'primary_color' in style, "primary_color should always be present"
        assert style['primary_color'] is not None, "primary_color should not be None"
        
        assert 'dpi' in style, "dpi should always be present"
        assert style['dpi'] is not None, "dpi should not be None"
        assert isinstance(style['dpi'], (int, float)), "dpi should be numeric"
        
        # Data sources required fields
        assert 'urdf_path' in data_sources, "urdf_path should always be present"
        assert data_sources['urdf_path'] is not None, "urdf_path should not be None"
        
        assert 'joint_states_topic' in data_sources, "joint_states_topic should always be present"
        assert data_sources['joint_states_topic'] is not None, "joint_states_topic should not be None"
        
        # Output required fields
        assert 'directory' in output, "directory should always be present"
        assert output['directory'] is not None, "directory should not be None"
        
        assert 'format' in output, "format should always be present"
        assert output['format'] is not None, "format should not be None"
        
        # Verify user-provided values are correctly applied
        if 'style' in config_data:
            user_style = config_data['style']
            if 'dpi' in user_style:
                assert style['dpi'] == user_style['dpi'], (
                    f"User-provided DPI value should be applied: "
                    f"expected {user_style['dpi']}, got {style['dpi']}"
                )
            if 'background_color' in user_style:
                assert style['background_color'] == user_style['background_color'], (
                    f"User-provided background_color should be applied"
                )
        
        if 'output' in config_data:
            user_output = config_data['output']
            if 'directory' in user_output:
                assert output['directory'] == user_output['directory'], (
                    f"User-provided output directory should be applied"
                )
            if 'format' in user_output:
                assert output['format'] == user_output['format'], (
                    f"User-provided output format should be applied"
                )


@settings(max_examples=50)
@given(st.text(min_size=0, max_size=1000))
def test_property_19_empty_and_invalid_yaml_robustness(yaml_content):
    """
    Property Test: Empty and Invalid YAML Robustness
    
    For any string content (including empty, invalid YAML), ConfigManager should
    handle it gracefully without crashing and fall back to defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Write arbitrary content to file
        with open(config_file, 'w') as f:
            f.write(yaml_content)
        
        # Should not raise exceptions, even with invalid YAML
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle invalid YAML gracefully, but raised: {e}\n"
                f"YAML content: {repr(yaml_content[:100])}"
            )
        
        # Should still have valid default configuration
        style = config_manager.get_style()
        assert style is not None
        assert 'dpi' in style
        assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi']


@settings(max_examples=50)
@given(st.none() | st.text(min_size=1, max_size=200))
def test_property_19_missing_file_robustness(config_path):
    """
    Property Test: Missing File Robustness
    
    For any file path (including None or non-existent paths), ConfigManager should
    handle it gracefully and use default configuration.
    """
    if config_path is not None:
        # Create a path that definitely doesn't exist
        config_path = f"/tmp/nonexistent_{hash(config_path)}_config.yaml"
    
    # Should not raise exceptions
    try:
        config_manager = ConfigManager(config_path)
    except Exception as e:
        raise AssertionError(
            f"ConfigManager should handle missing files gracefully, but raised: {e}\n"
            f"Config path: {config_path}"
        )
    
    # Should have valid default configuration
    style = config_manager.get_style()
    assert style is not None
    assert 'color_scheme' in style
    assert style['color_scheme'] == ConfigManager.DEFAULT_CONFIG['style']['color_scheme']
    
    output = config_manager.get_output_config()
    assert output is not None
    assert 'directory' in output
    assert output['directory'] == ConfigManager.DEFAULT_CONFIG['output']['directory']


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ConfigManager Configuration Loading Robustness")
    print("=" * 80)
    
    try:
        print("\n1. Testing valid configuration loading...")
        test_property_19_configuration_loading_robustness()
        print("   ✓ PASSED: Valid configurations load successfully")
        
        print("\n2. Testing empty and invalid YAML robustness...")
        test_property_19_empty_and_invalid_yaml_robustness()
        print("   ✓ PASSED: Invalid YAML handled gracefully")
        
        print("\n3. Testing missing file robustness...")
        test_property_19_missing_file_robustness()
        print("   ✓ PASSED: Missing files handled gracefully")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: ConfigManager loads any valid YAML without exceptions")
        print("  Verified: All required fields have non-null values")
        print("  Verified: Invalid YAML and missing files handled gracefully")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
