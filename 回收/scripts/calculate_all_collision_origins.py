#!/usr/bin/env python3
"""
计算所有链接的碰撞体origin偏移
"""

import numpy as np
from stl import mesh
import os
import glob

def calculate_mesh_center(stl_file):
    """计算STL网格的几何中心"""
    try:
        stl_mesh = mesh.Mesh.from_file(stl_file)
        vertices = stl_mesh.vectors.reshape(-1, 3)
        
        # 计算边界框
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        
        # 几何中心 = (min + max) / 2
        center = (min_coords + max_coords) / 2
        
        return center, min_coords, max_coords
    except Exception as e:
        print(f"错误: 无法读取 {stl_file}: {e}")
        return None, None, None

def main():
    print("=" * 80)
    print("所有碰撞体Origin偏移计算")
    print("=" * 80)
    print()
    
    collision_dir = "src/dog2_description/meshes/collision"
    collision_files = sorted(glob.glob(f"{collision_dir}/*.STL"))
    
    results = {}
    
    for collision_file in collision_files:
        basename = os.path.basename(collision_file)
        link_name = basename.replace('_collision.STL', '')
        
        center, min_coords, max_coords = calculate_mesh_center(collision_file)
        
        if center is not None:
            print(f"【{link_name}】")
            print(f"  文件: {basename}")
            print(f"  几何中心: X={center[0]:.6f}, Y={center[1]:.6f}, Z={center[2]:.6f}")
            print(f"  推荐Origin: <origin xyz=\"{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}\" rpy=\"0 0 0\"/>")
            print()
            
            results[link_name] = {
                'center': center,
                'min': min_coords,
                'max': max_coords
            }
    
    print("=" * 80)
    print("URDF更新建议")
    print("=" * 80)
    print()
    print("将以下origin偏移应用到对应的<collision>标签:")
    print()
    
    for link_name, data in results.items():
        center = data['center']
        print(f"<!-- {link_name} -->")
        print(f"<collision>")
        print(f"  <origin xyz=\"{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}\" rpy=\"0 0 0\"/>")
        print(f"  <geometry>")
        print(f"    <mesh filename=\"package://dog2_description/meshes/collision/{link_name}_collision.STL\"/>")
        print(f"  </geometry>")
        print(f"</collision>")
        print()

if __name__ == "__main__":
    main()
