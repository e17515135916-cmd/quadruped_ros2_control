#!/usr/bin/env python3
"""
测量小腿凸包的实际尺寸
检查是否与脚部位置重叠
"""

import numpy as np
from stl import mesh
import os

def measure_shin_mesh(stl_file):
    """测量小腿网格的边界框"""
    shin_mesh = mesh.Mesh.from_file(stl_file)
    
    # 获取所有顶点
    vertices = shin_mesh.vectors.reshape(-1, 3)
    
    # 计算边界框
    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)
    dimensions = max_coords - min_coords
    
    print(f"\n文件: {os.path.basename(stl_file)}")
    print("=" * 60)
    print(f"边界框:")
    print(f"  X: [{min_coords[0]:.6f}, {max_coords[0]:.6f}] 范围: {dimensions[0]:.6f}m")
    print(f"  Y: [{min_coords[1]:.6f}, {max_coords[1]:.6f}] 范围: {dimensions[1]:.6f}m")
    print(f"  Z: [{min_coords[2]:.6f}, {max_coords[2]:.6f}] 范围: {dimensions[2]:.6f}m")
    
    # 小腿是沿Y轴延伸的
    shin_length = dimensions[1]
    print(f"\n小腿长度 (Y轴): {shin_length:.6f}m ({shin_length*1000:.2f}mm)")
    
    # 脚部连接点在 Y=-0.299478
    foot_connection_y = -0.299478
    print(f"脚部连接点: Y = {foot_connection_y:.6f}m")
    
    # 检查是否重叠
    if min_coords[1] < foot_connection_y:
        overlap = foot_connection_y - min_coords[1]
        print(f"\n⚠️  警告: 小腿凸包延伸超过脚部连接点!")
        print(f"   重叠距离: {overlap:.6f}m ({overlap*1000:.2f}mm)")
        print(f"   这会导致小腿凸包与脚部球体碰撞!")
    else:
        clearance = min_coords[1] - foot_connection_y
        print(f"\n✅ 小腿凸包未超过脚部连接点")
        print(f"   间隙: {clearance:.6f}m ({clearance*1000:.2f}mm)")
    
    return min_coords, max_coords, dimensions

if __name__ == "__main__":
    print("=" * 60)
    print("小腿凸包尺寸分析")
    print("=" * 60)
    
    # 测量原始小腿网格
    print("\n【原始小腿网格】")
    measure_shin_mesh("src/dog2_description/meshes/l111.STL")
    
    # 测量凸包小腿网格
    print("\n【凸包小腿网格】")
    measure_shin_mesh("src/dog2_description/meshes/collision/l111_collision.STL")
    
    print("\n" + "=" * 60)
    print("结论:")
    print("=" * 60)
    print("如果凸包延伸超过脚部连接点，需要:")
    print("  方案1: 添加碰撞过滤（禁用小腿-脚部碰撞）")
    print("  方案2: 在Blender中截断小腿凸包")
    print("  方案3: 使用简化几何体（圆柱体）代替凸包")
