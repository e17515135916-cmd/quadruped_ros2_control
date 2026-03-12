#!/usr/bin/env python3
"""
计算正确的碰撞体origin偏移
确保碰撞体中心与几何体中心对齐
"""

import numpy as np
from stl import mesh
import os

def calculate_mesh_center(stl_file):
    """计算STL网格的几何中心"""
    stl_mesh = mesh.Mesh.from_file(stl_file)
    vertices = stl_mesh.vectors.reshape(-1, 3)
    
    # 计算边界框
    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)
    
    # 几何中心 = (min + max) / 2
    center = (min_coords + max_coords) / 2
    
    return center, min_coords, max_coords

def analyze_leg_collisions():
    """分析腿部碰撞体的正确偏移"""
    
    print("=" * 70)
    print("碰撞体Origin偏移计算")
    print("=" * 70)
    print()
    
    # 分析大腿
    print("【大腿 (Thigh) - l111】")
    print("-" * 70)
    thigh_center, thigh_min, thigh_max = calculate_mesh_center(
        "src/dog2_description/meshes/collision/l111_collision.STL"
    )
    print(f"几何中心: X={thigh_center[0]:.6f}, Y={thigh_center[1]:.6f}, Z={thigh_center[2]:.6f}")
    print(f"边界框: ")
    print(f"  X: [{thigh_min[0]:.6f}, {thigh_max[0]:.6f}]")
    print(f"  Y: [{thigh_min[1]:.6f}, {thigh_max[1]:.6f}]")
    print(f"  Z: [{thigh_min[2]:.6f}, {thigh_max[2]:.6f}]")
    print(f"\n推荐Origin偏移: <origin xyz=\"{thigh_center[0]:.6f} {thigh_center[1]:.6f} {thigh_center[2]:.6f}\" rpy=\"0 0 0\"/>")
    print()
    
    # 分析小腿
    print("【小腿 (Shin) - l1111】")
    print("-" * 70)
    shin_center, shin_min, shin_max = calculate_mesh_center(
        "src/dog2_description/meshes/collision/l1111_collision.STL"
    )
    print(f"几何中心: X={shin_center[0]:.6f}, Y={shin_center[1]:.6f}, Z={shin_center[2]:.6f}")
    print(f"边界框: ")
    print(f"  X: [{shin_min[0]:.6f}, {shin_max[0]:.6f}]")
    print(f"  Y: [{shin_min[1]:.6f}, {shin_max[1]:.6f}]")
    print(f"  Z: [{shin_min[2]:.6f}, {shin_max[2]:.6f}]")
    print(f"\n推荐Origin偏移: <origin xyz=\"{shin_center[0]:.6f} {shin_center[1]:.6f} {shin_center[2]:.6f}\" rpy=\"0 0 0\"/>")
    print()
    
    # 检查膝关节处的间隙
    print("【膝关节间隙检查】")
    print("-" * 70)
    # 膝关节在大腿坐标系的 (0, -0.15201, 0.12997)
    knee_in_thigh = np.array([0, -0.15201, 0.12997])
    
    # 大腿末端（最小Y值）
    thigh_end_y = thigh_min[1]
    
    # 小腿顶端（最大Y值）
    shin_start_y = shin_max[1]
    
    print(f"膝关节位置（大腿坐标系）: Y = {knee_in_thigh[1]:.6f}")
    print(f"大腿碰撞体末端: Y = {thigh_end_y:.6f}")
    print(f"小腿碰撞体顶端: Y = {shin_start_y:.6f}")
    
    # 计算间隙（考虑origin偏移后）
    thigh_end_global = knee_in_thigh[1] + thigh_end_y
    shin_start_global = shin_start_y  # 小腿origin在膝关节
    
    gap = shin_start_global - thigh_end_global
    
    if gap < 0:
        print(f"\n⚠️  警告: 大腿和小腿重叠 {abs(gap)*1000:.2f}mm!")
        print(f"   这会导致碰撞冲突和爆炸!")
    else:
        print(f"\n✅ 间隙: {gap*1000:.2f}mm (安全)")
    
    print()
    
    # 检查脚部连接
    print("【脚部连接检查】")
    print("-" * 70)
    foot_connection_y = -0.299478
    print(f"脚部连接点（小腿坐标系）: Y = {foot_connection_y:.6f}")
    print(f"小腿碰撞体末端: Y = {shin_min[1]:.6f}")
    
    foot_gap = shin_min[1] - foot_connection_y
    
    if foot_gap < 0:
        print(f"\n⚠️  警告: 小腿碰撞体延伸到脚部 {abs(foot_gap)*1000:.2f}mm!")
        print(f"   这会导致小腿-脚部碰撞冲突!")
    else:
        print(f"\n✅ 间隙: {foot_gap*1000:.2f}mm (安全)")
    
    print()
    print("=" * 70)
    print("总结")
    print("=" * 70)
    print()
    print("修复方案:")
    print("1. 为大腿碰撞体设置正确的origin偏移")
    print("2. 为小腿碰撞体设置正确的origin偏移")
    print("3. 或者：移除小腿碰撞体，只保留脚部球体")
    print()
    
    return {
        'thigh_center': thigh_center,
        'shin_center': shin_center,
        'knee_gap': gap,
        'foot_gap': foot_gap
    }

if __name__ == "__main__":
    results = analyze_leg_collisions()
