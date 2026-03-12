#!/usr/bin/env python3
"""
自动修复URDF中所有碰撞体的origin偏移
"""

import re
from stl import mesh
import glob
import os

def calculate_mesh_center(stl_file):
    """计算STL网格的几何中心"""
    stl_mesh = mesh.Mesh.from_file(stl_file)
    vertices = stl_mesh.vectors.reshape(-1, 3)
    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)
    center = (min_coords + max_coords) / 2
    return center

def get_all_collision_centers():
    """获取所有碰撞网格的中心点"""
    collision_dir = "src/dog2_description/meshes/collision"
    collision_files = glob.glob(f"{collision_dir}/*.STL")
    
    centers = {}
    for collision_file in collision_files:
        basename = os.path.basename(collision_file)
        link_name = basename.replace('_collision.STL', '')
        center = calculate_mesh_center(collision_file)
        centers[link_name] = center
    
    return centers

def fix_urdf_collision_origins(urdf_file):
    """修复URDF中的碰撞origin"""
    
    # 获取所有碰撞中心
    centers = get_all_collision_centers()
    
    # 读取URDF
    with open(urdf_file, 'r') as f:
        content = f.read()
    
    # 备份
    backup_file = urdf_file + '.backup_before_origin_fix'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ 已备份到: {backup_file}")
    print()
    
    # 为每个链接更新碰撞origin
    updates = 0
    
    for link_name, center in centers.items():
        # 构建正则表达式来匹配碰撞块
        # 匹配模式：<collision>...</collision> 包含特定的mesh文件名
        pattern = rf'(<collision>.*?<origin[^>]*xyz="[^"]*"[^>]*/>.*?<mesh filename="package://dog2_description/meshes/collision/{re.escape(link_name)}_collision\.STL"/>.*?</collision>)'
        
        def replace_origin(match):
            collision_block = match.group(1)
            # 替换origin
            new_origin = f'<origin xyz="{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}" rpy="0 0 0"/>'
            new_block = re.sub(r'<origin[^>]*xyz="[^"]*"[^>]*/>', new_origin, collision_block)
            return new_block
        
        new_content, count = re.subn(pattern, replace_origin, content, flags=re.DOTALL)
        
        if count > 0:
            content = new_content
            updates += count
            print(f"✅ 更新 {link_name}: origin = ({center[0]:.6f}, {center[1]:.6f}, {center[2]:.6f})")
    
    # 写回文件
    with open(urdf_file, 'w') as f:
        f.write(content)
    
    print()
    print(f"✅ 总共更新了 {updates} 个碰撞origin")
    print(f"✅ 已保存到: {urdf_file}")
    
    return updates

if __name__ == "__main__":
    print("=" * 70)
    print("自动修复碰撞体Origin偏移")
    print("=" * 70)
    print()
    
    urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    updates = fix_urdf_collision_origins(urdf_file)
    
    print()
    print("=" * 70)
    print("下一步:")
    print("=" * 70)
    print("1. 重新编译: colcon build --packages-select dog2_description")
    print("2. 测试Gazebo: ./test_final_collision_fix.sh")
