#!/usr/bin/env python3
"""
在Blender中导入完整的Dog2 URDF模型
自动导入所有STL文件并应用坐标变换
"""

import bpy
import os
import math
from mathutils import Matrix, Euler, Vector

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 工作空间路径
workspace = os.path.expanduser("~/aperfect/carbot_ws")
meshes_dir = os.path.join(workspace, "src/dog2_description/meshes")

print("=" * 70)
print("导入Dog2机器人模型到Blender")
print("=" * 70)
print(f"Meshes目录: {meshes_dir}")
print()

def rpy_to_matrix(roll, pitch, yaw):
    """将RPY角度转换为旋转矩阵"""
    euler = Euler((roll, pitch, yaw), 'XYZ')
    return euler.to_matrix().to_4x4()

def import_stl(filepath, name, location=(0, 0, 0), rotation=(0, 0, 0)):
    """导入STL文件并设置位置和旋转"""
    if not os.path.exists(filepath):
        print(f"⚠️  文件不存在: {filepath}")
        return None
    
    # 导入STL
    bpy.ops.import_mesh.stl(filepath=filepath)
    
    # 获取刚导入的对象
    obj = bpy.context.selected_objects[0]
    obj.name = name
    
    # 设置位置
    obj.location = location
    
    # 设置旋转（RPY）
    obj.rotation_euler = rotation
    
    print(f"✅ 导入: {name}")
    return obj

# 导入base_link
print("1. 导入base_link")
print("-" * 70)
base_link = import_stl(
    os.path.join(meshes_dir, "base_link.STL"),
    "base_link",
    location=(0, 0, 0),
    rotation=(0, 0, 0)
)

# Leg 1 (左前腿)
print("\n2. 导入Leg 1 (左前腿)")
print("-" * 70)
l1 = import_stl(
    os.path.join(meshes_dir, "l1.STL"),
    "l1",
    location=(1.1026, -0.80953, 0.2649),
    rotation=(1.5708, 0, 0)
)

l11 = import_stl(
    os.path.join(meshes_dir, "l11.STL"),
    "l11",
    location=(1.1026 - 0.016, -0.80953 + 0.0199, 0.2649 + 0.055),
    rotation=(1.5708, 0, 1.5708)
)

l111 = import_stl(
    os.path.join(meshes_dir, "l111.STL"),
    "l111",
    location=(1.1026 - 0.016 - 0.0233, -0.80953 + 0.0199 - 0.055, 0.2649 + 0.055 + 0.0274),
    rotation=(0, 0, 0)
)

l1111 = import_stl(
    os.path.join(meshes_dir, "l1111.STL"),
    "l1111",
    location=(1.1026 - 0.016 - 0.0233, -0.80953 + 0.0199 - 0.055 - 0.15201, 0.2649 + 0.055 + 0.0274 + 0.12997),
    rotation=(0, 0, 0)
)

# Leg 2 (右前腿)
print("\n3. 导入Leg 2 (右前腿)")
print("-" * 70)
l2 = import_stl(
    os.path.join(meshes_dir, "l2.STL"),
    "l2",
    location=(1.3491, -0.80953, 0.2649),
    rotation=(1.5708, 0, 0)
)

l21 = import_stl(
    os.path.join(meshes_dir, "l21.STL"),
    "l21",
    location=(1.3491 - 0.016, -0.80953 + 0.0199, 0.2649 + 0.055),
    rotation=(1.5708, 0, 1.5708)
)

l211 = import_stl(
    os.path.join(meshes_dir, "l211.STL"),
    "l211",
    location=(1.3491 - 0.016 - 0.0233, -0.80953 + 0.0199 - 0.055, 0.2649 + 0.055 + 0.0274),
    rotation=(0, 0, 0)
)

l2111 = import_stl(
    os.path.join(meshes_dir, "l2111.STL"),
    "l2111",
    location=(1.3491 - 0.016 - 0.0233, -0.80953 + 0.0199 - 0.055 - 0.15201, 0.2649 + 0.055 + 0.0274 + 0.12997),
    rotation=(0, 0, 0)
)

# Leg 3 (左后腿)
print("\n4. 导入Leg 3 (左后腿)")
print("-" * 70)
l3 = import_stl(
    os.path.join(meshes_dir, "l3.STL"),
    "l3",
    location=(1.3491, -0.68953, 0.2649),
    rotation=(1.5708, 0, -3.1416)
)

l31 = import_stl(
    os.path.join(meshes_dir, "l31.STL"),
    "l31",
    location=(1.3491 - 0.016, -0.68953 + 0.0199, 0.2649 + 0.055),
    rotation=(3.1416, 0, 1.5708)
)

l311 = import_stl(
    os.path.join(meshes_dir, "l311.STL"),
    "l311",
    location=(1.3491 - 0.016 - 0.0233, -0.68953 + 0.0199 - 0.055, 0.2649 + 0.055 - 0.0254),
    rotation=(0, 0, 0)
)

l3111 = import_stl(
    os.path.join(meshes_dir, "l3111.STL"),
    "l3111",
    location=(1.3491 - 0.016 - 0.0233, -0.68953 + 0.0199 - 0.055 - 0.15201, 0.2649 + 0.055 - 0.0254 + 0.12997),
    rotation=(0, 0, 0)
)

# Leg 4 (右后腿) - 使用修复后的配置
print("\n5. 导入Leg 4 (右后腿) - 已修复")
print("-" * 70)
l4 = import_stl(
    os.path.join(meshes_dir, "l4.STL"),
    "l4",
    location=(1.1071, -0.68953, 0.2649),
    rotation=(1.5708, 0, -3.1416)
)

l41 = import_stl(
    os.path.join(meshes_dir, "l41.STL"),
    "l41",
    location=(1.1071 - 0.016, -0.68953 + 0.0199, 0.2649 + 0.055),  # 使用修复后的-0.016
    rotation=(3.1416, 0, 1.5708)
)

l411 = import_stl(
    os.path.join(meshes_dir, "l411.STL"),
    "l411",
    location=(1.1071 - 0.016 - 0.0233, -0.68953 + 0.0199 - 0.055, 0.2649 + 0.055 - 0.0254),
    rotation=(0, 3.1416, 0)
)

l4111 = import_stl(
    os.path.join(meshes_dir, "l4111.STL"),
    "l4111",
    location=(1.1071 - 0.016 - 0.0233, -0.68953 + 0.0199 - 0.055 - 0.15201, 0.2649 + 0.055 - 0.0254 + 0.12997),
    rotation=(0, 0, 0)
)

print()
print("=" * 70)
print("✅ 完成！所有部件已导入")
print("=" * 70)
print()
print("提示：")
print("- 使用鼠标中键旋转视图")
print("- 使用滚轮缩放")
print("- 按数字键盘7查看顶视图")
print("- 按数字键盘1查看前视图")
print("- 按数字键盘3查看侧视图")
print()
print("⚠️  注意：")
print("- 这是简化的导入，坐标变换可能不完全准确")
print("- 推荐使用RViz查看精确的装配体")
