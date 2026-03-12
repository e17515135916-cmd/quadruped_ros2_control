#!/usr/bin/env python3
"""
验证URDF中视觉和碰撞网格的配置
确保视觉使用原始STL，碰撞使用凸包文件
"""

import xml.etree.ElementTree as ET
import sys

def verify_urdf_mesh_config(urdf_file):
    """验证URDF网格配置"""
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    print("=" * 60)
    print("URDF 网格配置验证")
    print("=" * 60)
    
    visual_correct = 0
    visual_incorrect = 0
    collision_correct = 0
    collision_incorrect = 0
    
    # 检查所有link
    for link in root.findall('.//link'):
        link_name = link.get('name')
        
        # 检查视觉网格
        for visual in link.findall('visual'):
            mesh = visual.find('.//mesh')
            if mesh is not None:
                filename = mesh.get('filename')
                # 视觉应该使用原始STL（不在collision目录）
                if '/collision/' in filename:
                    print(f"❌ {link_name} 视觉网格错误: {filename}")
                    print(f"   应该使用原始STL，不应该在collision目录")
                    visual_incorrect += 1
                else:
                    print(f"✅ {link_name} 视觉网格正确: {filename}")
                    visual_correct += 1
        
        # 检查碰撞网格
        for collision in link.findall('collision'):
            geom = collision.find('geometry')
            if geom is not None:
                mesh = geom.find('mesh')
                if mesh is not None:
                    filename = mesh.get('filename')
                    # 碰撞应该使用凸包文件（在collision目录）
                    if '/collision/' in filename and '_collision.STL' in filename:
                        print(f"✅ {link_name} 碰撞网格正确: {filename}")
                        collision_correct += 1
                    else:
                        print(f"❌ {link_name} 碰撞网格错误: {filename}")
                        print(f"   应该使用凸包文件（collision目录）")
                        collision_incorrect += 1
                else:
                    # 球体或其他几何体（如foot）
                    sphere = geom.find('sphere')
                    if sphere is not None:
                        print(f"ℹ️  {link_name} 使用球体碰撞（正常）")
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    print(f"视觉网格: {visual_correct} 正确, {visual_incorrect} 错误")
    print(f"碰撞网格: {collision_correct} 正确, {collision_incorrect} 错误")
    
    if visual_incorrect == 0 and collision_incorrect == 0:
        print("\n✅ 所有网格配置正确！")
        return True
    else:
        print("\n❌ 发现配置错误，需要修复")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 verify_urdf_mesh_config.py <urdf_file>")
        sys.exit(1)
    
    urdf_file = sys.argv[1]
    success = verify_urdf_mesh_config(urdf_file)
    sys.exit(0 if success else 1)
