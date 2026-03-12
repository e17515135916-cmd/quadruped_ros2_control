#!/usr/bin/env python3
"""
关键帧序列生成器 - 展示穿越窗框的连续动作
Keyframe Sequence Generator - Shows continuous motion of window crossing
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import os

def draw_robot_pose(ax, x, y, rail_ext, leg_angle, body_height, alpha=1.0):
    """绘制机器人姿态"""
    # 身体
    body_width = 0.15
    body_height_val = 0.08
    body = Rectangle((x - body_width/2, y + body_height), 
                     body_width, body_height_val,
                     facecolor='#00bcd4', edgecolor='#ffffff', 
                     linewidth=2, alpha=alpha)
    ax.add_patch(body)
    
    # 导轨 (简化表示)
    rail_color = '#ff9800' if rail_ext > 0.01 else '#606060'
    rail = Rectangle((x - 0.02, y + body_height - 0.02), 
                    0.04, rail_ext + 0.02,
                    facecolor=rail_color, edgecolor='#ffffff',
                    linewidth=1.5, alpha=alpha)
    ax.add_patch(rail)
    
    # 腿部 (简化为两段)
    leg_x = x
    leg_y = y + body_height + rail_ext
    
    l1 = 0.12  # 大腿
    l2 = 0.12  # 小腿
    
    # 大腿
    knee_x = leg_x + l1 * np.sin(leg_angle)
    knee_y = leg_y - l1 * np.cos(leg_angle)
    ax.plot([leg_x, knee_x], [leg_y, knee_y], 
           color='#4caf50', linewidth=4, alpha=alpha)
    
    # 小腿
    foot_x = knee_x + l2 * np.sin(leg_angle * 1.5)
    foot_y = knee_y - l2 * np.cos(leg_angle * 1.5)
    ax.plot([knee_x, foot_x], [knee_y, foot_y],
           color='#8bc34a', linewidth=4, alpha=alpha)
    
    # 足端
    foot = Circle((foot_x, foot_y), 0.015, 
                 color='#ff5722', alpha=alpha)
    ax.add_patch(foot)

def plot_keyframe_sequence(output_path='../presentation_outputs/keyframe_sequence.png'):
    """生成关键帧序列图"""
    
    fig, axes = plt.subplots(1, 5, figsize=(20, 5), facecolor='#1a1a1a')
    
    # 窗框参数
    window_x = 0.5
    window_y = 0.15
    window_width = 0.08
    window_height = 0.35
    
    # 五个关键帧的参数
    keyframes = [
        {'name': 'Approach\n接近', 'x': 0.2, 'rail': 0.0, 'angle': 0.0, 'height': 0.0, 'time': 't=0s'},
        {'name': 'Rail Extend\n导轨伸出', 'x': 0.35, 'rail': 0.08, 'angle': 0.0, 'height': 0.0, 'time': 't=2s'},
        {'name': 'Leg Fold\n腿部折叠', 'x': 0.5, 'rail': 0.08, 'angle': 0.6, 'height': -0.05, 'time': 't=4s'},
        {'name': 'Passing\n穿越中', 'x': 0.65, 'rail': 0.08, 'angle': 0.6, 'height': -0.05, 'time': 't=6s'},
        {'name': 'Recover\n恢复', 'x': 0.8, 'rail': 0.0, 'angle': 0.0, 'height': 0.0, 'time': 't=8s'},
    ]
    
    for idx, (ax, kf) in enumerate(zip(axes, keyframes)):
        ax.set_facecolor('#1a1a1a')
        
        # 绘制地面
        ax.axhline(y=0, color='#404040', linewidth=3, linestyle='-')
        ax.fill_between([0, 1], 0, -0.05, color='#2a2a2a', alpha=0.5)
        
        # 绘制窗框 (只在中间三帧显示)
        if 1 <= idx <= 3:
            # 窗框上边
            ax.add_patch(Rectangle((window_x - 0.02, window_y + window_height), 
                                  window_width + 0.04, 0.03,
                                  facecolor='#757575', edgecolor='#ffffff', linewidth=2))
            # 窗框下边
            ax.add_patch(Rectangle((window_x - 0.02, window_y - 0.03), 
                                  window_width + 0.04, 0.03,
                                  facecolor='#757575', edgecolor='#ffffff', linewidth=2))
            # 窗框左边
            ax.add_patch(Rectangle((window_x - 0.02, window_y), 
                                  0.02, window_height,
                                  facecolor='#757575', edgecolor='#ffffff', linewidth=2))
            # 窗框右边
            ax.add_patch(Rectangle((window_x + window_width, window_y), 
                                  0.02, window_height,
                                  facecolor='#757575', edgecolor='#ffffff', linewidth=2))
            
            # 标注窗框高度
            if idx == 2:
                ax.plot([window_x - 0.05, window_x - 0.05], 
                       [window_y, window_y + window_height],
                       'r--', linewidth=2)
                ax.text(window_x - 0.08, window_y + window_height/2, 
                       f'{window_height*100:.0f}cm',
                       fontsize=10, color='#ff5722', weight='bold', rotation=90,
                       va='center')
        
        # 绘制机器人
        draw_robot_pose(ax, kf['x'], 0, kf['rail'], kf['angle'], kf['height'])
        
        # 添加运动轨迹箭头
        if idx < len(keyframes) - 1:
            next_kf = keyframes[idx + 1]
            ax.annotate('', xy=(next_kf['x'] - 0.08, 0.25), 
                       xytext=(kf['x'] + 0.08, 0.25),
                       arrowprops=dict(arrowstyle='->', lw=3, 
                                     color='#ffeb3b', alpha=0.7))
        
        # 标题和时间
        ax.text(0.5, 0.92, kf['name'], fontsize=14, color='#ffffff',
               weight='bold', ha='center', transform=ax.transAxes)
        ax.text(0.5, 0.05, kf['time'], fontsize=11, color='#00bcd4',
               ha='center', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8))
        
        # 状态指示器
        if idx == 0:
            status = '● Normal'
            color = '#4caf50'
        elif idx == 1:
            status = '● Extending'
            color = '#ff9800'
        elif idx == 2 or idx == 3:
            status = '● Folded'
            color = '#f44336'
        else:
            status = '● Normal'
            color = '#4caf50'
        
        ax.text(0.5, 0.85, status, fontsize=10, color=color,
               ha='center', transform=ax.transAxes, weight='bold')
        
        # 设置坐标轴
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.05, 0.6)
        ax.set_aspect('equal')
        ax.axis('off')
    
    # 总标题
    fig.suptitle('Window Crossing Keyframe Sequence\n窗框穿越关键帧序列', 
                fontsize=20, color='#ffffff', weight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
    print(f"✅ 关键帧序列图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_keyframe_sequence()
