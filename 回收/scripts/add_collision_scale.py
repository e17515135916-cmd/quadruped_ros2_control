#!/usr/bin/env python3
"""
为所有碰撞网格添加scale参数（缩水大法）
只修改collision，不修改visual
"""

import re

urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"

# 读取文件
with open(urdf_file, 'r') as f:
    content = f.read()

# 备份
backup_file = urdf_file + '.backup_before_scale'
with open(backup_file, 'w') as f:
    f.write(content)
print(f"✅ 已备份到: {backup_file}")
print()

# 缩放比例（可调整）
SCALE = "0.9 0.9 0.9"  # 缩小10%

print(f"应用缩放比例: {SCALE}")
print()

# 查找所有collision块中的mesh标签，添加scale属性
# 匹配: <collision>...<mesh filename="..." />...</collision>
# 替换为: <collision>...<mesh filename="..." scale="0.9 0.9 0.9"/>...</collision>

# 方法1: 匹配没有scale属性的mesh标签（在collision块内）
pattern = r'(<collision>.*?<mesh\s+filename="[^"]*")(/>)'

def add_scale(match):
    # 检查是否已经有scale属性
    if 'scale=' in match.group(0):
        return match.group(0)
    return match.group(1) + f' scale="{SCALE}"' + match.group(2)

new_content, count = re.subn(pattern, add_scale, content, flags=re.DOTALL)

if count > 0:
    content = new_content
    print(f"✅ 为 {count} 个碰撞网格添加了scale属性")
else:
    print("⚠️  没有找到需要修改的碰撞网格")

# 写回文件
with open(urdf_file, 'w') as f:
    f.write(content)

print(f"✅ 已保存到: {urdf_file}")
print()
print("=" * 70)
print("缩水大法效果:")
print("=" * 70)
print("• 碰撞体缩小10%，在关节处创造间隙")
print("• 视觉模型保持原样，外观完美")
print("• 防止大腿-小腿在膝关节处重叠")
print("• 应该能彻底解决'量子爆炸'问题")
print()
print("如果还有问题，可以进一步缩小到0.85或0.8")
