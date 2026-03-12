#!/usr/bin/env python3
"""
添加碰撞过滤到URDF
禁用小腿-脚部之间的碰撞检测
"""

import xml.etree.ElementTree as ET
import sys

def add_collision_filtering(urdf_file):
    """在URDF中添加碰撞过滤"""
    
    # 解析URDF
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    # 备份原文件
    backup_file = urdf_file + '.backup_before_filtering'
    tree.write(backup_file)
    print(f"✅ 已备份原文件到: {backup_file}")
    
    # 为每条腿添加碰撞过滤
    legs = ['1', '2', '3', '4']
    
    for leg_num in legs:
        shin_link = f"l{leg_num}111"
        foot_link = f"l{leg_num}1111"
        
        # 创建Gazebo标签来禁用碰撞
        # 注意：Gazebo使用<collision>标签来配置碰撞过滤
        # 我们需要在<gazebo>标签中添加<disable_link_collision>
        
        # 查找是否已存在该腿的gazebo配置
        existing_gazebo = None
        for gazebo in root.findall('gazebo'):
            ref = gazebo.get('reference')
            if ref == shin_link:
                existing_gazebo = gazebo
                break
        
        if existing_gazebo is None:
            # 创建新的gazebo标签
            gazebo_elem = ET.Element('gazebo', {'reference': shin_link})
            root.append(gazebo_elem)
            print(f"✅ 为 {shin_link} 创建了新的 <gazebo> 标签")
        else:
            gazebo_elem = existing_gazebo
            print(f"ℹ️  {shin_link} 已有 <gazebo> 标签，将添加碰撞过滤")
    
    # 在robot根元素下添加disable_link_collision标签
    # 这是Gazebo的标准方式来禁用特定链接对之间的碰撞
    for leg_num in legs:
        shin_link = f"l{leg_num}111"
        foot_link = f"l{leg_num}1111"
        
        # 创建disable_link_collision元素
        disable_collision = ET.Element('gazebo')
        disable_elem = ET.SubElement(disable_collision, 'disable_link_collision')
        disable_elem.set('link1', shin_link)
        disable_elem.set('link2', foot_link)
        
        root.append(disable_collision)
        print(f"✅ 禁用碰撞: {shin_link} <-> {foot_link}")
    
    # 保存修改后的URDF
    tree.write(urdf_file, encoding='utf-8', xml_declaration=True)
    print(f"\n✅ 已更新URDF文件: {urdf_file}")
    
    return True

if __name__ == "__main__":
    urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    print("=" * 60)
    print("添加碰撞过滤")
    print("=" * 60)
    print()
    print("将禁用以下碰撞对:")
    print("  • l1111 (小腿1) <-> l11111 (脚1)")
    print("  • l2111 (小腿2) <-> l21111 (脚2)")
    print("  • l3111 (小腿3) <-> l31111 (脚3)")
    print("  • l4111 (小腿4) <-> l41111 (脚4)")
    print()
    
    success = add_collision_filtering(urdf_file)
    
    if success:
        print()
        print("=" * 60)
        print("下一步:")
        print("=" * 60)
        print("1. 重新编译: colcon build --packages-select dog2_description")
        print("2. 测试Gazebo: ./test_collision_fixes.sh")
    else:
        print("\n❌ 添加碰撞过滤失败")
        sys.exit(1)
