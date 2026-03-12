#!/usr/bin/env python3
"""
批量中文化脚本
将所有深色系图表的英文改成中文
"""

import re
import os

# 英文到中文的映射字典
TRANSLATIONS = {
    # 通用术语
    "Normal Workspace": "普通工作空间",
    "Extended Workspace": "扩展工作空间",
    "Extended Area": "扩展区域",
    "Rail Advantage": "导轨优势",
    "Rail Extension": "导轨伸缩",
    "X Position": "X 位置",
    "Y Position": "Y 位置",
    "Z Position": "Z 位置",
    "Time": "时间",
    "Workspace Comparison": "工作空间对比",
    
    # ROS图相关
    "Input Nodes": "输入节点",
    "Control Nodes": "控制节点",
    "Simulation": "仿真",
    "Sensors": "传感器",
    "Forward Flow": "前向流",
    "Feedback Flow": "反馈流",
    "ROS Node Communication": "ROS节点通信",
    
    # 状态机相关
    "State Machine": "状态机",
    "Initial": "初始",
    "Approach": "接近",
    "Extend": "伸展",
    "Cross": "穿越",
    "Retract": "收缩",
    "Complete": "完成",
    
    # 数据图相关
    "Body Height": "机身高度",
    "Rail Position": "导轨位置",
    "Velocity": "速度",
    "IMU Data": "IMU数据",
    "Linear": "线性",
    "Angular": "角度",
    
    # 运动学相关
    "Hip Joint": "髋关节",
    "Knee Joint": "膝关节",
    "Ankle Joint": "踝关节",
    "Rail": "导轨",
    "Kinematic Diagram": "运动学简图",
    
    # 力矩相关
    "Torque": "力矩",
    "Analysis": "分析",
    "Joint Torque": "关节力矩",
    
    # 轨迹相关
    "Trajectory": "轨迹",
    "Comparison": "对比",
    "Desired": "期望",
    "Actual": "实际",
    "Error": "误差",
    "RMSE": "均方根误差",
}

def localize_file(filepath):
    """
    将文件中的英文替换为中文
    """
    print(f"处理文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换字体配置
    content = re.sub(
        r"plt\.rcParams\['font\.sans-serif'\] = \[.*?\]",
        "plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'AR PL UKai CN', 'DejaVu Sans']",
        content
    )
    
    # 替换英文文本
    for en, zh in TRANSLATIONS.items():
        # 替换字符串中的文本
        content = content.replace(f'"{en}"', f'"{zh}"')
        content = content.replace(f"'{en}'", f"'{zh}'")
    
    # 保存修改后的文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 完成: {filepath}")

def main():
    """
    批量处理所有深色系图表文件
    """
    files_to_process = [
        'workspace_comparison.py',
        'ros_graph.py',
        'fsm_diagram.py',
        'data_plot.py',
        'kinematic_diagram.py',
        'keyframe_sequence.py',
        'torque_analysis.py',
        'trajectory_comparison.py',
    ]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("开始批量中文化处理")
    print("=" * 60)
    print()
    
    for filename in files_to_process:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            localize_file(filepath)
        else:
            print(f"⚠️  文件不存在: {filepath}")
        print()
    
    print("=" * 60)
    print("批量处理完成！")
    print("=" * 60)
    print()
    print("现在可以运行 generate_all.py 重新生成所有图表")

if __name__ == '__main__':
    main()
