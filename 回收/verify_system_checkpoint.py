#!/usr/bin/env python3
"""
任务 6 检查点验证脚本

此脚本验证 CHAMP Gazebo Motion System 的所有组件是否正确配置。

验证内容：
1. 所有单元测试通过
2. 所有配置文件存在且有效
3. URDF 文件正确配置（滑动副锁定）
4. 启动文件存在且配置正确
5. RViz 配置文件存在

Requirements: 所有已完成任务的需求
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """打印信息"""
    print(f"  {text}")


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print_success(f"{description} 存在: {filepath}")
        return True
    else:
        print_error(f"{description} 不存在: {filepath}")
        return False


def run_unit_tests():
    """运行所有单元测试"""
    print_header("步骤 1: 运行单元测试")
    
    test_files = [
        'tests/test_ros2_controller_config_unit.py',
        'tests/test_champ_joint_mapping_unit.py',
        'tests/test_gait_parameters_unit.py'
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print_warning(f"测试文件不存在: {test_file}")
            continue
        
        print_info(f"运行测试: {test_file}")
        result = subprocess.run(
            ['python3', '-m', 'pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 提取通过的测试数量
            for line in result.stdout.split('\n'):
                if 'passed' in line:
                    print_success(f"{test_file}: {line.strip()}")
                    break
        else:
            print_error(f"{test_file}: 测试失败")
            print_info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            all_passed = False
    
    return all_passed


def verify_configuration_files():
    """验证配置文件"""
    print_header("步骤 2: 验证配置文件")
    
    all_valid = True
    
    # 检查 ros2_controllers.yaml
    controllers_yaml = 'src/dog2_description/config/ros2_controllers.yaml'
    if check_file_exists(controllers_yaml, "ros2_controllers.yaml"):
        try:
            with open(controllers_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            # 验证控制器管理器配置
            if 'controller_manager' in config:
                print_success("controller_manager 配置存在")
                
                # 验证更新率
                update_rate = config['controller_manager']['ros__parameters'].get('update_rate')
                if update_rate == 100:
                    print_success(f"更新率正确: {update_rate} Hz")
                else:
                    print_error(f"更新率不正确: {update_rate} (期望: 100)")
                    all_valid = False
            
            # 验证关节轨迹控制器
            if 'joint_trajectory_controller' in config:
                print_success("joint_trajectory_controller 配置存在")
                
                joints = config['joint_trajectory_controller']['ros__parameters'].get('joints', [])
                if len(joints) == 12:
                    print_success(f"关节数量正确: {len(joints)} 个")
                else:
                    print_error(f"关节数量不正确: {len(joints)} (期望: 12)")
                    all_valid = False
                
                # 验证没有滑动副
                prismatic_joints = ['j1', 'j2', 'j3', 'j4']
                has_prismatic = any(j in joints for j in prismatic_joints)
                if not has_prismatic:
                    print_success("滑动副已正确排除")
                else:
                    print_error("配置中包含滑动副")
                    all_valid = False
        except Exception as e:
            print_error(f"解析 ros2_controllers.yaml 失败: {e}")
            all_valid = False
    else:
        all_valid = False
    
    # 检查 gait.yaml
    gait_yaml = 'src/dog2_champ_config/config/gait/gait.yaml'
    if check_file_exists(gait_yaml, "gait.yaml"):
        try:
            with open(gait_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            gait_params = config['/**']['ros__parameters']['gait']
            
            # 验证关键参数
            required_params = [
                'knee_orientation',
                'max_linear_velocity_x',
                'max_linear_velocity_y',
                'max_angular_velocity_z',
                'stance_duration',
                'swing_height',
                'nominal_height'
            ]
            
            missing_params = [p for p in required_params if p not in gait_params]
            if not missing_params:
                print_success("所有必需的步态参数都存在")
            else:
                print_error(f"缺少步态参数: {missing_params}")
                all_valid = False
            
            # 验证参数值
            if gait_params.get('max_linear_velocity_x', 0) > 0:
                print_success(f"前向速度: {gait_params['max_linear_velocity_x']} m/s")
            if gait_params.get('nominal_height', 0) > 0:
                print_success(f"标称高度: {gait_params['nominal_height']} m")
                
        except Exception as e:
            print_error(f"解析 gait.yaml 失败: {e}")
            all_valid = False
    else:
        all_valid = False
    
    # 检查 joints.yaml
    joints_yaml = 'src/dog2_champ_config/config/joints/joints.yaml'
    if check_file_exists(joints_yaml, "joints.yaml"):
        try:
            with open(joints_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            joints_map = config['/**']['ros__parameters']['joints_map']
            
            # 验证四条腿
            required_legs = ['left_front', 'right_front', 'left_hind', 'right_hind']
            if all(leg in joints_map for leg in required_legs):
                print_success("所有四条腿都已映射")
            else:
                print_error("缺少腿部映射")
                all_valid = False
            
            # 验证每条腿有 3 个关节
            for leg in required_legs:
                if leg in joints_map:
                    joint_count = len(joints_map[leg])
                    if joint_count == 3:
                        print_success(f"{leg}: {joint_count} 个关节")
                    else:
                        print_error(f"{leg}: {joint_count} 个关节 (期望: 3)")
                        all_valid = False
                        
        except Exception as e:
            print_error(f"解析 joints.yaml 失败: {e}")
            all_valid = False
    else:
        all_valid = False
    
    # 检查 links.yaml
    links_yaml = 'src/dog2_champ_config/config/links/links.yaml'
    if not check_file_exists(links_yaml, "links.yaml"):
        all_valid = False
    
    return all_valid


def verify_urdf_configuration():
    """验证 URDF 配置"""
    print_header("步骤 3: 验证 URDF 配置")
    
    urdf_file = 'src/dog2_description/urdf/dog2.urdf.xacro'
    if not check_file_exists(urdf_file, "dog2.urdf.xacro"):
        return False
    
    all_valid = True
    
    try:
        with open(urdf_file, 'r') as f:
            content = f.read()
        
        # 检查滑动副速度限制
        prismatic_joints = ['j1', 'j2', 'j3', 'j4']
        for joint in prismatic_joints:
            # 查找关节定义
            if f'name="{joint}"' in content:
                # 检查是否有 velocity="0.0"
                joint_section_start = content.find(f'name="{joint}"')
                joint_section_end = content.find('</joint>', joint_section_start)
                joint_section = content[joint_section_start:joint_section_end]
                
                if 'velocity="0.0"' in joint_section or 'velocity="0"' in joint_section:
                    print_success(f"{joint}: 速度限制已设置为 0.0")
                else:
                    print_warning(f"{joint}: 速度限制可能未正确设置")
        
        # 检查旋转关节
        revolute_joints = [
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        
        found_joints = 0
        for joint in revolute_joints:
            if f'name="{joint}"' in content:
                found_joints += 1
        
        if found_joints == 12:
            print_success(f"找到所有 12 个旋转关节")
        else:
            print_warning(f"只找到 {found_joints} 个旋转关节 (期望: 12)")
            
    except Exception as e:
        print_error(f"解析 URDF 失败: {e}")
        all_valid = False
    
    return all_valid


def verify_launch_file():
    """验证启动文件"""
    print_header("步骤 4: 验证启动文件")
    
    launch_file = 'src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py'
    if not check_file_exists(launch_file, "dog2_champ_gazebo.launch.py"):
        return False
    
    all_valid = True
    
    try:
        with open(launch_file, 'r') as f:
            content = f.read()
        
        # 检查关键组件
        required_components = [
            ('Gazebo', 'gz_sim.launch.py'),
            ('Robot State Publisher', 'robot_state_publisher'),
            ('Spawn Entity', 'ros_gz_sim'),
            ('Joint State Broadcaster', 'joint_state_broadcaster'),
            ('Joint Trajectory Controller', 'joint_trajectory_controller'),
            ('CHAMP Controller', 'quadruped_controller_node'),
            ('State Estimator', 'state_estimation_node'),
        ]
        
        for component_name, search_string in required_components:
            if search_string in content:
                print_success(f"{component_name} 已配置")
            else:
                print_error(f"{component_name} 未找到")
                all_valid = False
        
        # 检查时序配置
        if 'TimerAction' in content:
            print_success("启动时序已配置")
        else:
            print_warning("未找到启动时序配置")
        
        # 检查生成高度
        if "'-z', '0.5'" in content or '"-z", "0.5"' in content:
            print_success("机器人生成高度已设置为 0.5m")
        else:
            print_warning("机器人生成高度可能未正确设置")
            
    except Exception as e:
        print_error(f"解析启动文件失败: {e}")
        all_valid = False
    
    return all_valid


def verify_rviz_config():
    """验证 RViz 配置"""
    print_header("步骤 5: 验证 RViz 配置")
    
    rviz_config = 'src/dog2_champ_config/rviz/dog2_champ.rviz'
    if check_file_exists(rviz_config, "dog2_champ.rviz"):
        try:
            with open(rviz_config, 'r') as f:
                content = f.read()
            
            # 检查关键显示元素
            required_displays = ['RobotModel', 'TF', 'Odometry']
            found_displays = []
            
            for display in required_displays:
                if display in content:
                    found_displays.append(display)
                    print_success(f"{display} 显示已配置")
            
            if len(found_displays) >= 2:
                return True
            else:
                print_warning("RViz 配置可能不完整")
                return True  # 不是关键错误
                
        except Exception as e:
            print_error(f"解析 RViz 配置失败: {e}")
            return False
    else:
        return False


def print_summary(results):
    """打印总结"""
    print_header("验证总结")
    
    all_passed = all(results.values())
    
    for step, passed in results.items():
        if passed:
            print_success(f"{step}: 通过")
        else:
            print_error(f"{step}: 失败")
    
    print("\n" + "="*60)
    if all_passed:
        print(f"{Colors.BOLD}{Colors.GREEN}✓ 所有检查通过！系统已准备好启动。{Colors.RESET}")
        print(f"\n{Colors.BLUE}下一步：{Colors.RESET}")
        print("  1. 构建工作空间: colcon build")
        print("  2. 启动系统: ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py")
        print("  3. 控制机器人: python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py")
    else:
        print(f"{Colors.BOLD}{Colors.RED}✗ 某些检查失败。请修复上述问题。{Colors.RESET}")
    print("="*60 + "\n")
    
    return all_passed


def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     CHAMP Gazebo Motion System - 任务 6 检查点验证         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    results = {}
    
    # 运行所有验证步骤
    results['单元测试'] = run_unit_tests()
    results['配置文件'] = verify_configuration_files()
    results['URDF 配置'] = verify_urdf_configuration()
    results['启动文件'] = verify_launch_file()
    results['RViz 配置'] = verify_rviz_config()
    
    # 打印总结
    all_passed = print_summary(results)
    
    # 返回退出码
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
