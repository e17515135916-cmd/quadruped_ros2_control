#!/usr/bin/env python3
"""
查看STL mesh的基本信息

使用方法：
    blender --background --python scripts/查看mesh信息.py -- <stl_file>

示例：
    blender --background --python scripts/查看mesh信息.py -- src/dog2_description/meshes/l1.STL
"""

import bpy
import sys
from pathlib import Path

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_stl(filepath):
    """导入STL文件"""
    bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

def analyze_mesh(obj):
    """分析mesh"""
    mesh = obj.data
    
    # 基本信息
    num_vertices = len(mesh.vertices)
    num_faces = len(mesh.polygons)
    num_edges = len(mesh.edges)
    
    # 计算边界
    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
    
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)
    
    width = max_x - min_x
    depth = max_y - min_y
    height = max_z - min_z
    
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2
    mid_z = (min_z + max_z) / 2
    
    # 计算体积（近似）
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 打印信息
    print("\n" + "="*70)
    print(f"Mesh信息：{obj.name}")
    print("="*70)
    
    print(f"\n几何信息：")
    print(f"  顶点数：{num_vertices:,}")
    print(f"  面数：{num_faces:,}")
    print(f"  边数：{num_edges:,}")
    
    print(f"\n边界框：")
    print(f"  X范围：{min_x:.6f}m 到 {max_x:.6f}m  (宽度: {width:.6f}m)")
    print(f"  Y范围：{min_y:.6f}m 到 {max_y:.6f}m  (深度: {depth:.6f}m)")
    print(f"  Z范围：{min_z:.6f}m 到 {max_z:.6f}m  (高度: {height:.6f}m)")
    
    print(f"\n中心点：")
    print(f"  X: {mid_x:.6f}m")
    print(f"  Y: {mid_y:.6f}m")
    print(f"  Z: {mid_z:.6f}m")
    
    print(f"\n建议的分离位置（Z轴中点）：")
    print(f"  {mid_z:.6f}m")
    
    print(f"\n其他可能的分离位置：")
    print(f"  1/4高度：{min_z + height * 0.25:.6f}m")
    print(f"  1/3高度：{min_z + height * 0.33:.6f}m")
    print(f"  1/2高度：{mid_z:.6f}m")
    print(f"  2/3高度：{min_z + height * 0.67:.6f}m")
    print(f"  3/4高度：{min_z + height * 0.75:.6f}m")
    
    print("\n" + "="*70 + "\n")

def main():
    """主函数"""
    # 解析命令行参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        print("使用方法：blender --background --python 查看mesh信息.py -- <stl_file>")
        sys.exit(1)
    
    if len(argv) < 1:
        print("✗ 错误：需要提供STL文件路径")
        sys.exit(1)
    
    stl_file = Path(argv[0])
    
    if not stl_file.exists():
        print(f"✗ 错误：文件不存在：{stl_file}")
        sys.exit(1)
    
    print(f"\n正在分析：{stl_file}")
    
    # 清空场景
    clear_scene()
    
    # 导入mesh
    obj = import_stl(str(stl_file))
    
    # 分析mesh
    analyze_mesh(obj)

if __name__ == "__main__":
    main()
