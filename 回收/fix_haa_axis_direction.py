#!/usr/bin/env python3
"""
正确修复 HAA 关节轴方向

问题：Prismatic joint 有 rpy="1.5708 0 0" (绕 x 轴旋转 90°)
这导致坐标系旋转，原来的 z 轴现在指向 -y 方向

解决方案：将 HAA 的轴从 "0 0 1" (z轴) 改为 "0 -1 0" (-y轴)
这样在旋转后，HAA 轴会指向世界坐标系的 z 轴（垂直方向）
"""

import re

xacro_file = "src/dog2_description/urdf/dog2.urdf.xacro"

# 读取文件
with open(xacro_file, 'r') as f:
    content = f.read()

# 修改 Leg 1 和 Leg 2 的 haa_axis
# 从 "0 0 1" 改为 "0 -1 0"

# Leg 1
content = re.sub(
    r'(<!-- Leg 1: Front Left -->.*?<xacro:leg prefix="lf".*?)haa_axis="0 0 1"',
    r'\1haa_axis="0 -1 0"',
    content,
    flags=re.DOTALL
)

# Leg 2
content = re.sub(
    r'(<!-- Leg 2: Front Right -->.*?<xacro:leg prefix="rf".*?)haa_axis="0 0 1"',
    r'\1haa_axis="0 -1 0"',
    content,
    flags=re.DOTALL
)

# 写回文件
with open(xacro_file, 'w') as f:
    f.write(content)

print("✓ 已修改 Leg 1 和 Leg 2 的 HAA 轴方向")
print("  从: haa_axis=\"0 0 1\" (z轴)")
print("  到: haa_axis=\"0 -1 0\" (-y轴)")
print("\n原理：")
print("  Prismatic joint 绕 x 轴旋转 90°")
print("  原来的 z 轴 → 现在的 -y 方向")
print("  所以 HAA 使用 -y 轴，旋转后会指向世界坐标系的 z 轴")
