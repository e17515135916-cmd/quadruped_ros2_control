#!/usr/bin/env python3
"""
Blender 批量凸包处理脚本
自动将所有腿部 STL 文件转换为凸包碰撞网格

使用方法：
    blender --background --python scripts/blender_batch_convex_hull.py

或者使用包装脚本：
    ./scripts/generate_convex_hulls.sh
"""

import bpy
import os
import sys
import math

# ============================================================================
# 配置区域
# ============================================================================

# 项目根目录（自动检测）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 输入输出目录
INPUT_DIR = os.path.join(PROJECT_ROOT, "src/dog2_description/meshes")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "src/dog2_description/meshes/collision")

# 需要处理的文件列表（所有腿部和基座）
FILES_TO_PROCESS = [
    # 基座
    "base_link.STL",
    # 第1条腿
    "l1.STL",     # 髋关节
    "l11.STL",    # 大腿上段
    "l111.STL",   # 大腿下段
    "l1111.STL",  # 小腿
    # 第2条腿
    "l2.STL",
    "l21.STL",
    "l211.STL",
    "l2111.STL",
    # 第3条腿
    "l3.STL",
    "l31.STL",
    "l311.STL",
    "l3111.STL",
    # 第4条腿
    "l4.STL",
    "l41.STL",
    "l411.STL",
    "l4111.STL",
]

# 凸包处理参数
DECIMATE_RATIO = 0.35  # 保留 35% 的面（可调整：0.2-0.5）
TARGET_FACE_COUNT = 300  # 目标面数


# ============================================================================
# 辅助函数
# ============================================================================

def clear_scene():
    """清空 Blender 场景中的所有对象"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("  ✓ 场景已清空")


def import_stl(filepath):
    """导入 STL 文件"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    bpy.ops.import_mesh.stl(filepath=filepath)
    
    # 获取导入的对象
    if len(bpy.context.selected_objects) == 0:
        raise RuntimeError(f"导入失败: {filepath}")
    
    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj
    print(f"  ✓ 已导入: {os.path.basename(filepath)}")
    return obj


def apply_convex_hull(obj):
    """应用凸包操作"""
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 全选所有顶点
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 应用凸包
    bpy.ops.mesh.convex_hull()
    
    # 返回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    face_count = len(obj.data.polygons)
    print(f"  ✓ 凸包已生成，面数: {face_count}")
    return face_count


def simplify_mesh(obj, target_ratio=0.35):
    """简化网格"""
    original_faces = len(obj.data.polygons)
    
    # 添加 Decimate 修改器
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.ratio = target_ratio
    
    # 应用修改器
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    final_faces = len(obj.data.polygons)
    reduction = (1 - final_faces / original_faces) * 100
    
    print(f"  ✓ 网格已简化: {original_faces} → {final_faces} 面 ({reduction:.1f}% 减少)")
    return final_faces


def clean_mesh(obj):
    """清理网格：移除重复顶点，重新计算法线"""
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 移除重复顶点
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # 重新计算法线
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # 返回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"  ✓ 网格已清理")



def export_stl(obj, filepath):
    """导出 STL 文件"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 选中对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 导出 STL
    bpy.ops.export_mesh.stl(
        filepath=filepath,
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=True,
        ascii=False,
        use_mesh_modifiers=True,
        axis_forward='Y',
        axis_up='Z'
    )
    
    # 检查文件大小
    file_size = os.path.getsize(filepath) / 1024  # KB
    print(f"  ✓ 已导出: {os.path.basename(filepath)} ({file_size:.1f} KB)")


def get_mesh_stats(obj):
    """获取网格统计信息"""
    vertices = len(obj.data.vertices)
    faces = len(obj.data.polygons)
    edges = len(obj.data.edges)
    
    # 计算边界框
    bbox = [obj.matrix_world @ v.co for v in obj.data.vertices]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    
    return {
        'vertices': vertices,
        'faces': faces,
        'edges': edges,
        'size': (size_x, size_y, size_z)
    }


# ============================================================================
# 主处理函数
# ============================================================================

def process_single_file(input_path, output_path):
    """处理单个 STL 文件"""
    filename = os.path.basename(input_path)
    print(f"\n{'='*60}")
    print(f"处理文件: {filename}")
    print(f"{'='*60}")
    
    try:
        # 1. 清空场景
        clear_scene()
        
        # 2. 导入 STL
        obj = import_stl(input_path)
        
        # 3. 获取原始统计信息
        original_stats = get_mesh_stats(obj)
        print(f"  原始网格: {original_stats['vertices']} 顶点, {original_stats['faces']} 面")
        print(f"  尺寸: {original_stats['size'][0]:.3f} x {original_stats['size'][1]:.3f} x {original_stats['size'][2]:.3f} m")
        
        # 4. 应用凸包
        face_count = apply_convex_hull(obj)
        
        # 5. 简化网格（如果面数太多）
        if face_count > TARGET_FACE_COUNT:
            # 动态计算需要的 ratio
            target_ratio = TARGET_FACE_COUNT / face_count
            target_ratio = max(0.2, min(0.5, target_ratio))  # 限制在 0.2-0.5
            simplify_mesh(obj, target_ratio)
        
        # 6. 清理网格
        clean_mesh(obj)
        
        # 7. 获取最终统计信息
        final_stats = get_mesh_stats(obj)
        print(f"  最终网格: {final_stats['vertices']} 顶点, {final_stats['faces']} 面")
        
        # 8. 导出
        export_stl(obj, output_path)
        
        print(f"✅ 成功处理: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {filename}")
        print(f"   错误: {str(e)}")
        return False



def main():
    """主函数：批量处理所有文件"""
    print("\n" + "="*60)
    print("Blender 批量凸包处理脚本")
    print("="*60)
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"待处理文件数: {len(FILES_TO_PROCESS)}")
    print("="*60)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 统计
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # 处理每个文件
    for filename in FILES_TO_PROCESS:
        input_path = os.path.join(INPUT_DIR, filename)
        
        # 生成输出文件名
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_collision.STL"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            print(f"\n⚠️  跳过: {filename} (文件不存在)")
            failed_count += 1
            failed_files.append(filename)
            continue
        
        # 处理文件
        success = process_single_file(input_path, output_path)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            failed_files.append(filename)
    
    # 打印总结
    print("\n" + "="*60)
    print("处理完成！")
    print("="*60)
    print(f"✅ 成功: {success_count} 个文件")
    print(f"❌ 失败: {failed_count} 个文件")
    
    if failed_files:
        print("\n失败的文件:")
        for f in failed_files:
            print(f"  - {f}")
    
    print("\n输出文件位置:")
    print(f"  {OUTPUT_DIR}")
    print("="*60)
    
    # 返回退出码
    return 0 if failed_count == 0 else 1


# ============================================================================
# 脚本入口
# ============================================================================

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
