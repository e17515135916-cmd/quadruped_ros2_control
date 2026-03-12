#!/usr/bin/env python3
"""
合并共面的三角形，减少冗余面数
将过度细分的平面恢复成简单的面

使用方法：
    blender --background --python scripts/merge_coplanar_faces.py -- <input> <output> <angle>

参数：
    input: 输入STL文件
    output: 输出STL文件
    angle: 角度阈值（度），默认5度。共面判断的容差，越小越严格

示例：
    # 使用5度角度阈值
    blender --background --python scripts/merge_coplanar_faces.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_merged.STL \
        5
    
    # 使用1度角度阈值（更严格）
    blender --background --python scripts/merge_coplanar_faces.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_merged.STL \
        1
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

def merge_coplanar_faces(obj, angle_limit):
    """
    合并共面的面
    
    这个操作会：
    1. 将共面的三角形合并成一个大面
    2. 移除不必要的边和顶点
    3. 保持原始形状不变
    """
    # 确保对象是活动对象
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 选择所有
    bpy.ops.mesh.select_all(action='SELECT')
    
    print(f"  使用Limited Dissolve...")
    print(f"  角度阈值：{angle_limit}度")
    
    # Limited Dissolve - 合并共面的面
    bpy.ops.mesh.dissolve_limited(
        angle_limit=math.radians(angle_limit),
        use_dissolve_boundaries=False,
        delimit={'NORMAL'}  # 只根据法向量判断
    )
    
    print(f"  ✓ 已合并共面的面")
    
    # 移除重复顶点
    bpy.ops.mesh.select_all(action='SELECT')
    removed = bpy.ops.mesh.remove_doubles(threshold=0.0001)
    print(f"  ✓ 已移除重复顶点")
    
    # 重新计算法向量
    bpy.ops.mesh.normals_make_consistent(inside=False)
    print(f"  ✓ 已重新计算法向量")
    
    # 退出编辑模式
    bpy.ops.object.mode_set(mode='OBJECT')

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
    print("合并共面三角形工具")
    print("="*70 + "\n")
    
    # 解析参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        print("使用方法：blender --background --python merge_coplanar_faces.py -- <input> <output> [angle]")
        sys.exit(1)
    
    if len(argv) < 2:
        print("✗ 错误：参数不足")
        print("需要：input output [angle]")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_file = Path(argv[1])
    angle_limit = float(argv[2]) if len(argv) > 2 else 5.0
    
    print(f"输入文件：{input_file}")
    print(f"输出文件：{output_file}")
    print(f"角度阈值：{angle_limit}度\n")
    
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在")
        sys.exit(1)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：导入
    print("步骤1：导入mesh...")
    clear_scene()
    obj = import_stl(str(input_file))
    
    original = get_stats(obj)
    print(f"✓ 原始mesh：")
    print(f"  顶点：{original['verts']:,}")
    print(f"  面：{original['faces']:,}")
    print(f"  边：{original['edges']:,}\n")
    
    # 步骤2：合并共面的面
    print("步骤2：合并共面的面...")
    merge_coplanar_faces(obj, angle_limit)
    
    merged = get_stats(obj)
    print(f"\n✓ 合并后mesh：")
    print(f"  顶点：{merged['verts']:,} (减少 {original['verts']-merged['verts']:,})")
    print(f"  面：{merged['faces']:,} (减少 {original['faces']-merged['faces']:,})")
    print(f"  边：{merged['edges']:,} (减少 {original['edges']-merged['edges']:,})")
    
    face_reduction = (1 - merged['faces'] / original['faces']) * 100
    print(f"\n面数减少：{face_reduction:.1f}%\n")
    
    # 步骤3：导出
    print("步骤3：导出...")
    export_stl(obj, str(output_file))
    
    # 文件大小
    input_size = input_file.stat().st_size / 1024
    output_size = output_file.stat().st_size / 1024
    size_reduction = (1 - output_size / input_size) * 100
    
    print(f"\n文件大小：")
    print(f"  原始：{input_size:.1f} KB")
    print(f"  合并后：{output_size:.1f} KB")
    print(f"  减少：{size_reduction:.1f}%")
    
    print("\n" + "="*70)
    print("✓ 完成！")
    print("="*70)
    print(f"\n说明：")
    print(f"  - 共面的三角形已合并成大面")
    print(f"  - 保持了原始形状")
    print(f"  - 移除了冗余的顶点和边")
    print(f"  - 如果减少不明显，可以增大角度阈值\n")

if __name__ == "__main__":
    main()
