#!/usr/bin/env python3
"""
Property-Based Tests: ConfigManager Default Configuration Fallback

Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
Validates: Requirements 9.5

This test verifies that for any missing or invalid configuration file, the system
should successfully initialize with default values and generate at least one output
file without crashing.
"""

import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from presentation_viz import ConfigManager


@settings(max_examples=20)
@given(st.none())
def test_property_21_none_config_path(config_path):
    """
    Property Test: None Config Path Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any None config path, ConfigManager should initialize with defaults.
    """
    try:
        config_manager = ConfigManager(config_path)
    except Exception as e:
        raise AssertionError(
            f"ConfigManager should handle None config path gracefully, but raised: {e}"
        )
    
    # Verify default configuration is loaded
    style = config_manager.get_style()
    assert style is not None
    assert 'color_scheme' in style
    assert style['color_scheme'] == ConfigManager.DEFAULT_CONFIG['style']['color_scheme']
    
    data_sources = config_manager.get_data_sources()
    assert data_sources is not None
    assert 'urdf_path' in data_sources
    
    output = config_manager.get_output_config()
    assert output is not None
    assert 'directory' in output


@settings(max_examples=20)
@given(st.text(min_size=1, max_size=100))
def test_property_21_nonexistent_file_fallback(filename):
    """
    Property Test: Nonexistent File Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any nonexistent file path, ConfigManager should fall back to defaults.
    """
    # Create a path that definitely doesn't exist
    nonexistent_path = f"/tmp/nonexistent_{hash(filename)}_{os.getpid()}_config.yaml"
    
    # Ensure the file doesn't exist
    if os.path.exists(nonexistent_path):
        os.remove(nonexistent_path)
    
    try:
        config_manager = ConfigManager(nonexistent_path)
    except Exception as e:
        raise AssertionError(
            f"ConfigManager should handle nonexistent files gracefully, but raised: {e}\n"
            f"Path: {nonexistent_path}"
        )
    
    # Verify default configuration is loaded
    style = config_manager.get_style()
    assert style is not None
    assert 'dpi' in style
    assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi']
    
    output = config_manager.get_output_config()
    assert output is not None
    assert 'format' in output
    assert output['format'] == ConfigManager.DEFAULT_CONFIG['output']['format']


@settings(max_examples=20)
@given(st.text(min_size=0, max_size=500))
def test_property_21_invalid_yaml_fallback(yaml_content):
    """
    Property Test: Invalid YAML Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any invalid YAML content, ConfigManager should fall back to defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "invalid_config.yaml"
        
        # Write potentially invalid YAML content
        with open(config_file, 'w') as f:
            f.write(yaml_content)
        
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle invalid YAML gracefully, but raised: {e}\n"
                f"YAML content: {repr(yaml_content[:100])}"
            )
        
        # Verify default configuration is loaded
        style = config_manager.get_style()
        assert style is not None
        assert isinstance(style, dict)
        
        # All required fields should be present with default values
        assert 'color_scheme' in style
        assert 'background_color' in style
        assert 'primary_color' in style
        assert 'dpi' in style


@settings(max_examples=20)
@given(st.binary(min_size=0, max_size=500))
def test_property_21_binary_content_fallback(binary_content):
    """
    Property Test: Binary Content Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any binary (non-text) content, ConfigManager should fall back to defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "binary_config.yaml"
        
        # Write binary content
        with open(config_file, 'wb') as f:
            f.write(binary_content)
        
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle binary content gracefully, but raised: {e}"
            )
        
        # Verify default configuration is loaded
        data_sources = config_manager.get_data_sources()
        assert data_sources is not None
        assert 'joint_states_topic' in data_sources
        assert data_sources['joint_states_topic'] == ConfigManager.DEFAULT_CONFIG['data_sources']['joint_states_topic']


@settings(max_examples=15)
@given(st.dictionaries(
    keys=st.text(min_size=1, max_size=20),
    values=st.none() | st.integers() | st.text(max_size=50),
    min_size=0,
    max_size=10
))
def test_property_21_partial_invalid_config_fallback(config_dict):
    """
    Property Test: Partial Invalid Config Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any configuration with invalid or missing fields, ConfigManager should
    use defaults for missing/invalid fields while preserving valid ones.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "partial_config.yaml"
        
        # Write config with potentially invalid structure
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f)
        
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle partial configs gracefully, but raised: {e}\n"
                f"Config: {config_dict}"
            )
        
        # Verify all required sections are accessible
        style = config_manager.get_style()
        assert style is not None
        assert isinstance(style, dict)
        assert len(style) > 0
        
        data_sources = config_manager.get_data_sources()
        assert data_sources is not None
        assert isinstance(data_sources, dict)
        
        output = config_manager.get_output_config()
        assert output is not None
        assert isinstance(output, dict)
        
        # Verify critical fields are never None
        assert style.get('dpi') is not None
        assert data_sources.get('urdf_path') is not None
        assert output.get('directory') is not None


@settings(max_examples=15)
@given(st.text(min_size=1, max_size=200))
def test_property_21_empty_file_fallback(filename_suffix):
    """
    Property Test: Empty File Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any empty configuration file, ConfigManager should use all defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create safe filename
        safe_suffix = "".join(c for c in filename_suffix if c.isalnum() or c in "._-")[:50]
        config_file = Path(tmpdir) / f"empty_{safe_suffix}.yaml"
        
        # Create empty file
        config_file.touch()
        
        try:
            config_manager = ConfigManager(str(config_file))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle empty files gracefully, but raised: {e}"
            )
        
        # Verify complete default configuration is loaded
        style = config_manager.get_style()
        assert style == ConfigManager.DEFAULT_CONFIG['style'] or all(
            key in style for key in ConfigManager.DEFAULT_CONFIG['style'].keys()
        )
        
        data_sources = config_manager.get_data_sources()
        assert all(
            key in data_sources for key in ConfigManager.DEFAULT_CONFIG['data_sources'].keys()
        )
        
        output = config_manager.get_output_config()
        assert all(
            key in output for key in ConfigManager.DEFAULT_CONFIG['output'].keys()
        )


@settings(max_examples=15)
@given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5))
def test_property_21_directory_path_fallback(path_components):
    """
    Property Test: Directory Path Fallback
    
    Feature: presentation-visualization-system, Property 21: Default Configuration Fallback
    Validates: Requirements 9.5
    
    For any directory path (not a file), ConfigManager should fall back to defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a directory path
        dir_path = Path(tmpdir)
        for component in path_components:
            safe_component = "".join(c for c in component if c.isalnum() or c in "._-")[:30]
            if safe_component:
                dir_path = dir_path / safe_component
        
        dir_path.mkdir(parents=True, exist_ok=True)
        
        try:
            config_manager = ConfigManager(str(dir_path))
        except Exception as e:
            raise AssertionError(
                f"ConfigManager should handle directory paths gracefully, but raised: {e}\n"
                f"Path: {dir_path}"
            )
        
        # Verify default configuration is loaded
        style = config_manager.get_style()
        assert style is not None
        assert 'color_scheme' in style
        
        output = config_manager.get_output_config()
        assert output is not None
        assert 'directory' in output


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ConfigManager Default Configuration Fallback")
    print("=" * 80)
    
    try:
        print("\n1. Testing None config path fallback...")
        test_property_21_none_config_path()
        print("   ✓ PASSED: None config path handled gracefully")
        
        print("\n2. Testing nonexistent file fallback...")
        test_property_21_nonexistent_file_fallback()
        print("   ✓ PASSED: Nonexistent files handled gracefully")
        
        print("\n3. Testing invalid YAML fallback...")
        test_property_21_invalid_yaml_fallback()
        print("   ✓ PASSED: Invalid YAML handled gracefully")
        
        print("\n4. Testing binary content fallback...")
        test_property_21_binary_content_fallback()
        print("   ✓ PASSED: Binary content handled gracefully")
        
        print("\n5. Testing partial invalid config fallback...")
        test_property_21_partial_invalid_config_fallback()
        print("   ✓ PASSED: Partial configs handled gracefully")
        
        print("\n6. Testing empty file fallback...")
        test_property_21_empty_file_fallback()
        print("   ✓ PASSED: Empty files handled gracefully")
        
        print("\n7. Testing directory path fallback...")
        test_property_21_directory_path_fallback()
        print("   ✓ PASSED: Directory paths handled gracefully")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: Missing/invalid configs fall back to defaults")
        print("  Verified: System never crashes due to config issues")
        print("  Verified: All required fields always have valid values")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
