#!/usr/bin/env python3
"""
修复 URDF 中的 ros2_control 关节名称

问题：ros2_control 部分使用原始关节名称 (j11, j111, 等)
需要：使用 CHAMP 风格的关节名称 (lf_haa_joint, lf_hfe_joint, 等)

这样 Gazebo 才能暴露正确的关节接口给 joint_trajectory_controller
"""

import re

def fix_ros2_control():
    urdf_path = 'src/dog2_description/urdf/dog2.urdf.xacro'
    
    print("=" * 60)
    print("修复 ros2_control 关节名称")
    print("=" * 60)
    print()
    
    # 读取文件
    with open(urdf_path, 'r') as f:
        content = f.read()
    
    # 关节名称映射
    # 原始名称 -> CHAMP 名称
    joint_mapping = {
        # Leg 1 (Front Left)
        'j11': 'lf_haa_joint',
        'j111': 'lf_hfe_joint',
        'j1111': 'lf_kfe_joint',
        # Leg 2 (Front Right)
        'j21': 'rf_haa_joint',
        'j211': 'rf_hfe_joint',
        'j2111': 'rf_kfe_joint',
        # Leg 3 (Rear Left)
        'j31': 'lh_haa_joint',
        'j311': 'lh_hfe_joint',
        'j3111': 'lh_kfe_joint',
        # Leg 4 (Rear Right)
        'j41': 'rh_haa_joint',
        'j411': 'rh_hfe_joint',
        'j4111': 'rh_kfe_joint',
    }
    
    # 找到 ros2_control 部分
    ros2_control_start = content.find('<ros2_control name="GazeboSystem"')
    ros2_control_end = content.find('</ros2_control>')
    
    if ros2_control_start == -1 or ros2_control_end == -1:
        print("❌ 未找到 ros2_control 标签")
        return False
    
    # 提取 ros2_control 部分
    before = content[:ros2_control_start]
    ros2_control_section = content[ros2_control_start:ros2_control_end + len('</ros2_control>')]
    after = content[ros2_control_end + len('</ros2_control>'):]
    
    print("📝 更新关节名称:")
    print()
    
    # 替换关节名称
    modified = False
    for old_name, new_name in joint_mapping.items():
        pattern = f'<joint name="{old_name}">'
        if pattern in ros2_control_section:
            ros2_control_section = ros2_control_section.replace(pattern, f'<joint name="{new_name}">')
            print(f"  {old_name:12} -> {new_name}")
            modified = True
    
    if not modified:
        print("✅ 关节名称已经是 CHAMP 风格")
        return True
    
    # 重新组合文件
    new_content = before + ros2_control_section + after
    
    # 写回文件
    with open(urdf_path, 'w') as f:
        f.write(new_content)
    
    print()
    print("✅ URDF 已更新")
    
    # 验证
    with open(urdf_path, 'r') as f:
        verify_content = f.read()
    
    champ_joints = ['lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
                    'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
                    'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
                    'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint']
    
    found_count = sum(1 for joint in champ_joints if f'<joint name="{joint}">' in verify_content)
    
    print()
    print(f"📊 验证: 找到 {found_count}/12 个 CHAMP 风格的关节")
    
    if found_count == 12:
        print("✅ 所有关节名称已正确更新")
        return True
    else:
        print("⚠️  部分关节名称可能未更新")
        return False

def main():
    if fix_ros2_control():
        print()
        print("=" * 60)
        print("下一步操作")
        print("=" * 60)
        print()
        print("1. 停止当前 Gazebo (Ctrl+C)")
        print()
        print("2. 重新编译:")
        print("   colcon build --packages-select dog2_description --symlink-install")
        print()
        print("3. Source 环境:")
        print("   source install/setup.bash")
        print()
        print("4. 重新启动:")
        print("   ./quick_start_keyboard_control.sh")
        print()
        print("5. 等待 7-10 秒后，检查硬件接口:")
        print("   source /opt/ros/humble/setup.bash")
        print("   source install/setup.bash")
        print("   ros2 control list_hardware_interfaces")
        print()
        print("   应该看到 16 个关节接口:")
        print("   - 4 个滑轨: j1, j2, j3, j4")
        print("   - 12 个腿部: lf_haa_joint, lf_hfe_joint, ... rh_kfe_joint")
        print()
        print("6. 检查控制器状态:")
        print("   ros2 control list_controllers")
        print()
        print("   应该看到:")
        print("   joint_trajectory_controller ... active")
        print()
        print("7. 测试键盘控制:")
        print("   ./start_keyboard_control.sh")
        print("   按 W 键，机器人应该向前移动！")
    else:
        print("\n❌ 修复失败")

if __name__ == '__main__':
    main()
