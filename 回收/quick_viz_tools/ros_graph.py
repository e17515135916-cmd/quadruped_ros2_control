#!/usr/bin/env python3
"""
必杀图三：ROS节点通信图 - 展示系统架构

快速生成ROS节点通信图，展示闭环控制架构
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_node(ax, x, y, width, height, label, node_type='core', sublabel=None):
    """
    绘制节点框
    
    Args:
        node_type: 'input', 'core', 'sim', 'sensor'
    """
    colors = {
        'input': '#4CAF50',    # 绿色 - 输入
        'core': '#2196F3',     # 蓝色 - 核心控制
        'sim': '#FF9800',      # 橙色 - 仿真
        'sensor': '#9C27B0'    # 紫色 - 传感器
    }
    
    color = colors.get(node_type, '#00bcd4')
    
    # 绘制圆角矩形
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.02", 
                         facecolor=color, edgecolor='white',
                         linewidth=2, alpha=0.8)
    ax.add_patch(box)
    
    # 添加标签
    ax.text(x, y + 0.01, label, fontsize=13, fontweight='bold',
           ha='center', va='center', color='white')
    
    if sublabel:
        ax.text(x, y - 0.02, sublabel, fontsize=9,
               ha='center', va='center', color='white', style='italic')

def draw_arrow(ax, x1, y1, x2, y2, label, style='solid', color='#00bcd4'):
    """
    绘制连接箭头
    
    Args:
        style: 'solid' (前向) 或 'dashed' (反馈)
    """
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20,
                           linewidth=2, linestyle=style,
                           color=color, alpha=0.8)
    ax.add_patch(arrow)
    
    # 添加标签
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mid_x, mid_y + 0.05, label, fontsize=10,
           ha='center', va='bottom', color=color,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#2b2b2b', 
                    edgecolor=color, linewidth=1))

def plot_ros_graph(output_path='ros_graph.png'):
    """
    生成ROS节点通信图
    """
    print("🚀 开始绘制ROS通信图...")
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='#2b2b2b')
    ax.set_facecolor('#1e1e1e')
    
    # 定义节点位置
    # 输入层
    joystick_pos = (0.2, 0.8)
    fsm_pos = (0.2, 0.5)
    
    # 控制层
    mpc_pos = (0.5, 0.8)
    wbc_pos = (0.5, 0.5)
    gait_pos = (0.5, 0.2)
    
    # 仿真层
    gazebo_pos = (0.8, 0.65)
    
    # 传感器层
    imu_pos = (0.8, 0.35)
    
    # 绘制节点
    print("  绘制节点...")
    draw_node(ax, *joystick_pos, 0.15, 0.08, 'Joystick', 'input', 'User Input')
    draw_node(ax, *fsm_pos, 0.15, 0.08, 'FSM', 'input', '状态机')
    
    draw_node(ax, *mpc_pos, 0.15, 0.08, 'MPC', 'core', 'Model Predictive')
    draw_node(ax, *wbc_pos, 0.15, 0.08, 'WBC', 'core', 'Whole Body Control')
    draw_node(ax, *gait_pos, 0.15, 0.08, 'Gait Planner', 'core', 'Trajectory Gen')
    
    draw_node(ax, *gazebo_pos, 0.15, 0.08, 'Gazebo', 'sim', '仿真')
    draw_node(ax, *imu_pos, 0.15, 0.08, '传感器', 'sensor', 'IMU/Encoders')
    
    # 绘制前向数据流（实线）
    print("  绘制前向数据流...")
    draw_arrow(ax, joystick_pos[0] + 0.08, joystick_pos[1], 
              mpc_pos[0] - 0.08, mpc_pos[1],
              'Target Velocity', 'solid', '#4CAF50')
    
    draw_arrow(ax, fsm_pos[0] + 0.08, fsm_pos[1],
              wbc_pos[0] - 0.08, wbc_pos[1],
              'State Command', 'solid', '#4CAF50')
    
    draw_arrow(ax, mpc_pos[0], mpc_pos[1] - 0.05,
              wbc_pos[0], wbc_pos[1] + 0.05,
              'Foot Forces', 'solid', '#2196F3')
    
    draw_arrow(ax, gait_pos[0], gait_pos[1] + 0.05,
              wbc_pos[0], wbc_pos[1] - 0.05,
              'Foot Positions', 'solid', '#2196F3')
    
    draw_arrow(ax, wbc_pos[0] + 0.08, wbc_pos[1],
              gazebo_pos[0] - 0.08, gazebo_pos[1] + 0.05,
              'Joint Commands', 'solid', '#FF9800')
    
    # 绘制反馈数据流（虚线）
    print("  绘制反馈数据流...")
    draw_arrow(ax, gazebo_pos[0], gazebo_pos[1] - 0.05,
              imu_pos[0], imu_pos[1] + 0.05,
              'Sensor Data', 'dashed', '#9C27B0')
    
    draw_arrow(ax, imu_pos[0] - 0.08, imu_pos[1],
              wbc_pos[0] + 0.08, wbc_pos[1] - 0.1,
              'Joint States', 'dashed', '#9C27B0')
    
    draw_arrow(ax, imu_pos[0] - 0.08, imu_pos[1] + 0.05,
              mpc_pos[0] + 0.08, mpc_pos[1] - 0.1,
              'IMU数据', 'dashed', '#9C27B0')
    
    # 添加标题和说明
    ax.text(0.5, 0.95, 'Dog2 Robot Control Architecture', 
           fontsize=18, fontweight='bold', ha='center', color='white')
    
    ax.text(0.5, 0.05, 'Closed-Loop Control System with MPC + WBC',
           fontsize=12, ha='center', color='#00bcd4', style='italic')
    
    # 添加图例
    legend_elements = [
        mpatches.Patch(facecolor='#4CAF50', edgecolor='white', label='输入节点'),
        mpatches.Patch(facecolor='#2196F3', edgecolor='white', label='控制节点'),
        mpatches.Patch(facecolor='#FF9800', edgecolor='white', label='仿真'),
        mpatches.Patch(facecolor='#9C27B0', edgecolor='white', label='传感器'),
        mpatches.Patch(facecolor='none', edgecolor='#00bcd4', label='前向流'),
        mpatches.Patch(facecolor='none', edgecolor='#9C27B0', 
                      linestyle='--', label='反馈流')
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
    print(f"✅ ROS通信图已保存: {output_path}")
    
    return fig

if __name__ == "__main__":
    print("=" * 60)
    print("必杀图三：ROS节点通信图生成器")
    print("=" * 60)
    
    plot_ros_graph()
    
    print("\n💡 这张图展示了:")
    print("   ✓ 闭环控制架构")
    print("   ✓ MPC + WBC 控制策略")
    print("   ✓ 前向控制流和反馈数据流")
