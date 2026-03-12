#!/usr/bin/env python3
"""
ROS 2 控制系统架构图生成脚本
使用 Graphviz 生成高质量的系统架构图
"""

import subprocess
import sys

def check_graphviz():
    """检查 Graphviz 是否安装"""
    try:
        subprocess.run(['dot', '-V'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_diagram():
    """生成系统架构图"""
    
    dot_content = '''
digraph ROS2_Control_Architecture {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial"];
    edge [fontname="Arial"];
    
    // 定义子图和节点
    subgraph cluster_user {
        label="用户层 User Layer";
        style=filled;
        color=lightblue;
        
        cmd_vel [label="cmd_vel\n速度指令\nTwist Message", fillcolor="#e1f5ff", shape=note];
    }
    
    subgraph cluster_control {
        label="控制层 Control Layer";
        style=filled;
        color=lightyellow;
        
        controller [label="SpiderRobotController\n主控制节点", fillcolor="#fff3e0"];
        gait [label="GaitGenerator\n步态生成器", fillcolor="#f3e5f5"];
        kinematics [label="KinematicsSolver\n运动学求解器", fillcolor="#e8f5e9"];
        
        controller -> gait;
        gait -> kinematics;
    }
    
    subgraph cluster_dual_channel {
        label="双通道指令生成 Dual-Channel Command Generation";
        style=filled;
        color="#fff9c4";
        
        cmd_gen [label="16 通道关节指令生成", fillcolor="#fff9c4"];
        
        subgraph cluster_channel_a {
            label="通道 A - 静态锁定";
            style=filled;
            color="#ffebee";
            
            rail1 [label="导轨 1: j11_prismatic\n位置: 0.0m 锁定", fillcolor="#ffcdd2"];
            rail2 [label="导轨 2: j21_prismatic\n位置: 0.0m 锁定", fillcolor="#ffcdd2"];
            rail3 [label="导轨 3: j31_prismatic\n位置: 0.0m 锁定", fillcolor="#ffcdd2"];
            rail4 [label="导轨 4: j41_prismatic\n位置: 0.0m 锁定", fillcolor="#ffcdd2"];
        }
        
        subgraph cluster_channel_b {
            label="通道 B - 动态执行";
            style=filled;
            color="#e8f5e9";
            
            leg1 [label="腿 1 旋转关节\nj12_haa, j13_hfe, j14_kfe", fillcolor="#c8e6c9"];
            leg2 [label="腿 2 旋转关节\nj22_haa, j23_hfe, j24_kfe", fillcolor="#c8e6c9"];
            leg3 [label="腿 3 旋转关节\nj32_haa, j33_hfe, j34_kfe", fillcolor="#c8e6c9"];
            leg4 [label="腿 4 旋转关节\nj42_haa, j43_hfe, j44_kfe", fillcolor="#c8e6c9"];
        }
        
        cmd_gen -> rail1;
        cmd_gen -> rail2;
        cmd_gen -> rail3;
        cmd_gen -> rail4;
        cmd_gen -> leg1;
        cmd_gen -> leg2;
        cmd_gen -> leg3;
        cmd_gen -> leg4;
    }
    
    subgraph cluster_framework {
        label="ROS 2 Control 框架层";
        style=filled;
        color="#e1bee7";
        
        jtc [label="JointTrajectoryController\n关节轨迹控制器", fillcolor="#e1bee7"];
        cm [label="ControllerManager\n控制器管理器", fillcolor="#c5cae9"];
        
        jtc -> cm;
    }
    
    subgraph cluster_hardware {
        label="硬件抽象层 Hardware Interface";
        style=filled;
        color="#b2dfdb";
        
        gazebo_sys [label="GazeboSystem\nGazebo 硬件接口插件", fillcolor="#b2dfdb"];
        
        cmd_if_static [label="4 个导轨位置命令接口\nposition command", fillcolor="#ffccbc"];
        cmd_if_dynamic [label="12 个旋转关节位置命令接口\nposition command", fillcolor="#c8e6c9"];
        
        state_pos [label="16 个关节位置状态\nposition state", fillcolor="#d1c4e9"];
        state_vel [label="16 个关节速度状态\nvelocity state", fillcolor="#d1c4e9"];
        state_eff [label="16 个关节力矩状态\neffort state", fillcolor="#d1c4e9"];
        
        gazebo_sys -> cmd_if_static;
        gazebo_sys -> cmd_if_dynamic;
        gazebo_sys -> state_pos;
        gazebo_sys -> state_vel;
        gazebo_sys -> state_eff;
    }
    
    subgraph cluster_simulation {
        label="物理仿真层 Physics Simulation";
        style=filled;
        color="#bbdefb";
        
        gazebo [label="Gazebo Fortress\n物理引擎", fillcolor="#bbdefb"];
        urdf [label="URDF 机器人模型\n16 关节定义", fillcolor="#c5e1a5"];
        
        gazebo -> urdf;
    }
    
    subgraph cluster_viz {
        label="可视化层 Visualization";
        style=filled;
        color="#f8bbd0";
        
        rviz [label="RViz2\n实时状态显示", fillcolor="#f8bbd0"];
        joint_states [label="joint_states\nTopic", fillcolor="#dcedc8", shape=note];
        
        joint_states -> rviz;
    }
    
    // 主数据流
    cmd_vel -> controller [label="Twist 消息", color=blue, penwidth=2];
    kinematics -> cmd_gen [label="足端轨迹", color=blue, penwidth=2];
    
    rail1 -> jtc [label="静态指令 0.0", color=red, penwidth=2];
    rail2 -> jtc [color=red, penwidth=2];
    rail3 -> jtc [color=red, penwidth=2];
    rail4 -> jtc [color=red, penwidth=2];
    
    leg1 -> jtc [label="动态指令", color=green, penwidth=2];
    leg2 -> jtc [color=green, penwidth=2];
    leg3 -> jtc [color=green, penwidth=2];
    leg4 -> jtc [color=green, penwidth=2];
    
    cm -> gazebo_sys [label="命令分发", color=blue, penwidth=2];
    
    cmd_if_static -> gazebo [label="导轨锁定", color=red, style=dashed, penwidth=2];
    cmd_if_dynamic -> gazebo [label="旋转执行", color=green, style=dashed, penwidth=2];
    
    gazebo -> state_pos [label="物理状态", color=purple, penwidth=2];
    gazebo -> state_vel [color=purple, penwidth=2];
    gazebo -> state_eff [color=purple, penwidth=2];
    
    state_pos -> cm [label="状态反馈", color=purple, penwidth=2];
    state_vel -> cm [color=purple, penwidth=2];
    state_eff -> cm [color=purple, penwidth=2];
    
    cm -> joint_states [label="joint_states", color=blue, penwidth=2];
    
    // 反馈回路
    state_pos -> controller [label="闭环反馈", color=orange, style=dashed];
    state_vel -> controller [color=orange, style=dashed];
}
'''
    
    # 写入临时文件
    with open('/tmp/ros2_architecture.dot', 'w') as f:
        f.write(dot_content)
    
    # 生成 PNG (高分辨率)
    try:
        subprocess.run([
            'dot', '-Tpng', '/tmp/ros2_architecture.dot',
            '-o', 'ros2_control_architecture.png',
            '-Gdpi=300'
        ], check=True)
        print("✓ 成功生成 PNG 图片: ros2_control_architecture.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 PNG 失败: {e}")
        return False
    
    # 生成 SVG (矢量图，用于 PPT)
    try:
        subprocess.run([
            'dot', '-Tsvg', '/tmp/ros2_architecture.dot',
            '-o', 'ros2_control_architecture.svg'
        ], check=True)
        print("✓ 成功生成 SVG 矢量图: ros2_control_architecture.svg")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 SVG 失败: {e}")
    
    print("\n图片已生成，可以直接插入到 PPT 中！")
    print("推荐使用 SVG 格式，在 PPT 中缩放不会失真。")
    return True

def main():
    print("ROS 2 控制系统架构图生成工具")
    print("=" * 50)
    
    if not check_graphviz():
        print("\n错误: 未找到 Graphviz")
        print("请运行以下命令安装:")
        print("  Ubuntu/Debian: sudo apt-get install graphviz")
        print("  macOS: brew install graphviz")
        print("  Windows: 从 https://graphviz.org/download/ 下载安装")
        sys.exit(1)
    
    print("✓ Graphviz 已安装")
    print("\n正在生成架构图...")
    
    if generate_diagram():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
