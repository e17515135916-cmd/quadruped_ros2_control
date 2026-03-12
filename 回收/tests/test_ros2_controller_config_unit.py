"""
Unit Tests for ROS2 Controller Configuration

Tests that the ros2_controllers.yaml configuration:
- Loads successfully
- Contains all 12 revolute joints (3 per leg × 4 legs)
- Excludes prismatic joints (j1, j2, j3, j4)

Validates: Requirements 3.1
"""

import pytest
import yaml
from pathlib import Path


class TestROS2ControllerConfiguration:
    """Tests for ros2_controllers.yaml configuration file."""
    
    @pytest.fixture
    def config_path(self):
        """Get path to ros2_controllers.yaml configuration file."""
        # Assuming tests run from workspace root
        config_file = Path("src/dog2_description/config/ros2_controllers.yaml")
        if not config_file.exists():
            pytest.skip(f"Configuration file not found: {config_file}")
        return config_file
    
    @pytest.fixture
    def config_data(self, config_path):
        """Load and parse the ros2_controllers.yaml file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def test_config_file_loads_successfully(self, config_path):
        """Test that the configuration file loads without errors."""
        # Should not raise any exceptions
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_controller_manager_section_exists(self, config_data):
        """Test that controller_manager section exists."""
        assert 'controller_manager' in config_data
        assert 'ros__parameters' in config_data['controller_manager']
    
    def test_controller_manager_update_rate(self, config_data):
        """Test that controller_manager has correct update rate."""
        params = config_data['controller_manager']['ros__parameters']
        assert 'update_rate' in params
        assert params['update_rate'] == 100  # 100 Hz as per design
    
    def test_joint_state_broadcaster_configured(self, config_data):
        """Test that joint_state_broadcaster is configured."""
        params = config_data['controller_manager']['ros__parameters']
        assert 'joint_state_broadcaster' in params
        assert params['joint_state_broadcaster']['type'] == 'joint_state_broadcaster/JointStateBroadcaster'
    
    def test_joint_trajectory_controller_configured(self, config_data):
        """Test that joint_trajectory_controller is configured."""
        params = config_data['controller_manager']['ros__parameters']
        assert 'joint_trajectory_controller' in params
        assert params['joint_trajectory_controller']['type'] == 'joint_trajectory_controller/JointTrajectoryController'
    
    def test_all_12_revolute_joints_included(self, config_data):
        """Test that all 12 revolute joints are included in the controller."""
        # Expected joints: 3 joints per leg × 4 legs = 12 joints
        expected_joints = [
            # Left Front (lf)
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            # Right Front (rf)
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            # Left Hind (lh)
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            # Right Hind (rh)
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint',
        ]
        
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        actual_joints = controller_params['joints']
        
        # Check count
        assert len(actual_joints) == 12, f"Expected 12 joints, found {len(actual_joints)}"
        
        # Check all expected joints are present
        for joint in expected_joints:
            assert joint in actual_joints, f"Missing joint: {joint}"
    
    def test_prismatic_joints_excluded(self, config_data):
        """Test that prismatic joints (j1, j2, j3, j4) are NOT included."""
        prismatic_joints = ['j1', 'j2', 'j3', 'j4']
        
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        actual_joints = controller_params['joints']
        
        # Verify none of the prismatic joints are in the list
        for prismatic_joint in prismatic_joints:
            assert prismatic_joint not in actual_joints, \
                f"Prismatic joint {prismatic_joint} should not be in controller configuration"
    
    def test_joint_naming_convention(self, config_data):
        """Test that joints follow CHAMP naming convention (leg_prefix + joint_type)."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        actual_joints = controller_params['joints']
        
        # Valid leg prefixes
        valid_prefixes = ['lf_', 'rf_', 'lh_', 'rh_']
        # Valid joint types
        valid_suffixes = ['haa_joint', 'hfe_joint', 'kfe_joint']
        
        for joint in actual_joints:
            # Check prefix
            has_valid_prefix = any(joint.startswith(prefix) for prefix in valid_prefixes)
            assert has_valid_prefix, f"Joint {joint} has invalid prefix"
            
            # Check suffix
            has_valid_suffix = any(joint.endswith(suffix) for suffix in valid_suffixes)
            assert has_valid_suffix, f"Joint {joint} has invalid suffix"
    
    def test_each_leg_has_three_joints(self, config_data):
        """Test that each leg (lf, rf, lh, rh) has exactly 3 joints."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        actual_joints = controller_params['joints']
        
        legs = ['lf', 'rf', 'lh', 'rh']
        
        for leg in legs:
            leg_joints = [j for j in actual_joints if j.startswith(f'{leg}_')]
            assert len(leg_joints) == 3, \
                f"Leg {leg} should have 3 joints, found {len(leg_joints)}: {leg_joints}"
    
    def test_command_interfaces_configured(self, config_data):
        """Test that command interfaces are properly configured."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        
        assert 'command_interfaces' in controller_params
        assert 'position' in controller_params['command_interfaces']
    
    def test_state_interfaces_configured(self, config_data):
        """Test that state interfaces are properly configured."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        
        assert 'state_interfaces' in controller_params
        assert 'position' in controller_params['state_interfaces']
        assert 'velocity' in controller_params['state_interfaces']
    
    def test_state_publish_rate_configured(self, config_data):
        """Test that state publish rate is configured."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        
        assert 'state_publish_rate' in controller_params
        assert controller_params['state_publish_rate'] == 100.0  # 100 Hz
    
    def test_action_monitor_rate_configured(self, config_data):
        """Test that action monitor rate is configured."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        
        assert 'action_monitor_rate' in controller_params
        assert controller_params['action_monitor_rate'] == 20.0  # 20 Hz
    
    def test_joint_state_broadcaster_publish_rate(self, config_data):
        """Test that joint_state_broadcaster has correct publish rate."""
        assert 'joint_state_broadcaster' in config_data
        broadcaster_params = config_data['joint_state_broadcaster']['ros__parameters']
        
        assert 'publish_rate' in broadcaster_params
        assert broadcaster_params['publish_rate'] == 100.0  # 100 Hz


class TestROS2ControllerJointOrdering:
    """Tests for joint ordering in the configuration."""
    
    @pytest.fixture
    def config_path(self):
        """Get path to ros2_controllers.yaml configuration file."""
        config_file = Path("src/dog2_description/config/ros2_controllers.yaml")
        if not config_file.exists():
            pytest.skip(f"Configuration file not found: {config_file}")
        return config_file
    
    @pytest.fixture
    def config_data(self, config_path):
        """Load and parse the ros2_controllers.yaml file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def test_joints_grouped_by_leg(self, config_data):
        """Test that joints are logically grouped by leg."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        joints = controller_params['joints']
        
        # Expected order: lf (0-2), rf (3-5), lh (6-8), rh (9-11)
        # Left Front
        assert joints[0].startswith('lf_')
        assert joints[1].startswith('lf_')
        assert joints[2].startswith('lf_')
        
        # Right Front
        assert joints[3].startswith('rf_')
        assert joints[4].startswith('rf_')
        assert joints[5].startswith('rf_')
        
        # Left Hind
        assert joints[6].startswith('lh_')
        assert joints[7].startswith('lh_')
        assert joints[8].startswith('lh_')
        
        # Right Hind
        assert joints[9].startswith('rh_')
        assert joints[10].startswith('rh_')
        assert joints[11].startswith('rh_')
    
    def test_joints_ordered_haa_hfe_kfe_per_leg(self, config_data):
        """Test that within each leg, joints are ordered HAA, HFE, KFE."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        joints = controller_params['joints']
        
        legs = ['lf', 'rf', 'lh', 'rh']
        
        for i, leg in enumerate(legs):
            base_idx = i * 3
            
            # HAA (Hip Abduction/Adduction) should be first
            assert joints[base_idx].endswith('haa_joint'), \
                f"Expected HAA joint at index {base_idx}, got {joints[base_idx]}"
            
            # HFE (Hip Flexion/Extension) should be second
            assert joints[base_idx + 1].endswith('hfe_joint'), \
                f"Expected HFE joint at index {base_idx + 1}, got {joints[base_idx + 1]}"
            
            # KFE (Knee Flexion/Extension) should be third
            assert joints[base_idx + 2].endswith('kfe_joint'), \
                f"Expected KFE joint at index {base_idx + 2}, got {joints[base_idx + 2]}"


class TestROS2ControllerConfigurationIntegrity:
    """Tests for overall configuration integrity."""
    
    @pytest.fixture
    def config_path(self):
        """Get path to ros2_controllers.yaml configuration file."""
        config_file = Path("src/dog2_description/config/ros2_controllers.yaml")
        if not config_file.exists():
            pytest.skip(f"Configuration file not found: {config_file}")
        return config_file
    
    @pytest.fixture
    def config_data(self, config_path):
        """Load and parse the ros2_controllers.yaml file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def test_no_duplicate_joints(self, config_data):
        """Test that there are no duplicate joints in the configuration."""
        controller_params = config_data['joint_trajectory_controller']['ros__parameters']
        joints = controller_params['joints']
        
        # Check for duplicates
        unique_joints = set(joints)
        assert len(joints) == len(unique_joints), \
            f"Found duplicate joints. Total: {len(joints)}, Unique: {len(unique_joints)}"
    
    def test_yaml_structure_valid(self, config_data):
        """Test that YAML structure is valid and complete."""
        # Top-level keys
        assert 'controller_manager' in config_data
        assert 'joint_state_broadcaster' in config_data
        assert 'joint_trajectory_controller' in config_data
        
        # Nested structure
        assert 'ros__parameters' in config_data['controller_manager']
        assert 'ros__parameters' in config_data['joint_state_broadcaster']
        assert 'ros__parameters' in config_data['joint_trajectory_controller']
    
    def test_all_required_parameters_present(self, config_data):
        """Test that all required parameters are present."""
        # Controller manager parameters
        cm_params = config_data['controller_manager']['ros__parameters']
        required_cm_params = ['update_rate', 'joint_state_broadcaster', 'joint_trajectory_controller']
        for param in required_cm_params:
            assert param in cm_params, f"Missing controller_manager parameter: {param}"
        
        # Joint trajectory controller parameters
        jtc_params = config_data['joint_trajectory_controller']['ros__parameters']
        required_jtc_params = ['joints', 'command_interfaces', 'state_interfaces', 
                               'state_publish_rate', 'action_monitor_rate']
        for param in required_jtc_params:
            assert param in jtc_params, f"Missing joint_trajectory_controller parameter: {param}"
        
        # Joint state broadcaster parameters
        jsb_params = config_data['joint_state_broadcaster']['ros__parameters']
        required_jsb_params = ['publish_rate']
        for param in required_jsb_params:
            assert param in jsb_params, f"Missing joint_state_broadcaster parameter: {param}"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
