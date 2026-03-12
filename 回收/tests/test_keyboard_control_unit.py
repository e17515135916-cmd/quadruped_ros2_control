#!/usr/bin/env python3
"""
单元测试：键盘控制脚本
验证键盘控制脚本的基本功能
"""

import unittest
import sys
import os

# 添加脚本路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'dog2_champ_config', 'scripts'))

class TestKeyboardControlScript(unittest.TestCase):
    """测试键盘控制脚本的基本功能"""
    
    def test_script_exists(self):
        """测试脚本文件是否存在"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        self.assertTrue(os.path.exists(script_path), "键盘控制脚本文件不存在")
    
    def test_script_is_executable(self):
        """测试脚本是否有执行权限"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        self.assertTrue(os.access(script_path, os.X_OK), "脚本没有执行权限")
    
    def test_script_has_shebang(self):
        """测试脚本是否有正确的shebang"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        self.assertTrue(
            first_line.startswith('#!/usr/bin/env python3'),
            "脚本缺少正确的shebang"
        )
    
    def test_script_imports(self):
        """测试脚本的导入语句"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        with open(script_path, 'r') as f:
            content = f.read()
        
        # 检查必要的导入
        self.assertIn('import rclpy', content, "缺少rclpy导入")
        self.assertIn('from geometry_msgs.msg import Twist', content, "缺少Twist消息导入")
        self.assertIn('import termios', content, "缺少termios导入")
        self.assertIn('import tty', content, "缺少tty导入")
    
    def test_script_has_key_bindings(self):
        """测试脚本是否包含所有必需的按键绑定"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        with open(script_path, 'r') as f:
            content = f.read()
        
        # 检查所有按键绑定
        required_keys = ['w', 's', 'a', 'd', 'q', 'e', ' ', 'x']
        for key in required_keys:
            self.assertIn(f"'{key}'", content.lower(), f"缺少按键 '{key}' 的绑定")
    
    def test_script_publishes_to_cmd_vel(self):
        """测试脚本是否发布到/cmd_vel话题"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        with open(script_path, 'r') as f:
            content = f.read()
        
        self.assertIn('/cmd_vel', content, "脚本未发布到/cmd_vel话题")
        self.assertIn('Twist', content, "脚本未使用Twist消息类型")
    
    def test_script_has_velocity_parameters(self):
        """测试脚本是否定义了速度参数"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'dog2_champ_config', 
            'scripts', 
            'dog2_keyboard_control.py'
        )
        with open(script_path, 'r') as f:
            content = f.read()
        
        # 检查速度参数
        self.assertIn('linear_speed', content, "缺少线速度参数")
        self.assertIn('angular_speed', content, "缺少角速度参数")
        self.assertIn('lateral_speed', content, "缺少侧向速度参数")

if __name__ == '__main__':
    unittest.main()
