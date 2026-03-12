#!/usr/bin/env python3
"""
修复 Leg 1 和 Leg 2 的实例化，添加 hip_joint_rpy 参数
"""

import re

xacro_file = "src/dog2_description/urdf/dog2.urdf.xacro"

# 读取文件
with open(xacro_file, 'r') as f:
    content = f.read()

# 修复 Leg 1
# 在 shin_inertia_xyz 后面添加 hip_joint_rpy
leg1_pattern = r'(<!-- Leg 1: Front Left -->.*?<xacro:leg prefix="lf".*?shin_inertia_xyz="\$\{leg12_shin_inertia_xyz\}")(.*?foot_xyz="0\.026 -0\.289478 -0\.14"/>)'
leg1_replacement = r'\1\n             hip_joint_rpy="-1.5708 0 0"\2'
content = re.sub(leg1_pattern, leg1_replacement, content, flags=re.DOTALL)

# 修复 Leg 2
# 在 prismatic_inertia_xyz 前面添加 hip_joint_rpy
leg2_pattern = r'(<!-- Leg 2: Front Right -->.*?<xacro:leg prefix="rf".*?shin_inertia_xyz="\$\{leg12_shin_inertia_xyz\}")(.*?prismatic_inertia_xyz=)'
leg2_replacement = r'\1\n             hip_joint_rpy="-1.5708 0 0"\2'
content = re.sub(leg2_pattern, leg2_replacement, content, flags=re.DOTALL)

# 写回文件
with open(xacro_file, 'w') as f:
    f.write(content)

print("✓ 已修复 Leg 1 和 Leg 2 的实例化")
print("✓ 添加了 hip_joint_rpy=\"-1.5708 0 0\" 参数")
