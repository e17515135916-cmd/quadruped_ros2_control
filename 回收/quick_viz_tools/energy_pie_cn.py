#!/usr/bin/env python3
"""
能耗分析饼图生成器（亮色系+中文）
Energy Consumption Pie Chart Generator (Bright Colors + Chinese)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_energy_pie(output_path='../presentation_outputs/energy_pie_cn.png'):
    """生成能耗分析饼图"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), facecolor='#ffffff')
    
    # 数据：各部件能耗占比
    components = ['髋关节', '膝关节', '踝关节', '导轨伸缩', '控制系统']
    
    # 传统方案能耗（总计100W）
    traditional_energy = [28, 32, 18, 0, 22]  # 无导轨
    traditional_total = sum(traditional_energy)
    
    # 本方案能耗（总计95W，更高效）
    our_energy = [25, 28, 16, 12, 14]  # 有导轨但总能耗更低
    our_total = sum(our_energy)
    
    # 亮色系配色
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    explode = (0.05, 0.05, 0.05, 0.1, 0.05)  # 突出导轨
    
    # 子图1：传统方案
    ax1.set_facecolor('#ffffff')
    wedges1, texts1, autotexts1 = ax1.pie(traditional_energy, explode=explode, labels=components,
                                           colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 12, 'weight': 'bold'},
                                           pctdistance=0.85, labeldistance=1.1)
    
    # 美化百分比文字
    for autotext in autotexts1:
        autotext.set_color('white')
        autotext.set_fontsize(13)
        autotext.set_weight('bold')
    
    # 美化标签
    for text in texts1:
        text.set_fontsize(13)
        text.set_weight('bold')
        text.set_color('#333333')
    
    ax1.set_title(f'传统方案能耗分布\n总功耗: {traditional_total}W', 
                 fontsize=16, weight='bold', pad=20, color='#333333')
    
    # 子图2：本方案
    ax2.set_facecolor('#ffffff')
    wedges2, texts2, autotexts2 = ax2.pie(our_energy, explode=explode, labels=components,
                                           colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 12, 'weight': 'bold'},
                                           pctdistance=0.85, labeldistance=1.1)
    
    # 美化百分比文字
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontsize(13)
        autotext.set_weight('bold')
    
    # 美化标签
    for text in texts2:
        text.set_fontsize(13)
        text.set_weight('bold')
        text.set_color('#333333')
    
    ax2.set_title(f'本方案能耗分布\n总功耗: {our_total}W', 
                 fontsize=16, weight='bold', pad=20, color='#333333')
    
    # 总标题
    energy_saving = ((traditional_total - our_total) / traditional_total) * 100
    fig.suptitle(f'能耗对比分析\nEnergy Consumption Comparison\n节能: {energy_saving:.1f}%', 
                fontsize=20, weight='bold', y=0.98, color='#333333')
    
    # 添加图例
    legend_labels = [f'{comp}: {trad}W → {our}W' 
                    for comp, trad, our in zip(components, traditional_energy, our_energy)]
    fig.legend(legend_labels, loc='lower center', ncol=3, 
              fontsize=11, frameon=True, fancybox=True, shadow=True,
              bbox_to_anchor=(0.5, -0.05), facecolor='white', 
              edgecolor='#4ECDC4', framealpha=0.95)
    
    # 添加说明文字
    note_text = '注：导轨伸缩机构虽增加12W功耗，但通过优化控制算法，\n整体功耗降低5W，节能5%'
    fig.text(0.5, 0.02, note_text, ha='center', fontsize=11, 
            style='italic', color='#666666',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', 
                     edgecolor='#FFA07A', linewidth=2, alpha=0.8))
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    
    # 保存图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#ffffff', bbox_inches='tight')
    print(f"✅ 能耗饼图已保存: {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_energy_pie()
