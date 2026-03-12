#!/usr/bin/env python3
"""
缩小URDF中惯性显示的质量值
注意：这只用于可视化，不要用于物理仿真！
"""

import re
import sys

def scale_inertia_visualization(urdf_path, output_path, scale_factor=0.3):
    """
    缩小URDF中的质量值以减小RViz2中惯性球体的显示大小
    
    参数:
        urdf_path: 输入URDF文件路径
        output_path: 输出URDF文件路径  
        scale_factor: 缩放因子（0.3表示缩小到30%）
    """
    
    with open(urdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式查找并替换质量值
    # 匹配 <mass value="数字" />
    def replace_mass(match):
        original_value = float(match.group(1))
        new_value = original_value * scale_factor
        return f'<mass value="{new_value}" />'
    
    # 替换所有质量值
    modified_content = re.sub(
        r'<mass value="([0-9.Ee+-]+)" />',
        replace_mass,
        content
    )
    
    # 在文件开头添加注释
    comment = f"""<?xml version="1.0"?>
<!-- 
  警告：此URDF文件的质量值已缩放{scale_factor}倍，仅用于RViz2可视化！
  不要用于Gazebo仿真或物理计算！
  原始文件：{urdf_path}
-->
"""
    
    # 移除原有的XML声明（如果有）
    modified_content = re.sub(r'<\?xml[^>]*\?>\s*', '', modified_content)
    
    # 添加新的注释和XML声明
    final_content = comment + modified_content
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✓ 已生成缩小惯性显示的URDF文件")
    print(f"  输入: {urdf_path}")
    print(f"  输出: {output_path}")
    print(f"  缩放因子: {scale_factor}")
    print(f"\n注意：此文件仅用于可视化，不要用于物理仿真！")

if __name__ == "__main__":
    import os
    
    # 默认路径
    workspace = os.path.expanduser("~/aperfect/carbot_ws")
    input_urdf = os.path.join(workspace, "src/dog2_description/urdf/dog2.urdf")
    output_urdf = os.path.join(workspace, "src/dog2_description/urdf/dog2_visual.urdf")
    
    # 缩放因子：0.3表示缩小到30%大小
    scale_factor = 0.3
    
    if len(sys.argv) > 1:
        scale_factor = float(sys.argv[1])
    
    scale_inertia_visualization(input_urdf, output_urdf, scale_factor)
