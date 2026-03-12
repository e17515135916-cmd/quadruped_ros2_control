#!/usr/bin/env python3
"""
使用Bisect方法在Blender中分离mesh

这个方法不需要选择面，直接用平面切割，适合面数很多的mesh。

使用方法：
    blender --background --python scripts/split_mesh_bisect.py -- <input_file> <output_upper> <output_lower> <split_z>

参数：
    input_file: 输入STL文件路径
    output_upper: 输出上半部分STL文件路径
    output_lower: 输出下半部分STL文件路径
    split_z: 分离的Z坐标（米）

示例：
    blender --background --python scripts/split_mesh_bisect.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_upper.STL \
        src/dog2_description/meshes/l1_lower.STL \
        0.05
"""

import bpy
import sys
import os
import bmesh
from mathutils import Vector
from pathlib import Path

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_stl(filepath):
    """导入STL文件"""
    bpy.ops.import_mesh.stl(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    return obj

def get_mesh_bounds(obj):
    """获取mesh的边界"""
    vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)
    return min_z, max_z

def bisect_mesh(obj, plane_co, plane_no, clear_inner=False, clear_outer=False):
    """
    使用Bisect切割mesh
    
    参数:
        obj: Blender对象
        plane_co: 平面位置 (x, y, z)
        plane_no: 平面法向量 (x, y, z)
        clear_inner: 是否删除内侧（下方）
        clear_outer: 是否删除外侧（上方）
    """
    # 确保对象是活动对象
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 选择所有
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 使用bmesh进行bisect操作
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    # 执行bisect
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    
    bmesh.ops.bisect_plane(
        bm,
        geom=geom,
        dist=0.0001,
        plane_co=plane_co,
        plane_no=plane_no,
        use_snap_center=False,
        clear_inner=clear_inner,
        clear_outer=clear_outer
    )
    
    # 更新mesh
    bmesh.update_edit_mesh(me)
    
    # 退出编辑模式
    bpy.ops.object.mode_set(mode='OBJECT')

def export_stl(obj, filepath):
    """导出STL文件"""
    # 取消所有选择
    bpy.ops.object.select_all(action='DESELECT')
    
    # 选择要导出的对象
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 导出
    bpy.ops.export_mesh.stl(
        filepath=filepath,
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=True,
        ascii=False
    )

def duplicate_object(obj):
    """复制对象"""
    # 取消所有选择
    bpy.ops.object.select_all(action='DESELECT')
    
    # 选择要复制的对象
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 复制
    bpy.ops.object.duplicate()
    
    # 返回新对象
    return bpy.context.selected_objects[0]

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Mesh Bisect分离工具")
    print("="*70 + "\n")
    
    # 解析命令行参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        print("使用方法：blender --background --python split_mesh_bisect.py -- <input> <output_upper> <output_lower> <split_z>")
        sys.exit(1)
    
    if len(argv) < 4:
        print("✗ 错误：参数不足")
        print("需要4个参数：input_file output_upper output_lower split_z")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_upper = Path(argv[1])
    output_lower = Path(argv[2])
    split_z = float(argv[3])
    
    print(f"输入文件：{input_file}")
    print(f"输出上部：{output_upper}")
    print(f"输出下部：{output_lower}")
    print(f"分离高度：{split_z}m\n")
    
    # 检查输入文件
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在：{input_file}")
        sys.exit(1)
    
    # 创建输出目录
    output_upper.parent.mkdir(parents=True, exist_ok=True)
    output_lower.parent.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：清空场景
    print("步骤1：清空场景...")
    clear_scene()
    print("✓ 完成\n")
    
    # 步骤2：导入mesh
    print("步骤2：导入mesh...")
    obj = import_stl(str(input_file))
    print(f"✓ 已导入：{obj.name}\n")
    
    # 显示mesh信息
    min_z, max_z = get_mesh_bounds(obj)
    height = max_z - min_z
    mid_z = (min_z + max_z) / 2
    
    print(f"Mesh信息：")
    print(f"  顶点数：{len(obj.data.vertices)}")
    print(f"  面数：{len(obj.data.polygons)}")
    print(f"  Z范围：{min_z:.4f}m 到 {max_z:.4f}m")
    print(f"  高度：{height:.4f}m")
    print(f"  中点：{mid_z:.4f}m")
    print(f"  分离位置：{split_z:.4f}m")
    
    # 检查分离位置是否合理
    if split_z < min_z or split_z > max_z:
        print(f"\n⚠ 警告：分离位置 {split_z}m 超出mesh范围 [{min_z:.4f}m, {max_z:.4f}m]")
        print(f"建议使用中点：{mid_z:.4f}m")
    
    print()
    
    # 步骤3：创建上半部分
    print("步骤3：创建上半部分...")
    obj_upper = duplicate_object(obj)
    obj_upper.name = "upper"
    
    # 使用bisect删除下半部分
    plane_co = Vector((0, 0, split_z))
    plane_no = Vector((0, 0, 1))  # 向上的法向量
    
    bisect_mesh(obj_upper, plane_co, plane_no, clear_inner=True, clear_outer=False)
    
    upper_min_z, upper_max_z = get_mesh_bounds(obj_upper)
    print(f"✓ 上半部分：")
    print(f"  顶点数：{len(obj_upper.data.vertices)}")
    print(f"  面数：{len(obj_upper.data.polygons)}")
    print(f"  Z范围：{upper_min_z:.4f}m 到 {upper_max_z:.4f}m")
    print(f"  高度：{upper_max_z - upper_min_z:.4f}m\n")
    
    # 步骤4：创建下半部分
    print("步骤4：创建下半部分...")
    obj_lower = obj  # 使用原始对象
    obj_lower.name = "lower"
    
    # 使用bisect删除上半部分
    bisect_mesh(obj_lower, plane_co, plane_no, clear_inner=False, clear_outer=True)
    
    lower_min_z, lower_max_z = get_mesh_bounds(obj_lower)
    print(f"✓ 下半部分：")
    print(f"  顶点数：{len(obj_lower.data.vertices)}")
    print(f"  面数：{len(obj_lower.data.polygons)}")
    print(f"  Z范围：{lower_min_z:.4f}m 到 {lower_max_z:.4f}m")
    print(f"  高度：{lower_max_z - lower_min_z:.4f}m\n")
    
    # 步骤5：导出
    print("步骤5：导出文件...")
    export_stl(obj_upper, str(output_upper))
    print(f"✓ 已导出上半部分：{output_upper}")
    
    export_stl(obj_lower, str(output_lower))
    print(f"✓ 已导出下半部分：{output_lower}\n")
    
    # 完成
    print("="*70)
    print("✓ 分离完成！")
    print("="*70)
    print(f"\n生成的文件：")
    print(f"  上半部分：{output_upper}")
    print(f"  下半部分：{output_lower}\n")

if __name__ == "__main__":
    main()
