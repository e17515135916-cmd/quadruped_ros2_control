#!/usr/bin/env python3
"""
Unit tests for CHAMP gait parameters configuration.

Tests verify that the gait parameters in gait.yaml:
1. All parameters are within valid ranges
2. Velocity parameters are positive
3. Height parameters are positive
4. Configuration loads successfully

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import unittest
import yaml
import os
from pathlib import Path


class TestGaitParameters(unittest.TestCase):
    """Unit tests for CHAMP gait parameters configuration."""
    
    @classmethod
    def setUpClass(cls):
        """Load gait configuration once for all tests."""
        # Find the gait.yaml file
        workspace_root = Path(__file__).parent.parent
        gait_yaml_path = workspace_root / "src" / "dog2_champ_config" / "config" / "gait" / "gait.yaml"
        
        if not gait_yaml_path.exists():
            raise FileNotFoundError(f"gait.yaml not found at {gait_yaml_path}")
        
        # Load the YAML configuration
        with open(gait_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract gait parameters from the configuration
        cls.gait_params = config['/**']['ros__parameters']['gait']
    
    def test_gait_yaml_loads_successfully(self):
        """Test that gait.yaml loads without errors."""
        self.assertIsNotNone(self.gait_params, "Gait parameters should not be None")
        self.assertIsInstance(self.gait_params, dict, "Gait parameters should be a dictionary")
    
    def test_max_linear_velocity_x_positive(self):
        """Test that max_linear_velocity_x is positive (Requirement 5.1)."""
        velocity_x = self.gait_params.get('max_linear_velocity_x')
        self.assertIsNotNone(velocity_x, "max_linear_velocity_x should be defined")
        self.assertGreater(
            velocity_x,
            0.0,
            f"max_linear_velocity_x should be positive, but got {velocity_x}"
        )
    
    def test_max_linear_velocity_x_within_range(self):
        """Test that max_linear_velocity_x is within reasonable range (Requirement 5.1)."""
        velocity_x = self.gait_params.get('max_linear_velocity_x')
        self.assertLessEqual(
            velocity_x,
            2.0,
            f"max_linear_velocity_x should be <= 2.0 m/s for safety, but got {velocity_x}"
        )
        self.assertEqual(
            velocity_x,
            0.5,
            f"max_linear_velocity_x should be 0.5 m/s as per spec, but got {velocity_x}"
        )
    
    def test_max_linear_velocity_y_positive(self):
        """Test that max_linear_velocity_y is positive (Requirement 5.1)."""
        velocity_y = self.gait_params.get('max_linear_velocity_y')
        self.assertIsNotNone(velocity_y, "max_linear_velocity_y should be defined")
        self.assertGreater(
            velocity_y,
            0.0,
            f"max_linear_velocity_y should be positive, but got {velocity_y}"
        )
    
    def test_max_linear_velocity_y_within_range(self):
        """Test that max_linear_velocity_y is within reasonable range (Requirement 5.1)."""
        velocity_y = self.gait_params.get('max_linear_velocity_y')
        self.assertLessEqual(
            velocity_y,
            1.0,
            f"max_linear_velocity_y should be <= 1.0 m/s for safety, but got {velocity_y}"
        )
        self.assertEqual(
            velocity_y,
            0.3,
            f"max_linear_velocity_y should be 0.3 m/s as per spec, but got {velocity_y}"
        )
    
    def test_max_angular_velocity_z_positive(self):
        """Test that max_angular_velocity_z is positive (Requirement 5.2)."""
        velocity_z = self.gait_params.get('max_angular_velocity_z')
        self.assertIsNotNone(velocity_z, "max_angular_velocity_z should be defined")
        self.assertGreater(
            velocity_z,
            0.0,
            f"max_angular_velocity_z should be positive, but got {velocity_z}"
        )
    
    def test_max_angular_velocity_z_within_range(self):
        """Test that max_angular_velocity_z is within reasonable range (Requirement 5.2)."""
        velocity_z = self.gait_params.get('max_angular_velocity_z')
        self.assertLessEqual(
            velocity_z,
            3.0,
            f"max_angular_velocity_z should be <= 3.0 rad/s for safety, but got {velocity_z}"
        )
        self.assertEqual(
            velocity_z,
            1.0,
            f"max_angular_velocity_z should be 1.0 rad/s as per spec, but got {velocity_z}"
        )
    
    def test_stance_duration_positive(self):
        """Test that stance_duration is positive (Requirement 5.3)."""
        stance_duration = self.gait_params.get('stance_duration')
        self.assertIsNotNone(stance_duration, "stance_duration should be defined")
        self.assertGreater(
            stance_duration,
            0.0,
            f"stance_duration should be positive, but got {stance_duration}"
        )
    
    def test_stance_duration_within_range(self):
        """Test that stance_duration is within reasonable range (Requirement 5.3)."""
        stance_duration = self.gait_params.get('stance_duration')
        self.assertGreaterEqual(
            stance_duration,
            0.1,
            f"stance_duration should be >= 0.1s for stability, but got {stance_duration}"
        )
        self.assertLessEqual(
            stance_duration,
            1.0,
            f"stance_duration should be <= 1.0s for reasonable gait, but got {stance_duration}"
        )
        self.assertEqual(
            stance_duration,
            0.25,
            f"stance_duration should be 0.25s as per spec, but got {stance_duration}"
        )
    
    def test_swing_height_positive(self):
        """Test that swing_height is positive (Requirement 5.4)."""
        swing_height = self.gait_params.get('swing_height')
        self.assertIsNotNone(swing_height, "swing_height should be defined")
        self.assertGreater(
            swing_height,
            0.0,
            f"swing_height should be positive, but got {swing_height}"
        )
    
    def test_swing_height_within_range(self):
        """Test that swing_height is within reasonable range (Requirement 5.4)."""
        swing_height = self.gait_params.get('swing_height')
        self.assertGreaterEqual(
            swing_height,
            0.01,
            f"swing_height should be >= 0.01m for clearance, but got {swing_height}"
        )
        self.assertLessEqual(
            swing_height,
            0.15,
            f"swing_height should be <= 0.15m for efficiency, but got {swing_height}"
        )
        self.assertEqual(
            swing_height,
            0.04,
            f"swing_height should be 0.04m as per spec, but got {swing_height}"
        )
    
    def test_nominal_height_positive(self):
        """Test that nominal_height is positive (Requirement 5.5)."""
        nominal_height = self.gait_params.get('nominal_height')
        self.assertIsNotNone(nominal_height, "nominal_height should be defined")
        self.assertGreater(
            nominal_height,
            0.0,
            f"nominal_height should be positive, but got {nominal_height}"
        )
    
    def test_nominal_height_within_range(self):
        """Test that nominal_height is within reasonable range (Requirement 5.5)."""
        nominal_height = self.gait_params.get('nominal_height')
        self.assertGreaterEqual(
            nominal_height,
            0.1,
            f"nominal_height should be >= 0.1m for ground clearance, but got {nominal_height}"
        )
        self.assertLessEqual(
            nominal_height,
            0.5,
            f"nominal_height should be <= 0.5m for stability, but got {nominal_height}"
        )
        self.assertEqual(
            nominal_height,
            0.20,
            f"nominal_height should be 0.20m as per spec, but got {nominal_height}"
        )
    
    def test_stance_depth_non_negative(self):
        """Test that stance_depth is non-negative."""
        stance_depth = self.gait_params.get('stance_depth')
        self.assertIsNotNone(stance_depth, "stance_depth should be defined")
        self.assertGreaterEqual(
            stance_depth,
            0.0,
            f"stance_depth should be non-negative, but got {stance_depth}"
        )
    
    def test_odom_scaler_within_range(self):
        """Test that odom_scaler is within reasonable range."""
        odom_scaler = self.gait_params.get('odom_scaler')
        self.assertIsNotNone(odom_scaler, "odom_scaler should be defined")
        self.assertGreaterEqual(
            odom_scaler,
            0.5,
            f"odom_scaler should be >= 0.5, but got {odom_scaler}"
        )
        self.assertLessEqual(
            odom_scaler,
            1.5,
            f"odom_scaler should be <= 1.5, but got {odom_scaler}"
        )
    
    def test_knee_orientation_valid(self):
        """Test that knee_orientation is a valid value."""
        knee_orientation = self.gait_params.get('knee_orientation')
        self.assertIsNotNone(knee_orientation, "knee_orientation should be defined")
        valid_orientations = ['>>','><', '<<', '<>']
        self.assertIn(
            knee_orientation,
            valid_orientations,
            f"knee_orientation should be one of {valid_orientations}, but got '{knee_orientation}'"
        )
    
    def test_pantograph_leg_is_boolean(self):
        """Test that pantograph_leg is a boolean value."""
        pantograph_leg = self.gait_params.get('pantograph_leg')
        self.assertIsNotNone(pantograph_leg, "pantograph_leg should be defined")
        self.assertIsInstance(
            pantograph_leg,
            bool,
            f"pantograph_leg should be boolean, but got {type(pantograph_leg)}"
        )
    
    def test_com_x_translation_within_range(self):
        """Test that com_x_translation is within reasonable range."""
        com_x = self.gait_params.get('com_x_translation')
        self.assertIsNotNone(com_x, "com_x_translation should be defined")
        self.assertGreaterEqual(
            com_x,
            -0.2,
            f"com_x_translation should be >= -0.2m, but got {com_x}"
        )
        self.assertLessEqual(
            com_x,
            0.2,
            f"com_x_translation should be <= 0.2m, but got {com_x}"
        )
    
    def test_all_required_parameters_present(self):
        """Test that all required gait parameters are present."""
        required_params = [
            'knee_orientation',
            'pantograph_leg',
            'odom_scaler',
            'max_linear_velocity_x',
            'max_linear_velocity_y',
            'max_angular_velocity_z',
            'com_x_translation',
            'swing_height',
            'stance_depth',
            'stance_duration',
            'nominal_height'
        ]
        
        for param in required_params:
            with self.subTest(parameter=param):
                self.assertIn(
                    param,
                    self.gait_params,
                    f"Required parameter '{param}' is missing from gait configuration"
                )
    
    def test_lateral_velocity_less_than_forward(self):
        """Test that lateral velocity is typically less than forward velocity."""
        velocity_x = self.gait_params.get('max_linear_velocity_x')
        velocity_y = self.gait_params.get('max_linear_velocity_y')
        
        # This is a typical constraint for quadruped robots
        self.assertLessEqual(
            velocity_y,
            velocity_x,
            f"Lateral velocity ({velocity_y}) should typically be <= forward velocity ({velocity_x})"
        )
    
    def test_swing_height_less_than_nominal_height(self):
        """Test that swing_height is less than nominal_height."""
        swing_height = self.gait_params.get('swing_height')
        nominal_height = self.gait_params.get('nominal_height')
        
        self.assertLess(
            swing_height,
            nominal_height,
            f"swing_height ({swing_height}) should be < nominal_height ({nominal_height})"
        )


if __name__ == '__main__':
    unittest.main()
