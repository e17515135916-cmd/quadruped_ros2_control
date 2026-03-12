#!/usr/bin/env python3
"""
在Blender中自动分离L1 mesh为上下两部分

使用方法：
    blender --background --python scripts/split_l1_mesh.py -- <workspace_path> <split_height>

参数：
    workspace_path: ROS2工作空间路径（例如：~/aperfect/carbot_ws）
    split_height: 分离高度（米），默认为0.05（即在Z=0.05处分离）

示例：
    blender --background --python scripts/split_l1_mesh.py -- ~/aperfect/carbot_ws 0.05
"""

import bpy
import sys
import os
import math
from pathlib import Path

def clear_scene():
    """清空场景中的所有对象"""
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

def split_mesh_by_height(obj, split_z):
    """
    按Z坐标分离mesh
    
    参数：
        obj: Blender对象
        split_z: 分离的Z坐标值（米）
    """
    # 确保对象被选中
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    print(f"✓ 进入编辑模式")
    
    # 取消所有选择
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # 切换到面选择模式
    bpy.ops.mesh.select_mode(type='FACE')
    
    # 回到对象模式以访问mesh数据
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 选择Z坐标大于split_z的所有顶点
    mesh = obj.data
    selected_count = 0
    
    for vertex in mesh.vertices:
        # 获取顶点的世界坐标
        world_coord = obj.matrix_world @ vertex.co
        if world_coord.z >= split_z:
            vertex.select = True
            selected_count += 1
        else:
            vertex.select = False
    
    print(f"✓ 已选择 {selected_count} 个顶点（Z >= {split_z}m）")
    
    # 回到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 选择相关的面
    bpy.ops.mesh.select_mode(type='FACE')
    
    # 分离选中的部分
    bpy.ops.mesh.separate(type='SELECTED')
    print(f"✓ 已分离mesh")
    
    # 回到对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 现在应该有两个对象
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    
    if len(objects) != 2:
        print(f"✗ 错误：分离后应该有2个对象，但实际有 {len(objects)} 个")
        return None, None
    
    # 根据Z坐标判断哪个是上部，哪个是下部
    obj1, obj2 = objects
    
    # 计算每个对象的中心Z坐标
    z1 = sum((obj1.matrix_world @ v.co).z for v in obj1.data.vertices) / len(obj1.data.vertices)
    z2 = sum((obj2.matrix_world @ v.co).z for v in obj2.data.vertices) / len(obj2.data.vertices)
    
    if z1 > z2:
        upper, lower = obj1, obj2
    else:
        upper, lower = obj2, obj1
    
    # 重命名
    upper.name = "l1_upper"
    lower.name = "l1_lower"
    
    print(f"✓ 上部中心Z坐标：{max(z1, z2):.4f}m")
    print(f"✓ 下部中心Z坐标：{min(z1, z2):.4f}m")
    
    return upper, lower

def export_stl(obj, filepath):
    """导出单个对象为STL"""
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

def get_mesh_info(obj):
    """获取mesh的基本信息"""
    mesh = obj.data
    vertices = len(mesh.vertices)
    faces = len(mesh.polygons)
    
    # 计算边界框
    bbox = [obj.matrix_world @ v.co for v in mesh.vertices]
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    height = max_z - min_z
    
    return {
        'vertices': vertices,
        'faces': faces,
        'min_z': min_z,
        'max_z': max_z,
        'height': height
    }

def main():
    """主函数"""
    print("\n" + "="*60)
    print("L1 Mesh分离工具")
    print("="*60 + "\n")
    
    # 解析命令行参数
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        print("✗ 错误：缺少参数")
        print("使用方法：blender --background --python split_l1_mesh.py -- <workspace_path> [split_height]")
        sys.exit(1)
    
    if len(argv) < 1:
        print("✗ 错误：需要提供工作空间路径")
        sys.exit(1)
    
    workspace_path = Path(argv[0]).expanduser()
    split_height = float(argv[1]) if len(argv) > 1 else 0.05  # 默认在5cm处分离
    
    print(f"工作空间：{workspace_path}")
    print(f"分离高度：{split_height}m\n")
    
    # 设置文件路径
    meshes_dir = workspace_path / "src/dog2_description/meshes"
    collision_dir = meshes_dir / "collision"
    
    input_file = meshes_dir / "l1.STL"
    output_upper = meshes_dir / "l1_upper.STL"
    output_lower = meshes_dir / "l1_lower.STL"
    output_upper_collision = collision_dir / "l1_upper_collision.STL"
    output_lower_collision = collision_dir / "l1_lower_collision.STL"
    
    # 检查输入文件
    if not input_file.exists():
        print(f"✗ 错误：找不到输入文件 {input_file}")
        sys.exit(1)
    
    # 创建碰撞目录（如果不存在）
    collision_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份原文件
    backup_file = input_file.with_suffix('.STL.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy2(input_file, backup_file)
        print(f"✓ 已备份原文件到：{backup_file}\n")
    
    # 步骤1：清空场景
    clear_scene()
    
    # 步骤2：导入L1 mesh
    obj = import_stl(str(input_file))
    
    # 显示原始mesh信息
    info = get_mesh_info(obj)
    print(f"\n原始mesh信息：")
    print(f"  顶点数：{info['vertices']}")
    print(f"  面数：{info['faces']}")
    print(f"  Z范围：{info['min_z']:.4f}m 到 {info['max_z']:.4f}m")
    print(f"  高度：{info['height']:.4f}m\n")
    
    # 步骤3：分离mesh
    upper, lower = split_mesh_by_height(obj, split_height)
    
    if upper is None or lower is None:
        print("✗ 分离失败")
        sys.exit(1)
    
    # 显示分离后的信息
    upper_info = get_mesh_info(upper)
    lower_info = get_mesh_info(lower)
    
    print(f"\n上部mesh信息：")
    print(f"  顶点数：{upper_info['vertices']}")
    print(f"  面数：{upper_info['faces']}")
    print(f"  高度：{upper_info['height']:.4f}m")
    
    print(f"\n下部mesh信息：")
    print(f"  顶点数：{lower_info['vertices']}")
    print(f"  面数：{lower_info['faces']}")
    print(f"  高度：{lower_info['height']:.4f}m\n")
    
    # 步骤4：导出视觉mesh
    export_stl(upper, str(output_upper))
    export_stl(lower, str(output_lower))
    
    # 步骤5：导出碰撞mesh（使用相同的mesh）
    export_stl(upper, str(output_upper_collision))
    export_stl(lower, str(output_lower_collision))
    
    print("\n" + "="*60)
    print("✓ 分离完成！")
    print("="*60)
    print(f"\n生成的文件：")
    print(f"  视觉mesh（上部）：{output_upper}")
    print(f"  视觉mesh（下部）：{output_lower}")
    print(f"  碰撞mesh（上部）：{output_upper_collision}")
    print(f"  碰撞mesh（下部）：{output_lower_collision}")
    print(f"\n备份文件：{backup_file}")
    
    print(f"\n下一步：")
    print(f"1. 在RViz中查看分离结果")
    print(f"2. 更新URDF文件以使用新的mesh")
    print(f"3. 添加新的关节连接上下两部分")
    print(f"4. 重新编译并测试\n")

if __name__ == "__main__":
    main()
