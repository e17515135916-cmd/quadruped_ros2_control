#!/usr/bin/env python3
"""
必杀图六：数据曲线图 - 展示控制效果

快速生成专业的数据曲线图，展示机器人运动的稳定性
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def generate_demo_data(duration=10.0, dt=0.01):
    """
    生成演示数据（如果没有真实数据）
    
    模拟机器人穿越窗框的数据
    """
    t = np.arange(0, duration, dt)
    n = len(t)
    
    # 模拟身体高度（穿越时降低）
    body_height = 0.3 * np.ones(n)
    # 在5-7秒时降低高度（穿越窗框）
    crossing_mask = (t >= 5.0) & (t <= 7.0)
    body_height[crossing_mask] -= 0.1 * np.sin(np.pi * (t[crossing_mask] - 5.0) / 2.0)
    body_height += np.random.normal(0, 0.005, n)  # 添加噪声
    
    # 模拟导轨位置（伸出和收回）
    rail_position = np.zeros(n)
    extend_mask = (t >= 4.5) & (t <= 5.5)
    retract_mask = (t >= 7.0) & (t <= 8.0)
    rail_position[extend_mask] = 0.1 * (t[extend_mask] - 4.5)
    rail_position[(t > 5.5) & (t < 7.0)] = 0.1
    rail_position[retract_mask] = 0.1 * (1 - (t[retract_mask] - 7.0))
    rail_position += np.random.normal(0, 0.002, n)
    
    # 模拟前进速度
    velocity = 0.3 * np.ones(n)
    velocity[crossing_mask] *= 0.5  # 穿越时减速
    velocity += np.random.normal(0, 0.02, n)
    
    # 模拟IMU加速度
    imu_az = 9.81 * np.ones(n)
    imu_az += np.random.normal(0, 0.5, n)
    imu_az[crossing_mask] += 2.0 * np.sin(2 * np.pi * (t[crossing_mask] - 5.0))
    
    # 创建DataFrame
    data = pd.DataFrame({
        'timestamp': t,
        'body_height': body_height,
        'rail_position': rail_position,
        'velocity_x': velocity,
        'imu_az': imu_az
    })
    
    return data

def plot_data_curves(csv_path=None, output_path='data_plot.png'):
    """
    生成数据曲线图
    
    Args:
        csv_path: CSV数据文件路径（如果为None，使用演示数据）
        output_path: 输出图像路径
    """
    print("🚀 开始生成数据曲线图...")
    
    # 加载数据
    if csv_path and Path(csv_path).exists():
        print(f"  加载数据: {csv_path}")
        data = pd.read_csv(csv_path)
    else:
        print("  使用演示数据...")
        data = generate_demo_data()
    
    # 创建图形（2x2子图）
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#2b2b2b')
    fig.suptitle('Robot Performance Data: Window Crossing Experiment',
                fontsize=16, fontweight='bold', color='white', y=0.98)
    
    # 设置样式
    for ax in axes.flat:
        ax.set_facecolor('#1e1e1e')
        ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('#404040')
        ax.spines['right'].set_color('#404040')
    
    # 子图1: 身体高度
    print("  绘制身体高度曲线...")
    ax1 = axes[0, 0]
    ax1.plot(data['timestamp'].values, data['body_height'].values, 
            color='#00bcd4', linewidth=2, label='机身高度')
    ax1.axhline(y=0.3, color='#4CAF50', linestyle='--', 
               linewidth=1, alpha=0.5, label='Target Height')
    ax1.set_xlabel('Time (s)', color='white', fontsize=12)
    ax1.set_ylabel('Height (m)', color='white', fontsize=12)
    ax1.set_title('Body Height Stability', color='white', fontsize=13, pad=10)
    ax1.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
    
    # 标注穿越阶段
    ax1.axvspan(5.0, 7.0, alpha=0.2, color='#FF9800', label='Crossing Phase')
    ax1.text(6.0, 0.32, 'Window Crossing', ha='center', 
            color='#FF9800', fontsize=10)
    
    # 子图2: 导轨位置
    print("  绘制导轨位置曲线...")
    ax2 = axes[0, 1]
    ax2.plot(data['timestamp'].values, data['rail_position'].values * 1000,  # 转换为mm
            color='#FF9800', linewidth=2, label='导轨伸缩')
    ax2.fill_between(data['timestamp'].values, 0, data['rail_position'].values * 1000,
                     alpha=0.3, color='#FF9800')
    ax2.set_xlabel('Time (s)', color='white', fontsize=12)
    ax2.set_ylabel('Extension (mm)', color='white', fontsize=12)
    ax2.set_title('Rail Extension Profile', color='white', fontsize=13, pad=10)
    ax2.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
    
    # 子图3: 前进速度
    print("  绘制速度曲线...")
    ax3 = axes[1, 0]
    ax3.plot(data['timestamp'].values, data['velocity_x'].values,
            color='#4CAF50', linewidth=2, label='Forward Velocity')
    ax3.axhline(y=0.3, color='#00bcd4', linestyle='--',
               linewidth=1, alpha=0.5, label='Target Velocity')
    ax3.set_xlabel('Time (s)', color='white', fontsize=12)
    ax3.set_ylabel('Velocity (m/s)', color='white', fontsize=12)
    ax3.set_title('Forward Velocity Control', color='white', fontsize=13, pad=10)
    ax3.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
    
    # 子图4: IMU加速度
    print("  绘制IMU数据...")
    ax4 = axes[1, 1]
    ax4.plot(data['timestamp'].values, data['imu_az'].values,
            color='#9C27B0', linewidth=2, label='Z Acceleration')
    ax4.axhline(y=9.81, color='#00bcd4', linestyle='--',
               linewidth=1, alpha=0.5, label='Gravity')
    ax4.set_xlabel('Time (s)', color='white', fontsize=12)
    ax4.set_ylabel('Acceleration (m/s²)', color='white', fontsize=12)
    ax4.set_title('IMU Z-Axis Acceleration', color='white', fontsize=13, pad=10)
    ax4.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图像
    plt.savefig(output_path, dpi=300, facecolor='#2b2b2b')
    print(f"✅ 数据曲线图已保存: {output_path}")
    
    # 计算统计信息
    print(f"\n📊 数据统计:")
    print(f"  时间范围: {data['timestamp'].min():.2f} - {data['timestamp'].max():.2f} s")
    print(f"  平均身体高度: {data['body_height'].mean():.3f} m")
    print(f"  最大导轨伸出: {data['rail_position'].max() * 1000:.1f} mm")
    print(f"  平均速度: {data['velocity_x'].mean():.3f} m/s")
    
    return fig

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("必杀图六：数据曲线图生成器")
    print("=" * 60)
    
    # 可以通过命令行参数指定CSV文件
    csv_path = None
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    plot_data_curves(csv_path=csv_path)
    
    print("\n💡 提示:")
    print("   - 如果有真实数据CSV，可以运行:")
    print("     python3 data_plot.py your_data.csv")
    print("   - 否则会使用演示数据生成图表")
