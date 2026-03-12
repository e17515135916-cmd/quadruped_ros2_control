#!/usr/bin/env python3
"""
必杀图四：状态机流转图 - 展示穿越窗框策略

快速生成状态机气泡图，展示机器人穿越窗框的控制策略
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_state(ax, x, y, radius, label, description, color='#2196F3'):
    """绘制状态圆圈"""
    circle = Circle((x, y), radius, facecolor=color, edgecolor='white',
                   linewidth=3, alpha=0.8)
    ax.add_patch(circle)
    
    # 状态名称
    ax.text(x, y + 0.02, label, fontsize=14, fontweight='bold',
           ha='center', va='center', color='white')
    
    # 状态描述
    ax.text(x, y - 0.02, description, fontsize=10,
           ha='center', va='center', color='white', style='italic')

def draw_transition(ax, x1, y1, x2, y2, label, curved=False):
    """绘制状态转换箭头"""
    if curved:
        # 曲线箭头
        connectionstyle = "arc3,rad=0.3"
    else:
        connectionstyle = "arc3,rad=0"
    
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=25,
                           linewidth=2.5, color='#00bcd4',
                           connectionstyle=connectionstyle,
                           alpha=0.9)
    ax.add_patch(arrow)
    
    # 转换条件标签
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    if curved:
        mid_y += 0.08  # 曲线箭头的标签位置调整
    
    ax.text(mid_x, mid_y, label, fontsize=9,
           ha='center', va='bottom', color='#00bcd4',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#2b2b2b',
                    edgecolor='#00bcd4', linewidth=1.5))

def draw_robot_icon(ax, x, y, size, pose='normal'):
    """绘制简化的机器人姿态图标"""
    if pose == 'normal':
        # 正常站立姿态
        body = Rectangle((x - size/2, y - size/4), size, size/2,
                        facecolor='#FF9800', edgecolor='white', linewidth=1)
        ax.add_patch(body)
        # 腿
        for leg_x in [x - size/3, x + size/3]:
            ax.plot([leg_x, leg_x], [y - size/4, y - size/2],
                   'w-', linewidth=2)
    
    elif pose == 'extended':
        # 导轨伸出姿态
        body = Rectangle((x - size/2, y - size/4), size, size/2,
                        facecolor='#FF9800', edgecolor='white', linewidth=1)
        ax.add_patch(body)
        # 前腿伸出
        ax.plot([x - size/3, x - size/2], [y - size/4, y - size/2],
               'w-', linewidth=2)
        ax.plot([x + size/3, x + size/3], [y - size/4, y - size/2],
               'w-', linewidth=2)
    
    elif pose == 'folded':
        # 折叠姿态
        body = Rectangle((x - size/2, y - size/4), size, size/2,
                        facecolor='#FF9800', edgecolor='white', linewidth=1)
        ax.add_patch(body)
        # 腿折叠
        for leg_x in [x - size/3, x + size/3]:
            ax.plot([leg_x, leg_x - size/6], [y - size/4, y - size/3],
                   'w-', linewidth=2)

def plot_fsm_diagram(output_path='fsm_diagram.png'):
    """
    生成状态机流转图
    """
    print("🚀 开始绘制状态机流转图...")
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#2b2b2b')
    ax.set_facecolor('#1e1e1e')
    
    # 定义状态位置（圆形布局）
    center_x, center_y = 0.5, 0.5
    radius_layout = 0.25
    
    # 4个状态的位置
    angles = [90, 0, 270, 180]  # 度数
    states = [
        ('接近', 'Normal Walking', '#4CAF50', 'normal'),
        ('Rail_Extend', '导轨伸缩', '#2196F3', 'extended'),
        ('Leg_Fold', 'Folding Through', '#FF9800', 'folded'),
        ('Recover', 'Posture Recovery', '#9C27B0', 'normal')
    ]
    
    state_positions = []
    
    print("  绘制状态节点...")
    for i, (name, desc, color, pose) in enumerate(states):
        angle_rad = np.radians(angles[i])
        x = center_x + radius_layout * np.cos(angle_rad)
        y = center_y + radius_layout * np.sin(angle_rad)
        state_positions.append((x, y))
        
        # 绘制状态圆圈
        draw_state(ax, x, y, 0.08, name, desc, color)
        
        # 绘制机器人姿态图标
        icon_offset = 0.15
        icon_x = center_x + (radius_layout + icon_offset) * np.cos(angle_rad)
        icon_y = center_y + (radius_layout + icon_offset) * np.sin(angle_rad)
        draw_robot_icon(ax, icon_x, icon_y, 0.06, pose)
    
    # 绘制状态转换
    print("  绘制状态转换...")
    transitions = [
        (0, 1, 'Detect Obstacle'),
        (1, 2, 'Rail Ready'),
        (2, 3, 'Body Through'),
        (3, 0, '完成')
    ]
    
    for i, (from_idx, to_idx, label) in enumerate(transitions):
        x1, y1 = state_positions[from_idx]
        x2, y2 = state_positions[to_idx]
        
        # 调整箭头起点和终点（避免与圆圈重叠）
        angle = np.arctan2(y2 - y1, x2 - x1)
        x1_adj = x1 + 0.08 * np.cos(angle)
        y1_adj = y1 + 0.08 * np.sin(angle)
        x2_adj = x2 - 0.08 * np.cos(angle)
        y2_adj = y2 - 0.08 * np.sin(angle)
        
        draw_transition(ax, x1_adj, y1_adj, x2_adj, y2_adj, label)
    
    # 添加中心标题
    ax.text(center_x, center_y, 'Window\nCrossing\nFSM',
           fontsize=16, fontweight='bold', ha='center', va='center',
           color='#00bcd4',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#2b2b2b',
                    edgecolor='#00bcd4', linewidth=2))
    
    # 添加标题
    ax.text(0.5, 0.95, 'Finite State Machine: Window Crossing Strategy',
           fontsize=18, fontweight='bold', ha='center', color='white')
    
    # 添加说明
    ax.text(0.5, 0.05, 'Rail-Assisted Obstacle Traversal Control',
           fontsize=12, ha='center', color='#00bcd4', style='italic')
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4CAF50', edgecolor='white', label='Approach Phase'),
        Patch(facecolor='#2196F3', edgecolor='white', label='Extension Phase'),
        Patch(facecolor='#FF9800', edgecolor='white', label='Crossing Phase'),
        Patch(facecolor='#9C27B0', edgecolor='white', label='Recovery Phase')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10,
             facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
    
    # 设置坐标轴
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # 保存图像
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='#2b2b2b', bbox_inches='tight')
    print(f"✅ 状态机流转图已保存: {output_path}")
    
    return fig

if __name__ == "__main__":
    print("=" * 60)
    print("必杀图四：状态机流转图生成器")
    print("=" * 60)
    
    plot_fsm_diagram()
    
    print("\n💡 这张图展示了:")
    print("   ✓ 4个关键状态")
    print("   ✓ 状态转换条件")
    print("   ✓ 机器人姿态变化")
    print("   ✓ 穿越窗框的完整策略")
