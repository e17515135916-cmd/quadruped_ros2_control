#!/usr/bin/env python3
"""
继续调整足端位置：更低、更靠近中间
"""

import re

# 读取URDF文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# 当前偏移: xyz="0 -0.31 -0.13"
# 新偏移: xyz="0 -0.33 -0.10" (更低、更靠近中间)
old_pattern = r'<origin rpy="0 0 0" xyz="0 -0\.31 -0\.13"/>'
new_pattern = '<origin rpy="0 0 0" xyz="0 -0.33 -0.10"/>'

content = re.sub(old_pattern, new_pattern, content)
print("✓ 更新足端关节偏移:")
print("  y: -0.31 → -0.33 (向下2cm)")
print("  z: -0.13 → -0.10 (向前3cm，更靠近中间)")

# 写回
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("完成!")
