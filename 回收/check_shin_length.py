#!/usr/bin/env python3
"""
检查小腿STL文件的实际尺寸，确定足端应该放置的位置
"""
import struct
import sys

def read_stl_bounds(filename):
    """读取STL文件并计算边界框"""
    with open(filename, 'rb') as f:
        # 跳过80字节的头部
        f.read(80)
        
        # 读取三角形数量
        num_triangles = struct.unpack('I', f.read(4))[0]
        
        # 初始化边界
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        # 读取每个三角形
        for _ in range(num_triangles):
            # 跳过法向量（3个float）
            f.read(12)
            
            # 读取3个顶点
            for _ in range(3):
                x, y, z = struct.unpack('fff', f.read(12))
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_z = min(min_z, z)
                max_z = max(max_z, z)
            
            # 跳过属性字节计数
            f.read(2)
    
    return {
        'min': (min_x, min_y, min_z),
        'max': (max_x, max_y, max_z),
        'size': (max_x - min_x, max_y - min_y, max_z - min_z),
        'center': ((min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2)
    }

# 检查所有4条腿的小腿STL文件
for leg_num in [1, 2, 3, 4]:
    stl_file = f'src/dog2_description/meshes/l{leg_num}111.STL'
    try:
        bounds = read_stl_bounds(stl_file)
        print(f"\n=== Leg {leg_num} 小腿 (l{leg_num}111) ===")
        print(f"最小坐标: X={bounds['min'][0]:.6f}, Y={bounds['min'][1]:.6f}, Z={bounds['min'][2]:.6f}")
        print(f"最大坐标: X={bounds['max'][0]:.6f}, Y={bounds['max'][1]:.6f}, Z={bounds['max'][2]:.6f}")
        print(f"尺寸: X={bounds['size'][0]:.6f}, Y={bounds['size'][1]:.6f}, Z={bounds['size'][2]:.6f}")
        print(f"中心: X={bounds['center'][0]:.6f}, Y={bounds['center'][1]:.6f}, Z={bounds['center'][2]:.6f}")
        print(f"\n小腿末端（Y方向最小值）: Y = {bounds['min'][1]:.6f} m")
        print(f"建议足端偏移量: xyz=\"0 {bounds['min'][1]:.6f} 0\"")
    except FileNotFoundError:
        print(f"文件不存在: {stl_file}")
    except Exception as e:
        print(f"读取 {stl_file} 时出错: {e}")
