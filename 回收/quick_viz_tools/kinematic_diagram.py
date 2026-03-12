#!/usr/bin/env python3
"""
运动学简图生成器 - 展示机器人腿部结构和关节配置
Kinematic Diagram Generator - Shows robot leg structure and joint configuration
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import os

def plot_kinematic_diagram(output_path='../presentation_outputs/kinematic_diagram.png'):
    """生成运动学简图"""
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # 腿部参数 (单位: m)
    rail_length = 0.10  # 导轨伸出距离
    l1 = 0.08  # 髋关节到膝关节
    l2 = 0.20  # 大腿长度
    l3 = 0.20  # 小腿长度
    
    # 基准位置
    base_x = 0.5
    base_y = 0.7
    
    # 绘制导轨机构
    rail_start_x = base_x - 0.15
    rail_end_x = base_x + rail_length
    
    # 导轨外壳
    rail_housing = Rectangle((rail_start_x, base_y - 0.02), 0.15, 0.04, 
                             facecolor='#404040', edgecolor='#00bcd4', linewidth=2)
    ax.add_patch(rail_housing)
    
    # 导轨滑块
    rail_slider = Rectangle((base_x - 0.02, base_y - 0.025), rail_length + 0.02, 0.05,
                            facecolor='#606060', edgecolor='#ff9800', linewidth=2)
    ax.add_patch(rail_slider)
    
    # 导轨伸出方向箭头
    arrow = FancyArrowPatch((rail_start_x + 0.075, base_y + 0.08), 
                           (rail_end_x, base_y + 0.08),
                           arrowstyle='->', mutation_scale=30, 
                           color='#ff9800', linewidth=3)
    ax.add_patch(arrow)
    ax.text(rail_start_x + 0.12, base_y + 0.12, r'$d_1$ (Rail Extension)', 
           fontsize=14, color='#ff9800', weight='bold')
    
    # 髋关节位置
    hip_x = rail_end_x
    hip_y = base_y
    
    # 关节角度 (示例姿态)
    theta1 = -30 * np.pi / 180  # 髋关节角度
    theta2 = 60 * np.pi / 180   # 膝关节角度
    theta3 = -90 * np.pi / 180  # 踝关节角度
    
    # 计算关节位置
    # 大腿端点 (膝关节)
    knee_x = hip_x + l2 * np.cos(theta1)
    knee_y = hip_y + l2 * np.sin(theta1)
    
    # 小腿端点 (踝关节)
    ankle_x = knee_x + l3 * np.cos(theta1 + theta2)
    ankle_y = knee_y + l3 * np.sin(theta1 + theta2)
    
    # 足端
    foot_x = ankle_x
    foot_y = ankle_y - 0.05
    
    # 绘制连杆
    # 大腿
    ax.plot([hip_x, knee_x], [hip_y, knee_y], 'o-', 
           color='#00bcd4', linewidth=6, markersize=12, label='Thigh')
    
    # 小腿
    ax.plot([knee_x, ankle_x], [knee_y, ankle_y], 'o-',
           color='#4caf50', linewidth=6, markersize=12, label='Shin')
    
    # 足部
    ax.plot([ankle_x, foot_x], [ankle_y, foot_y], 'o-',
           color='#ff5722', linewidth=5, markersize=10, label='Foot')
    
    # 绘制关节
    # 髋关节
    hip_joint = Circle((hip_x, hip_y), 0.025, color='#ff9800', zorder=5)
    ax.add_patch(hip_joint)
    ax.text(hip_x - 0.08, hip_y + 0.03, '髋关节', 
           fontsize=12, color='#ffffff', weight='bold')
    
    # 膝关节
    knee_joint = Circle((knee_x, knee_y), 0.025, color='#ff9800', zorder=5)
    ax.add_patch(knee_joint)
    ax.text(knee_x + 0.03, knee_y, '膝关节', 
           fontsize=12, color='#ffffff', weight='bold')
    
    # 踝关节
    ankle_joint = Circle((ankle_x, ankle_y), 0.025, color='#ff9800', zorder=5)
    ax.add_patch(ankle_joint)
    ax.text(ankle_x + 0.03, ankle_y, '踝关节', 
           fontsize=12, color='#ffffff', weight='bold')
    
    # 标注角度
    # θ1
    arc1 = plt.Circle((hip_x, hip_y), 0.08, fill=False, 
                     edgecolor='#ffeb3b', linewidth=2, linestyle='--')
    ax.add_patch(arc1)
    ax.text(hip_x + 0.05, hip_y - 0.08, r'$\theta_1$', 
           fontsize=16, color='#ffeb3b', weight='bold')
    
    # θ2
    arc2 = plt.Circle((knee_x, knee_y), 0.06, fill=False,
                     edgecolor='#ffeb3b', linewidth=2, linestyle='--')
    ax.add_patch(arc2)
    ax.text(knee_x - 0.08, knee_y - 0.05, r'$\theta_2$', 
           fontsize=16, color='#ffeb3b', weight='bold')
    
    # θ3
    arc3 = plt.Circle((ankle_x, ankle_y), 0.05, fill=False,
                     edgecolor='#ffeb3b', linewidth=2, linestyle='--')
    ax.add_patch(arc3)
    ax.text(ankle_x - 0.08, ankle_y + 0.02, r'$\theta_3$', 
           fontsize=16, color='#ffeb3b', weight='bold')
    
    # 绘制坐标系
    coord_size = 0.08
    # X轴
    ax.arrow(hip_x, hip_y, coord_size, 0, head_width=0.02, head_length=0.02,
            fc='#f44336', ec='#f44336', linewidth=2)
    ax.text(hip_x + coord_size + 0.02, hip_y, 'X', fontsize=14, 
           color='#f44336', weight='bold')
    
    # Y轴
    ax.arrow(hip_x, hip_y, 0, coord_size, head_width=0.02, head_length=0.02,
            fc='#4caf50', ec='#4caf50', linewidth=2)
    ax.text(hip_x, hip_y + coord_size + 0.02, 'Y', fontsize=14,
           color='#4caf50', weight='bold')
    
    # 标注连杆长度
    mid_thigh_x = (hip_x + knee_x) / 2
    mid_thigh_y = (hip_y + knee_y) / 2
    ax.text(mid_thigh_x - 0.05, mid_thigh_y + 0.05, f'L₂ = {l2*1000:.0f}mm',
           fontsize=11, color='#00bcd4', weight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))
    
    mid_shin_x = (knee_x + ankle_x) / 2
    mid_shin_y = (knee_y + ankle_y) / 2
    ax.text(mid_shin_x + 0.03, mid_shin_y, f'L₃ = {l3*1000:.0f}mm',
           fontsize=11, color='#4caf50', weight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))
    
    # 添加标题和说明
    ax.text(0.5, 0.95, '4-DOF Leg Kinematic Diagram\n四自由度腿部运动学简图',
           fontsize=18, color='#ffffff', weight='bold',
           ha='center', transform=ax.transAxes)
    
    # 添加DOF说明
    dof_text = 'DOF Configuration:\n• d₁: Rail Extension (Prismatic)\n• θ₁: Hip Rotation\n• θ₂: Knee Rotation\n• θ₃: Ankle Rotation'
    ax.text(0.05, 0.15, dof_text, fontsize=11, color='#ffffff',
           transform=ax.transAxes,
           bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.9, pad=0.8))
    
    # 设置坐标轴
    ax.set_xlim(0.2, 0.9)
    ax.set_ylim(0.0, 0.85)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加图例
    ax.legend(loc='upper right', fontsize=11, facecolor='#2a2a2a', 
             edgecolor='#00bcd4', framealpha=0.9)
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
    print(f"✅ 运动学简图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_kinematic_diagram()
