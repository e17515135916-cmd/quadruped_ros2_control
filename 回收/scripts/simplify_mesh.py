#!/usr/bin/env python3
"""
简化STL mesh，减少面数

使用方法：
    blender --background --python scripts/simplify_mesh.py -- <input_file> <output_file> <ratio>

参数：
    input_file: 输入STL文件路径
    output_file: 输出STL文件路径
    ratio: 保留的面数比例 (0.0-1.0)，例如0.1表示保留10%的面

示例：
    # 保留10%的面
    blender --background --python scripts/simplify_mesh.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_simplified.STL \
        0.1
    
    # 保留50%的面
    blender --background --python scripts/simplify_mesh.py -- \
        src/dog2_description/meshes/l1.STL \
        src/dog2_description/meshes/l1_simplified.STL \
        0.5
"""

import bpy
import sys
import os
from pathlib import Path

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("✓ 场景已清空")

def import_stl(filepath):
    """导入STL文件"""
    if not os.path.exists(filepath):
        print(f"✗ 错误：文件不存在 {filepath}")
        sys.exit(1)
    
    bpy.ops.import_mesh.stl(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    print(f"✓ 已导入：{filepath}")
    return obj

def get_mesh_stats(obj):
    """获取mesh统计信息"""
    mesh = obj.data
    return {
        'vertices': len(mesh.vertices),
        'faces': len(mesh.polygons),
        'edges': len(mesh.edges)
    }

def simplify_mesh(obj, ratio):
    """
    使用Decimate Modifier简化mesh
    
    参数:
        obj: Blender对象
        ratio: 保留的面数比例 (0.0-1.0)
    """
    # 确保对象被选中
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # 添加Decimate modifier
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    
    print(f"✓ 已添加Decimate modifier (ratio={ratio})")
    
    # 应用modifier
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print(f"✓ 已应用modifier")

def export_stl(obj, filepath):
    """导出STL文件"""
    # 取消所有选择
    bpy.ops.object.select_all(action='DESELECT')
    
    # 只选择要导出的对象
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
    
    print(f"✓ 已导出：{filepath}")

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Mesh简化工具")
    print("="*70 + "\n")
    
    # 解析命令行参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        print("使用方法：blender --background --python simplify_mesh.py -- <input> <output> <ratio>")
        sys.exit(1)
    
    if len(argv) < 3:
        print("✗ 错误：参数不足")
        print("需要3个参数：input_file output_file ratio")
        sys.exit(1)
    
    input_file = Path(argv[0])
    output_file = Path(argv[1])
    ratio = float(argv[2])
    
    # 验证ratio
    if ratio <= 0 or ratio > 1:
        print(f"✗ 错误：ratio必须在0到1之间，当前值：{ratio}")
        sys.exit(1)
    
    print(f"输入文件：{input_file}")
    print(f"输出文件：{output_file}")
    print(f"简化比例：{ratio} ({ratio*100:.1f}%)\n")
    
    # 检查输入文件
    if not input_file.exists():
        print(f"✗ 错误：输入文件不存在：{input_file}")
        sys.exit(1)
    
    # 创建输出目录
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：清空场景
    clear_scene()
    print()
    
    # 步骤2：导入mesh
    print("步骤1：导入mesh...")
    obj = import_stl(str(input_file))
    
    # 显示原始统计信息
    original_stats = get_mesh_stats(obj)
    print(f"\n原始mesh统计：")
    print(f"  顶点数：{original_stats['vertices']:,}")
    print(f"  面数：{original_stats['faces']:,}")
    print(f"  边数：{original_stats['edges']:,}\n")
    
    # 步骤3：简化mesh
    print("步骤2：简化mesh...")
    simplify_mesh(obj, ratio)
    
    # 显示简化后的统计信息
    simplified_stats = get_mesh_stats(obj)
    print(f"\n简化后mesh统计：")
    print(f"  顶点数：{simplified_stats['vertices']:,} (减少 {original_stats['vertices'] - simplified_stats['vertices']:,})")
    print(f"  面数：{simplified_stats['faces']:,} (减少 {original_stats['faces'] - simplified_stats['faces']:,})")
    print(f"  边数：{simplified_stats['edges']:,} (减少 {original_stats['edges'] - simplified_stats['edges']:,})")
    
    # 计算实际减少比例
    actual_ratio = simplified_stats['faces'] / original_stats['faces']
    print(f"\n实际保留比例：{actual_ratio:.2%}")
    print(f"减少比例：{(1-actual_ratio):.2%}\n")
    
    # 步骤4：导出
    print("步骤3：导出简化后的mesh...")
    export_stl(obj, str(output_file))
    
    # 比较文件大小
    input_size = input_file.stat().st_size
    output_size = output_file.stat().st_size
    size_reduction = (1 - output_size / input_size) * 100
    
    print(f"\n文件大小：")
    print(f"  原始：{input_size / 1024:.1f} KB")
    print(f"  简化后：{output_size / 1024:.1f} KB")
    print(f"  减少：{size_reduction:.1f}%")
    
    # 完成
    print("\n" + "="*70)
    print("✓ 简化完成！")
    print("="*70)
    print(f"\n输出文件：{output_file}\n")

if __name__ == "__main__":
    main()
