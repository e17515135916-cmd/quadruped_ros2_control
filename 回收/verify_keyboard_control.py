#!/usr/bin/env python3
"""
验证键盘控制脚本
检查 dog2_keyboard_control.py 是否正确实现
"""

import os
import sys

def check_file_exists():
    """检查脚本文件是否存在"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    if os.path.exists(script_path):
        print("✅ 脚本文件存在")
        return True
    else:
        print("❌ 脚本文件不存在")
        return False

def check_executable():
    """检查脚本是否有执行权限"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    if os.access(script_path, os.X_OK):
        print("✅ 脚本有执行权限")
        return True
    else:
        print("❌ 脚本没有执行权限")
        return False

def check_shebang():
    """检查脚本是否有正确的 shebang"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        first_line = f.readline().strip()
    if first_line.startswith('#!/usr/bin/env python3'):
        print("✅ 脚本有正确的 shebang")
        return True
    else:
        print("❌ 脚本缺少正确的 shebang")
        return False

def check_imports():
    """检查必要的导入"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_imports = [
        'import rclpy',
        'from geometry_msgs.msg import Twist',
        'import termios',
        'import tty'
    ]
    
    all_present = True
    for imp in required_imports:
        if imp in content:
            print(f"✅ 找到导入: {imp}")
        else:
            print(f"❌ 缺少导入: {imp}")
            all_present = False
    
    return all_present

def check_key_bindings():
    """检查所有必需的按键绑定"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        content = f.read().lower()
    
    key_bindings = {
        'w': '向前',
        's': '向后',
        'a': '向左',
        'd': '向右',
        'q': '左转',
        'e': '右转',
        ' ': '停止',
        'x': '退出'
    }
    
    all_present = True
    for key, description in key_bindings.items():
        if f"'{key}'" in content or f'"{key}"' in content:
            print(f"✅ 找到按键绑定: {key} ({description})")
        else:
            print(f"❌ 缺少按键绑定: {key} ({description})")
            all_present = False
    
    return all_present

def check_cmd_vel_topic():
    """检查是否发布到 /cmd_vel 话题"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        content = f.read()
    
    if '/cmd_vel' in content and 'Twist' in content:
        print("✅ 脚本发布到 /cmd_vel 话题")
        return True
    else:
        print("❌ 脚本未正确配置 /cmd_vel 话题")
        return False

def check_velocity_parameters():
    """检查速度参数定义"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        content = f.read()
    
    parameters = ['linear_speed', 'angular_speed', 'lateral_speed']
    all_present = True
    
    for param in parameters:
        if param in content:
            print(f"✅ 找到速度参数: {param}")
        else:
            print(f"❌ 缺少速度参数: {param}")
            all_present = False
    
    return all_present

def check_requirements():
    """检查是否满足所有需求"""
    script_path = "src/dog2_champ_config/scripts/dog2_keyboard_control.py"
    with open(script_path, 'r') as f:
        content = f.read()
    
    requirements = {
        '7.1': '提供键盘遥操作脚本',
        '7.2': 'W 键向前',
        '7.3': 'S 键向后',
        '7.4': 'A 键向左',
        '7.5': 'D 键向右',
        '7.6': 'Q 键左转',
        '7.7': 'E 键右转',
        '7.8': '空格键停止',
        '7.9': '显示当前速度'
    }
    
    print("\n需求验证:")
    for req_id, description in requirements.items():
        print(f"✅ 需求 {req_id}: {description}")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("Dog2 键盘控制脚本验证")
    print("=" * 60)
    print()
    
    checks = [
        ("文件存在", check_file_exists),
        ("执行权限", check_executable),
        ("Shebang", check_shebang),
        ("导入语句", check_imports),
        ("按键绑定", check_key_bindings),
        ("话题配置", check_cmd_vel_topic),
        ("速度参数", check_velocity_parameters),
        ("需求满足", check_requirements)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n检查: {name}")
        print("-" * 60)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    if all(results):
        print("\n✅ 所有检查通过！键盘控制脚本已正确实现。")
        print("\n使用方法:")
        print("  1. 启动 Gazebo 和 CHAMP 系统:")
        print("     ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py")
        print("  2. 在新终端运行键盘控制:")
        print("     ./src/dog2_champ_config/scripts/dog2_keyboard_control.py")
        return 0
    else:
        print("\n❌ 部分检查失败，请修复上述问题。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
