#!/usr/bin/env python3
"""
Property-Based Tests: ConfigManager Configuration Application

Feature: presentation-visualization-system, Property 20: Configuration Application
Validates: Requirements 9.2, 9.3, 9.4

This test verifies that for any configuration parameter (color, font, data source),
when specified in the config file, the generated outputs should reflect that parameter.
"""

import tempfile
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from presentation_viz import ConfigManager


# Strategy for generating valid color codes
@st.composite
def valid_color_code(draw):
    """Generate valid hex color codes."""
    color_type = draw(st.sampled_from(['hex3', 'hex6']))
    
    if color_type == 'hex3':
        # 3-digit hex color
        hex_chars = '0123456789abcdef'
        color = '#' + ''.join(draw(st.lists(st.sampled_from(hex_chars), min_size=3, max_size=3)))
        return color
    else:
        # 6-digit hex color
        hex_chars = '0123456789abcdef'
        color = '#' + ''.join(draw(st.lists(st.sampled_from(hex_chars), min_size=6, max_size=6)))
        return color


@settings(max_examples=100)
@given(
    background_color=valid_color_code(),
    primary_color=valid_color_code(),
    secondary_color=valid_color_code()
)
def test_property_20_color_configuration_application(background_color, primary_color, secondary_color):
    """
    Property Test: Color Configuration Application
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.2
    
    For any valid color configuration, when specified in the config file,
    the ConfigManager should return exactly those color values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with specific colors
        config_data = {
            'style': {
                'background_color': background_color,
                'primary_color': primary_color,
                'secondary_color': secondary_color
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        style = config_manager.get_style()
        
        # Verify colors are applied exactly as specified
        assert style['background_color'] == background_color, (
            f"Background color not applied correctly: "
            f"expected {background_color}, got {style['background_color']}"
        )
        
        assert style['primary_color'] == primary_color, (
            f"Primary color not applied correctly: "
            f"expected {primary_color}, got {style['primary_color']}"
        )
        
        assert style['secondary_color'] == secondary_color, (
            f"Secondary color not applied correctly: "
            f"expected {secondary_color}, got {style['secondary_color']}"
        )


@settings(max_examples=100)
@given(
    font_family=st.sampled_from(['Arial', 'Helvetica', 'Times New Roman', 'Courier', 'Verdana', 'Georgia']),
    font_size_title=st.integers(min_value=8, max_value=72),
    font_size_label=st.integers(min_value=6, max_value=48),
    dpi=st.integers(min_value=72, max_value=600)
)
def test_property_20_font_configuration_application(font_family, font_size_title, font_size_label, dpi):
    """
    Property Test: Font Configuration Application
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.3
    
    For any valid font configuration, when specified in the config file,
    the ConfigManager should return exactly those font values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with specific fonts
        config_data = {
            'style': {
                'font_family': font_family,
                'font_size_title': font_size_title,
                'font_size_label': font_size_label,
                'dpi': dpi
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        style = config_manager.get_style()
        
        # Verify fonts are applied exactly as specified
        assert style['font_family'] == font_family, (
            f"Font family not applied correctly: "
            f"expected {font_family}, got {style['font_family']}"
        )
        
        assert style['font_size_title'] == font_size_title, (
            f"Title font size not applied correctly: "
            f"expected {font_size_title}, got {style['font_size_title']}"
        )
        
        assert style['font_size_label'] == font_size_label, (
            f"Label font size not applied correctly: "
            f"expected {font_size_label}, got {style['font_size_label']}"
        )
        
        assert style['dpi'] == dpi, (
            f"DPI not applied correctly: "
            f"expected {dpi}, got {style['dpi']}"
        )


@settings(max_examples=100)
@given(
    urdf_path=st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_.-'
    )),
    joint_states_topic=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    )),
    imu_topic=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    )),
    odom_topic=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    ))
)
def test_property_20_data_source_configuration_application(urdf_path, joint_states_topic, imu_topic, odom_topic):
    """
    Property Test: Data Source Configuration Application
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.4
    
    For any valid data source configuration, when specified in the config file,
    the ConfigManager should return exactly those data source values.
    """
    # Ensure topics start with '/' (ROS convention)
    if not joint_states_topic.startswith('/'):
        joint_states_topic = '/' + joint_states_topic
    if not imu_topic.startswith('/'):
        imu_topic = '/' + imu_topic
    if not odom_topic.startswith('/'):
        odom_topic = '/' + odom_topic
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with specific data sources
        config_data = {
            'data_sources': {
                'urdf_path': urdf_path,
                'joint_states_topic': joint_states_topic,
                'imu_topic': imu_topic,
                'odom_topic': odom_topic
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        data_sources = config_manager.get_data_sources()
        
        # Verify data sources are applied exactly as specified
        assert data_sources['urdf_path'] == urdf_path, (
            f"URDF path not applied correctly: "
            f"expected {urdf_path}, got {data_sources['urdf_path']}"
        )
        
        assert data_sources['joint_states_topic'] == joint_states_topic, (
            f"Joint states topic not applied correctly: "
            f"expected {joint_states_topic}, got {data_sources['joint_states_topic']}"
        )
        
        assert data_sources['imu_topic'] == imu_topic, (
            f"IMU topic not applied correctly: "
            f"expected {imu_topic}, got {data_sources['imu_topic']}"
        )
        
        assert data_sources['odom_topic'] == odom_topic, (
            f"Odom topic not applied correctly: "
            f"expected {odom_topic}, got {data_sources['odom_topic']}"
        )


@settings(max_examples=100)
@given(
    output_directory=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_-'
    )),
    output_format=st.sampled_from(['png', 'jpg', 'jpeg', 'svg', 'pdf']),
    preview_enabled=st.booleans()
)
def test_property_20_output_configuration_application(output_directory, output_format, preview_enabled):
    """
    Property Test: Output Configuration Application
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.2, 9.4
    
    For any valid output configuration, when specified in the config file,
    the ConfigManager should return exactly those output values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with specific output settings
        config_data = {
            'output': {
                'directory': output_directory,
                'format': output_format,
                'preview_enabled': preview_enabled
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        output = config_manager.get_output_config()
        
        # Verify output settings are applied exactly as specified
        assert output['directory'] == output_directory, (
            f"Output directory not applied correctly: "
            f"expected {output_directory}, got {output['directory']}"
        )
        
        assert output['format'] == output_format, (
            f"Output format not applied correctly: "
            f"expected {output_format}, got {output['format']}"
        )
        
        assert output['preview_enabled'] == preview_enabled, (
            f"Preview enabled not applied correctly: "
            f"expected {preview_enabled}, got {output['preview_enabled']}"
        )


@settings(max_examples=50)
@given(
    color=valid_color_code(),
    font=st.sampled_from(['Arial', 'Helvetica', 'Courier']),
    dpi=st.integers(min_value=72, max_value=600),
    topic=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    ))
)
def test_property_20_mixed_configuration_application(color, font, dpi, topic):
    """
    Property Test: Mixed Configuration Application
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.2, 9.3, 9.4
    
    For any combination of configuration parameters across different sections,
    all specified values should be correctly applied.
    """
    # Ensure topic starts with '/'
    if not topic.startswith('/'):
        topic = '/' + topic
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with mixed settings
        config_data = {
            'style': {
                'background_color': color,
                'font_family': font,
                'dpi': dpi
            },
            'data_sources': {
                'joint_states_topic': topic
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        style = config_manager.get_style()
        data_sources = config_manager.get_data_sources()
        
        # Verify all settings are applied correctly
        assert style['background_color'] == color
        assert style['font_family'] == font
        assert style['dpi'] == dpi
        assert data_sources['joint_states_topic'] == topic
        
        # Verify defaults are still present for unspecified values
        assert 'primary_color' in style
        assert 'urdf_path' in data_sources


@settings(max_examples=50)
@given(
    partial_style=st.booleans(),
    partial_data=st.booleans(),
    partial_output=st.booleans()
)
def test_property_20_partial_configuration_with_defaults(partial_style, partial_data, partial_output):
    """
    Property Test: Partial Configuration with Defaults
    
    Feature: presentation-visualization-system, Property 20: Configuration Application
    Validates: Requirements 9.2, 9.3, 9.4
    
    For any partial configuration (some sections present, some missing),
    specified values should be applied while defaults fill in the gaps.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        config_data = {}
        
        # Randomly include partial sections
        if partial_style:
            config_data['style'] = {'dpi': 450}  # Only override DPI
        
        if partial_data:
            config_data['data_sources'] = {'joint_states_topic': '/custom/joints'}
        
        if partial_output:
            config_data['output'] = {'format': 'svg'}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        style = config_manager.get_style()
        data_sources = config_manager.get_data_sources()
        output = config_manager.get_output_config()
        
        # Verify specified values are applied
        if partial_style:
            assert style['dpi'] == 450, "Specified DPI should be applied"
        else:
            assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi'], "Default DPI should be used"
        
        if partial_data:
            assert data_sources['joint_states_topic'] == '/custom/joints', "Specified topic should be applied"
        else:
            assert data_sources['joint_states_topic'] == ConfigManager.DEFAULT_CONFIG['data_sources']['joint_states_topic']
        
        if partial_output:
            assert output['format'] == 'svg', "Specified format should be applied"
        else:
            assert output['format'] == ConfigManager.DEFAULT_CONFIG['output']['format']
        
        # Verify all required fields are present (from defaults or user config)
        assert 'background_color' in style
        assert 'primary_color' in style
        assert 'font_family' in style
        assert 'urdf_path' in data_sources
        assert 'imu_topic' in data_sources
        assert 'directory' in output


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ConfigManager Configuration Application")
    print("=" * 80)
    
    try:
        print("\n1. Testing color configuration application...")
        test_property_20_color_configuration_application()
        print("   ✓ PASSED: Color configurations applied correctly")
        
        print("\n2. Testing font configuration application...")
        test_property_20_font_configuration_application()
        print("   ✓ PASSED: Font configurations applied correctly")
        
        print("\n3. Testing data source configuration application...")
        test_property_20_data_source_configuration_application()
        print("   ✓ PASSED: Data source configurations applied correctly")
        
        print("\n4. Testing output configuration application...")
        test_property_20_output_configuration_application()
        print("   ✓ PASSED: Output configurations applied correctly")
        
        print("\n5. Testing mixed configuration application...")
        test_property_20_mixed_configuration_application()
        print("   ✓ PASSED: Mixed configurations applied correctly")
        
        print("\n6. Testing partial configuration with defaults...")
        test_property_20_partial_configuration_with_defaults()
        print("   ✓ PASSED: Partial configurations with defaults work correctly")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: Color parameters are correctly applied")
        print("  Verified: Font parameters are correctly applied")
        print("  Verified: Data source parameters are correctly applied")
        print("  Verified: Output parameters are correctly applied")
        print("  Verified: Mixed and partial configurations work correctly")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
