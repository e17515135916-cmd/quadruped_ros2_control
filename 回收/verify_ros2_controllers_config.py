#!/usr/bin/env python3
"""
验证 ros2_controllers.yaml 配置是否符合 CHAMP Gazebo Motion 系统要求
"""

import yaml
import sys

def verify_ros2_controllers_config():
    """验证 ros2_controllers.yaml 配置"""
    
    config_path = "src/dog2_description/config/ros2_controllers.yaml"
    
    print("=" * 60)
    print("验证 ros2_controllers.yaml 配置")
    print("=" * 60)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ 错误: 找不到配置文件 {config_path}")
        return False
    except yaml.YAMLError as e:
        print(f"❌ 错误: YAML 解析失败: {e}")
        return False
    
    all_checks_passed = True
    
    # 检查 1: controller_manager 更新率
    print("\n检查 1: Controller Manager 更新率")
    if 'controller_manager' in config:
        update_rate = config['controller_manager']['ros__parameters'].get('update_rate')
        if update_rate == 100:
            print(f"  ✓ 更新率设置为 100 Hz")
        else:
            print(f"  ❌ 更新率应为 100 Hz，当前为 {update_rate} Hz")
            all_checks_passed = False
    else:
        print("  ❌ 缺少 controller_manager 配置")
        all_checks_passed = False
    
    # 检查 2: joint_state_broadcaster 配置
    print("\n检查 2: Joint State Broadcaster")
    if 'joint_state_broadcaster' in config['controller_manager']['ros__parameters']:
        broadcaster_type = config['controller_manager']['ros__parameters']['joint_state_broadcaster'].get('type')
        if broadcaster_type == 'joint_state_broadcaster/JointStateBroadcaster':
            print(f"  ✓ Joint State Broadcaster 类型正确")
        else:
            print(f"  ❌ Joint State Broadcaster 类型错误: {broadcaster_type}")
            all_checks_passed = False
    else:
        print("  ❌ 缺少 joint_state_broadcaster 配置")
        all_checks_passed = False
    
    # 检查 3: joint_trajectory_controller 配置
    print("\n检查 3: Joint Trajectory Controller")
    if 'joint_trajectory_controller' in config['controller_manager']['ros__parameters']:
        controller_type = config['controller_manager']['ros__parameters']['joint_trajectory_controller'].get('type')
        if controller_type == 'joint_trajectory_controller/JointTrajectoryController':
            print(f"  ✓ Joint Trajectory Controller 类型正确")
        else:
            print(f"  ❌ Joint Trajectory Controller 类型错误: {controller_type}")
            all_checks_passed = False
    else:
        print("  ❌ 缺少 joint_trajectory_controller 配置")
        all_checks_passed = False
    
    # 检查 4: 关节列表（12 个旋转关节）
    print("\n检查 4: 关节列表（应包含 12 个旋转关节）")
    if 'joint_trajectory_controller' in config:
        joints = config['joint_trajectory_controller']['ros__parameters'].get('joints', [])
        
        # 期望的关节名称（CHAMP 命名约定）
        expected_joints = [
            # Left Front
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            # Right Front
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            # Left Hind
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            # Right Hind
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        
        if len(joints) == 12:
            print(f"  ✓ 关节数量正确: 12 个")
        else:
            print(f"  ❌ 关节数量错误: {len(joints)} 个（应为 12 个）")
            all_checks_passed = False
        
        # 检查每个期望的关节
        missing_joints = []
        for joint in expected_joints:
            if joint in joints:
                print(f"  ✓ {joint}")
            else:
                print(f"  ❌ 缺少关节: {joint}")
                missing_joints.append(joint)
                all_checks_passed = False
        
        # 检查是否有多余的关节
        extra_joints = [j for j in joints if j not in expected_joints]
        if extra_joints:
            print(f"  ❌ 发现多余的关节: {extra_joints}")
            all_checks_passed = False
    else:
        print("  ❌ 缺少 joint_trajectory_controller 关节配置")
        all_checks_passed = False
    
    # 检查 5: 命令接口
    print("\n检查 5: 命令接口")
    if 'joint_trajectory_controller' in config:
        command_interfaces = config['joint_trajectory_controller']['ros__parameters'].get('command_interfaces', [])
        if 'position' in command_interfaces:
            print(f"  ✓ 包含 position 命令接口")
        else:
            print(f"  ❌ 缺少 position 命令接口")
            all_checks_passed = False
    
    # 检查 6: 状态接口
    print("\n检查 6: 状态接口")
    if 'joint_trajectory_controller' in config:
        state_interfaces = config['joint_trajectory_controller']['ros__parameters'].get('state_interfaces', [])
        if 'position' in state_interfaces and 'velocity' in state_interfaces:
            print(f"  ✓ 包含 position 和 velocity 状态接口")
        else:
            print(f"  ❌ 状态接口不完整: {state_interfaces}")
            all_checks_passed = False
    
    # 检查 7: 确认移动副关节未包含
    print("\n检查 7: 移动副关节（应被排除）")
    prismatic_joints = ['j1', 'j2', 'j3', 'j4']
    if 'joint_trajectory_controller' in config:
        joints = config['joint_trajectory_controller']['ros__parameters'].get('joints', [])
        found_prismatic = [j for j in prismatic_joints if j in joints]
        if not found_prismatic:
            print(f"  ✓ 移动副关节已正确排除")
        else:
            print(f"  ❌ 发现移动副关节: {found_prismatic}")
            all_checks_passed = False
    
    # 检查 8: 确认 rail_position_controller 已移除
    print("\n检查 8: Rail Position Controller（应被移除）")
    if 'rail_position_controller' not in config.get('controller_manager', {}).get('ros__parameters', {}):
        print(f"  ✓ rail_position_controller 已正确移除")
    else:
        print(f"  ❌ rail_position_controller 仍然存在")
        all_checks_passed = False
    
    # 检查 9: 状态发布率
    print("\n检查 9: 状态发布率")
    if 'joint_trajectory_controller' in config:
        state_publish_rate = config['joint_trajectory_controller']['ros__parameters'].get('state_publish_rate')
        if state_publish_rate == 100.0:
            print(f"  ✓ 状态发布率设置为 100.0 Hz")
        else:
            print(f"  ⚠ 状态发布率为 {state_publish_rate} Hz（建议 100.0 Hz）")
    
    # 总结
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✓ 所有检查通过！配置符合要求。")
        print("=" * 60)
        return True
    else:
        print("❌ 部分检查失败，请修复上述问题。")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = verify_ros2_controllers_config()
    sys.exit(0 if success else 1)
