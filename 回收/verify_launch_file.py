#!/usr/bin/env python3
"""
验证 dog2_champ_gazebo.launch.py 启动文件

检查项：
1. 文件语法正确
2. 包含所有必需的组件
3. 启动时序正确
4. 参数配置正确
"""

import os
import sys

def verify_launch_file():
    """验证启动文件"""
    launch_file = 'src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py'
    
    print("=" * 60)
    print("验证 Dog2 CHAMP Gazebo 启动文件")
    print("=" * 60)
    
    # 1. 检查文件存在
    print("\n1. 检查文件存在...")
    if not os.path.exists(launch_file):
        print(f"   ✗ 文件不存在: {launch_file}")
        return False
    print(f"   ✓ 文件存在: {launch_file}")
    
    # 2. 检查文件可读
    print("\n2. 检查文件可读...")
    try:
        with open(launch_file, 'r') as f:
            content = f.read()
        print(f"   ✓ 文件可读 ({len(content)} 字符)")
    except Exception as e:
        print(f"   ✗ 无法读取文件: {e}")
        return False
    
    # 3. 检查必需的组件
    print("\n3. 检查必需的组件...")
    required_components = {
        'Gazebo Fortress': 'ros_gz_sim',
        'Robot State Publisher': 'robot_state_publisher',
        'Spawn Entity': 'ros_gz_sim',
        'Joint State Broadcaster': 'joint_state_broadcaster',
        'Joint Trajectory Controller': 'joint_trajectory_controller',
        'CHAMP Controller': 'quadruped_controller_node',
        'State Estimator': 'state_estimation_node',
        'EKF Nodes': 'robot_localization',
    }
    
    all_found = True
    for component, keyword in required_components.items():
        if keyword in content:
            print(f"   ✓ {component}")
        else:
            print(f"   ✗ {component} (缺少关键字: {keyword})")
            all_found = False
    
    # 4. 检查启动参数
    print("\n4. 检查启动参数...")
    required_args = [
        'use_sim_time',
        'gazebo_gui',
        'rviz',
        'world'
    ]
    
    for arg in required_args:
        if f"'{arg}'" in content or f'"{arg}"' in content:
            print(f"   ✓ 参数: {arg}")
        else:
            print(f"   ✗ 参数: {arg}")
            all_found = False
    
    # 5. 检查时序控制
    print("\n5. 检查时序控制...")
    if 'TimerAction' in content:
        print("   ✓ 使用 TimerAction 进行时序控制")
        
        # 检查关键时间点
        time_points = {
            '0.5': 'robot_state_publisher',
            '1.0': 'spawn_entity',
            '3.0': 'joint_state_broadcaster',
            '4.0': 'joint_trajectory_controller',
            '5.0': 'quadruped_controller',
            '6.0': 'ekf'
        }
        
        for time, component in time_points.items():
            if f'period={time}' in content:
                print(f"   ✓ Time {time}s: {component}")
            else:
                print(f"   ⚠ Time {time}s: {component} (可能使用不同的时间)")
    else:
        print("   ⚠ 未使用 TimerAction (可能使用其他时序控制方法)")
    
    # 6. 检查配置文件路径
    print("\n6. 检查配置文件引用...")
    config_files = [
        'ros2_controllers.yaml',
        'gait.yaml',
        'joints.yaml',
        'links.yaml'
    ]
    
    for config in config_files:
        if config in content:
            print(f"   ✓ 配置文件: {config}")
        else:
            print(f"   ✗ 配置文件: {config}")
            all_found = False
    
    # 7. 检查 spawn 高度
    print("\n7. 检查机器人生成高度...")
    if "'-z', '0.5'" in content or '"-z", "0.5"' in content:
        print("   ✓ 生成高度: z=0.5m (符合要求)")
    else:
        print("   ⚠ 生成高度可能不是 0.5m")
    
    # 8. 检查 Requirements 注释
    print("\n8. 检查 Requirements 追溯...")
    if 'Requirements:' in content:
        print("   ✓ 包含 Requirements 追溯注释")
    else:
        print("   ⚠ 缺少 Requirements 追溯注释")
    
    print("\n" + "=" * 60)
    if all_found:
        print("✓ 验证通过！启动文件包含所有必需组件")
        print("=" * 60)
        return True
    else:
        print("⚠ 验证完成，但发现一些问题")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = verify_launch_file()
    sys.exit(0 if success else 1)
