#!/usr/bin/env python3
"""
用圆柱体替换复杂的mesh

使用方法：
    blender --background --python scripts/replace_with_cylinder.py -- <input> <output> <axis> [vertices]

参数：
    input: 输入STL文件
    output: 输出STL文件
    axis: 圆柱体轴向 (x, y, z)
    vertices: 圆柱体的顶点数（默认32，越少越简单）

示例：
    # 沿Z轴的圆柱体，32个顶点
    blender --background --python scripts/replace_with_cylinder.py -- \
        l1.STL l1_cylinder.STL z 32
    
    # 沿X轴的圆柱体，16个顶点（更简单）
    blender --background --python scripts/replace_with_cylinder.py -- \
        l1.STL l1_cylinder.STL x 16
"""

import bpy
import sys
import math
from pathlib import Path
from mathutils import Vector, Matrix

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_stl(filepath):
    """导入STL"""
    bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

def get_bounding_box(obj):
    """获取边界框"""
    vertices = [obj.matrix_world @ Vector(v.co) for v in obj.data.vertices]
    
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)
    
    size = Vector((max_x - min_x, max_y - min_y, max_z - min_z))
    center = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    
    return {'size': size, 'center': center}

def create_cylinder(bbox, axis='z', vertices=32):
    """创建圆柱体"""
    size = bbox['size']
    center = bbox['center']
    
    # 根据轴向确定半径和高度
    if axis == 'x':
        radius = max(size.y, size.z) / 2
        depth = size.x
        rotation = (0, math.pi/2, 0)
    elif axis == 'y':
        radius = max(size.x, size.z) / 2
        depth = size.y
        rotation = (math.pi/2, 0, 0)
    else:  # z
        radius = max(size.x, size.y) / 2
        depth = size.z
        rotation = (0, 0, 0)
    
    # 创建圆柱体
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=center,
        rotation=rotation
    )
    
    cylinder = bpy.context.active_object
    
    return cylinder, radius, depth

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
    print("Mesh → Cylinder 替换工具")
    print("="*70 + "\n")
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        sys.exit(1)
    
    if len(argv) < 3:
        print("✗ 错误：参数不足")
        print("需要：input output axis [vertices]")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_file = Path(argv[1])
    axis = argv[2].lower()
    vertices = int(argv[3]) if len(argv) > 3 else 32
    
    if axis not in ['x', 'y', 'z']:
        print(f"✗ 错误：axis必须是x, y或z")
        sys.exit(1)
    
    print(f"输入：{input_file}")
    print(f"输出：{output_file}")
    print(f"轴向：{axis.upper()}")
    print(f"顶点数：{vertices}\n")
    
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在")
        sys.exit(1)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 导入
    print("导入原始mesh...")
    clear_scene()
    original = import_stl(str(input_file))
    print(f"✓ 顶点：{len(original.data.vertices):,}, 面：{len(original.data.polygons):,}\n")
    
    # 计算边界
    print("计算边界框...")
    bbox = get_bounding_box(original)
    print(f"✓ 尺寸：({bbox['size'].x:.4f}, {bbox['size'].y:.4f}, {bbox['size'].z:.4f})\n")
    
    # 删除原始mesh
    bpy.data.objects.remove(original, do_unlink=True)
    
    # 创建圆柱体
    print("创建圆柱体...")
    cylinder, radius, depth = create_cylinder(bbox, axis, vertices)
    print(f"✓ 半径：{radius:.4f}m, 高度：{depth:.4f}m")
    print(f"  顶点：{len(cylinder.data.vertices)}, 面：{len(cylinder.data.polygons)}\n")
    
    # 导出
    print("导出...")
    export_stl(cylinder, str(output_file))
    
    input_size = input_file.stat().st_size / 1024
    output_size = output_file.stat().st_size / 1024
    
    print(f"\n文件大小：")
    print(f"  原始：{input_size:.1f} KB")
    print(f"  圆柱体：{output_size:.1f} KB")
    print(f"  减少：{(1 - output_size / input_size) * 100:.1f}%")
    
    print("\n" + "="*70)
    print("✓ 完成！")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
