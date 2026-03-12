#!/usr/bin/env python3
"""修改足端偏移量"""
import re

xacro_file = 'src/dog2_description/urdf/dog2.urdf.xacro'

with open(xacro_file, 'r') as f:
    content = f.read()

# 替换足端关节的偏移量
# 从 -0.29 改为 -0.30
content = re.sub(
    r'(<joint name="j\$\{leg_num\}1111"[^>]*>.*?<origin[^>]*xyz=")0 -0\.29 0(")',
    r'\g<1>0 -0.30 0\g<2>',
    content,
    flags=re.DOTALL
)

with open(xacro_file, 'w') as f:
    f.write(content)

print("✅ 足端偏移量已修改为 -0.30m")
