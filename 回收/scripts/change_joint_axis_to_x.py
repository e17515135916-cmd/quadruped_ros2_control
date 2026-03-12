#!/usr/bin/env python3
"""
修改URDF文件，将髋关节的axis从Z轴改为X轴
j11, j21, j31, j41的axis从"-1 0 0"改为"0 0 -1"
"""

import os
import re
import shutil

def modify_urdf_joint_axis(urdf_path):
    """修改URDF文件中的joint axis"""
    
    print(f"正在修改: {urdf_path}")
    
    # 备份原文件
    backup_path = urdf_path + ".backup_axis_change"
    if not os.path.exists(backup_path):
        shutil.copy2(urdf_path, backup_path)
        print(f"✅ 已备份到: {backup_path}")
    
    # 读取文件
    with open(urdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要修改的joint列表
    joints_to_modify = ['j11', 'j21', 'j31', 'j41']
    
    modified_count = 0
    
    for joint_name in joints_to_modify:
        # 查找joint定义
        # 匹配模式：<joint name="j11" type="revolute"> ... <axis xyz="-1 0 0"/> ... </joint>
        
        # 使用正则表达式找到joint块
        pattern = rf'(<joint name="{joint_name}"[^>]*>.*?<axis xyz=")(-1 0 0)(" */?>)'
        
        def replace_axis(match):
            nonlocal modified_count
            modified_count += 1
            print(f"  ✅ 修改 {joint_name}: axis从 '-1 0 0' 改为 '0 0 -1'")
            return match.group(1) + "0 0 -1" + match.group(3)
        
        content = re.sub(pattern, replace_axis, content, flags=re.DOTALL)
    
    # 保存修改后的文件
    with open(urdf_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 完成！共修改了 {modified_count} 个joint的axis")
    return modified_count > 0

def main():
    """主函数"""
    workspace_dir = os.path.expanduser("~/aperfect/carbot_ws")
    urdf_path = os.path.join(workspace_dir, "src/dog2_description/urdf/dog2.urdf.xacro")
    
    print("=" * 70)
    print("修改URDF joint axis（从Z轴改为X轴）")
    print("=" * 70)
    print()
    print(f"工作空间: {workspace_dir}")
    print(f"URDF文件: {urdf_path}")
    print()
    
    if not os.path.exists(urdf_path):
        print(f"❌ URDF文件不存在: {urdf_path}")
        return
    
    print("将要修改的joint：")
    print("  - j11 (左前腿髋关节)")
    print("  - j21 (右前腿髋关节)")
    print("  - j31 (左后腿髋关节)")
    print("  - j41 (右后腿髋关节)")
    print()
    print("修改内容：")
    print("  axis xyz=\"-1 0 0\" → axis xyz=\"0 0 -1\"")
    print()
    print("效果：")
    print("  原来：ZYY配置（第一个关节绕Z轴）")
    print("  修改后：XYY配置（第一个关节绕X轴）")
    print()
    
    if modify_urdf_joint_axis(urdf_path):
        print()
        print("=" * 70)
        print("✅ URDF修改完成！")
        print("=" * 70)
        print()
        print("下一步：")
        print("1. colcon build --packages-select dog2_description")
        print("2. source install/setup.bash")
        print("3. ros2 launch dog2_description view_dog2.launch.py")
        print()
        print("如果需要恢复：")
        print(f"  cp {urdf_path}.backup_axis_change {urdf_path}")
    else:
        print()
        print("❌ 修改失败")

if __name__ == "__main__":
    main()
