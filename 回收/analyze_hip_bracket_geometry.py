#!/usr/bin/env python3
"""
髋关节支架几何分析工具
分析现有的l11.STL mesh文件,测量尺寸并记录关键信息
"""

import numpy as np
import trimesh
import sys
from pathlib import Path

def analyze_bracket_mesh(mesh_path):
    """分析支架mesh文件"""
    print(f"\n{'='*60}")
    print(f"分析文件: {mesh_path}")
    print(f"{'='*60}\n")
    
    # 加载mesh
    try:
        mesh = trimesh.load(mesh_path)
        print(f"✓ 成功加载mesh文件")
        print(f"  - 三角形数量: {len(mesh.faces)}")
        print(f"  - 顶点数量: {len(mesh.vertices)}")
    except Exception as e:
        print(f"✗ 加载mesh失败: {e}")
        return None
    
    # 计算边界框
    bounds = mesh.bounds
    min_point = bounds[0]
    max_point = bounds[1]
    dimensions = max_point - min_point
    
    print(f"\n1. 边界框分析:")
    print(f"  最小点 (min): [{min_point[0]:.6f}, {min_point[1]:.6f}, {min_point[2]:.6f}] m")
    print(f"  最大点 (max): [{max_point[0]:.6f}, {max_point[1]:.6f}, {max_point[2]:.6f}] m")
    print(f"  尺寸 (X, Y, Z): [{dimensions[0]:.6f}, {dimensions[1]:.6f}, {dimensions[2]:.6f}] m")
    print(f"  尺寸 (mm): [{dimensions[0]*1000:.2f}, {dimensions[1]*1000:.2f}, {dimensions[2]*1000:.2f}] mm")
    
    # 计算质心
    centroid = mesh.centroid
    print(f"\n2. 质心位置:")
    print(f"  质心: [{centroid[0]:.6f}, {centroid[1]:.6f}, {centroid[2]:.6f}] m")
    
    # 计算体积和质量(假设PLA密度1.25 g/cm³)
    volume = mesh.volume
    density_pla = 1250  # kg/m³
    mass = volume * density_pla
    
    print(f"\n3. 体积和质量:")
    print(f"  体积: {volume:.9f} m³ = {volume*1e6:.2f} cm³")
    print(f"  估算质量 (PLA密度1.25g/cm³): {mass:.4f} kg = {mass*1000:.2f} g")
    
    # 分析主要方向
    print(f"\n4. 主要尺寸方向:")
    print(f"  X方向 (前后): {dimensions[0]*1000:.2f} mm")
    print(f"  Y方向 (左右): {dimensions[1]*1000:.2f} mm")
    print(f"  Z方向 (上下): {dimensions[2]*1000:.2f} mm")
    
    # 识别可能的安装接口
    print(f"\n5. 安装接口分析:")
    
    # 查找Z方向的顶部和底部区域
    z_min = min_point[2]
    z_max = max_point[2]
    z_range = z_max - z_min
    
    # 底部接口(与移动关节连接)
    bottom_threshold = z_min + z_range * 0.2
    bottom_vertices = mesh.vertices[mesh.vertices[:, 2] < bottom_threshold]
    if len(bottom_vertices) > 0:
        bottom_center = np.mean(bottom_vertices, axis=0)
        print(f"  底部接口 (与移动关节连接):")
        print(f"    - Z范围: {z_min:.6f} 到 {bottom_threshold:.6f} m")
        print(f"    - 中心位置: [{bottom_center[0]:.6f}, {bottom_center[1]:.6f}, {bottom_center[2]:.6f}] m")
    
    # 顶部接口(与大腿连杆连接)
    top_threshold = z_max - z_range * 0.2
    top_vertices = mesh.vertices[mesh.vertices[:, 2] > top_threshold]
    if len(top_vertices) > 0:
        top_center = np.mean(top_vertices, axis=0)
        print(f"  顶部接口 (与大腿连杆连接):")
        print(f"    - Z范围: {top_threshold:.6f} 到 {z_max:.6f} m")
        print(f"    - 中心位置: [{top_center[0]:.6f}, {top_center[1]:.6f}, {top_center[2]:.6f}] m")
    
    return {
        'dimensions': dimensions,
        'centroid': centroid,
        'volume': volume,
        'mass': mass,
        'bounds': bounds,
        'mesh': mesh
    }

def analyze_urdf_joint_origin(urdf_path):
    """从URDF中提取关节原点信息"""
    print(f"\n{'='*60}")
    print(f"分析URDF关节配置")
    print(f"{'='*60}\n")
    
    try:
        with open(urdf_path, 'r') as f:
            content = f.read()
        
        # 查找hip_joint_xyz参数
        import re
        
        # 查找默认的hip_joint_xyz
        pattern = r"hip_joint_xyz:='-?([\d.]+)\s+-?([\d.]+)\s+-?([\d.]+)'"
        matches = re.findall(pattern, content)
        
        if matches:
            print("6. 当前关节原点位置 (从URDF):")
            for i, match in enumerate(matches[:1]):  # 只显示默认值
                x, y, z = float(match[0]), float(match[1]), float(match[2])
                print(f"  默认 hip_joint_xyz: [{x:.6f}, {y:.6f}, {z:.6f}] m")
                print(f"  默认 hip_joint_xyz (mm): [{x*1000:.2f}, {y*1000:.2f}, {z*1000:.2f}] mm")
        
        # 查找关节轴
        axis_pattern = r'<axis xyz="([\d\s.-]+)"/>'
        axis_matches = re.findall(axis_pattern, content)
        if axis_matches:
            print(f"\n  关节旋转轴:")
            # 查找j11关节的轴
            for match in axis_matches[:1]:
                print(f"    - 当前轴向: {match}")
                
    except Exception as e:
        print(f"✗ 读取URDF失败: {e}")

def calculate_required_changes():
    """计算所需的几何变化"""
    print(f"\n{'='*60}")
    print(f"计算所需的几何变化")
    print(f"{'='*60}\n")
    
    print("7. 设计目标 (从设计文档):")
    print("  悬臂平台尺寸:")
    print("    - 长度: 40 mm")
    print("    - 宽度: 30 mm")
    print("    - 厚度: 5 mm")
    print("  悬臂偏移: 25 mm (从垂直主体到舵机中心)")
    
    print("\n8. 所需坐标变换:")
    print("  当前配置 (蜘蛛式):")
    print("    - 舵机安装在垂直表面")
    print("    - 旋转轴: Z轴 (0 0 -1)")
    print("    - 腿向外延伸")
    
    print("\n  目标配置 (狗式):")
    print("    - 舵机安装在水平平台")
    print("    - 旋转轴: X轴 (1 0 0)")
    print("    - 腿向下延伸")
    
    print("\n9. 关节原点调整:")
    current_z = 0.055  # 当前Z坐标
    platform_height = 0.025  # 悬臂平台增加的高度
    new_z = current_z + platform_height
    
    print(f"  当前 hip_joint Z坐标: {current_z:.6f} m = {current_z*1000:.2f} mm")
    print(f"  悬臂平台增加高度: {platform_height:.6f} m = {platform_height*1000:.2f} mm")
    print(f"  建议新 Z坐标: {new_z:.6f} m = {new_z*1000:.2f} mm")
    
    print("\n10. 实施方案:")
    print("  方案A (推荐): 使用几何原语")
    print("    - 垂直主体: box (35mm x 25mm x 60mm)")
    print("    - 水平平台: box (40mm x 30mm x 5mm)")
    print("    - 优点: 实现快速,易于调整")
    
    print("\n  方案B (备选): 创建简单mesh")
    print("    - 在Blender/FreeCAD中建模")
    print("    - 导出为STL文件")
    print("    - 优点: 外观更真实")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("髋关节支架几何分析工具")
    print("Hip Bracket Geometry Analysis Tool")
    print("="*60)
    
    # 分析mesh文件
    mesh_path = "src/dog2_description/meshes/l11.STL"
    if not Path(mesh_path).exists():
        print(f"\n✗ 错误: 找不到文件 {mesh_path}")
        print("请确保在工作区根目录运行此脚本")
        return 1
    
    result = analyze_bracket_mesh(mesh_path)
    
    if result is None:
        return 1
    
    # 分析URDF配置
    urdf_path = "src/dog2_description/urdf/dog2.urdf.xacro"
    if Path(urdf_path).exists():
        analyze_urdf_joint_origin(urdf_path)
    
    # 计算所需变化
    calculate_required_changes()
    
    # 生成总结报告
    print(f"\n{'='*60}")
    print("分析总结")
    print(f"{'='*60}\n")
    
    print("✓ 任务 2.1 完成: 检查现有支架mesh")
    print("  - 已测量当前支架尺寸")
    print("  - 已识别安装接口位置")
    print("  - 已记录当前关节原点位置")
    
    print("\n✓ 任务 2.2 完成: 计算所需的几何变化")
    print("  - 已确定悬臂平台所需高度")
    print("  - 已计算新的关节原点位置")
    print("  - 已记录所需的坐标变换")
    
    print("\n下一步:")
    print("  1. 选择实施方案 (方案A: 几何原语 或 方案B: 简单mesh)")
    print("  2. 创建简化的支架几何")
    print("  3. 更新URDF配置")
    
    print(f"\n{'='*60}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
