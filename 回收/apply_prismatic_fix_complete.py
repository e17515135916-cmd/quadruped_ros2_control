#!/usr/bin/env python3
"""
完整应用 Prismatic 坐标系修复

这个脚本会：
1. 移除 Prismatic joint 的 RPY 旋转（设为 0 0 0）
2. 更新 HAA joint 的 xyz 和 rpy（补偿坐标系变化）
3. 更新 HFE joint 的 rpy（适应新坐标系）
4. 重命名所有关节和连杆为 CHAMP 标准
5. 更新 ROS 2 Control 配置
6. 添加 world link
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def apply_fix(input_file, output_file):
    """应用完整的修复"""
    
    # 解析 XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # 注册命名空间
    ET.register_namespace('xacro', 'http://www.ros.org/wiki/xacro')
    
    print("=" * 60)
    print("应用 Prismatic 坐标系修复")
    print("=" * 60)
    
    # 1. 添加 world link（如果不存在）
    print("\n1. 检查 world link...")
    world_link = root.find(".//link[@name='world']")
    if world_link is None:
        print("   添加 world link")
        # 找到 base_link 之前插入
        base_link = root.find(".//link[@name='base_link']")
        if base_link is not None:
            base_link_index = list(root).index(base_link)
            
            # 创建 world link
            world_link = ET.Element('link', name='world')
            root.insert(base_link_index, world_link)
            
            # 创建 world_joint
            world_joint = ET.Element('joint', name='world_joint', type='fixed')
            parent = ET.SubElement(world_joint, 'parent', link='world')
            child = ET.SubElement(world_joint, 'child', link='base_link')
            origin = ET.SubElement(world_joint, 'origin', xyz='0 0 0', rpy='0 0 0')
            root.insert(base_link_index + 1, world_joint)
    else:
        print("   world link 已存在")
    
    # 2. 更新 leg macro 参数
    print("\n2. 更新 leg macro 参数...")
    for macro in root.findall(".//{http://www.ros.org/wiki/xacro}macro[@name='leg']"):
        params = macro.get('params', '')
        if 'prefix' not in params:
            print("   添加 prefix 参数")
            # 在 leg_num 之前添加 prefix
            params = params.replace('leg_num', 'prefix leg_num')
        if 'haa_axis' not in params:
            print("   添加 haa_axis 参数")
            params += " haa_axis:='0 0 1'"
        macro.set('params', params)
    
    # 3. 更新 leg macro 中的关节和连杆名称
    print("\n3. 更新 macro 中的关节和连杆名称...")
    for macro in root.findall(".//{http://www.ros.org/wiki/xacro}macro[@name='leg']"):
        # 更新 HAA joint
        for joint in macro.findall(".//joint"):
            name = joint.get('name', '')
            if '${leg_num}1' in name and 'j${leg_num}1' in name:
                print(f"   重命名 HAA joint: j${{leg_num}}1 -> ${{prefix}}_haa_joint")
                joint.set('name', '${prefix}_haa_joint')
                # 更新 axis
                axis = joint.find('axis')
                if axis is not None:
                    axis.set('xyz', '${haa_axis}')
        
        # 更新 HAA link
        for link in macro.findall(".//link"):
            name = link.get('name', '')
            if 'l${leg_num}1' == name:
                print(f"   重命名 HAA link: l${{leg_num}}1 -> ${{prefix}}_hip_link")
                link.set('name', '${prefix}_hip_link')
        
        # 更新 HFE joint
        for joint in macro.findall(".//joint"):
            name = joint.get('name', '')
            if 'j${leg_num}11' in name:
                print(f"   重命名 HFE joint: j${{leg_num}}11 -> ${{prefix}}_hfe_joint")
                joint.set('name', '${prefix}_hfe_joint')
        
        # 更新 HFE link
        for link in macro.findall(".//link"):
            name = link.get('name', '')
            if 'l${leg_num}11' == name:
                print(f"   重命名 HFE link: l${{leg_num}}11 -> ${{prefix}}_upper_leg_link")
                link.set('name', '${prefix}_upper_leg_link')
        
        # 更新 KFE joint
        for joint in macro.findall(".//joint"):
            name = joint.get('name', '')
            if 'j${leg_num}111' in name and 'j${leg_num}1111' not in name:
                print(f"   重命名 KFE joint: j${{leg_num}}111 -> ${{prefix}}_kfe_joint")
                joint.set('name', '${prefix}_kfe_joint')
        
        # 更新 KFE link
        for link in macro.findall(".//link"):
            name = link.get('name', '')
            if 'l${leg_num}111' == name and 'l${leg_num}1111' not in name:
                print(f"   重命名 KFE link: l${{leg_num}}111 -> ${{prefix}}_lower_leg_link")
                link.set('name', '${prefix}_lower_leg_link')
        
        # 更新 foot joint
        for joint in macro.findall(".//joint"):
            name = joint.get('name', '')
            if 'j${leg_num}1111' in name:
                print(f"   重命名 foot joint: j${{leg_num}}1111 -> ${{prefix}}_foot_fixed_joint")
                joint.set('name', '${prefix}_foot_fixed_joint')
        
        # 更新 foot link
        for link in macro.findall(".//link"):
            name = link.get('name', '')
            if 'l${leg_num}1111' == name:
                print(f"   重命名 foot link: l${{leg_num}}1111 -> ${{prefix}}_foot_link")
                link.set('name', '${prefix}_foot_link')
        
        # 更新 parent/child 引用
        for parent in macro.findall(".//parent"):
            link_name = parent.get('link', '')
            if 'l${leg_num}1' == link_name:
                parent.set('link', '${prefix}_hip_link')
            elif 'l${leg_num}11' == link_name:
                parent.set('link', '${prefix}_upper_leg_link')
            elif 'l${leg_num}111' == link_name:
                parent.set('link', '${prefix}_lower_leg_link')
        
        for child in macro.findall(".//child"):
            link_name = child.get('link', '')
            if 'l${leg_num}1' == link_name:
                child.set('link', '${prefix}_hip_link')
            elif 'l${leg_num}11' == link_name:
                child.set('link', '${prefix}_upper_leg_link')
            elif 'l${leg_num}111' == link_name:
                child.set('link', '${prefix}_lower_leg_link')
            elif 'l${leg_num}1111' == link_name:
                child.set('link', '${prefix}_foot_link')
        
        # 更新 gazebo reference
        for gazebo in macro.findall(".//gazebo"):
            ref = gazebo.get('reference', '')
            if 'l${leg_num}111' == ref:
                gazebo.set('reference', '${prefix}_lower_leg_link')
            elif 'l${leg_num}1111' == ref:
                gazebo.set('reference', '${prefix}_foot_link')
    
    # 4. 更新 leg 实例化
    print("\n4. 更新 leg 实例化...")
    leg_configs = [
        ('lf', '1', '1.1026 -0.80953 0.2649', '0 0 0', '-0.111', '0.0', 
         '-0.016 -0.08 0.0199', '0 0 0', '1.5708 0 0', '0 0 1'),
        ('rf', '2', '1.3491 -0.80953 0.2649', '0 0 0', '0.0', '0.111',
         '-0.016 -0.08 0.0199', '0 0 0', '1.5708 0 0', '0 0 1'),
        ('lh', '3', '1.3491 -0.68953 0.2649', '0 0 0', '-0.111', '0.0',
         '0.016 -0.08 0.0199', '0 0 0', '1.5708 0 0', '0 0 1'),
        ('rh', '4', '1.1071 -0.68953 0.2649', '0 0 0', '0.0', '0.111',
         '-0.016 -0.08 0.0199', '0 0 0', '1.5708 0 0', '0 0 1'),
    ]
    
    for leg_elem in root.findall(".//{http://www.ros.org/wiki/xacro}leg"):
        leg_num = leg_elem.get('leg_num', '')
        if leg_num:
            idx = int(leg_num) - 1
            if idx < len(leg_configs):
                prefix, num, xyz, rpy, lower, upper, hip_xyz, hip_rpy, thigh_rpy, haa_axis = leg_configs[idx]
                
                print(f"   更新 Leg {num} ({prefix}):")
                print(f"     - 添加 prefix={prefix}")
                print(f"     - Prismatic RPY: 1.5708 0 0 -> {rpy}")
                print(f"     - HAA xyz: 调整为 {hip_xyz}")
                print(f"     - HAA rpy: 调整为 {hip_rpy}")
                print(f"     - HFE rpy: 调整为 {thigh_rpy}")
                print(f"     - HAA axis: {haa_axis}")
                
                leg_elem.set('prefix', prefix)
                leg_elem.set('origin_rpy', rpy)
                leg_elem.set('hip_joint_xyz', hip_xyz)
                leg_elem.set('hip_joint_rpy', hip_rpy)
                leg_elem.set('thigh_joint_rpy', thigh_rpy)
                leg_elem.set('haa_axis', haa_axis)
    
    # 5. 更新 ROS 2 Control 配置
    print("\n5. 更新 ROS 2 Control 配置...")
    for ros2_control in root.findall(".//ros2_control"):
        # 重命名关节
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
        
        for joint in ros2_control.findall(".//joint"):
            old_name = joint.get('name', '')
            if old_name in joint_mapping:
                new_name = joint_mapping[old_name]
                print(f"   重命名: {old_name} -> {new_name}")
                joint.set('name', new_name)
    
    # 保存文件
    print(f"\n6. 保存到 {output_file}...")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)
    print(f"\n下一步:")
    print(f"1. 编译 URDF: xacro {output_file} > /tmp/dog2_fixed.urdf")
    print(f"2. 验证: check_urdf /tmp/dog2_fixed.urdf")
    print(f"3. 运行验证脚本: python3 verify_prismatic_fix.py")
    
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
    sys.exit(main())
