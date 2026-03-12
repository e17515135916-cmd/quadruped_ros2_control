#!/usr/bin/env python3
"""
轨迹对比图生成器 - 展示规划轨迹 vs 实际轨迹
Trajectory Comparison Generator - Shows planned vs actual trajectory
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def plot_trajectory_comparison(output_path='../presentation_outputs/trajectory_comparison.png'):
    """生成轨迹对比图"""
    
    fig = plt.figure(figsize=(16, 10), facecolor='#1a1a1a')
    
    # 时间序列
    t = np.linspace(0, 10, 200)
    
    # 规划轨迹 (理想轨迹)
    x_planned = 0.3 * t / 10
    y_planned = np.zeros_like(t)
    z_planned = 0.3 + 0.05 * np.sin(2 * np.pi * t / 10)
    
    # 实际轨迹 (带噪声和跟踪误差)
    x_actual = x_planned + np.random.normal(0, 0.002, len(t))
    y_actual = y_planned + np.random.normal(0, 0.001, len(t))
    z_actual = z_planned + np.random.normal(0, 0.003, len(t)) + 0.002 * np.sin(5 * np.pi * t / 10)
    
    # 子图1: 3D轨迹对比
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#1a1a1a')
    ax1.plot(x_planned, y_planned, z_planned, 
            color='#00bcd4', linewidth=3, label='Planned', linestyle='--', alpha=0.8)
    ax1.plot(x_actual, y_actual, z_actual,
            color='#ff9800', linewidth=2, label='实际')
    
    # 起点和终点标记
    ax1.scatter([x_planned[0]], [y_planned[0]], [z_planned[0]], 
               color='#4caf50', s=200, marker='o', label='Start', edgecolors='white', linewidths=2)
    ax1.scatter([x_planned[-1]], [y_planned[-1]], [z_planned[-1]],
               color='#f44336', s=200, marker='s', label='End', edgecolors='white', linewidths=2)
    
    ax1.set_xlabel('X (m)', fontsize=11, color='#ffffff', labelpad=10)
    ax1.set_ylabel('Y (m)', fontsize=11, color='#ffffff', labelpad=10)
    ax1.set_zlabel('Z (m)', fontsize=11, color='#ffffff', labelpad=10)
    ax1.set_title('3D Trajectory Comparison\n三维轨迹对比', 
                 fontsize=13, color='#ffffff', weight='bold', pad=15)
    ax1.tick_params(colors='#ffffff')
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.xaxis.pane.set_edgecolor('#404040')
    ax1.yaxis.pane.set_edgecolor('#404040')
    ax1.zaxis.pane.set_edgecolor('#404040')
    ax1.grid(True, alpha=0.2, color='#ffffff')
    ax1.legend(loc='upper left', fontsize=9, facecolor='#2a2a2a', edgecolor='#00bcd4')
    
    # 子图2: X方向位置对比
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#1a1a1a')
    ax2.plot(t, x_planned, color='#00bcd4', linewidth=2.5, 
            linestyle='--', label='Planned X', alpha=0.8)
    ax2.plot(t, x_actual, color='#ff9800', linewidth=2, label='Actual X')
    ax2.fill_between(t, x_planned, x_actual, alpha=0.2, color='#ffeb3b')
    
    ax2.set_xlabel('Time (s)', fontsize=11, color='#ffffff')
    ax2.set_ylabel('X Position (m)', fontsize=11, color='#ffffff')
    ax2.set_title('X-axis Tracking Performance\nX轴跟踪性能', 
                 fontsize=13, color='#ffffff', weight='bold', pad=10)
    ax2.grid(True, alpha=0.2, color='#ffffff')
    ax2.tick_params(colors='#ffffff')
    ax2.legend(loc='upper left', fontsize=9, facecolor='#2a2a2a', edgecolor='#00bcd4')
    
    # 子图3: Z方向位置对比
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#1a1a1a')
    ax3.plot(t, z_planned, color='#00bcd4', linewidth=2.5,
            linestyle='--', label='Planned Z', alpha=0.8)
    ax3.plot(t, z_actual, color='#ff9800', linewidth=2, label='Actual Z')
    ax3.fill_between(t, z_planned, z_actual, alpha=0.2, color='#ffeb3b')
    
    ax3.set_xlabel('Time (s)', fontsize=11, color='#ffffff')
    ax3.set_ylabel('Z Position (m)', fontsize=11, color='#ffffff')
    ax3.set_title('Z-axis Tracking Performance\nZ轴跟踪性能', 
                 fontsize=13, color='#ffffff', weight='bold', pad=10)
    ax3.grid(True, alpha=0.2, color='#ffffff')
    ax3.tick_params(colors='#ffffff')
    ax3.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#00bcd4')
    
    # 子图4: 跟踪误差分析
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#1a1a1a')
    
    # 计算跟踪误差
    error_x = x_actual - x_planned
    error_y = y_actual - y_planned
    error_z = z_actual - z_planned
    error_total = np.sqrt(error_x**2 + error_y**2 + error_z**2)
    
    ax4.plot(t, error_x * 1000, color='#f44336', linewidth=2, label='X Error', alpha=0.7)
    ax4.plot(t, error_y * 1000, color='#4caf50', linewidth=2, label='Y Error', alpha=0.7)
    ax4.plot(t, error_z * 1000, color='#2196f3', linewidth=2, label='Z Error', alpha=0.7)
    ax4.plot(t, error_total * 1000, color='#ff9800', linewidth=3, 
            label='Total Error', linestyle='--')
    
    # 误差限制线
    ax4.axhline(y=5, color='#ffeb3b', linestyle=':', linewidth=2, label='±5mm Limit')
    ax4.axhline(y=-5, color='#ffeb3b', linestyle=':', linewidth=2)
    
    ax4.set_xlabel('Time (s)', fontsize=11, color='#ffffff')
    ax4.set_ylabel('Tracking Error (mm)', fontsize=11, color='#ffffff')
    ax4.set_title('Tracking Error Analysis\n跟踪误差分析', 
                 fontsize=13, color='#ffffff', weight='bold', pad=10)
    ax4.grid(True, alpha=0.2, color='#ffffff')
    ax4.tick_params(colors='#ffffff')
    ax4.legend(loc='upper right', fontsize=9, facecolor='#2a2a2a', edgecolor='#ff9800')
    
    # 添加统计信息
    rmse = np.sqrt(np.mean(error_total**2)) * 1000
    max_error = np.max(error_total) * 1000
    stats_text = f'RMSE: {rmse:.2f}mm\nMax Error: {max_error:.2f}mm'
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
            fontsize=10, color='#ffffff', weight='bold',
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.9, pad=0.5))
    
    # 总标题
    fig.suptitle('Trajectory Tracking Performance Analysis\n轨迹跟踪性能分析',
                fontsize=18, color='#ffffff', weight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
    print(f"✅ 轨迹对比图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_trajectory_comparison()
