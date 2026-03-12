#!/usr/bin/env python3
"""
修复j21关节位置
根据图片显示，j21的位置不正确，需要调整hip_joint_xyz参数
"""

import re

# 读取URDF文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找Leg 2的定义
# 当前: origin_xyz="1.3491 -0.80953 0.2649"
# 需要添加: hip_joint_xyz参数

# 找到Leg 2的定义行
leg2_pattern = r'(<!-- Leg 2: Front Right -->.*?<xacro:leg leg_num="2".*?)(thigh_inertia_xyz="\$\{leg12_thigh_inertia_xyz\}".*?shin_inertia_xyz="\$\{leg12_shin_inertia_xyz\}"/>)'

match = re.search(leg2_pattern, content, re.DOTALL)

if match:
    print("找到Leg 2定义")
    print("当前配置:")
    print(match.group(0))
    print("\n" + "="*60 + "\n")
    
    # 检查是否已经有hip_joint_xyz参数
    if 'hip_joint_xyz' in match.group(0):
        print("⚠️  Leg 2已经有hip_joint_xyz参数")
        # 提取当前值
        hip_xyz_match = re.search(r'hip_joint_xyz="([^"]+)"', match.group(0))
        if hip_xyz_match:
            print(f"当前值: {hip_xyz_match.group(1)}")
    else:
        print("✓ Leg 2没有hip_joint_xyz参数，使用默认值: -0.016 0.0199 0.055")
        print("\n建议的修复方案:")
        print("1. 添加 hip_joint_xyz=\"-0.016 0.0199 0.055\" (使用默认值)")
        print("2. 或者调整为与Leg 1相同的值")
        
        # 显示Leg 1的配置作为参考
        leg1_match = re.search(r'<!-- Leg 1: Front Left -->.*?<xacro:leg leg_num="1".*?shin_inertia_xyz="\$\{leg12_shin_inertia_xyz\}"/>', content, re.DOTALL)
        if leg1_match:
            print("\nLeg 1配置（参考）:")
            print(leg1_match.group(0))
else:
    print("❌ 未找到Leg 2定义")

print("\n" + "="*60)
print("分析:")
print("="*60)
print("""
从图片看，j21（第二条腿的髋关节）位置不对。

可能的原因:
1. hip_joint_xyz参数使用了默认值，但应该根据实际机器人结构调整
2. Leg 2的origin_xyz可能需要调整

建议:
1. 检查实际机器人的CAD模型，确定j21相对于l2的正确位置
2. 对比Leg 1和Leg 2的配置，确保对称性
3. 如果Leg 1正确，可以参考其配置调整Leg 2
""")
