#!/usr/bin/env python3
"""
根据小腿STL实际尺寸，将足端偏移量设置为小腿末端位置
"""
import re

xacro_file = 'src/dog2_description/urdf/dog2.urdf.xacro'

with open(xacro_file, 'r') as f:
    content = f.read()

# 小腿STL末端位置: Y = -0.299478 m
# 足端球体半径: 0.02 m (碰撞) / 0.05 m (视觉)
# 
# 如果要让球心在小腿末端，偏移量应该是 -0.299478
# 如果要让球体表面接触小腿末端，偏移量应该是 -0.299478 - 0.02 = -0.319478
#
# 用户说"移过去"，应该是让球心接近小腿末端，所以使用 -0.299478

new_offset = -0.299478

# 替换足端关节的偏移量
content = re.sub(
    r'(<joint name="j\$\{leg_num\}1111"[^>]*>.*?<origin[^>]*xyz=")0 -0\.\d+ 0(")',
    f'\\g<1>0 {new_offset:.6f} 0\\g<2>',
    content,
    flags=re.DOTALL
)

with open(xacro_file, 'w') as f:
    f.write(content)

print(f"✅ 足端偏移量已修改为 {new_offset:.6f}m")
print(f"   这将使足端球心位于小腿STL末端位置")
