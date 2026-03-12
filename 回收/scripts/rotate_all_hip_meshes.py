#!/usr/bin/env python3
"""
旋转所有髋关节相关的mesh文件（l1, l11, l2, l21, l3, l31, l4, l41）
绕Y轴旋转90度
"""

import os
import numpy as np
import shutil

try:
    import trimesh
except ImportError:
    print("❌ trimesh库未安装")
    print("请运行: pip3 install trimesh")
    exit(1)

def rotate_mesh_file(stl_path, angle_degrees=90, axis='y'):
    """旋转STL文件"""
    
    print(f"  正在处理: {os.path.basename(stl_path)}")
    
    # 检查文件是否存在
    if not os.path.exists(stl_path):
        print(f"    ❌ 文件不存在")
        return False
    
    # 备份原文件
    backup_path = stl_path + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy2(stl_path, backup_path)
        print(f"    ✅ 已备份")
    
    # 加载mesh
    mesh = trimesh.load(stl_path)
    
    # 创建旋转矩阵
    angle_radians = np.radians(angle_degrees)
    
    if axis == 'x':
        rotation_matrix = trimesh.transformations.rotation_matrix(
            angle_radians, [1, 0, 0])
    elif axis == 'y':
        rotation_matrix = trimesh.transformations.rotation_matrix(
            angle_radians, [0, 1, 0])
    elif axis == 'z':
        rotation_matrix = trimesh.transformations.rotation_matrix(
            angle_radians, [0, 0, 1])
    
    # 应用旋转
    mesh.apply_transform(rotation_matrix)
    
    # 保存
    mesh.export(stl_path)
    
    print(f"    ✅ 已旋转并保存")
    return True

def main():
    """主函数"""
    workspace_dir = os.path.expanduser("~/aperfect/carbot_ws")
    
    print("=" * 70)
    print("旋转所有髋关节mesh文件（绕Y轴90度）")
    print("=" * 70)
    print()
    print(f"工作空间: {workspace_dir}")
    print()
    
    if not os.path.exists(workspace_dir):
        print(f"❌ 工作空间不存在: {workspace_dir}")
        return
    
    # 需要旋转的mesh文件列表
    meshes_to_rotate = [
        # 左前腿
        "l1.STL",
        "l11.STL",
        # 右前腿
        "l2.STL",
        "l21.STL",
        # 左后腿
        "l3.STL",
        "l31.STL",
        # 右后腿
        "l4.STL",
        "l41.STL",
    ]
    
    meshes_dir = os.path.join(workspace_dir, "src/dog2_description/meshes")
    collision_dir = os.path.join(meshes_dir, "collision")
    
    success_count = 0
    total_count = 0
    
    # 旋转视觉mesh
    print("1. 旋转视觉mesh")
    print("-" * 70)
    for mesh_name in meshes_to_rotate:
        mesh_path = os.path.join(meshes_dir, mesh_name)
        if rotate_mesh_file(mesh_path):
            success_count += 1
        total_count += 1
    
    print()
    
    # 旋转碰撞mesh
    print("2. 旋转碰撞mesh")
    print("-" * 70)
    for mesh_name in meshes_to_rotate:
        collision_name = mesh_name.replace(".STL", "_collision.STL")
        collision_path = os.path.join(collision_dir, collision_name)
        if os.path.exists(collision_path):
            if rotate_mesh_file(collision_path):
                success_count += 1
            total_count += 1
        else:
            print(f"  跳过: {collision_name} (不存在)")
    
    print()
    print("=" * 70)
    print(f"✅ 完成！成功旋转 {success_count}/{total_count} 个文件")
    print("=" * 70)
    print()
    print("旋转的mesh文件：")
    for mesh_name in meshes_to_rotate:
        print(f"  - {mesh_name}")
    print()
    print("⚠️  重要：现在需要修改URDF文件中的joint轴向！")
    print()
    print("下一步：")
    print("1. 运行脚本修改URDF中的joint axis")
    print("2. colcon build --packages-select dog2_description")
    print("3. ros2 launch dog2_description view_dog2.launch.py")

if __name__ == "__main__":
    main()
