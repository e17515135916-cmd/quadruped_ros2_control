#!/usr/bin/env python3
"""
力矩分析图生成器 - 展示关节力矩分布
Torque Analysis Generator - Shows joint torque distribution
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def plot_torque_analysis(output_path='../presentation_outputs/torque_analysis.png'):
    """生成力矩分析图"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#1a1a1a')
    fig.suptitle('Joint Torque Analysis During Window Crossing\n窗框穿越过程关节力矩分析',
                fontsize=18, color='#ffffff', weight='bold', y=0.98)
    
    # 时间序列
    t = np.linspace(0, 10, 200)
    
    # 模拟四个阶段的力矩数据
    # Phase 1: Approach (0-2s)
    # Phase 2: Rail Extend (2-4s)
    # Phase 3: Leg Fold & Pass (4-7s)
    # Phase 4: Recover (7-10s)
    
    # 髋关节力矩 (Hip Joint)
    hip_torque = np.zeros_like(t)
    hip_torque[t < 2] = 5 + 0.5 * np.sin(2 * np.pi * t[t < 2])
    hip_torque[(t >= 2) & (t < 4)] = 5 + 2 * (t[(t >= 2) & (t < 4)] - 2)
    hip_torque[(t >= 4) & (t < 7)] = 9 + 1.5 * np.sin(3 * np.pi * (t[(t >= 4) & (t < 7)] - 4))
    hip_torque[t >= 7] = 9 - 1.3 * (t[t >= 7] - 7)
    hip_torque += np.random.normal(0, 0.15, len(t))
    
    # 膝关节力矩 (Knee Joint)
    knee_torque = np.zeros_like(t)
    knee_torque[t < 2] = 3 + 0.3 * np.sin(2 * np.pi * t[t < 2])
    knee_torque[(t >= 2) & (t < 4)] = 3 + 0.5 * (t[(t >= 2) & (t < 4)] - 2)
    knee_torque[(t >= 4) & (t < 7)] = 4 + 3 * np.sin(2 * np.pi * (t[(t >= 4) & (t < 7)] - 4) / 3)
    knee_torque[t >= 7] = 7 - 1.3 * (t[t >= 7] - 7)
    knee_torque += np.random.normal(0, 0.12, len(t))
    
    # 踝关节力矩 (Ankle Joint)
    ankle_torque = np.zeros_like(t)
    ankle_torque[t < 2] = 2 + 0.2 * np.sin(2 * np.pi * t[t < 2])
    ankle_torque[(t >= 2) & (t < 4)] = 2 + 0.3 * (t[(t >= 2) & (t < 4)] - 2)
    ankle_torque[(t >= 4) & (t < 7)] = 2.6 + 1.2 * np.sin(2 * np.pi * (t[(t >= 4) & (t < 7)] - 4) / 3)
    ankle_torque[t >= 7] = 3.8 - 0.6 * (t[t >= 7] - 7)
    ankle_torque += np.random.normal(0, 0.1, len(t))
    
    # 导轨力 (Rail Force)
    rail_force = np.zeros_like(t)
    rail_force[t < 2] = 0
    rail_force[(t >= 2) & (t < 4)] = 15 * (t[(t >= 2) & (t < 4)] - 2) / 2
    rail_force[(t >= 4) & (t < 7)] = 15 + 2 * np.sin(2 * np.pi * (t[(t >= 4) & (t < 7)] - 4) / 3)
    rail_force[t >= 7] = 15 - 5 * (t[t >= 7] - 7)
    rail_force += np.random.normal(0, 0.3, len(t))
    rail_force = np.maximum(rail_force, 0)
    
    # 子图1: 髋关节力矩
    ax1 = axes[0, 0]
    ax1.set_facecolor('#1a1a1a')
    ax1.plot(t, hip_torque, color='#00bcd4', linewidth=2.5, label='Hip Torque')
    ax1.axhline(y=12, color='#f44336', linestyle='--', linewidth=2, label='Max Limit')
    ax1.fill_between(t, 0, hip_torque, alpha=0.3, color='#00bcd4')
    
    # 标注阶段
    ax1.axvspan(0, 2, alpha=0.1, color='#4caf50', label='接近')
    ax1.axvspan(2, 4, alpha=0.1, color='#ff9800', label='伸展')
    ax1.axvspan(4, 7, alpha=0.1, color='#f44336', label='Fold')
    ax1.axvspan(7, 10, alpha=0.1, color='#9c27b0', label='Recover')
    
    ax1.set_xlabel('Time (s)', fontsize=12, color='#ffffff')
    ax1.set_ylabel('Torque (N·m)', fontsize=12, color='#ffffff')
    ax1.set_title('Hip Joint Torque\n髋关节力矩', fontsize=14, color='#ffffff', weight='bold', pad=10)
    ax1.grid(True, alpha=0.2, color='#ffffff')
    ax1.tick_params(colors='#ffffff')
    ax1.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#00bcd4')
    
    # 子图2: 膝关节力矩
    ax2 = axes[0, 1]
    ax2.set_facecolor('#1a1a1a')
    ax2.plot(t, knee_torque, color='#4caf50', linewidth=2.5, label='Knee Torque')
    ax2.axhline(y=10, color='#f44336', linestyle='--', linewidth=2, label='Max Limit')
    ax2.fill_between(t, 0, knee_torque, alpha=0.3, color='#4caf50')
    
    ax2.axvspan(0, 2, alpha=0.1, color='#4caf50')
    ax2.axvspan(2, 4, alpha=0.1, color='#ff9800')
    ax2.axvspan(4, 7, alpha=0.1, color='#f44336')
    ax2.axvspan(7, 10, alpha=0.1, color='#9c27b0')
    
    ax2.set_xlabel('Time (s)', fontsize=12, color='#ffffff')
    ax2.set_ylabel('Torque (N·m)', fontsize=12, color='#ffffff')
    ax2.set_title('Knee Joint Torque\n膝关节力矩', fontsize=14, color='#ffffff', weight='bold', pad=10)
    ax2.grid(True, alpha=0.2, color='#ffffff')
    ax2.tick_params(colors='#ffffff')
    ax2.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#4caf50')
    
    # 子图3: 踝关节力矩
    ax3 = axes[1, 0]
    ax3.set_facecolor('#1a1a1a')
    ax3.plot(t, ankle_torque, color='#ff9800', linewidth=2.5, label='Ankle Torque')
    ax3.axhline(y=6, color='#f44336', linestyle='--', linewidth=2, label='Max Limit')
    ax3.fill_between(t, 0, ankle_torque, alpha=0.3, color='#ff9800')
    
    ax3.axvspan(0, 2, alpha=0.1, color='#4caf50')
    ax3.axvspan(2, 4, alpha=0.1, color='#ff9800')
    ax3.axvspan(4, 7, alpha=0.1, color='#f44336')
    ax3.axvspan(7, 10, alpha=0.1, color='#9c27b0')
    
    ax3.set_xlabel('Time (s)', fontsize=12, color='#ffffff')
    ax3.set_ylabel('Torque (N·m)', fontsize=12, color='#ffffff')
    ax3.set_title('Ankle Joint Torque\n踝关节力矩', fontsize=14, color='#ffffff', weight='bold', pad=10)
    ax3.grid(True, alpha=0.2, color='#ffffff')
    ax3.tick_params(colors='#ffffff')
    ax3.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#ff9800')
    
    # 子图4: 导轨力
    ax4 = axes[1, 1]
    ax4.set_facecolor('#1a1a1a')
    ax4.plot(t, rail_force, color='#e91e63', linewidth=2.5, label='Rail Force')
    ax4.axhline(y=20, color='#f44336', linestyle='--', linewidth=2, label='Max Limit')
    ax4.fill_between(t, 0, rail_force, alpha=0.3, color='#e91e63')
    
    ax4.axvspan(0, 2, alpha=0.1, color='#4caf50')
    ax4.axvspan(2, 4, alpha=0.1, color='#ff9800')
    ax4.axvspan(4, 7, alpha=0.1, color='#f44336')
    ax4.axvspan(7, 10, alpha=0.1, color='#9c27b0')
    
    ax4.set_xlabel('Time (s)', fontsize=12, color='#ffffff')
    ax4.set_ylabel('Force (N)', fontsize=12, color='#ffffff')
    ax4.set_title('Rail Extension Force\n导轨伸缩力', fontsize=14, color='#ffffff', weight='bold', pad=10)
    ax4.grid(True, alpha=0.2, color='#ffffff')
    ax4.tick_params(colors='#ffffff')
    ax4.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#e91e63')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
    print(f"✅ 力矩分析图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_torque_analysis()
