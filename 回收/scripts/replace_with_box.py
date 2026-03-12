#!/usr/bin/env python3
"""
用简单的方形box替换复杂的mesh

使用方法：
    blender --background --python scripts/replace_with_box.py -- <input_file> <output_file> [padding]

参数：
    input_file: 输入STL文件
    output_file: 输出STL文件
    padding: 边界扩展量（米），默认0.0

示例：
    # 创建刚好包围原mesh的box
    blender --background --python scripts/replace_with_box.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_box.STL
    
    # 创建稍大一点的box（扩展1cm）
    blender --background --python scripts/replace_with_box.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_box.STL \
        0.01
"""

import bpy
import sys
from pathlib import Path
from mathutils import Vector

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_stl(filepath):
    """导入STL"""
    bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

def get_bounding_box(obj):
    """获取对象的边界框"""
    # 获取所有顶点的世界坐标
    vertices = [obj.matrix_world @ Vector(v.co) for v in obj.data.vertices]
    
    # 计算边界
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)
    
    # 计算尺寸和中心
    size = Vector((
        max_x - min_x,
        max_y - min_y,
        max_z - min_z
    ))
    
    center = Vector((
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2
    ))
    
    return {
        'min': Vector((min_x, min_y, min_z)),
        'max': Vector((max_x, max_y, max_z)),
        'size': size,
        'center': center
    }

def create_box(size, location, padding=0.0):
    """创建一个box"""
    # 添加立方体
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location
    )
    
    box = bpy.context.active_object
    
    # 缩放到指定尺寸（加上padding）
    box.scale = (
        (size.x + padding * 2) / 2,
        (size.y + padding * 2) / 2,
        (size.z + padding * 2) / 2
    )
    
    # 应用缩放
    bpy.ops.object.transform_apply(scale=True)
    
    return box

def export_stl(obj, filepath):
    """导出STL"""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.export_mesh.stl(
        filepath=filepath,
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=True,
        ascii=False
    )

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Mesh → Box 替换工具")
    print("="*70 + "\n")
    
    # 解析参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        sys.exit(1)
    
    if len(argv) < 2:
        print("✗ 错误：参数不足")
        print("需要：input_file output_file [padding]")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_file = Path(argv[1])
    padding = float(argv[2]) if len(argv) > 2 else 0.0
    
    print(f"输入文件：{input_file}")
    print(f"输出文件：{output_file}")
    print(f"边界扩展：{padding}m\n")
    
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在")
        sys.exit(1)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：导入原始mesh
    print("步骤1：导入原始mesh...")
    clear_scene()
    original_obj = import_stl(str(input_file))
    
    print(f"✓ 已导入：{original_obj.name}")
    print(f"  顶点数：{len(original_obj.data.vertices):,}")
    print(f"  面数：{len(original_obj.data.polygons):,}\n")
    
    # 步骤2：计算边界框
    print("步骤2：计算边界框...")
    bbox = get_bounding_box(original_obj)
    
    print(f"✓ 边界框信息：")
    print(f"  最小点：({bbox['min'].x:.4f}, {bbox['min'].y:.4f}, {bbox['min'].z:.4f})")
    print(f"  最大点：({bbox['max'].x:.4f}, {bbox['max'].y:.4f}, {bbox['max'].z:.4f})")
    print(f"  尺寸：({bbox['size'].x:.4f}, {bbox['size'].y:.4f}, {bbox['size'].z:.4f})")
    print(f"  中心：({bbox['center'].x:.4f}, {bbox['center'].y:.4f}, {bbox['center'].z:.4f})\n")
    
    # 步骤3：删除原始mesh
    print("步骤3：创建替换box...")
    bpy.data.objects.remove(original_obj, do_unlink=True)
    
    # 步骤4：创建box
    box = create_box(bbox['size'], bbox['center'], padding)
    box.name = "box"
    
    final_size = Vector((
        bbox['size'].x + padding * 2,
        bbox['size'].y + padding * 2,
        bbox['size'].z + padding * 2
    ))
    
    print(f"✓ 已创建box：")
    print(f"  尺寸：({final_size.x:.4f}, {final_size.y:.4f}, {final_size.z:.4f})")
    print(f"  位置：({bbox['center'].x:.4f}, {bbox['center'].y:.4f}, {bbox['center'].z:.4f})")
    print(f"  顶点数：{len(box.data.vertices)}")
    print(f"  面数：{len(box.data.polygons)}\n")
    
    # 步骤5：导出
    print("步骤4：导出box...")
    export_stl(box, str(output_file))
    
    # 文件大小对比
    input_size = input_file.stat().st_size / 1024
    output_size = output_file.stat().st_size / 1024
    
    print(f"\n文件大小：")
    print(f"  原始mesh：{input_size:.1f} KB")
    print(f"  Box：{output_size:.1f} KB")
    print(f"  减少：{(1 - output_size / input_size) * 100:.1f}%")
    
    print("\n" + "="*70)
    print("✓ 完成！")
    print("="*70)
    print(f"\n输出文件：{output_file}")
    print(f"\n提示：")
    print(f"  - Box有8个顶点，12条边，6个面")
    print(f"  - 这是最简单的碰撞几何体")
    print(f"  - 适合用作碰撞mesh\n")

if __name__ == "__main__":
    main()
