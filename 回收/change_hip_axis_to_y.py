#!/usr/bin/env python3
"""
将髋关节轴向从 X 轴改为 Y 轴（绿色轴）。

当前：hip_axis="1 0 0" (红色轴 - X轴)
目标：hip_axis="0 1 0" (绿色轴 - Y轴)
"""

import re
import sys
from datetime import datetime

def modify_hip_axis(xacro_path):
    """修改 xacro 文件中的 hip_axis 参数。"""
    
    # 读取文件
    with open(xacro_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = f"{xacro_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 已创建备份: {backup_path}")
    
    # 替换所有 hip_axis="1 0 0" 为 hip_axis="0 1 0"
    original_content = content
    content = re.sub(
        r'hip_axis="1 0 0"',
        'hip_axis="0 1 0"',
        content
    )
    
    # 检查是否有修改
    if content == original_content:
        print("⚠ 警告: 未找到需要修改的 hip_axis 参数")
        return False
    
    # 统计修改次数
    count = len(re.findall(r'hip_axis="0 1 0"', content))
    
    # 写入修改后的内容
    with open(xacro_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 已修改 {count} 处 hip_axis 参数")
    print(f"  从: hip_axis=\"1 0 0\" (X轴/红色)")
    print(f"  到: hip_axis=\"0 1 0\" (Y轴/绿色)")
    
    return True

def main():
    xacro_path = 'src/dog2_description/urdf/dog2.urdf.xacro'
    
    print("="*70)
    print("修改髋关节轴向: X轴 → Y轴")
    print("="*70)
    print(f"\n目标文件: {xacro_path}")
    print("\n修改内容:")
    print("  j11, j21, j31, j41 的 hip_axis")
    print("  从 X轴 (1 0 0 / 红色轴) 改为 Y轴 (0 1 0 / 绿色轴)")
    print("\n这将使髋关节绕绿色轴旋转（在 RViz TF 显示中）\n")
    
    if modify_hip_axis(xacro_path):
        print("\n✓ 修改完成！")
        print("\n验证修改:")
        print("  运行: xacro src/dog2_description/urdf/dog2.urdf.xacro | grep -A 5 'joint name=\"j11\"'")
        print("\n在 RViz 中测试:")
        print("  运行: ros2 launch verify_hip_axis_rviz.py")
        print("  移动 j11, j21, j31, j41 滑块，观察关节绕绿色轴旋转")
    else:
        print("\n✗ 修改失败")
        return 1
    
    print("="*70)
    return 0

if __name__ == '__main__':
    sys.exit(main())
