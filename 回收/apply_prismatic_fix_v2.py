#!/usr/bin/env python3
"""
Prismatic 坐标系修复 V2 - 使用字符串替换

这个脚本直接修改 URDF 文件的文本内容，避免 XML 解析问题
"""

import re
from pathlib import Path

def apply_fix(input_file, output_file):
    """应用修复"""
    
    print("=" * 60)
    print("应用 Prismatic 坐标系修复 V2")
    print("=" * 60)
    
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加 world link（在 base_link 之前）
    print("\n1. 添加 world link...")
    if '<link name="world"/>' not in content and '<link name="world">' not in content:
        # 在 base_link 之前插入
        content = content.replace(
            '  <!-- Base link (main body) -->',
            '''  <link name="world"/>
  
  <joint name="world_joint" type="fixed">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <!-- Base link (main body) -->'''
        )
        print("   ✓ 已添加 world link")
    else:
        print("   ✓ world link 已存在")
    
    # 2. 更新 macro 参数
    print("\n2. 更新 macro 参数...")
    content = content.replace(
        '<xacro:macro name="leg" params="leg_num origin_xyz origin_rpy',
        '<xacro:macro name="leg" params="prefix leg_num origin_xyz origin_rpy'
    )
    # 添加 haa_axis 参数
    if 'haa_axis' not in content:
        content = content.replace(
            'foot_xyz:=\'-0.034 -0.299478 -0.12\'">',
            'foot_xyz:=\'-0.034 -0.299478 -0.12\'\n                                 haa_axis:=\'0 0 1\'">'
        )
    print("   ✓ 已添加 prefix 和 haa_axis 参数")
    
    # 3. 更新 macro 中的关节和连杆名称
    print("\n3. 更新 macro 中的关节和连杆名称...")
    
    # HAA joint: j${leg_num}1 -> ${prefix}_haa_joint
    content = content.replace(
        '<joint name="j${leg_num}1" type="revolute">',
        '<joint name="${prefix}_haa_joint" type="revolute">'
    )
    # HAA link: l${leg_num}1 -> ${prefix}_hip_link
    content = content.replace(
        '<link name="l${leg_num}1">',
        '<link name="${prefix}_hip_link">'
    )
    content = content.replace(
        '<parent link="l${leg_num}1"/>',
        '<parent link="${prefix}_hip_link"/>'
    )
    content = content.replace(
        '<child link="l${leg_num}1"/>',
        '<child link="${prefix}_hip_link"/>'
    )
    
    # HFE joint: j${leg_num}11 -> ${prefix}_hfe_joint
    content = content.replace(
        '<joint name="j${leg_num}11" type="revolute">',
        '<joint name="${prefix}_hfe_joint" type="revolute">'
    )
    # HFE link: l${leg_num}11 -> ${prefix}_upper_leg_link
    content = content.replace(
        '<link name="l${leg_num}11">',
        '<link name="${prefix}_upper_leg_link">'
    )
    content = content.replace(
        '<parent link="l${leg_num}11"/>',
        '<parent link="${prefix}_upper_leg_link"/>'
    )
    content = content.replace(
        '<child link="l${leg_num}11"/>',
        '<child link="${prefix}_upper_leg_link"/>'
    )
    
    # KFE joint: j${leg_num}111 -> ${prefix}_kfe_joint
    content = content.replace(
        '<joint name="j${leg_num}111" type="revolute">',
        '<joint name="${prefix}_kfe_joint" type="revolute">'
    )
    # KFE link: l${leg_num}111 -> ${prefix}_lower_leg_link
    content = content.replace(
        '<link name="l${leg_num}111">',
        '<link name="${prefix}_lower_leg_link">'
    )
    content = content.replace(
        '<parent link="l${leg_num}111"/>',
        '<parent link="${prefix}_lower_leg_link"/>'
    )
    content = content.replace(
        '<child link="l${leg_num}111"/>',
        '<child link="${prefix}_lower_leg_link"/>'
    )
    
    # Foot joint: j${leg_num}1111 -> ${prefix}_foot_fixed_joint
    content = content.replace(
        '<joint name="j${leg_num}1111" type="fixed">',
        '<joint name="${prefix}_foot_fixed_joint" type="fixed">'
    )
    # Foot link: l${leg_num}1111 -> ${prefix}_foot_link
    content = content.replace(
        '<link name="l${leg_num}1111">',
        '<link name="${prefix}_foot_link">'
    )
    content = content.replace(
        '<child link="l${leg_num}1111"/>',
        '<child link="${prefix}_foot_link"/>'
    )
    
    # 更新 gazebo reference
    content = content.replace(
        '<gazebo reference="l${leg_num}111">',
        '<gazebo reference="${prefix}_lower_leg_link">'
    )
    content = content.replace(
        '<gazebo reference="l${leg_num}1111">',
        '<gazebo reference="${prefix}_foot_link">'
    )
    
    # 更新 HAA joint axis
    content = re.sub(
        r'(<joint name="\$\{prefix\}_haa_joint"[^>]*>.*?<axis xyz=")[^"]*(")',
        r'\1${haa_axis}\2',
        content,
        flags=re.DOTALL
    )
    
    print("   ✓ 已更新所有关节和连杆名称")
    
    # 4. 更新 HFE joint rpy（从 1.5708 1.5708 0 改为 1.5708 0 0）
    print("\n4. 更新 HFE joint RPY...")
    content = re.sub(
        r'(<joint name="\$\{prefix\}_hfe_joint"[^>]*>.*?<origin rpy=")1\.5708 1\.5708 0(")',
        r'\g<1>1.5708 0 0\g<2>',
        content,
        flags=re.DOTALL
    )
    print("   ✓ HFE joint rpy: 1.5708 1.5708 0 -> 1.5708 0 0")
    
    # 5. 更新 leg 实例化
    print("\n5. 更新 leg 实例化...")
    
    # Leg 1: Front Left
    content = re.sub(
        r'<xacro:leg leg_num="1"[^>]*origin_rpy="1\.5708 0 0"',
        '<xacro:leg prefix="lf"\n             leg_num="1"\n             origin_xyz="1.1026 -0.80953 0.2649"\n             origin_rpy="0 0 0"',
        content
    )
    # 添加 hip_joint_xyz 和 haa_axis
    content = re.sub(
        r'(<xacro:leg prefix="lf".*?shin_inertia_xyz="\$\{leg12_shin_inertia_xyz\}")',
        r'\1\n             hip_joint_xyz="-0.016 -0.08 0.0199"\n             hip_joint_rpy="0 0 0"\n             haa_axis="0 0 1"',
        content,
        flags=re.DOTALL
    )
    
    # Leg 2: Front Right
    content = re.sub(
        r'<xacro:leg leg_num="2"[^>]*origin_rpy="1\.5708 0 0"',
        '<xacro:leg prefix="rf"\n             leg_num="2"\n             origin_xyz="1.3491 -0.80953 0.2649"\n             origin_rpy="0 0 0"',
        content
    )
    content = re.sub(
        r'(<xacro:leg prefix="rf".*?hip_joint_xyz="0\.0116 0\.0199 0\.055")',
        r'\1\n             hip_joint_rpy="0 0 0"\n             haa_axis="0 0 1"',
        content,
        flags=re.DOTALL
    )
    # 修改 hip_joint_xyz
    content = re.sub(
        r'(<xacro:leg prefix="rf".*?)hip_joint_xyz="0\.0116 0\.0199 0\.055"',
        r'\1hip_joint_xyz="-0.016 -0.08 0.0199"',
        content,
        flags=re.DOTALL
    )
    
    # Leg 3: Rear Left
    content = re.sub(
        r'<xacro:leg leg_num="3"[^>]*origin_rpy="1\.5708 0 -3\.1416"',
        '<xacro:leg prefix="lh"\n             leg_num="3"\n             origin_xyz="1.3491 -0.68953 0.2649"\n             origin_rpy="0 0 0"',
        content
    )
    content = re.sub(
        r'(<xacro:leg prefix="lh".*?)hip_joint_rpy="3\.1416 0 1\.5708"',
        r'\1hip_joint_rpy="0 0 0"',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(<xacro:leg prefix="lh".*?)hip_joint_xyz="[^"]*"',
        r'\1hip_joint_xyz="0.016 -0.08 0.0199"',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(<xacro:leg prefix="lh".*?knee_joint_xyz="-0\.0233 -0\.055 -0\.0254")',
        r'\1\n             haa_axis="0 0 1"',
        content,
        flags=re.DOTALL
    )
    
    # Leg 4: Rear Right
    content = re.sub(
        r'<xacro:leg leg_num="4"[^>]*origin_rpy="1\.5708 0 -3\.1416"',
        '<xacro:leg prefix="rh"\n             leg_num="4"\n             origin_xyz="1.1071 -0.68953 0.2649"\n             origin_rpy="0 0 0"',
        content
    )
    content = re.sub(
        r'(<xacro:leg prefix="rh".*?)hip_joint_rpy="3\.1416 0 1\.5708"',
        r'\1hip_joint_rpy="0 0 0"',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(<xacro:leg prefix="rh".*?)hip_joint_xyz="0\.0116 0\.0199 0\.055"',
        r'\1hip_joint_xyz="-0.016 -0.08 0.0199"',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(<xacro:leg prefix="rh".*?foot_xyz="-0\.0286 -0\.289478 -0\.14"/>)',
        r'\1\n             haa_axis="0 0 1"/>',
        content,
        flags=re.DOTALL
    )
    # 移除多余的 />
    content = re.sub(r'haa_axis="0 0 1"/>\s*/>', 'haa_axis="0 0 1"/>', content)
    
    print("   ✓ 已更新所有 leg 实例化")
    
    # 6. 更新 ROS 2 Control 配置
    print("\n6. 更新 ROS 2 Control 配置...")
    joint_mapping = {
        'j11': 'lf_haa_joint',
        'j111': 'lf_hfe_joint',
        'j1111': 'lf_kfe_joint',
        'j21': 'rf_haa_joint',
        'j211': 'rf_hfe_joint',
        'j2111': 'rf_kfe_joint',
        'j31': 'lh_haa_joint',
        'j311': 'lh_hfe_joint',
        'j3111': 'lh_kfe_joint',
        'j41': 'rh_haa_joint',
        'j411': 'rh_hfe_joint',
        'j4111': 'rh_kfe_joint',
    }
    
    for old_name, new_name in joint_mapping.items():
        content = content.replace(
            f'<joint name="{old_name}">',
            f'<joint name="{new_name}">'
        )
        print(f"   ✓ {old_name} -> {new_name}")
    
    # 保存文件
    print(f"\n7. 保存到 {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)
    
    return 0

def main():
    input_file = '/home/dell/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf.xacro'
    output_file = input_file
    
    try:
        return apply_fix(input_file, output_file)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
