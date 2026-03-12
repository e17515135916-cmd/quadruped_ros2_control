#!/usr/bin/env python3
"""
使用trimesh库旋转l1 mesh（不需要Blender）
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

def rotate_mesh_file(stl_path, angle_degrees, axis='y'):
    """旋转STL文件"""
    
    print(f"正在处理: {stl_path}")
    
    # 检查文件是否存在
    if not os.path.exists(stl_path):
        print(f"  ❌ 文件不存在")
        return False
    
    # 备份原文件
    backup_path = stl_path + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy2(stl_path, backup_path)
        print(f"  ✅ 已备份到: {backup_path}")
    
    # 加载mesh
    print(f"  正在加载mesh...")
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
    else:
        print(f"  ❌ 未知的旋转轴: {axis}")
        return False
    
    print(f"  正在旋转 {angle_degrees}度（绕{axis.upper()}轴）...")
    
    # 应用旋转
    mesh.apply_transform(rotation_matrix)
    
    # 保存
    print(f"  正在保存...")
    mesh.export(stl_path)
    
    print(f"  ✅ 完成！")
    return True

def main():
    """主函数"""
    workspace_dir = os.path.expanduser("~/aperfect/carbot_ws")
    
    print("=" * 60)
    print("使用trimesh旋转l1 mesh（绕Y轴90度）")
    print("=" * 60)
    print()
    print(f"工作空间: {workspace_dir}")
    print()
    
    if not os.path.exists(workspace_dir):
        print(f"❌ 工作空间不存在: {workspace_dir}")
        return
    
    # l1的STL文件路径
    l1_stl_path = os.path.join(workspace_dir, "src/dog2_description/meshes/l1.STL")
    l1_collision_path = os.path.join(workspace_dir, "src/dog2_description/meshes/collision/l1_collision.STL")
    
    # 旋转视觉mesh
    print("1. 旋转视觉mesh")
    print("-" * 60)
    success1 = rotate_mesh_file(l1_stl_path, 90, 'y')
    
    print()
    
    # 旋转碰撞mesh
    if os.path.exists(l1_collision_path):
        print("2. 旋转碰撞mesh")
        print("-" * 60)
        success2 = rotate_mesh_file(l1_collision_path, 90, 'y')
    else:
        print("2. 碰撞mesh不存在，跳过")
        success2 = True
    
    print()
    print("=" * 60)
    
    if success1 and success2:
        print("✅ 旋转完成！")
        print("=" * 60)
        print()
        print("下一步：")
        print("1. 重新编译: colcon build --packages-select dog2_description")
        print("2. 在RViz中查看: ros2 launch dog2_description view_dog2.launch.py")
        print()
        print("如果需要恢复原文件：")
        print(f"  cp {l1_stl_path}.backup {l1_stl_path}")
    else:
        print("❌ 旋转失败")

if __name__ == "__main__":
    main()
