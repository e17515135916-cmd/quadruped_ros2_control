#!/usr/bin/env python3
"""
修正足端位置：
1. 保持颜色为绿色
2. 沿Z轴负方向（蓝色坐标反方向）移动12cm
"""
import re

xacro_file = 'src/dog2_description/urdf/dog2.urdf.xacro'

with open(xacro_file, 'r') as f:
    content = f.read()

# 位置修正：
# 原位置: xyz="0 -0.299478 0"（小腿末端）
# 新位置: xyz="0 -0.299478 -0.12"（沿Z轴负方向移动12cm）
# 
# 之前错误地修改了Y轴，现在改为修改Z轴

content = re.sub(
    r'(<joint name="j\$\{leg_num\}1111"[^>]*>.*?<origin[^>]*xyz=")0 -0\.179478 0(")',
    r'\g<1>0 -0.299478 -0.12\g<2>',
    content,
    flags=re.DOTALL
)

with open(xacro_file, 'w') as f:
    f.write(content)

print("✅ 修改完成：")
print(f"   1. 颜色：保持绿色 (RGB: 0.0, 1.0, 0.0)")
print(f"   2. 位置：xyz='0 -0.299478 -0.12'")
print(f"      - Y = -0.299478m（小腿末端）")
print(f"      - Z = -0.12m（沿Z轴负方向移动12cm）")
