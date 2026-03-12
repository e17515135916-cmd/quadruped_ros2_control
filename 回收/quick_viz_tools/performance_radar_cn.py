#!/usr/bin/env python3
"""
性能对比雷达图生成器（亮色系+中文）
Performance Radar Chart Generator (Bright Colors + Chinese)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_performance_radar(output_path='../presentation_outputs/performance_radar_cn.png'):
    """生成性能对比雷达图"""
    
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'), 
                          facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    
    # 性能指标（6个维度）
    categories = ['工作空间\n扩展', '运动\n灵活性', '控制\n精度', 
                 '能量\n效率', '结构\n紧凑性', '越障\n能力']
    N = len(categories)
    
    # 角度
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    # 数据：本方案 vs 传统方案
    our_scores = [95, 90, 92, 85, 88, 93]  # 本方案（4-DOF导轨腿）
    traditional_scores = [60, 70, 75, 80, 85, 65]  # 传统方案（3-DOF固定腿）
    
    our_scores += our_scores[:1]
    traditional_scores += traditional_scores[:1]
    
    # 绘制雷达图
    # 本方案（亮蓝色）
    ax.plot(angles, our_scores, 'o-', linewidth=3, 
           color='#2196F3', label='本方案（4-DOF导轨腿）', markersize=10)
    ax.fill(angles, our_scores, alpha=0.25, color='#2196F3')
    
    # 传统方案（亮橙色）
    ax.plot(angles, traditional_scores, 's-', linewidth=3,
           color='#FF9800', label='传统方案（3-DOF固定腿）', markersize=10)
    ax.fill(angles, traditional_scores, alpha=0.25, color='#FF9800')
    
    # 设置刻度标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=14, weight='bold', color='#333333')
    
    # 设置径向刻度
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=11, color='#666666')
    ax.set_rlabel_position(30)
    
    # 网格线
    ax.grid(True, linestyle='--', linewidth=1.5, color='#CCCCCC', alpha=0.7)
    
    # 添加性能分数标注
    for angle, score, label in zip(angles[:-1], our_scores[:-1], categories):
        x = angle
        y = score + 5
        ax.text(x, y, f'{score}', fontsize=11, weight='bold',
               ha='center', va='center', color='#2196F3',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor='#2196F3', linewidth=2))
    
    # 标题
    ax.set_title('性能对比雷达图\nPerformance Comparison Radar Chart', 
                fontsize=20, weight='bold', pad=30, color='#333333')
    
    # 图例
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
             fontsize=13, frameon=True, fancybox=True, shadow=True,
             facecolor='white', edgecolor='#2196F3', framealpha=0.95)
    
    # 添加平均分数对比
    our_avg = np.mean(our_scores[:-1])
    trad_avg = np.mean(traditional_scores[:-1])
    improvement = ((our_avg - trad_avg) / trad_avg) * 100
    
    stats_text = f'平均性能分数\n本方案: {our_avg:.1f}分\n传统方案: {trad_avg:.1f}分\n提升: +{improvement:.1f}%'
    ax.text(0.5, -0.15, stats_text, transform=ax.transAxes,
           fontsize=13, ha='center', weight='bold', color='#333333',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#E3F2FD', 
                    edgecolor='#2196F3', linewidth=2))
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#ffffff', bbox_inches='tight')
    print(f"✅ 性能雷达图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_performance_radar()
