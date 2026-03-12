#!/usr/bin/env python3
"""
简单的 RViz2 启动脚本 - 直接读取 URDF 文件
"""

import subprocess
import time
import signal
import sys
import os

def main():
    print("=" * 60)
    print("启动 RViz2 测试 CHAMP 兼容配置")
    print("=" * 60)
    print()
    
    # 生成 URDF
    print("生成 URDF...")
    result = subprocess.run(
        ['xacro', 'src/dog2_description/urdf/dog2.urdf.xacro'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ URDF 生成失败")
        print(result.stderr)
        return 1
    
    urdf_content = result.stdout
    print("✅ URDF 已生成")
    print()
    
    # Source ROS 2 环境
    ros_setup = '/opt/ros/humble/setup.bash'
    
    # 启动 robot_state_publisher
    print("启动 robot_state_publisher...")
    rsp_process = subprocess.Popen(
        ['bash', '-c', f'source {ros_setup} && ros2 run robot_state_publisher robot_state_publisher'],
        stdin=subprocess.PIPE,
        env={**os.environ, 'ROS_DOMAIN_ID': '0'}
    )
    
    # 通过参数服务器设置 robot_description
    time.sleep(2)
    print("设置 robot_description 参数...")
    subprocess.run(
        ['bash', '-c', f'source {ros_setup} && ros2 param set /robot_state_publisher robot_description "{urdf_content}"'],
        capture_output=True
    )
    
    time.sleep(1)
    
    # 启动 joint_state_publisher_gui
    print("启动 joint_state_publisher_gui...")
    jsp_process = subprocess.Popen(
        ['bash', '-c', f'source {ros_setup} && ros2 run joint_state_publisher_gui joint_state_publisher_gui'],
        env={**os.environ, 'ROS_DOMAIN_ID': '0'}
    )
    
    time.sleep(2)
    
    # 启动 RViz2
    print("启动 RViz2...")
    print()
    print("在 RViz2 中：")
    print("1. 点击左下角 'Add' 按钮")
    print("2. 选择 'RobotModel'")
    print("3. 在左侧面板设置 Fixed Frame 为 'base_link'")
    print("4. 使用 joint_state_publisher_gui 窗口控制关节")
    print()
    
    rviz_process = subprocess.Popen(
        ['bash', '-c', f'source {ros_setup} && rviz2'],
        env={**os.environ, 'ROS_DOMAIN_ID': '0'}
    )
    
    # 等待 RViz2 关闭
    try:
        rviz_process.wait()
    except KeyboardInterrupt:
        print("\n中断信号接收")
    
    # 清理
    print("\n清理进程...")
    for proc in [rsp_process, jsp_process, rviz_process]:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            try:
                proc.kill()
            except:
                pass
    
    print("完成！")
    return 0

if __name__ == '__main__':
    sys.exit(main())
