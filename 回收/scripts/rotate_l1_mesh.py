#!/usr/bin/env python3
"""
旋转l1 mesh文件（绕Y轴90度）
保持其他所有东西不变
"""

import bpy
import os
import sys
import math

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def rotate_l1_mesh(workspace_dir):
    """旋转l1 mesh文件"""
    
    # l1的STL文件路径
    l1_stl_path = os.path.join(workspace_dir, "src/dog2_description/meshes/l1.STL")
    l1_collision_path = os.path.join(workspace_dir, "src/dog2_description/meshes/collision/l1_collision.STL")
    
    print("=" * 60)
    print("旋转l1 mesh文件（绕Y轴90度）")
    print("=" * 60)
    print()
    
    # 检查文件是否存在
    if not os.path.exists(l1_stl_path):
        print(f"❌ 文件不存在: {l1_stl_path}")
        return False
    
    print(f"✅ 找到文件: {l1_stl_path}")
    
    # 备份原文件
    backup_path = l1_stl_path + ".backup"
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(l1_stl_path, backup_path)
        print(f"✅ 已备份到: {backup_path}")
    
    # 清空场景
    clear_scene()
    
    # 导入l1.STL
    print()
    print("正在导入l1.STL...")
    bpy.ops.import_mesh.stl(filepath=l1_stl_path)
    
    # 获取导入的对象
    obj = bpy.context.selected_objects[0]
    print(f"✅ 已导入: {obj.name}")
    
    # 旋转90度（绕Y轴）
    print()
    print("正在旋转...")
    print(f"  旋转轴: Y轴")
    print(f"  旋转角度: 90度 (1.5708 弧度)")
    
    # 绕Y轴旋转90度
    obj.rotation_euler[1] = math.radians(90)
    
    # 应用旋转（将旋转烘焙到mesh数据中）
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    print("✅ 旋转已应用到mesh")
    
    # 导出修改后的STL
    print()
    print("正在导出修改后的文件...")
    bpy.ops.export_mesh.stl(
        filepath=l1_stl_path,
        use_selection=True,
        ascii=False
    )
    print(f"✅ 已保存: {l1_stl_path}")
    
    # 如果碰撞文件存在，也旋转它
    if os.path.exists(l1_collision_path):
        print()
        print("正在处理碰撞mesh...")
        
        # 备份碰撞文件
        collision_backup = l1_collision_path + ".backup"
        if not os.path.exists(collision_backup):
            import shutil
            shutil.copy2(l1_collision_path, collision_backup)
            print(f"✅ 已备份到: {collision_backup}")
        
        # 清空场景
        clear_scene()
        
        # 导入碰撞mesh
        bpy.ops.import_mesh.stl(filepath=l1_collision_path)
        obj = bpy.context.selected_objects[0]
        
        # 旋转90度
        obj.rotation_euler[1] = math.radians(90)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        # 导出
        bpy.ops.export_mesh.stl(
            filepath=l1_collision_path,
            use_selection=True,
            ascii=False
        )
        print(f"✅ 已保存: {l1_collision_path}")
    
    print()
    print("=" * 60)
    print("✅ 完成！l1 mesh已绕Y轴旋转90度")
    print("=" * 60)
    print()
    print("下一步：")
    print("1. 重新编译: colcon build --packages-select dog2_description")
    print("2. 在RViz中查看: ros2 launch dog2_description view_dog2.launch.py")
    print()
    print("如果需要恢复原文件：")
    print(f"  cp {backup_path} {l1_stl_path}")
    
    return True

def main():
    """主函数"""
    # 直接使用固定的工作空间路径
    workspace_dir = os.path.expanduser("~/aperfect/carbot_ws")
    
    print()
    print("工作空间:", workspace_dir)
    print()
    
    if not os.path.exists(workspace_dir):
        print(f"❌ 工作空间不存在: {workspace_dir}")
        print(f"当前目录: {os.getcwd()}")
        return
    
    # 旋转l1 mesh
    rotate_l1_mesh(workspace_dir)

if __name__ == "__main__":
    main()
