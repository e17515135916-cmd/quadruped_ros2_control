#!/usr/bin/env python3
"""
高级mesh简化工具，支持多种简化方法

使用方法：
    blender --background --python scripts/simplify_mesh_advanced.py -- <input> <output> <method> <param>

参数：
    input: 输入STL文件
    output: 输出STL文件
    method: 简化方法
        - collapse: 边折叠 (参数: ratio 0.0-1.0)
        - planar: 平面简化 (参数: angle_limit 度数)
        - unsubdivide: 反细分 (参数: iterations 整数)
    param: 方法参数

示例：
    # 边折叠，保留10%
    blender --background --python scripts/simplify_mesh_advanced.py -- \
        l1.STL l1_simple.STL collapse 0.1
    
    # 平面简化，5度角度限制
    blender --background --python scripts/simplify_mesh_advanced.py -- \
        l1.STL l1_simple.STL planar 5
    
    # 反细分，2次迭代
    blender --background --python scripts/simplify_mesh_advanced.py -- \
        l1.STL l1_simple.STL unsubdivide 2
"""

import bpy
import sys
import math
from pathlib import Path

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_stl(filepath):
    """导入STL"""
    bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

def get_stats(obj):
    """获取统计信息"""
    return {
        'verts': len(obj.data.vertices),
        'faces': len(obj.data.polygons),
        'edges': len(obj.data.edges)
    }

def simplify_collapse(obj, ratio):
    """边折叠简化"""
    print(f"使用边折叠方法，保留比例：{ratio}")
    
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Decimate")

def simplify_planar(obj, angle_limit):
    """平面简化"""
    print(f"使用平面简化方法，角度限制：{angle_limit}度")
    
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.decimate_type = 'DISSOLVE'
    modifier.angle_limit = math.radians(angle_limit)
    modifier.use_dissolve_boundaries = False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Decimate")

def simplify_unsubdivide(obj, iterations):
    """反细分简化"""
    print(f"使用反细分方法，迭代次数：{iterations}")
    
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.decimate_type = 'UNSUBDIV'
    modifier.iterations = iterations
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Decimate")

def remesh_blocks(obj, octree_depth):
    """使用Remesh创建块状简化版本"""
    print(f"使用Remesh方法，八叉树深度：{octree_depth}")
    
    modifier = obj.modifiers.new(name="Remesh", type='REMESH')
    modifier.mode = 'BLOCKS'
    modifier.octree_depth = octree_depth
    modifier.use_remove_disconnected = False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Remesh")

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
    print("高级Mesh简化工具")
    print("="*70 + "\n")
    
    # 解析参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        sys.exit(1)
    
    if len(argv) < 4:
        print("✗ 错误：参数不足")
        print("需要：input output method param")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_file = Path(argv[1])
    method = argv[2]
    param = argv[3]
    
    print(f"输入：{input_file}")
    print(f"输出：{output_file}")
    print(f"方法：{method}")
    print(f"参数：{param}\n")
    
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在")
        sys.exit(1)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 导入
    clear_scene()
    print("导入mesh...")
    obj = import_stl(str(input_file))
    
    original = get_stats(obj)
    print(f"\n原始mesh：")
    print(f"  顶点：{original['verts']:,}")
    print(f"  面：{original['faces']:,}")
    print(f"  边：{original['edges']:,}\n")
    
    # 简化
    print("简化中...")
    try:
        if method == 'collapse':
            simplify_collapse(obj, float(param))
        elif method == 'planar':
            simplify_planar(obj, float(param))
        elif method == 'unsubdivide':
            simplify_unsubdivide(obj, int(param))
        elif method == 'remesh':
            remesh_blocks(obj, int(param))
        else:
            print(f"✗ 错误：未知方法 '{method}'")
            print("支持的方法：collapse, planar, unsubdivide, remesh")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 简化失败：{e}")
        sys.exit(1)
    
    simplified = get_stats(obj)
    print(f"\n简化后mesh：")
    print(f"  顶点：{simplified['verts']:,} (减少 {original['verts']-simplified['verts']:,})")
    print(f"  面：{simplified['faces']:,} (减少 {original['faces']-simplified['faces']:,})")
    print(f"  边：{simplified['edges']:,} (减少 {original['edges']-simplified['edges']:,})")
    
    reduction = (1 - simplified['faces'] / original['faces']) * 100
    print(f"\n减少比例：{reduction:.1f}%\n")
    
    # 导出
    print("导出...")
    export_stl(obj, str(output_file))
    
    # 文件大小
    input_size = input_file.stat().st_size / 1024
    output_size = output_file.stat().st_size / 1024
    size_reduction = (1 - output_size / input_size) * 100
    
    print(f"\n文件大小：")
    print(f"  原始：{input_size:.1f} KB")
    print(f"  简化：{output_size:.1f} KB")
    print(f"  减少：{size_reduction:.1f}%")
    
    print("\n" + "="*70)
    print("✓ 完成！")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
