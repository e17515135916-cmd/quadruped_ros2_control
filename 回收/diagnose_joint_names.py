#!/usr/bin/env python3
"""
诊断 joint_state_publisher_gui 显示的关节名称问题
"""

import subprocess
import sys

print("="*70)
print("诊断 Joint State Publisher GUI 关节名称显示问题")
print("="*70)
print()

# 1. 检查 xacro 编译后的 URDF
print("步骤 1: 检查 URDF 中的关节名称")
print("-"*70)

try:
    result = subprocess.run(
        ['xacro', 'src/dog2_description/urdf/dog2.urdf.xacro'],
        capture_output=True,
        text=True,
        check=True
    )
    
    urdf_content = result.stdout
    
    # 提取关节名称
    import re
    joint_pattern = r'<joint name="([^"]+)" type="([^"]+)"'
    joints = re.findall(joint_pattern, urdf_content)
    
    print(f"找到 {len(joints)} 个关节：")
    print()
    
    # 分类显示
    prismatic_joints = [j for j in joints if j[1] == 'prismatic']
    revolute_joints = [j for j in joints if j[1] == 'revolute']
    fixed_joints = [j for j in joints if j[1] == 'fixed']
    
    print("滑动副关节 (prismatic):")
    for name, jtype in prismatic_joints:
        print(f"  ✓ {name}")
    print()
    
    print("旋转关节 (revolute):")
    for name, jtype in revolute_joints:
        print(f"  ✓ {name}")
    print()
    
    # 检查是否有旧的关节名称
    old_names = ['j11', 'j21', 'j31', 'j41', 'j111', 'j211', 'j311', 'j411', 'j1111', 'j2111', 'j3111', 'j4111']
    new_names = ['lf_haa_joint', 'rf_haa_joint', 'lh_haa_joint', 'rh_haa_joint',
                 'lf_hfe_joint', 'rf_hfe_joint', 'lh_hfe_joint', 'rh_hfe_joint',
                 'lf_kfe_joint', 'rf_kfe_joint', 'lh_kfe_joint', 'rh_kfe_joint']
    
    joint_names = [j[0] for j in joints]
    
    has_old_names = any(old in joint_names for old in old_names)
    has_new_names = any(new in joint_names for new in new_names)
    
    print("="*70)
    print("诊断结果:")
    print("-"*70)
    
    if has_old_names and not has_new_names:
        print("❌ 问题: URDF 中仍使用旧的关节名称 (j11, j111 等)")
        print()
        print("解决方案:")
        print("1. 检查 src/dog2_description/urdf/dog2.urdf.xacro 文件")
        print("2. 确认 leg macro 中的关节名称已更新")
        print("3. 重新构建: colcon build --packages-select dog2_description")
        sys.exit(1)
        
    elif has_new_names and not has_old_names:
        print("✓ URDF 中的关节名称正确 (使用 CHAMP 命名)")
        print()
        print("如果 joint_state_publisher_gui 仍显示旧名称，可能的原因:")
        print()
        print("1. ROS 2 缓存了旧的 URDF")
        print("   解决: 重新 source 环境")
        print("   命令: source install/setup.bash")
        print()
        print("2. 使用了错误的 launch 文件")
        print("   解决: 使用提供的 launch 文件")
        print("   命令: ros2 launch launch_champ_rviz_test.py")
        print()
        print("3. robot_state_publisher 使用了旧的 URDF")
        print("   解决: 重启所有 ROS 2 节点")
        print()
        
    elif has_new_names and has_old_names:
        print("⚠️  警告: URDF 中同时存在新旧关节名称")
        print()
        print("旧名称:")
        for old in old_names:
            if old in joint_names:
                print(f"  - {old}")
        print()
        print("新名称:")
        for new in new_names:
            if new in joint_names:
                print(f"  - {new}")
        print()
        print("这可能导致冲突。请检查 URDF 文件。")
        
    else:
        print("❌ 错误: 未找到预期的关节名称")
        print()
        print("请检查 URDF 文件是否正确。")
    
    print("="*70)
    
except subprocess.CalledProcessError as e:
    print(f"❌ 错误: 无法编译 xacro 文件")
    print(f"错误信息: {e.stderr}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
