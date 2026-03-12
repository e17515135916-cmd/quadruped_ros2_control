#!/usr/bin/env python3
"""
自动修复j21位置
通过对比Leg 1、Leg 3、Leg 4的配置，推断Leg 2的正确hip_xyz参数
"""

import re
import shutil
from datetime import datetime

# 读取URDF文件
urdf_file = 'src/dog2_description/urdf/dog2.urdf.xacro'
with open(urdf_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("="*60)
print("J21位置自动修复工具")
print("="*60)
print()

# 提取所有腿的配置
leg_configs = {}
for leg_num in [1, 2, 3, 4]:
    pattern = rf'<xacro:leg leg_num="{leg_num}".*?(?:/>|thigh_col_rpy="[^"]*"/>)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        leg_configs[leg_num] = match.group(0)

# 显示当前配置
print("当前配置:")
print("-" * 60)
for leg_num, config in leg_configs.items():
    print(f"\nLeg {leg_num}:")
    # 提取关键参数
    xyz_match = re.search(r'xyz="([^"]+)"', config)
    hip_xyz_match = re.search(r'hip_xyz="([^"]+)"', config)
    hip_rpy_match = re.search(r'hip_rpy="([^"]+)"', config)
    
    if xyz_match:
        print(f"  xyz: {xyz_match.group(1)}")
    if hip_xyz_match:
        print(f"  hip_xyz: {hip_xyz_match.group(1)}")
    else:
        print(f"  hip_xyz: -0.016 0.0199 0.055 (默认值)")
    if hip_rpy_match:
        print(f"  hip_rpy: {hip_rpy_match.group(1)}")
    else:
        print(f"  hip_rpy: 0 0 1.5708 (默认值)")

print()
print("="*60)
print("分析:")
print("="*60)
print("""
从配置看：
- Leg 1: 使用默认hip_xyz (-0.016 0.0199 0.055)
- Leg 2: 使用默认hip_xyz (-0.016 0.0199 0.055) ← 问题所在
- Leg 3: 使用默认hip_xyz，但有hip_rpy="3.1416 0 1.5708"
- Leg 4: 使用自定义hip_xyz="0.0116 0.0199 0.055"，有hip_rpy="3.1416 0 1.5708"

观察：
1. Leg 1和Leg 2是前腿，应该对称
2. Leg 4有自定义hip_xyz，X值从-0.016变为0.0116（符号相反）
3. 这表明左右腿的hip_xyz的X分量应该相反

推断：
- Leg 1 (左前): hip_xyz="-0.016 0.0199 0.055"
- Leg 2 (右前): hip_xyz="0.016 0.0199 0.055" (X取反)
""")

print()
print("="*60)
print("修复方案:")
print("="*60)
print("为Leg 2添加 hip_xyz=\"0.016 0.0199 0.055\"")
print()

# 询问是否执行修复
response = input("是否执行修复？(y/n): ")

if response.lower() == 'y':
    # 备份原文件
    backup_file = f"{urdf_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(urdf_file, backup_file)
    print(f"✓ 已备份到: {backup_file}")
    
    # 修改Leg 2配置
    # 找到Leg 2的配置行
    leg2_pattern = r'(<xacro:leg leg_num="2"[^>]*?thigh_xyz="\$\{leg12_thigh_xyz\}" shin_xyz="\$\{leg12_shin_xyz\}"/>)'
    
    def replace_leg2(match):
        original = match.group(1)
        # 在结束标签前添加hip_xyz参数
        modified = original.replace('thigh_xyz="${leg12_thigh_xyz}" shin_xyz="${leg12_shin_xyz}"/>',
                                   'thigh_xyz="${leg12_thigh_xyz}" shin_xyz="${leg12_shin_xyz}"\n             hip_xyz="0.016 0.0199 0.055"/>')
        return modified
    
    new_content = re.sub(leg2_pattern, replace_leg2, content)
    
    # 写入文件
    with open(urdf_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ 已更新Leg 2配置")
    print()
    
    # 显示修改后的配置
    with open(urdf_file, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    leg2_match = re.search(r'<xacro:leg leg_num="2".*?/>', new_content, re.DOTALL)
    if leg2_match:
        print("新的Leg 2配置:")
        print("-" * 60)
        print(leg2_match.group(0))
        print()
    
    print("="*60)
    print("下一步:")
    print("="*60)
    print("1. 编译: colcon build --packages-select dog2_description --symlink-install")
    print("2. 加载: source install/setup.bash")
    print("3. 查看: ros2 launch dog2_description view_dog2.launch.py")
    print()
    
    # 询问是否立即编译
    compile_response = input("是否立即编译并查看？(y/n): ")
    if compile_response.lower() == 'y':
        import subprocess
        import os
        
        print()
        print("正在编译...")
        result = subprocess.run(['colcon', 'build', '--packages-select', 'dog2_description', '--symlink-install'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 编译成功")
            print()
            print("正在启动RViz...")
            
            # 杀死旧进程
            subprocess.run(['killall', '-9', 'robot_state_publisher', 'joint_state_publisher', 'rviz2'],
                         stderr=subprocess.DEVNULL)
            
            # 等待一秒
            import time
            time.sleep(1)
            
            # 启动RViz
            print("请在新终端中运行:")
            print("source install/setup.bash && ros2 launch dog2_description view_dog2.launch.py")
        else:
            print("❌ 编译失败:")
            print(result.stderr)
else:
    print("已取消修复")
