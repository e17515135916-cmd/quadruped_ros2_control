#!/usr/bin/env python3
"""
必杀图二：工作空间对比图 - 证明导轨有用！

快速生成工作空间对比图，展示导轨扩展前后的差异
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def forward_kinematics_3dof(theta1, theta2, theta3, l1=0.08, l2=0.213, l3=0.213):
    """
    3-DOF腿部正运动学（髋关节旋转 + 大腿 + 小腿）
    返回足端位置 (x, z)
    """
    # 髋关节旋转后的位置
    x1 = 0
    z1 = 0
    
    # 大腿末端
    x2 = x1 + l2 * np.sin(theta2)
    z2 = z1 - l2 * np.cos(theta2)
    
    # 小腿末端（足端）
    x3 = x2 + l3 * np.sin(theta2 + theta3)
    z3 = z2 - l3 * np.cos(theta2 + theta3)
    
    return x3, z3

def compute_workspace(rail_extension=0.0, resolution=50):
    """
    计算工作空间点云
    
    Args:
        rail_extension: 导轨伸出距离（米）
        resolution: 采样分辨率
    
    Returns:
        points: Nx2 数组，工作空间点云
    """
    # 关节限位（根据Dog2实际参数）
    theta1_range = np.linspace(-0.5, 0.5, resolution)  # 髋关节旋转
    theta2_range = np.linspace(-1.0, 1.5, resolution)  # 大腿关节
    theta3_range = np.linspace(-2.5, -0.5, resolution)  # 小腿关节
    
    points = []
    
    for theta1 in theta1_range:
        for theta2 in theta2_range:
            for theta3 in theta3_range:
                x, z = forward_kinematics_3dof(theta1, theta2, theta3)
                # 加上导轨扩展
                x += rail_extension
                points.append([x, z])
    
    return np.array(points)

def plot_workspace_comparison(rail_extension=0.1, output_path='workspace_comparison.png'):
    """
    生成工作空间对比图
    
    Args:
        rail_extension: 导轨伸出距离（米）
        output_path: 输出文件路径
    """
    print("🚀 开始计算工作空间...")
    
    # 计算普通工作空间
    print("  计算普通工作空间...")
    normal_points = compute_workspace(rail_extension=0.0, resolution=30)
    
    # 计算扩展工作空间
    print("  计算扩展工作空间...")
    extended_points = compute_workspace(rail_extension=rail_extension, resolution=30)
    
    # 计算凸包边界
    print("  计算凸包边界...")
    normal_hull = ConvexHull(normal_points)
    extended_hull = ConvexHull(extended_points)
    
    # 创建图形
    print("🎨 绘制对比图...")
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#2b2b2b')
    ax.set_facecolor('#1e1e1e')
    
    # 绘制普通工作空间（蓝色）
    normal_boundary = normal_points[normal_hull.vertices]
    poly_normal = Polygon(normal_boundary, alpha=0.3, facecolor='#00bcd4', 
                         edgecolor='#00bcd4', linewidth=2, label='普通工作空间')
    ax.add_patch(poly_normal)
    
    # 绘制扩展工作空间（橙色）
    extended_boundary = extended_points[extended_hull.vertices]
    poly_extended = Polygon(extended_boundary, alpha=0.3, facecolor='#ff9800',
                           edgecolor='#ff9800', linewidth=2, label='扩展工作空间')
    ax.add_patch(poly_extended)
    
    # 标注扩展区域
    ax.annotate(f'扩展区域\n(导轨优势)', 
                xy=(0.15, -0.3), fontsize=14, color='#ff9800',
                ha='center')
    
    # 添加导轨示意
    ax.arrow(0, 0.05, rail_extension, 0, head_width=0.02, head_length=0.01,
            fc='#ff9800', ec='#ff9800', linewidth=2)
    ax.text(rail_extension/2, 0.08, f'导轨伸缩\n{rail_extension*1000:.0f}mm',
           fontsize=12, color='#ff9800', ha='center')
    
    # 设置坐标轴
    ax.set_xlabel('X 位置 (m)', fontsize=14, color='white')
    ax.set_ylabel('Z 位置 (m)', fontsize=14, color='white')
    ax.set_title('工作空间对比：普通 vs 扩展', 
                fontsize=16, color='white', pad=20)
    
    # 设置网格
    ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
    ax.tick_params(colors='white')
    
    # 图例
    ax.legend(fontsize=12, loc='upper right', facecolor='#2b2b2b', 
             edgecolor='white', labelcolor='white')
    
    # 设置坐标轴范围
    ax.set_xlim(-0.1, 0.5)
    ax.set_ylim(-0.5, 0.1)
    ax.set_aspect('equal')
    
    # 保存图像
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='#2b2b2b')
    print(f"✅ 工作空间对比图已保存: {output_path}")
    
    # 计算并显示统计信息
    normal_area = normal_hull.volume
    extended_area = extended_hull.volume
    increase_percent = (extended_area - normal_area) / normal_area * 100
    
    print(f"\n📊 工作空间统计:")
    print(f"  普通工作空间面积: {normal_area:.4f} m²")
    print(f"  扩展工作空间面积: {extended_area:.4f} m²")
    print(f"  面积增加: {increase_percent:.1f}%")
    print(f"  导轨扩展距离: {rail_extension*1000:.0f} mm")
    
    return fig

if __name__ == "__main__":
    import sys
    
    # 可以通过命令行参数指定导轨扩展距离
    rail_extension = 0.1  # 默认100mm
    if len(sys.argv) > 1:
        rail_extension = float(sys.argv[1])
    
    print("=" * 60)
    print("必杀图二：工作空间对比图生成器")
    print("=" * 60)
    
    plot_workspace_comparison(rail_extension=rail_extension)
    
    print("\n💡 提示: 可以用不同的导轨扩展距离运行:")
    print("   python3 workspace_comparison.py 0.15  # 150mm扩展")
