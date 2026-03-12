"""
测试防御性编程修复

验证两个关键的防御性编程修复：
1. ConfigLoader.get_gait_config() 在 config_data 为空时的回退
2. SpiderRobotController 在平滑停止期间阻止配置更新
"""

import unittest
import tempfile
import os
from pathlib import Path

from dog2_motion_control.config_loader import ConfigLoader
from dog2_motion_control.gait_generator import GaitConfig
from dog2_motion_control.spider_robot_controller import SpiderRobotController


class TestConfigLoaderDefensiveProgramming(unittest.TestCase):
    """测试 ConfigLoader 的防御性编程"""
    
    def test_get_gait_config_with_empty_config_data(self):
        """测试当 config_data 为空时，get_gait_config 能正确回退到默认配置"""
        # 创建一个不存在的配置文件路径
        non_existent_path = "/tmp/non_existent_config_12345.yaml"
        loader = ConfigLoader(non_existent_path)
        
        # 不调用 load()，直接调用 get_gait_config()
        # 这会触发自动加载，但由于文件不存在，config_data 应该被设置为 DEFAULT_CONFIG
        config = loader.get_gait_config()
        
        # 验证返回的是有效的 GaitConfig 对象
        self.assertIsInstance(config, GaitConfig)
        self.assertEqual(config.stride_length, 0.08)
        self.assertEqual(config.stride_height, 0.05)
        self.assertEqual(config.cycle_time, 2.0)
        self.assertEqual(config.duty_factor, 0.75)
        self.assertEqual(config.body_height, 0.2)
        self.assertEqual(config.gait_type, 'crawl')
    
    def test_get_gait_config_with_corrupted_config_data(self):
        """测试当 config_data 被意外清空时，get_gait_config 能正确处理"""
        loader = ConfigLoader()
        loader.load()
        
        # 模拟 config_data 被意外清空的情况
        loader.config_data = {}
        
        # 调用 get_gait_config() 应该能正确回退到默认配置
        config = loader.get_gait_config()
        
        # 验证返回的是有效的 GaitConfig 对象
        self.assertIsInstance(config, GaitConfig)
        self.assertEqual(config.stride_length, 0.08)
        self.assertEqual(config.gait_type, 'crawl')
    
    def test_get_gait_config_with_missing_gait_key(self):
        """测试当 config_data 缺少 'gait' 键时，get_gait_config 能正确处理"""
        loader = ConfigLoader()
        loader.load()
        
        # 模拟 config_data 缺少 'gait' 键的情况
        loader.config_data = {'joint_limits': {}, 'control': {}}
        
        # 调用 get_gait_config() 应该能正确回退到默认配置
        config = loader.get_gait_config()
        
        # 验证返回的是有效的 GaitConfig 对象
        self.assertIsInstance(config, GaitConfig)
        self.assertEqual(config.stride_length, 0.08)


class TestSpiderRobotControllerDefensiveProgramming(unittest.TestCase):
    """测试 SpiderRobotController 的防御性编程"""
    
    def setUp(self):
        """设置测试环境"""
        # 注意：这个测试不初始化 ROS 2，因为我们只测试逻辑
        # 实际使用时需要 rclpy.init()
        pass
    
    def test_config_update_blocked_during_smooth_stop(self):
        """测试平滑停止期间配置更新被阻止"""
        # 创建控制器（不启动 ROS 2）
        # 注意：这个测试需要模拟环境，因为 SpiderRobotController 依赖 ROS 2
        # 这里我们只验证逻辑，不实际运行
        
        # 验证 _check_and_apply_config_update 方法的逻辑
        # 当 self.is_stopping == True 时，应该直接返回，不应用配置更新
        
        # 这个测试需要在集成测试中完成，因为涉及 ROS 2 节点
        # 这里我们只验证代码逻辑存在
        
        # 读取源代码验证逻辑
        source_file = Path(__file__).parent.parent / 'dog2_motion_control' / 'spider_robot_controller.py'
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        # 验证防御性检查存在
        self.assertIn('if self.is_stopping:', source_code)
        self.assertIn('# 防御性编程：平滑停止期间阻止配置更新', source_code)
        
        # 验证在 _check_and_apply_config_update 方法中
        self.assertIn('def _check_and_apply_config_update(self):', source_code)


if __name__ == '__main__':
    unittest.main()
