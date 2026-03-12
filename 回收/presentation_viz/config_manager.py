"""
Configuration management for the presentation visualization system.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigManager:
    """
    Manages configuration loading, validation, and access for all visualization modules.
    """
    
    DEFAULT_CONFIG = {
        'style': {
            'color_scheme': 'dark_tech',
            'background_color': '#2b2b2b',
            'primary_color': '#00bcd4',
            'secondary_color': '#ff9800',
            'font_family': 'Arial',
            'font_size_title': 16,
            'font_size_label': 12,
            'dpi': 300
        },
        'data_sources': {
            'urdf_path': 'src/dog2_description/urdf/dog2.urdf.xacro',
            'joint_states_topic': '/joint_states',
            'imu_topic': '/imu/data',
            'odom_topic': '/odom'
        },
        'output': {
            'directory': 'presentation_outputs',
            'format': 'png',
            'preview_enabled': False
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to YAML configuration file. If None or file doesn't exist,
                        uses default configuration.
        """
        self.logger = logging.getLogger(__name__)
        # Deep copy the default config to avoid mutation
        import copy
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_path:
            self._load_config(config_path)
        else:
            self.logger.warning("No configuration file provided, using default configuration")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        path = Path(config_path)
        
        if not path.exists():
            self.logger.warning(f"Configuration file not found: {config_path}, using default configuration")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
            
            if user_config:
                # Deep merge user config with defaults
                self._merge_config(self.config, user_config)
                self.logger.info(f"Successfully loaded configuration from {config_path}")
                
                # Validate the merged configuration
                if not self.validate_config():
                    self.logger.warning("Configuration validation found issues, but continuing with current values")
            else:
                self.logger.warning(f"Empty configuration file: {config_path}, using default configuration")
                
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML configuration: {e}, using default configuration")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}, using default configuration")
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """
        Deep merge update dictionary into base dictionary.
        
        Args:
            base: Base dictionary to update
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_style(self) -> Dict[str, Any]:
        """
        Get global style configuration.
        
        Returns:
            Dictionary containing style parameters
        """
        return self.config.get('style', {})
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific module.
        
        Args:
            module_name: Name of the module (e.g., 'kinematic_diagram', 'workspace_analysis')
            
        Returns:
            Dictionary containing module-specific configuration
        """
        return self.config.get(module_name, {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration.
        
        Returns:
            Dictionary containing output parameters
        """
        return self.config.get('output', {})
    
    def get_data_sources(self) -> Dict[str, Any]:
        """
        Get data source configuration.
        
        Returns:
            Dictionary containing data source parameters
        """
        return self.config.get('data_sources', {})
    
    def validate_color(self, color: str) -> bool:
        """
        Validate color code format (hex or RGB).
        
        Args:
            color: Color string to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check hex format
        if color.startswith('#'):
            hex_part = color[1:]
            if len(hex_part) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                return True
        
        # Check RGB format (simplified)
        if color.startswith('rgb(') and color.endswith(')'):
            return True
        
        return False
    
    def validate_path(self, path: str) -> bool:
        """
        Validate that a file path exists.
        
        Args:
            path: File path to validate
            
        Returns:
            True if path exists, False otherwise
        """
        return Path(path).exists()
    
    def validate_numeric_range(self, value: Any, min_val: Optional[float] = None, 
                               max_val: Optional[float] = None) -> bool:
        """
        Validate that a numeric value is within specified range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            num_value = float(value)
            if min_val is not None and num_value < min_val:
                return False
            if max_val is not None and num_value > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_config(self) -> bool:
        """
        Validate all configuration values.
        
        Returns:
            True if all validations pass, False otherwise
        """
        valid = True
        
        # Validate style colors
        style = self.get_style()
        for color_key in ['background_color', 'primary_color', 'secondary_color']:
            if color_key in style:
                if not self.validate_color(style[color_key]):
                    self.logger.warning(f"Invalid color format for {color_key}: {style[color_key]}")
                    valid = False
        
        # Validate numeric ranges
        if 'dpi' in style:
            if not self.validate_numeric_range(style['dpi'], min_val=72, max_val=600):
                self.logger.warning(f"DPI value out of range (72-600): {style['dpi']}")
                valid = False
        
        if 'font_size_title' in style:
            if not self.validate_numeric_range(style['font_size_title'], min_val=8, max_val=72):
                self.logger.warning(f"Title font size out of range (8-72): {style['font_size_title']}")
                valid = False
        
        if 'font_size_label' in style:
            if not self.validate_numeric_range(style['font_size_label'], min_val=6, max_val=48):
                self.logger.warning(f"Label font size out of range (6-48): {style['font_size_label']}")
                valid = False
        
        # Validate data source paths (only if they are specified and not default)
        data_sources = self.get_data_sources()
        if 'urdf_path' in data_sources:
            urdf_path = data_sources['urdf_path']
            # Only validate if it's not the default path (which might not exist yet)
            if urdf_path != self.DEFAULT_CONFIG['data_sources']['urdf_path']:
                if not self.validate_path(urdf_path):
                    self.logger.warning(f"URDF path does not exist: {urdf_path}")
                    # Don't set valid=False for paths as they might be created later
        
        # Validate output format
        output = self.get_output_config()
        if 'format' in output:
            valid_formats = ['png', 'jpg', 'jpeg', 'svg', 'pdf']
            if output['format'].lower() not in valid_formats:
                self.logger.warning(f"Invalid output format: {output['format']}, must be one of {valid_formats}")
                valid = False
        
        return valid
