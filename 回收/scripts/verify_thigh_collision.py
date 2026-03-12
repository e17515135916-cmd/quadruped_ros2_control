#!/usr/bin/env python3
"""
验证大腿链接碰撞几何体修改

检查项：
1. 所有大腿链接使用 cylinder 碰撞几何体
2. 所有大腿链接的 visual 仍使用 STL mesh
3. 碰撞体参数符合设计要求
"""

import xml.etree.ElementTree as ET
import sys

def verify_thigh_collision(urdf_file):
    """验证大腿碰撞几何体配置"""
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    results = {
        'passed': [],
        'failed': []
    }
    
    # 检查所有大腿链接 (l111, l211, l311, l411)
    for leg_num in [1, 2, 3, 4]:
        link_name = f"l{leg_num}11"
        link = root.find(f".//link[@name='{link_name}']")
        
        if link is None:
            results['failed'].append(f"未找到链接 {link_name}")
            continue
        
        # 检查 visual 使用 mesh
        visual = link.find("visual/geometry/mesh")
        if visual is not None:
            mesh_file = visual.get('filename')
            if f"l{leg_num}11.STL" in mesh_file:
                results['passed'].append(f"{link_name}: visual 使用 STL mesh ✓")
            else:
                results['failed'].append(f"{link_name}: visual mesh 文件不正确")
        else:
            results['failed'].append(f"{link_name}: visual 未使用 mesh")
        
        # 检查 collision 使用 cylinder
        collision = link.find("collision/geometry/cylinder")
        if collision is not None:
            radius = float(collision.get('radius'))
            length = float(collision.get('length'))
            
            # 验证参数范围
            expected_radius = 0.072
            expected_length = 0.154
            
            if abs(radius - expected_radius) < 0.001:
                results['passed'].append(f"{link_name}: collision 使用 cylinder，半径 = {radius}m ✓")
            else:
                results['failed'].append(f"{link_name}: cylinder 半径不正确 ({radius}m，期望 {expected_radius}m)")
            
            if abs(length - expected_length) < 0.001:
                results['passed'].append(f"{link_name}: cylinder 长度 = {length}m ✓")
            else:
                results['failed'].append(f"{link_name}: cylinder 长度不正确 ({length}m，期望 {expected_length}m)")
            
            # 检查原点偏移
            origin = link.find("collision/origin")
            if origin is not None:
                rpy = origin.get('rpy')
                xyz = origin.get('xyz')
                results['passed'].append(f"{link_name}: collision 原点 rpy={rpy}, xyz={xyz} ✓")
        else:
            # 检查是否仍使用 mesh
            collision_mesh = link.find("collision/geometry/mesh")
            if collision_mesh is not None:
                results['failed'].append(f"{link_name}: collision 仍使用 mesh（应该使用 cylinder）")
            else:
                results['failed'].append(f"{link_name}: collision 几何体类型未知")
    
    # 打印结果
    print("=" * 60)
    print("大腿碰撞几何体验证结果")
    print("=" * 60)
    
    if results['passed']:
        print("\n✓ 通过的检查项：")
        for item in results['passed']:
            print(f"  {item}")
    
    if results['failed']:
        print("\n✗ 失败的检查项：")
        for item in results['failed']:
            print(f"  {item}")
    
    print("\n" + "=" * 60)
    print(f"总计：{len(results['passed'])} 项通过，{len(results['failed'])} 项失败")
    print("=" * 60)
    
    return len(results['failed']) == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 verify_thigh_collision.py <urdf_file>")
        sys.exit(1)
    
    urdf_file = sys.argv[1]
    success = verify_thigh_collision(urdf_file)
    sys.exit(0 if success else 1)
