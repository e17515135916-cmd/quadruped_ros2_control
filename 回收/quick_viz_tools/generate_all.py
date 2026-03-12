#!/usr/bin/env python3
"""
一键生成所有必杀图！

快速生成演示PPT所需的所有可视化图表
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 70)
    print("🎨 PPT必杀图生成器 - 一键生成所有图表")
    print("=" * 70)
    print()
    
    # 创建输出目录
    output_dir = Path("presentation_outputs")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_dir.absolute()}")
    print()
    
    # 图表列表（深色系英文图表）
    charts_en = [
        ("工作空间对比图", "workspace_comparison", "workspace_comparison.png"),
        ("ROS节点通信图", "ros_graph", "ros_graph.png"),
        ("状态机流转图", "fsm_diagram", "fsm_diagram.png"),
        ("数据曲线图", "data_plot", "data_plot.png"),
        ("运动学简图", "kinematic_diagram", "kinematic_diagram.png"),
        ("关键帧序列图", "keyframe_sequence", "keyframe_sequence.png"),
        ("力矩分析图", "torque_analysis", "torque_analysis.png"),
        ("轨迹对比图", "trajectory_comparison", "trajectory_comparison.png"),
    ]
    
    # 亮色系中文图表
    charts_cn = [
        ("性能雷达图", "performance_radar_cn", "performance_radar_cn.png"),
        ("能耗饼图", "energy_pie_cn", "energy_pie_cn.png"),
        ("成功率柱状图", "success_rate_bar_cn", "success_rate_bar_cn.png"),
        ("技术优势对比图", "advantage_comparison_cn", "advantage_comparison_cn.png"),
    ]
    
    charts = charts_en + charts_cn
    
    success_count = 0
    
    for i, (name, module_name, filename) in enumerate(charts, 1):
        print(f"[{i}/{len(charts)}] 生成 {name}...")
        print("-" * 70)
        
        try:
            # 动态导入模块
            module = __import__(module_name)
            
            # 调用生成函数
            output_path = output_dir / filename
            
            if module_name == "workspace_comparison":
                module.plot_workspace_comparison(
                    rail_extension=0.1,
                    output_path=str(output_path)
                )
            elif module_name == "ros_graph":
                module.plot_ros_graph(output_path=str(output_path))
            elif module_name == "fsm_diagram":
                module.plot_fsm_diagram(output_path=str(output_path))
            elif module_name == "data_plot":
                module.plot_data_curves(
                    csv_path=None,  # 使用演示数据
                    output_path=str(output_path)
                )
            elif module_name == "kinematic_diagram":
                module.plot_kinematic_diagram(output_path=str(output_path))
            elif module_name == "keyframe_sequence":
                module.plot_keyframe_sequence(output_path=str(output_path))
            elif module_name == "torque_analysis":
                module.plot_torque_analysis(output_path=str(output_path))
            elif module_name == "trajectory_comparison":
                module.plot_trajectory_comparison(output_path=str(output_path))
            elif module_name == "performance_radar_cn":
                module.plot_performance_radar(output_path=str(output_path))
            elif module_name == "energy_pie_cn":
                module.plot_energy_pie(output_path=str(output_path))
            elif module_name == "success_rate_bar_cn":
                module.plot_success_rate_bar(output_path=str(output_path))
            elif module_name == "advantage_comparison_cn":
                module.plot_advantage_comparison(output_path=str(output_path))
            
            success_count += 1
            print(f"✅ {name} 生成成功!")
            
        except Exception as e:
            print(f"❌ {name} 生成失败: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # 总结
    print("=" * 70)
    print(f"🎉 完成! 成功生成 {success_count}/{len(charts)} 张图表")
    print("=" * 70)
    print()
    print(f"📂 所有图表已保存到: {output_dir.absolute()}")
    print()
    print("生成的图表:")
    for name, _, filename in charts:
        filepath = output_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  ✓ {name:20s} -> {filename:30s} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {name:20s} -> {filename:30s} (未生成)")
    
    print()
    print("💡 提示:")
    print("   - 可以单独运行每个脚本来生成特定图表")
    print("   - 例如: python3 workspace_comparison.py")
    print("   - 所有图表都是高分辨率(300 DPI)，适合PPT使用")

if __name__ == "__main__":
    main()
