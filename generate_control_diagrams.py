#!/usr/bin/env python3
"""
生成 MPC + WBC 分层控制架构图和零空间投影数学图
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

def generate_hierarchical_control_diagram():
    """生成四层控制架构图"""
    
    dot_content = '''
digraph Hierarchical_Control {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];
    compound=true;
    
    // 规划层
    subgraph cluster_planning {
        label="规划层 Planning Layer (10Hz)";
        style=filled;
        color="#e3f2fd";
        fontsize=14;
        fontname="Arial Bold";
        
        planner [label="全局路径规划器\\nGlobal Path Planner", fillcolor="#bbdefb"];
        window [label="窗框识别\\nWindow Detection", fillcolor="#bbdefb"];
        fsm [label="状态机\\nState Machine", fillcolor="#90caf9", penwidth=2];
        
        mode_trot [label="平地 Trot 模式\\nTrotting Gait", fillcolor="#c5cae9"];
        mode_crawl [label="穿窗 Crawl 模式\\nCrawling Gait", fillcolor="#c5cae9"];
        
        planner -> fsm;
        window -> fsm;
        fsm -> mode_trot;
        fsm -> mode_crawl;
    }
    
    // MPC 层
    subgraph cluster_mpc {
        label="MPC 层 Model Predictive Control (100Hz)";
        style=filled;
        color="#fff3e0";
        fontsize=14;
        fontname="Arial Bold";
        
        mpc [label="MPC 优化器\\nMPC Optimizer\\n预测时域: 10 步", fillcolor="#ffb74d", penwidth=2];
        dynamics [label="动力学模型\\nDynamics Model\\n单刚体模型", fillcolor="#ffe0b2"];
        constraints [label="约束条件\\nConstraints\\n摩擦锥、ZMP", fillcolor="#ffe0b2"];
        
        grf [label="地面反作用力 GRF\\nGround Reaction Forces\\n未来 10 个周期\\nF₁, F₂, F₃, F₄", fillcolor="#ff9800", penwidth=2];
        
        mpc -> dynamics;
        mpc -> constraints;
        dynamics -> grf;
        constraints -> grf;
    }
    
    // WBC 层
    subgraph cluster_wbc {
        label="WBC 层 Whole Body Control (500Hz) - 核心创新";
        style=filled;
        color="#e8f5e9";
        fontsize=14;
        fontname="Arial Bold";
        
        wbc [label="全身控制器\\nWBC Controller\\nq̇ = J†ẋ + Nq̇ₛ", fillcolor="#66bb6a", penwidth=3];
        
        subgraph cluster_primary {
            label="主任务 Primary Tasks";
            style=filled;
            color="#c8e6c9";
            
            task1 [label="足端轨迹跟踪\\nFoot Trajectory", fillcolor="#a5d6a7"];
            task2 [label="质心稳定\\nCoM Stabilization", fillcolor="#a5d6a7"];
            task3 [label="姿态控制\\nOrientation", fillcolor="#a5d6a7"];
        }
        
        subgraph cluster_secondary {
            label="次级任务 Secondary Tasks\\n零空间优化 Null Space";
            style=filled;
            color="#ffccbc";
            
            sec1 [label="导轨优化\\nRail Optimization\\n4-DOF 冗余", fillcolor="#ff8a65", penwidth=2];
            sec2 [label="关节限位避让\\nJoint Limit Avoidance", fillcolor="#ffab91"];
            sec3 [label="能量最优\\nEnergy Minimization", fillcolor="#ffab91"];
        }
        
        nullspace [label="零空间投影\\nNull Space Projection\\nN = I - J†J\\nrank(N) = 4", fillcolor="#fff59d", penwidth=2, shape=ellipse];
        
        wbc -> task1;
        wbc -> task2;
        wbc -> task3;
        wbc -> sec1;
        wbc -> sec2;
        wbc -> sec3;
        
        sec1 -> nullspace [penwidth=2];
        sec2 -> nullspace;
        sec3 -> nullspace;
        
        joint_cmd [label="16 关节指令\\n16-DOF Joint Commands\\n━━━━━━━━━━━━━━━━\\n4 导轨 (静态锁定)\\n12 旋转 (动态执行)", fillcolor="#4db6ac", penwidth=3];
        
        task1 -> joint_cmd [penwidth=2];
        task2 -> joint_cmd [penwidth=2];
        task3 -> joint_cmd [penwidth=2];
        nullspace -> joint_cmd [penwidth=2, color="#ff6f00"];
    }
    
    // 执行层
    subgraph cluster_execution {
        label="执行层 Execution Layer (1000Hz)";
        style=filled;
        color="#f3e5f5";
        fontsize=14;
        fontname="Arial Bold";
        
        ros2ctrl [label="ros2_control 框架\\nROS 2 Control Framework", fillcolor="#ba68c8"];
        jtc [label="JointTrajectoryController\\n关节轨迹控制器", fillcolor="#ce93d8"];
        cm [label="ControllerManager\\n控制器管理器", fillcolor="#e1bee7"];
        
        ros2ctrl -> jtc;
        jtc -> cm;
        
        subgraph cluster_dual {
            label="双通道执行 Dual-Channel";
            style=filled;
            color="#fff9c4";
            
            rail_ch [label="通道 A: 4 导轨\\n静态锁定 0.0m\\nj11, j21, j31, j41", fillcolor="#ef5350", fontcolor=white];
            rot_ch [label="通道 B: 12 旋转\\n动态执行\\nhaa, hfe, kfe × 4", fillcolor="#66bb6a", fontcolor=white];
        }
        
        cm -> rail_ch [penwidth=2, color=red];
        cm -> rot_ch [penwidth=2, color=green];
        
        gazebo [label="Gazebo Fortress\\n物理仿真引擎\\n━━━━━━━━━━━━━━━━\\n动力学积分\\n碰撞检测\\n接触力计算", fillcolor="#42a5f5", penwidth=2, fontcolor=white];
        
        rail_ch -> gazebo [penwidth=2, color=red];
        rot_ch -> gazebo [penwidth=2, color=green];
    }
    
    // 层间数据流
    mode_trot -> mpc [label="步态参数", color=blue, penwidth=2, lhead=cluster_mpc];
    mode_crawl -> mpc [label="步态参数", color=blue, penwidth=2];
    
    grf -> wbc [label="期望 GRF", color=blue, penwidth=2, lhead=cluster_wbc];
    
    joint_cmd -> ros2ctrl [label="关节指令", color=blue, penwidth=2, lhead=cluster_execution];
    
    // 反馈回路
    gazebo -> wbc [label="状态反馈\\n500Hz", color=orange, style=dashed, penwidth=2];
    gazebo -> mpc [label="状态反馈\\n100Hz", color=orange, style=dashed, penwidth=2];
    gazebo -> fsm [label="任务完成\\n10Hz", color=orange, style=dashed];
    
    // 频率标注
    freq1 [label="10 Hz\\n规划周期", shape=note, fillcolor="#e1f5fe"];
    freq2 [label="100 Hz\\nMPC 周期", shape=note, fillcolor="#fff3e0"];
    freq3 [label="500 Hz\\nWBC 周期", shape=note, fillcolor="#f1f8e9"];
    freq4 [label="1000 Hz\\n执行周期", shape=note, fillcolor="#fce4ec"];
    
    {rank=same; planner; freq1;}
    {rank=same; mpc; freq2;}
    {rank=same; wbc; freq3;}
    {rank=same; ros2ctrl; freq4;}
}
'''
    
    with open('/tmp/hierarchical_control.dot', 'w') as f:
        f.write(dot_content)
    
    try:
        subprocess.run([
            'dot', '-Tpng', '/tmp/hierarchical_control.dot',
            '-o', 'mpc_wbc_hierarchical_control.png',
            '-Gdpi=300'
        ], check=True)
        print("✓ 成功生成分层控制架构图 PNG: mpc_wbc_hierarchical_control.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 PNG 失败: {e}")
        return False
    
    try:
        subprocess.run([
            'dot', '-Tsvg', '/tmp/hierarchical_control.dot',
            '-o', 'mpc_wbc_hierarchical_control.svg'
        ], check=True)
        print("✓ 成功生成分层控制架构图 SVG: mpc_wbc_hierarchical_control.svg")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 SVG 失败: {e}")
    
    return True

def generate_nullspace_diagram():
    """生成零空间投影数学图"""
    
    dot_content = '''
digraph Nullspace_Projection {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];
    
    // 关节空间
    joint_space [label="16 维关节空间\\nJoint Space ℝ¹⁶\\n━━━━━━━━━━━━━━━━\\n4 导轨 (prismatic)\\n12 旋转 (revolute)\\n━━━━━━━━━━━━━━━━\\nq = [q₁, q₂, ..., q₁₆]ᵀ", fillcolor="#e3f2fd", penwidth=3, fontsize=12];
    
    // 任务空间
    task_space [label="12 维任务空间\\nTask Space ℝ¹²\\n━━━━━━━━━━━━━━━━\\n4 条腿 × 3D 位置\\n━━━━━━━━━━━━━━━━\\nẋ = J(q)q̇", fillcolor="#c8e6c9", penwidth=3, fontsize=12];
    
    // 零空间
    null_space [label="4 维零空间\\nNull Space ℝ⁴\\n━━━━━━━━━━━━━━━━\\n冗余自由度\\n━━━━━━━━━━━━━━━━\\nN = I - J†J\\nrank(N) = 4", fillcolor="#fff9c4", penwidth=3, fontsize=12];
    
    // 主任务
    subgraph cluster_primary {
        label="主任务 Primary Tasks (m=12)";
        style=filled;
        color="#a5d6a7";
        fontsize=12;
        fontname="Arial Bold";
        
        foot1 [label="腿 1 足端\\n(x₁, y₁, z₁)", fillcolor="#81c784"];
        foot2 [label="腿 2 足端\\n(x₂, y₂, z₂)", fillcolor="#81c784"];
        foot3 [label="腿 3 足端\\n(x₃, y₃, z₃)", fillcolor="#81c784"];
        foot4 [label="腿 4 足端\\n(x₄, y₄, z₄)", fillcolor="#81c784"];
    }
    
    // 次级任务
    subgraph cluster_secondary {
        label="次级任务 Secondary Tasks (零空间)";
        style=filled;
        color="#ffccbc";
        fontsize=12;
        fontname="Arial Bold";
        
        rail1 [label="导轨 1 优化\\nq₁ → 0.0m", fillcolor="#ff8a65", penwidth=2];
        rail2 [label="导轨 2 优化\\nq₅ → 0.0m", fillcolor="#ff8a65", penwidth=2];
        rail3 [label="导轨 3 优化\\nq₉ → 0.0m", fillcolor="#ff8a65", penwidth=2];
        rail4 [label="导轨 4 优化\\nq₁₃ → 0.0m", fillcolor="#ff8a65", penwidth=2];
    }
    
    // 数学公式节点
    jacobian [label="雅可比矩阵\\nJ(q) ∈ ℝ¹²ˣ¹⁶\\n━━━━━━━━━━━━━━━━\\nẋ = J(q)q̇", fillcolor="#bbdefb", shape=ellipse, penwidth=2];
    
    pseudoinv [label="伪逆\\nJ†(q) ∈ ℝ¹⁶ˣ¹²\\n━━━━━━━━━━━━━━━━\\nJ† = Jᵀ(JJᵀ)⁻¹", fillcolor="#ce93d8", shape=ellipse, penwidth=2];
    
    projector [label="投影矩阵\\nN(q) ∈ ℝ¹⁶ˣ¹⁶\\n━━━━━━━━━━━━━━━━\\nN = I - J†J\\nN² = N", fillcolor="#fff59d", shape=ellipse, penwidth=3];
    
    final_cmd [label="最终关节指令\\nq̇ = J†ẋ + Nq̇ₛ\\n━━━━━━━━━━━━━━━━\\n主任务 + 次级任务", fillcolor="#4db6ac", penwidth=3, fontsize=12, fontcolor=white];
    
    // 连接
    joint_space -> jacobian [label="映射", penwidth=2, color=blue];
    jacobian -> task_space [label="ẋ = Jq̇", penwidth=2, color=blue];
    
    task_space -> foot1;
    task_space -> foot2;
    task_space -> foot3;
    task_space -> foot4;
    
    jacobian -> pseudoinv [label="求伪逆", penwidth=2, color=purple];
    pseudoinv -> projector [label="N = I - J†J", penwidth=2, color=orange];
    
    joint_space -> null_space [label="冗余度\\nn - m = 4", penwidth=2, color="#ff6f00", style=dashed];
    
    null_space -> rail1;
    null_space -> rail2;
    null_space -> rail3;
    null_space -> rail4;
    
    foot1 -> final_cmd [label="J†ẋ", penwidth=2, color=green];
    foot2 -> final_cmd [penwidth=2, color=green];
    foot3 -> final_cmd [penwidth=2, color=green];
    foot4 -> final_cmd [penwidth=2, color=green];
    
    rail1 -> projector [penwidth=2, color=red];
    rail2 -> projector [penwidth=2, color=red];
    rail3 -> projector [penwidth=2, color=red];
    rail4 -> projector [penwidth=2, color=red];
    
    projector -> final_cmd [label="Nq̇ₛ", penwidth=2, color=red];
    
    // 关键性质标注
    property1 [label="关键性质 1:\\nJN = 0\\n零空间不影响任务", shape=note, fillcolor="#e8f5e9"];
    property2 [label="关键性质 2:\\nN² = N\\n投影幂等性", shape=note, fillcolor="#fff3e0"];
    property3 [label="关键性质 3:\\nrank(N) = n - m\\n冗余度 = 4", shape=note, fillcolor="#fce4ec"];
    
    {rank=same; projector; property1; property2; property3;}
}
'''
    
    with open('/tmp/nullspace_projection.dot', 'w') as f:
        f.write(dot_content)
    
    try:
        subprocess.run([
            'dot', '-Tpng', '/tmp/nullspace_projection.dot',
            '-o', 'nullspace_projection_math.png',
            '-Gdpi=300'
        ], check=True)
        print("✓ 成功生成零空间投影数学图 PNG: nullspace_projection_math.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 PNG 失败: {e}")
        return False
    
    try:
        subprocess.run([
            'dot', '-Tsvg', '/tmp/nullspace_projection.dot',
            '-o', 'nullspace_projection_math.svg'
        ], check=True)
        print("✓ 成功生成零空间投影数学图 SVG: nullspace_projection_math.svg")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 SVG 失败: {e}")
    
    return True

def main():
    print("=" * 60)
    print("MPC + WBC 分层控制架构图生成工具")
    print("=" * 60)
    
    if not check_graphviz():
        print("\n✗ 错误: 未找到 Graphviz")
        print("请运行以下命令安装:")
        print("  Ubuntu/Debian: sudo apt-get install graphviz")
        print("  macOS: brew install graphviz")
        sys.exit(1)
    
    print("✓ Graphviz 已安装\\n")
    
    print("正在生成图表...")
    print("-" * 60)
    
    success = True
    
    # 生成分层控制架构图
    print("\\n[1/2] 生成分层控制架构图...")
    if not generate_hierarchical_control_diagram():
        success = False
    
    # 生成零空间投影数学图
    print("\\n[2/2] 生成零空间投影数学图...")
    if not generate_nullspace_diagram():
        success = False
    
    print("\\n" + "=" * 60)
    if success:
        print("✓ 所有图表生成完成！")
        print("\\n生成的文件:")
        print("  1. mpc_wbc_hierarchical_control.png/svg - 分层控制架构图")
        print("  2. nullspace_projection_math.png/svg - 零空间投影数学图")
        print("\\n推荐使用 SVG 格式插入 PPT，缩放不失真。")
        sys.exit(0)
    else:
        print("✗ 部分图表生成失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
