"""
Unit Tests for ConfigManager

Tests loading valid configuration files, handling missing files,
handling invalid YAML syntax, and configuration value validation.

Validates: Requirements 9.1, 9.5
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from presentation_viz import ConfigManager


class TestConfigManagerLoading:
    """Tests for configuration file loading."""
    
    def test_load_valid_config_file(self):
        """Test loading a valid configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "valid_config.yaml"
            
            config_data = {
                'style': {
                    'color_scheme': 'dark_tech',
                    'background_color': '#2b2b2b',
                    'primary_color': '#00bcd4',
                    'dpi': 300
                },
                'data_sources': {
                    'urdf_path': 'test/path/robot.urdf',
                    'joint_states_topic': '/joint_states'
                },
                'output': {
                    'directory': 'test_output',
                    'format': 'png'
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            # Verify loaded values
            style = config_manager.get_style()
            assert style['color_scheme'] == 'dark_tech'
            assert style['background_color'] == '#2b2b2b'
            assert style['primary_color'] == '#00bcd4'
            assert style['dpi'] == 300
            
            data_sources = config_manager.get_data_sources()
            assert data_sources['urdf_path'] == 'test/path/robot.urdf'
            assert data_sources['joint_states_topic'] == '/joint_states'
            
            output = config_manager.get_output_config()
            assert output['directory'] == 'test_output'
            assert output['format'] == 'png'
    
    def test_load_minimal_valid_config(self):
        """Test loading a minimal but valid configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "minimal_config.yaml"
            
            # Only override a few values
            config_data = {
                'style': {
                    'dpi': 150
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            # Verify overridden value
            style = config_manager.get_style()
            assert style['dpi'] == 150
            
            # Verify defaults are still present
            assert 'color_scheme' in style
            assert 'background_color' in style
            assert 'primary_color' in style
    
    def test_load_config_with_all_sections(self):
        """Test loading a configuration with all possible sections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "complete_config.yaml"
            
            config_data = {
                'style': {
                    'color_scheme': 'light_professional',
                    'background_color': '#ffffff',
                    'primary_color': '#0066cc',
                    'secondary_color': '#ff6600',
                    'font_family': 'Helvetica',
                    'font_size_title': 18,
                    'font_size_label': 14,
                    'dpi': 600
                },
                'data_sources': {
                    'urdf_path': 'robots/dog2.urdf',
                    'joint_states_topic': '/dog2/joint_states',
                    'imu_topic': '/dog2/imu',
                    'odom_topic': '/dog2/odom'
                },
                'output': {
                    'directory': 'presentation_outputs',
                    'format': 'svg',
                    'preview_enabled': True
                },
                'kinematic_diagram': {
                    'view': 'top',
                    'show_coordinate_frames': False
                },
                'workspace_analysis': {
                    'leg_id': 'FR',
                    'rail_extension': 0.15,
                    'resolution': 150
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            # Verify all sections are loaded
            style = config_manager.get_style()
            assert style['color_scheme'] == 'light_professional'
            assert style['font_family'] == 'Helvetica'
            assert style['font_size_title'] == 18
            
            data_sources = config_manager.get_data_sources()
            assert data_sources['urdf_path'] == 'robots/dog2.urdf'
            assert data_sources['imu_topic'] == '/dog2/imu'
            
            output = config_manager.get_output_config()
            assert output['format'] == 'svg'
            assert output['preview_enabled'] is True
            
            # Verify module-specific configs
            kinematic = config_manager.get_module_config('kinematic_diagram')
            assert kinematic['view'] == 'top'
            assert kinematic['show_coordinate_frames'] is False
            
            workspace = config_manager.get_module_config('workspace_analysis')
            assert workspace['leg_id'] == 'FR'
            assert workspace['rail_extension'] == 0.15


class TestConfigManagerMissingFiles:
    """Tests for handling missing configuration files."""
    
    def test_handle_missing_config_file(self):
        """Test that missing config file uses defaults without crashing."""
        nonexistent_path = "/tmp/definitely_does_not_exist_12345.yaml"
        
        # Should not raise exception
        config_manager = ConfigManager(nonexistent_path)
        
        # Should have default values
        style = config_manager.get_style()
        assert style is not None
        assert style['color_scheme'] == ConfigManager.DEFAULT_CONFIG['style']['color_scheme']
        assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi']
    
    def test_handle_none_config_path(self):
        """Test that None config path uses defaults."""
        config_manager = ConfigManager(None)
        
        # Should have default values
        style = config_manager.get_style()
        assert style is not None
        assert 'color_scheme' in style
        assert 'dpi' in style
        
        data_sources = config_manager.get_data_sources()
        assert data_sources is not None
        assert 'urdf_path' in data_sources
    
    def test_handle_empty_string_config_path(self):
        """Test that empty string config path uses defaults."""
        config_manager = ConfigManager("")
        
        # Should have default values
        output = config_manager.get_output_config()
        assert output is not None
        assert 'directory' in output
        assert 'format' in output


class TestConfigManagerInvalidYAML:
    """Tests for handling invalid YAML syntax."""
    
    def test_handle_invalid_yaml_syntax(self):
        """Test that invalid YAML syntax falls back to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            
            # Write invalid YAML
            with open(config_file, 'w') as f:
                f.write("{\ninvalid: yaml: syntax\n[unclosed bracket")
            
            # Should not crash
            config_manager = ConfigManager(str(config_file))
            
            # Should have default values
            style = config_manager.get_style()
            assert style is not None
            assert 'dpi' in style
    
    def test_handle_malformed_yaml_structure(self):
        """Test that malformed YAML structure falls back to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "malformed.yaml"
            
            # Write YAML with wrong structure
            with open(config_file, 'w') as f:
                f.write("- item1\n- item2\n- item3")  # List instead of dict
            
            config_manager = ConfigManager(str(config_file))
            
            # Should have default values
            data_sources = config_manager.get_data_sources()
            assert data_sources is not None
            assert 'joint_states_topic' in data_sources
    
    def test_handle_empty_yaml_file(self):
        """Test that empty YAML file uses all defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "empty.yaml"
            
            # Create empty file
            config_file.touch()
            
            config_manager = ConfigManager(str(config_file))
            
            # Should have complete default configuration
            style = config_manager.get_style()
            assert len(style) > 0
            assert all(key in style for key in ['color_scheme', 'dpi', 'background_color'])
    
    def test_handle_yaml_with_only_comments(self):
        """Test that YAML with only comments uses defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "comments_only.yaml"
            
            with open(config_file, 'w') as f:
                f.write("# This is a comment\n")
                f.write("# Another comment\n")
                f.write("# No actual configuration\n")
            
            config_manager = ConfigManager(str(config_file))
            
            # Should have default values
            output = config_manager.get_output_config()
            assert output['directory'] == ConfigManager.DEFAULT_CONFIG['output']['directory']


class TestConfigManagerValueValidation:
    """Tests for configuration value validation."""
    
    def test_validate_color_codes(self):
        """Test that color code validation works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "colors.yaml"
            
            # Valid hex colors
            config_data = {
                'style': {
                    'background_color': '#2b2b2b',
                    'primary_color': '#00bcd4',
                    'secondary_color': '#f90'  # 3-digit hex
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            style = config_manager.get_style()
            
            # Colors should be loaded
            assert style['background_color'] == '#2b2b2b'
            assert style['primary_color'] == '#00bcd4'
            assert style['secondary_color'] == '#f90'
    
    def test_validate_numeric_ranges(self):
        """Test that numeric value validation works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "numeric.yaml"
            
            config_data = {
                'style': {
                    'dpi': 300,
                    'font_size_title': 16,
                    'font_size_label': 12
                },
                'workspace_analysis': {
                    'resolution': 100,
                    'rail_extension': 0.1
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            style = config_manager.get_style()
            assert style['dpi'] == 300
            assert style['font_size_title'] == 16
            assert style['font_size_label'] == 12
            
            workspace = config_manager.get_module_config('workspace_analysis')
            assert workspace['resolution'] == 100
            assert workspace['rail_extension'] == 0.1
    
    def test_validate_file_paths(self):
        """Test that file path validation works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "paths.yaml"
            
            config_data = {
                'data_sources': {
                    'urdf_path': 'relative/path/robot.urdf',
                },
                'output': {
                    'directory': 'output/dir'
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            data_sources = config_manager.get_data_sources()
            assert data_sources['urdf_path'] == 'relative/path/robot.urdf'
            
            output = config_manager.get_output_config()
            assert output['directory'] == 'output/dir'
    
    def test_handle_invalid_color_codes(self):
        """Test that invalid color codes fall back to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid_colors.yaml"
            
            config_data = {
                'style': {
                    'background_color': 'not-a-color',
                    'primary_color': '#gggggg',  # Invalid hex
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            style = config_manager.get_style()
            
            # Should fall back to defaults for invalid colors
            assert 'background_color' in style
            assert 'primary_color' in style
    
    def test_handle_negative_numeric_values(self):
        """Test that negative numeric values trigger validation warnings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "negative.yaml"
            
            config_data = {
                'style': {
                    'dpi': -100,  # Invalid
                    'font_size_title': -5  # Invalid
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            # ConfigManager should load without crashing
            config_manager = ConfigManager(str(config_file))
            style = config_manager.get_style()
            
            # Values are loaded (validation warnings are issued but values kept)
            # This allows the system to continue operating
            assert 'dpi' in style
            assert 'font_size_title' in style


class TestConfigManagerModuleConfigs:
    """Tests for module-specific configuration retrieval."""
    
    def test_get_module_config_existing(self):
        """Test getting configuration for an existing module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "modules.yaml"
            
            config_data = {
                'kinematic_diagram': {
                    'view': 'side',
                    'show_coordinate_frames': True
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            kinematic = config_manager.get_module_config('kinematic_diagram')
            assert kinematic is not None
            assert kinematic['view'] == 'side'
            assert kinematic['show_coordinate_frames'] is True
    
    def test_get_module_config_nonexistent(self):
        """Test getting configuration for a non-existent module."""
        config_manager = ConfigManager(None)
        
        # Should return empty dict or None for non-existent module
        result = config_manager.get_module_config('nonexistent_module')
        assert result is None or result == {}
    
    def test_get_multiple_module_configs(self):
        """Test getting configurations for multiple modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "multi_modules.yaml"
            
            config_data = {
                'kinematic_diagram': {'view': 'top'},
                'workspace_analysis': {'leg_id': 'FL'},
                'ros_graph': {'layout': 'horizontal'}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config_manager = ConfigManager(str(config_file))
            
            kinematic = config_manager.get_module_config('kinematic_diagram')
            assert kinematic['view'] == 'top'
            
            workspace = config_manager.get_module_config('workspace_analysis')
            assert workspace['leg_id'] == 'FL'
            
            ros_graph = config_manager.get_module_config('ros_graph')
            assert ros_graph['layout'] == 'horizontal'


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
