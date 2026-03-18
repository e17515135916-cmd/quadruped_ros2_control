"""
Config Loader - 配置文件加载器

从YAML文件加载步态参数并验证有效性
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from .gait_generator import GaitConfig


class ConfigLoader:
    """配置文件加载器
    
    负责从YAML文件加载步态参数，并验证参数有效性
    """
    
    # 默认配置值
    DEFAULT_CONFIG = {
        'gait': {
            'stride_length': 0.08,
            'stride_height': 0.05,
            'cycle_time': 2.0,
            'duty_factor': 0.75,
            'body_height': 0.16,
            'gait_type': 'crawl'
        },
        'joint_limits': {
            'rail': {'min': -0.05, 'max': 0.05},
            'haa': {'min': -0.785, 'max': 0.785},
            'hfe': {'min': -1.57, 'max': 1.57},
            'kfe': {'min': -2.356, 'max': 0.0}
        },
        'control': {
            'frequency': 50.0,
            'max_joint_velocity': 2.0
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            # 优雅且绝对安全：通过 ament_index 查询 share 目录
            try:
                share_dir = get_package_share_directory('dog2_motion_control')
                config_path = os.path.join(share_dir, 'config', 'gait_params.yaml')
            except Exception as e:
                print(f"Warning: Package dog2_motion_control not found in ament index: {e}")
                print("Falling back to local development path...")
                # Fallback 到本地测试路径（仅用于开发和测试）
                current_dir = Path(__file__).parent
                config_path = current_dir.parent / 'config' / 'gait_params.yaml'
        
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        self.is_loaded = False
    
    def load(self) -> bool:
        """加载配置文件
        
        Returns:
            True表示加载成功，False表示加载失败（将使用默认值）
        """
        try:
            if not self.config_path.exists():
                print(f"Warning: Config file not found at {self.config_path}")
                print("Using default configuration.")
                self.config_data = self.DEFAULT_CONFIG.copy()
                self.is_loaded = True
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)

            # 兼容ROS参数文件结构：spider_robot_controller.ros__parameters
            if isinstance(self.config_data, dict):
                node_cfg = self.config_data.get('spider_robot_controller', {})
                if isinstance(node_cfg, dict) and 'ros__parameters' in node_cfg:
                    self.config_data = node_cfg['ros__parameters']
            
            # 验证配置有效性
            if not self._validate_config():
                print("Warning: Invalid configuration detected, using default values.")
                self.config_data = self.DEFAULT_CONFIG.copy()
                self.is_loaded = True
                return False
            
            self.is_loaded = True
            print(f"Configuration loaded successfully from {self.config_path}")
            return True
            
        except yaml.YAMLError as e:
            print(f"Error: Failed to parse YAML file: {e}")
            print("Using default configuration.")
            self.config_data = self.DEFAULT_CONFIG.copy()
            self.is_loaded = True
            return False
        except Exception as e:
            print(f"Error: Failed to load config file: {e}")
            print("Using default configuration.")
            self.config_data = self.DEFAULT_CONFIG.copy()
            self.is_loaded = True
            return False
    
    def _validate_config(self) -> bool:
        """验证配置参数有效性
        
        Returns:
            True表示配置有效，False表示配置无效
        """
        try:
            # 检查必需的顶层键
            required_keys = ['gait', 'joint_limits', 'control']
            for key in required_keys:
                if key not in self.config_data:
                    print(f"Error: Missing required key '{key}' in config")
                    return False
            
            # 验证步态参数
            gait = self.config_data['gait']
            if not self._validate_gait_params(gait):
                return False
            
            # 验证关节限位
            joint_limits = self.config_data['joint_limits']
            if not self._validate_joint_limits(joint_limits):
                return False
            
            # 验证控制参数
            control = self.config_data['control']
            if not self._validate_control_params(control):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error during validation: {e}")
            return False
    
    def _validate_gait_params(self, gait: Dict[str, Any]) -> bool:
        """验证步态参数
        
        Args:
            gait: 步态参数字典
        
        Returns:
            True表示有效，False表示无效
        """
        # 检查必需的参数
        required_params = ['stride_length', 'stride_height', 'cycle_time', 
                          'duty_factor', 'body_height', 'gait_type']
        for param in required_params:
            if param not in gait:
                print(f"Error: Missing gait parameter '{param}'")
                return False
        
        # 验证数值范围
        if gait['stride_length'] <= 0 or gait['stride_length'] > 0.2:
            print(f"Error: Invalid stride_length: {gait['stride_length']} (must be in (0, 0.2])")
            return False
        
        if gait['stride_height'] <= 0 or gait['stride_height'] > 0.15:
            print(f"Error: Invalid stride_height: {gait['stride_height']} (must be in (0, 0.15])")
            return False
        
        if gait['cycle_time'] <= 0 or gait['cycle_time'] > 10.0:
            print(f"Error: Invalid cycle_time: {gait['cycle_time']} (must be in (0, 10.0])")
            return False
        
        if gait['duty_factor'] <= 0 or gait['duty_factor'] >= 1.0:
            print(f"Error: Invalid duty_factor: {gait['duty_factor']} (must be in (0, 1.0))")
            return False
        
        # 爬行步态必须保证至少3腿着地（duty_factor >= 0.75）
        if gait['gait_type'] == 'crawl' and gait['duty_factor'] < 0.75:
            print(f"Error: Crawl gait requires duty_factor >= 0.75, got {gait['duty_factor']}")
            return False
        
        if gait['body_height'] <= 0 or gait['body_height'] > 0.5:
            print(f"Error: Invalid body_height: {gait['body_height']} (must be in (0, 0.5])")
            return False
        
        if gait['gait_type'] not in ['crawl', 'trot', 'walk']:
            print(f"Error: Invalid gait_type: {gait['gait_type']} (must be 'crawl', 'trot', or 'walk')")
            return False
        
        return True
    
    def _validate_joint_limits(self, joint_limits: Dict[str, Any]) -> bool:
        """验证关节限位
        
        Args:
            joint_limits: 关节限位字典
        
        Returns:
            True表示有效，False表示无效
        """
        required_joints = ['rail', 'haa', 'hfe', 'kfe']
        for joint in required_joints:
            if joint not in joint_limits:
                print(f"Error: Missing joint limit for '{joint}'")
                return False
            
            limits = joint_limits[joint]
            if 'min' not in limits or 'max' not in limits:
                print(f"Error: Joint '{joint}' must have 'min' and 'max' limits")
                return False
            
            if limits['min'] >= limits['max']:
                print(f"Error: Joint '{joint}' min limit must be less than max limit")
                return False
        
        return True
    
    def _validate_control_params(self, control: Dict[str, Any]) -> bool:
        """验证控制参数
        
        Args:
            control: 控制参数字典
        
        Returns:
            True表示有效，False表示无效
        """
        if 'frequency' not in control:
            print("Error: Missing control parameter 'frequency'")
            return False
        
        if control['frequency'] <= 0 or control['frequency'] > 1000:
            print(f"Error: Invalid frequency: {control['frequency']} (must be in (0, 1000])")
            return False
        
        if 'max_joint_velocity' not in control:
            print("Error: Missing control parameter 'max_joint_velocity'")
            return False
        
        if control['max_joint_velocity'] <= 0:
            print(f"Error: Invalid max_joint_velocity: {control['max_joint_velocity']} (must be > 0)")
            return False
        
        return True
    
    def get_gait_config(self) -> GaitConfig:
        """获取步态配置对象
        
        Returns:
            GaitConfig对象
        """
        if not self.is_loaded:
            self.load()
        
        # 防御性编程：确保即使 config_data 为空也能返回默认配置
        if not self.config_data or 'gait' not in self.config_data:
            print("Warning: config_data is empty or missing 'gait' key, using DEFAULT_CONFIG")
            self.config_data = self.DEFAULT_CONFIG.copy()
        
        gait = self.config_data['gait']
        return GaitConfig(
            stride_length=gait['stride_length'],
            stride_height=gait['stride_height'],
            cycle_time=gait['cycle_time'],
            duty_factor=gait['duty_factor'],
            body_height=gait['body_height'],
            gait_type=gait['gait_type']
        )
    
    def get_joint_limits(self) -> Dict[str, Dict[str, float]]:
        """获取关节限位
        
        Returns:
            关节限位字典
        """
        if not self.is_loaded:
            self.load()
        
        return self.config_data['joint_limits']
    
    def get_control_params(self) -> Dict[str, float]:
        """获取控制参数
        
        Returns:
            控制参数字典
        """
        if not self.is_loaded:
            self.load()
        
        return self.config_data['control']
    
    def get_config_data(self) -> Dict[str, Any]:
        """获取完整配置数据
        
        Returns:
            完整配置字典
        """
        if not self.is_loaded:
            self.load()
        
        return self.config_data.copy()
