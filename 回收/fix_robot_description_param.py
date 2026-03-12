#!/usr/bin/env python3
"""
修复 robot_description 参数传递问题

问题：使用 arguments + --params-file 时，临时参数文件会覆盖 parameters 列表
解决：将 robot_description 写入临时文件，然后通过 --params-file 传递
"""

import os

def fix_launch_file():
    launch_file = 'src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py'
    
    print("=" * 50)
    print("修复 robot_description 参数传递")
    print("=" * 50)
    print()
    
    with open(launch_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 quadruped_controller 节点定义并替换
    old_node = '''    # 6. CHAMP Quadruped Controller (Time 5s)
    # Requirements: 6.4
    quadruped_controller = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='quadruped_controller_node',
                name='quadruped_controller',
                output='screen',
                parameters=[
                    robot_description,  # robot_description 参数
                    {
                        'gazebo': True,
                        'publish_joint_states': False,
                        'publish_joint_control': True,
                        'publish_foot_contacts': True,
                        'joint_controller_topic': 'joint_trajectory_controller/joint_trajectory',
                        'use_sim_time': LaunchConfiguration('use_sim_time')
                    }
                ],
                arguments=[
                    '--ros-args',
                    '--params-file', gait_config,
                    '--params-file', joints_config,
                    '--params-file', links_config,
                ],
                remappings=[
                    ('cmd_vel/smooth', '/cmd_vel'),
                ],
            )
        ]
    )'''
    
    new_node = '''    # 6. CHAMP Quadruped Controller (Time 5s)
    # Requirements: 6.4
    # 创建包含 robot_description 的临时参数文件
    import yaml
    robot_desc_temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    robot_desc_params = {
        '/**': {
            'ros__parameters': {
                'robot_description': robot_description_config.toxml(),
                'gazebo': True,
                'publish_joint_states': False,
                'publish_joint_control': True,
                'publish_foot_contacts': True,
                'joint_controller_topic': 'joint_trajectory_controller/joint_trajectory',
                'use_sim_time': True
            }
        }
    }
    yaml.dump(robot_desc_params, robot_desc_temp_file)
    robot_desc_temp_file.close()
    robot_desc_param_file = robot_desc_temp_file.name
    
    quadruped_controller = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='quadruped_controller_node',
                name='quadruped_controller',
                output='screen',
                arguments=[
                    '--ros-args',
                    '--params-file', robot_desc_param_file,  # robot_description + 其他参数
                    '--params-file', gait_config,
                    '--params-file', joints_config,
                    '--params-file', links_config,
                ],
                remappings=[
                    ('cmd_vel/smooth', '/cmd_vel'),
                ],
            )
        ]
    )'''
    
    if old_node in content:
        content = content.replace(old_node, new_node)
        print("✅ 找到并替换了 quadruped_controller 节点定义")
    else:
        print("❌ 未找到预期的节点定义")
        return False
    
    # 同样修复 state_estimation_node
    old_state_est = '''    # 7. State Estimation Node (Time 5s)
    # Requirements: 6.4
    state_estimator = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='state_estimation_node',
                name='state_estimation',
                output='screen',
                parameters=[
                    {
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                        'orientation_from_imu': False  # Use kinematic estimation
                    }
                ]
            )
        ]
    )'''
    
    new_state_est = '''    # 7. State Estimation Node (Time 5s)
    # Requirements: 6.4
    # 创建 state_estimation 参数文件
    state_est_temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    state_est_params = {
        '/**': {
            'ros__parameters': {
                'robot_description': robot_description_config.toxml(),
                'use_sim_time': True,
                'orientation_from_imu': False
            }
        }
    }
    yaml.dump(state_est_params, state_est_temp_file)
    state_est_temp_file.close()
    state_est_param_file = state_est_temp_file.name
    
    state_estimator = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='champ_base',
                executable='state_estimation_node',
                name='state_estimation',
                output='screen',
                arguments=[
                    '--ros-args',
                    '--params-file', state_est_param_file,
                    '--params-file', links_config,
                ]
            )
        ]
    )'''
    
    if old_state_est in content:
        content = content.replace(old_state_est, new_state_est)
        print("✅ 找到并替换了 state_estimation_node 节点定义")
    else:
        print("⚠️  未找到 state_estimation_node 定义（可能已修改）")
    
    # 写回文件
    with open(launch_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("✅ 启动文件已修复")
    print()
    print("修改内容：")
    print("- 将 robot_description 写入临时 YAML 文件")
    print("- 通过 --params-file 传递所有参数")
    print("- 同时修复了 quadruped_controller 和 state_estimation_node")
    print()
    print("下一步：")
    print("1. 重新编译: colcon build --packages-select dog2_champ_config --symlink-install")
    print("2. 清理进程: ./clean_and_restart.sh")
    print("3. 重启 Gazebo: ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py")
    
    return True

if __name__ == '__main__':
    fix_launch_file()
