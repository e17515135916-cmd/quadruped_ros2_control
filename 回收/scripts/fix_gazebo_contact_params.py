#!/usr/bin/env python3
"""
修复Gazebo接触参数
降低接触刚度以避免数值不稳定
"""

import sys

def fix_contact_params(urdf_file):
    """降低Gazebo接触参数"""
    
    with open(urdf_file, 'r') as f:
        content = f.read()
    
    # 备份原文件
    backup_file = urdf_file + '.backup_contact_params'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ 已备份原文件到: {backup_file}")
    
    # 替换接触参数
    # 从 kp=1000000.0 降低到 kp=10000.0 (降低100倍)
    content = content.replace('<kp>1000000.0</kp>', '<kp>10000.0</kp>')
    
    # 从 kd=100.0 降低到 kd=10.0 (降低10倍)
    content = content.replace('<kd>100.0</kd>', '<kd>10.0</kd>')
    
    # 写回文件
    with open(urdf_file, 'w') as f:
        f.write(content)
    
    print(f"✅ 已更新接触参数:")
    print(f"   kp: 1000000.0 → 10000.0 (降低100倍)")
    print(f"   kd: 100.0 → 10.0 (降低10倍)")
    print(f"\n这应该能显著提高仿真稳定性")

if __name__ == "__main__":
    urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    print("=" * 60)
    print("修复Gazebo接触参数")
    print("=" * 60)
    print()
    
    fix_contact_params(urdf_file)
    
    print()
    print("=" * 60)
    print("下一步:")
    print("=" * 60)
    print("1. 重新编译: colcon build --packages-select dog2_description")
    print("2. 测试Gazebo: ./test_convex_hull_gazebo.sh")
