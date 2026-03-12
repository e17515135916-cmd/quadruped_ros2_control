#!/usr/bin/env python3
"""
修复 base_link 碰撞模型因缩放导致的位置偏移

原理：
当一个 mesh 被缩放时，如果它的几何中心不在 (0,0,0)，
缩放会导致模型向原点收缩，产生位置偏移。

解决方案：
1. 找到 mesh 的几何中心 C
2. 计算缩放因子 s (例如 0.95)
3. 偏移量 = C * (1 - s)
4. 调整 collision origin 来补偿这个偏移
"""

import numpy as np
from stl import mesh as stl_mesh

# 读取 base_link 碰撞 STL 文件
stl_file = "src/dog2_description/meshes/collision/base_link_collision.STL"

print("=" * 70)
print("计算 base_link 碰撞模型的几何中心")
print("=" * 70)

# 加载 STL
mesh = stl_mesh.Mesh.from_file(stl_file)

# 计算所有顶点的中心
vertices = mesh.vectors.reshape(-1, 3)
center = vertices.mean(axis=0)

print(f"STL 文件: {stl_file}")
print(f"顶点数量: {len(vertices)}")
print(f"几何中心: ({center[0]:.6f}, {center[1]:.6f}, {center[2]:.6f})")
print()

# 缩放因子
scale = 0.95

# 计算偏移量
# 当 mesh 从中心 C 缩放到 s*C 时，需要补偿的偏移量是 C*(1-s)
offset = center * (1 - scale)

print("=" * 70)
print("缩放补偿计算")
print("=" * 70)
print(f"缩放因子: {scale}")
print(f"需要补偿的偏移量: ({offset[0]:.6f}, {offset[1]:.6f}, {offset[2]:.6f})")
print()

# 读取 URDF 文件
urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"
with open(urdf_file, 'r') as f:
    content = f.read()

# 备份
backup_file = urdf_file + '.backup_offset'
with open(backup_file, 'w') as f:
    f.write(content)
print(f"✅ 已备份到: {backup_file}")

# 查找并替换 base_link collision origin
# 原始: <origin xyz="0 0 0" rpy="0 0 0" />
# 新的: <origin xyz="offset_x offset_y offset_z" rpy="0 0 0" />

old_origin = '<origin xyz="0 0 0" rpy="0 0 0" />'
new_origin = f'<origin xyz="{offset[0]:.6f} {offset[1]:.6f} {offset[2]:.6f}" rpy="0 0 0" />'

# 只替换 base_link collision 块中的 origin
# 需要精确匹配，避免替换其他地方的 origin

# 查找 base_link collision 块
import re

# 匹配 base_link 的 collision 块
pattern = r'(<link name="base_link">.*?<collision>\s*)<origin xyz="0 0 0" rpy="0 0 0" />'

def replace_base_origin(match):
    return match.group(1) + new_origin

content_new = re.sub(pattern, replace_base_origin, content, flags=re.DOTALL)

if content_new != content:
    content = content_new
    print(f"✅ 已更新 base_link collision origin")
    print(f"   旧值: xyz=\"0 0 0\"")
    print(f"   新值: xyz=\"{offset[0]:.6f} {offset[1]:.6f} {offset[2]:.6f}\"")
else:
    print("⚠️  未找到需要替换的 origin（可能已经修改过）")

# 写回文件
with open(urdf_file, 'w') as f:
    f.write(content)

print(f"✅ 已保存到: {urdf_file}")
print()
print("=" * 70)
print("说明")
print("=" * 70)
print("• 当 mesh 缩放时，如果几何中心不在原点，会产生位置偏移")
print("• 通过调整 collision origin，补偿这个偏移")
print("• 现在碰撞模型应该和视觉模型完美对齐了")
print()
print("下一步:")
print("1. colcon build --packages-select dog2_description --symlink-install")
print("2. source install/setup.bash")
print("3. 在 RViz 中查看，碰撞模型应该和视觉模型重合")
