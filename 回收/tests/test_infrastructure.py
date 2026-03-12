"""
Basic infrastructure tests to verify project setup.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from presentation_viz import ConfigManager, setup_logger


def test_package_import():
    """Test that the package can be imported"""
    import presentation_viz
    assert presentation_viz.__version__ == "0.1.0"


def test_logger_setup():
    """Test that logger can be set up"""
    logger = setup_logger(name="test_logger")
    assert logger is not None
    assert logger.name == "test_logger"


def test_logger_with_file():
    """Test logger with file output"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        logger = setup_logger(name="test_file_logger", log_file=str(log_file))
        logger.info("Test message")
        assert log_file.exists()


def test_config_manager_default():
    """Test ConfigManager with default configuration"""
    config = ConfigManager()
    
    style = config.get_style()
    assert style['color_scheme'] == 'dark_tech'
    assert style['dpi'] == 300
    
    output = config.get_output_config()
    assert output['directory'] == 'presentation_outputs'
    assert output['format'] == 'png'


def test_config_manager_load_valid_config():
    """Test ConfigManager loading a valid configuration file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        test_config = {
            'style': {
                'dpi': 600,
                'background_color': '#ffffff'
            },
            'output': {
                'directory': 'custom_output'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        config = ConfigManager(str(config_file))
        
        style = config.get_style()
        assert style['dpi'] == 600
        assert style['background_color'] == '#ffffff'
        # Default values should still be present
        assert style['color_scheme'] == 'dark_tech'
        
        output = config.get_output_config()
        assert output['directory'] == 'custom_output'


def test_config_manager_missing_file():
    """Test ConfigManager with missing configuration file"""
    # Create a unique path that definitely doesn't exist
    nonexistent_path = f"/tmp/nonexistent_{id(test_config_manager_missing_file)}.yaml"
    config = ConfigManager(nonexistent_path)
    
    # Should fall back to defaults
    style = config.get_style()
    assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi']
    assert style['color_scheme'] == 'dark_tech'


def test_config_manager_invalid_yaml():
    """Test ConfigManager with invalid YAML syntax"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "invalid.yaml"
        
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: syntax: [")
        
        config = ConfigManager(str(config_file))
        
        # Should fall back to defaults
        style = config.get_style()
        assert style['dpi'] == ConfigManager.DEFAULT_CONFIG['style']['dpi']
        assert style['color_scheme'] == 'dark_tech'


def test_config_manager_color_validation():
    """Test color validation"""
    config = ConfigManager()
    
    # Valid hex colors
    assert config.validate_color('#ffffff')
    assert config.validate_color('#fff')
    assert config.validate_color('#00bcd4')
    
    # Valid RGB colors
    assert config.validate_color('rgb(255, 255, 255)')
    
    # Invalid colors
    assert not config.validate_color('invalid')
    assert not config.validate_color('#gggggg')
    assert not config.validate_color('blue')


def test_config_manager_path_validation():
    """Test path validation"""
    config = ConfigManager()
    
    # Valid path (this file)
    assert config.validate_path(__file__)
    
    # Invalid path
    assert not config.validate_path('/nonexistent/path/to/file.txt')


def test_config_manager_module_config():
    """Test getting module-specific configuration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        test_config = {
            'kinematic_diagram': {
                'view': 'top',
                'show_coordinate_frames': False
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        config = ConfigManager(str(config_file))
        
        module_config = config.get_module_config('kinematic_diagram')
        assert module_config['view'] == 'top'
        assert module_config['show_coordinate_frames'] is False


def test_config_manager_data_sources():
    """Test getting data source configuration"""
    config = ConfigManager()
    
    data_sources = config.get_data_sources()
    assert 'urdf_path' in data_sources
    assert 'joint_states_topic' in data_sources
    assert data_sources['joint_states_topic'] == '/joint_states'


def test_config_template_exists():
    """Test that configuration template file exists"""
    template_path = Path(__file__).parent.parent / "presentation_viz" / "config_template.yaml"
    assert template_path.exists()
    
    # Verify it's valid YAML
    with open(template_path, 'r') as f:
        config = yaml.safe_load(f)
    
    assert 'style' in config
    assert 'output' in config
    assert 'data_sources' in config


def test_config_manager_numeric_range_validation():
    """Test numeric range validation"""
    config = ConfigManager()
    
    # Valid ranges
    assert config.validate_numeric_range(100, min_val=0, max_val=200)
    assert config.validate_numeric_range(50, min_val=50, max_val=100)
    assert config.validate_numeric_range(100, min_val=0, max_val=100)
    assert config.validate_numeric_range(300, min_val=72)  # No max
    assert config.validate_numeric_range(50, max_val=100)  # No min
    
    # Invalid ranges
    assert not config.validate_numeric_range(50, min_val=100, max_val=200)
    assert not config.validate_numeric_range(250, min_val=0, max_val=200)
    assert not config.validate_numeric_range('invalid', min_val=0, max_val=100)
    assert not config.validate_numeric_range(None, min_val=0, max_val=100)


def test_config_manager_validate_config():
    """Test full configuration validation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Valid configuration
        valid_config = {
            'style': {
                'background_color': '#2b2b2b',
                'primary_color': '#00bcd4',
                'secondary_color': '#ff9800',
                'dpi': 300,
                'font_size_title': 16,
                'font_size_label': 12
            },
            'output': {
                'format': 'png'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(valid_config, f)
        
        config = ConfigManager(str(config_file))
        assert config.validate_config() is True


def test_config_manager_validate_config_invalid_color():
    """Test configuration validation with invalid color"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Invalid color
        invalid_config = {
            'style': {
                'background_color': 'invalid_color'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        config = ConfigManager(str(config_file))
        assert config.validate_config() is False


def test_config_manager_validate_config_invalid_dpi():
    """Test configuration validation with invalid DPI"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # DPI out of range
        invalid_config = {
            'style': {
                'dpi': 1000  # Too high
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        config = ConfigManager(str(config_file))
        assert config.validate_config() is False


def test_config_manager_validate_config_invalid_format():
    """Test configuration validation with invalid output format"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Invalid format
        invalid_config = {
            'output': {
                'format': 'invalid_format'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        config = ConfigManager(str(config_file))
        assert config.validate_config() is False


def test_config_manager_deep_merge():
    """Test deep merge of nested configurations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "merge_test_config.yaml"
        
        # Partial override
        partial_config = {
            'style': {
                'dpi': 450  # Override only DPI
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(partial_config, f)
        
        config = ConfigManager(str(config_file))
        
        style = config.get_style()
        # Overridden value
        assert style['dpi'] == 450
        # Default values should still be present
        assert style['color_scheme'] == 'dark_tech'
        assert style['background_color'] == '#2b2b2b'
        assert style['primary_color'] == '#00bcd4'

