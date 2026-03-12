#!/usr/bin/env python3
"""
为碰撞网格添加 scale 参数（缩水大法）

配置：
- base_link: scale="0.95 0.95 0.95" (缩小5%)
- 腿部所有部件: scale="0.8 0.8 0.8" (缩小20%)
"""

urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"

# 读取文件
with open(urdf_file, 'r') as f:
    content = f.read()

# 备份
backup_file = urdf_file + '.backup_scale'
with open(backup_file, 'w') as f:
    f.write(content)
print(f"✅ 已备份到: {backup_file}\n")

# 替换规则
replacements = [
    # base_link: 缩小5%
    (
        'meshes/collision/base_link_collision.STL" />',
        'meshes/collision/base_link_collision.STL" scale="0.95 0.95 0.95" />'
    ),
    # 腿部所有部件（使用 xacro 变量）: 缩小20%
    ('meshes/collision/l${leg_num}_collision.STL"/>', 'meshes/collision/l${leg_num}_collision.STL" scale="0.8 0.8 0.8"/>'),
    ('meshes/collision/l${leg_num}1_collision.STL"/>', 'meshes/collision/l${leg_num}1_collision.STL" scale="0.8 0.8 0.8"/>'),
    ('meshes/collision/l${leg_num}11_collision.STL"/>', 'meshes/collision/l${leg_num}11_collision.STL" scale="0.8 0.8 0.8"/>'),
    ('meshes/collision/l${leg_num}111_collision.STL"/>', 'meshes/collision/l${leg_num}111_collision.STL" scale="0.8 0.8 0.8"/>'),
]

# 执行替换
count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
        # 提取文件名
        filename = old.split('/')[-1].replace('" />', '')
        print(f"  ✓ {filename}")

print(f"\n✅ 成功为 {count} 个碰撞网格添加 scale 参数")

# 写回文件
with open(urdf_file, 'w') as f:
    f.write(content)

print(f"✅ 已保存到: {urdf_file}\n")
print("=" * 70)
print("缩放配置:")
print("=" * 70)
print("• base_link: scale=0.95 (缩小5%，保持主体完整)")
print("• 腿部所有部件: scale=0.8 (缩小20%，在关节处创造间隙)")
print()
print("效果:")
print("• 碰撞体在关节处不再重叠")
print("• 视觉模型保持原样，外观完美")
print("• 应该能彻底解决'量子爆炸'问题")
print()
print("下一步:")
print("1. colcon build --packages-select dog2_description --symlink-install")
print("2. source install/setup.bash")
print("3. ./test_scale_fix.sh")
