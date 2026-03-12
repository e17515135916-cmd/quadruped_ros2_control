#!/usr/bin/env python3
"""
生成单腿 4 自由度冗余运动学拓扑图
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

def generate_kinematics_topology():
    """生成运动学拓扑图"""
    
    dot_content = '''
digraph Kinematics_Topology {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=12];
    edge [fontname="Arial", fontsize=11, penwidth=2];
    
    // 基座
    base [label="躯干 Base Link\\n━━━━━━━━━━━━━━━━\\n固定参考系\\nWorld Frame", 
          fillcolor="#e1f5fe", 
          penwidth=3,
          fontsize=13];
    
    // 直线导轨（创新点）
    rail [label="直线导轨\\nPrismatic Joint\\n━━━━━━━━━━━━━━━━\\n🔴 创新点: 扩展工作空间\\n━━━━━━━━━━━━━━━━\\n参数: s (位移)\\n范围: ±0.5m\\n类型: Prismatic DOF", 
          fillcolor="#ffcccc", 
          color="#ff0000",
          penwidth=4,
          style="rounded,filled,dashed",
          fontsize=13];
    
    // HAA 关节
    haa [label="HAA 髋部侧展关节\\nHip Abduction/Adduction\\n━━━━━━━━━━━━━━━━\\n参数: θ_haa (侧摆角)\\n范围: ±45°\\n类型: Revolute DOF", 
         fillcolor="#fff3e0",
         color="#f57c00",
         penwidth=3,
         fontsize=12];
    
    // HFE 关节
    hfe [label="HFE 大腿俯仰关节\\nHip Flexion/Extension\\n━━━━━━━━━━━━━━━━\\n参数: θ_hfe (俯仰角)\\n范围: ±90°\\n类型: Revolute DOF", 
         fillcolor="#f3e5f5",
         color="#7b1fa2",
         penwidth=3,
         fontsize=12];
    
    // KFE 关节
    kfe [label="KFE 小腿膝关节\\nKnee Flexion/Extension\\n━━━━━━━━━━━━━━━━\\n参数: θ_kfe (俯仰角)\\n范围: ±120°\\n类型: Revolute DOF", 
         fillcolor="#e8f5e9",
         color="#388e3c",
         penwidth=3,
         fontsize=12];
    
    // 足端
    foot [label="足端末端执行器\\nEnd Effector\\n━━━━━━━━━━━━━━━━\\n目标: 3D 位置\\n(x, y, z)\\n━━━━━━━━━━━━━━━━\\n任务空间维度: m = 3", 
          fillcolor="#fff9c4",
          color="#f57f17",
          penwidth=4,
          shape=ellipse,
          fontsize=13];
    
    // 连接
    base -> rail [label="  位移参数 s\\n  Prismatic DOF  ", 
                  color="#ff0000", 
                  penwidth=3,
                  fontcolor="#d32f2f",
                  fontsize=12];
    
    rail -> haa [label="  侧摆角 θ_haa\\n  Revolute DOF  ", 
                 color="#f57c00", 
                 penwidth=3,
                 fontcolor="#e65100",
                 fontsize=12];
    
    haa -> hfe [label="  俯仰角 θ_hfe\\n  Revolute DOF  ", 
                color="#7b1fa2", 
                penwidth=3,
                fontcolor="#4a148c",
                fontsize=12];
    
    hfe -> kfe [label="  俯仰角 θ_kfe\\n  Revolute DOF  ", 
                color="#388e3c", 
                penwidth=3,
                fontcolor="#1b5e20",
                fontsize=12];
    
    kfe -> foot [label="  足端位置\\n  p = [x, y, z]ᵀ  ", 
                 color="#f57f17", 
                 penwidth=3,
                 fontcolor="#e65100",
                 fontsize=12];
    
    // 冗余度标注
    redundancy [label="冗余度分析\\n━━━━━━━━━━━━━━━━\\n总自由度: n = 4\\n任务空间: m = 3\\n冗余度: r = n - m = 1\\n━━━━━━━━━━━━━━━━\\n解的特性: 无穷多解\\n解空间: 1 维流形", 
                shape=note,
                fillcolor="#e8eaf6",
                color="#3f51b5",
                penwidth=2,
                fontsize=11];
    
    // 降维策略标注
    strategy [label="降维策略\\n━━━━━━━━━━━━━━━━\\n策略 1: 导轨锁定 (s=0)\\n  → 降维为 3-DOF\\n  → 解析解，实时性好\\n━━━━━━━━━━━━━━━━\\n策略 2: 零空间优化\\n  → 充分利用冗余度\\n  → 优化次级任务", 
              shape=note,
              fillcolor="#fff3e0",
              color="#ff6f00",
              penwidth=2,
              fontsize=11];
    
    // 创新点标注
    innovation [label="硬件创新\\n━━━━━━━━━━━━━━━━\\n✓ 工作空间扩展 50%\\n✓ 非接触式穿越窗框\\n✓ 奇异性避免\\n✓ 灵活性提升", 
                shape=note,
                fillcolor="#ffebee",
                color="#c62828",
                penwidth=3,
                fontsize=11];
    
    // 布局辅助
    {rank=same; base; redundancy;}
    {rank=same; rail; innovation;}
    {rank=same; foot; strategy;}
    
    // 虚线连接标注
    rail -> innovation [style=dashed, color="#ff0000", penwidth=1, arrowhead=none];
    foot -> strategy [style=dashed, color="#f57f17", penwidth=1, arrowhead=none];
    base -> redundancy [style=dashed, color="#3f51b5", penwidth=1, arrowhead=none];
}
'''
    
    with open('/tmp/kinematics_topology.dot', 'w') as f:
        f.write(dot_content)
    
    try:
        subprocess.run([
            'dot', '-Tpng', '/tmp/kinematics_topology.dot',
            '-o', 'redundant_kinematics_topology.png',
            '-Gdpi=300'
        ], check=True)
        print("✓ 成功生成运动学拓扑图 PNG: redundant_kinematics_topology.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 PNG 失败: {e}")
        return False
    
    try:
        subprocess.run([
            'dot', '-Tsvg', '/tmp/kinematics_topology.dot',
            '-o', 'redundant_kinematics_topology.svg'
        ], check=True)
        print("✓ 成功生成运动学拓扑图 SVG: redundant_kinematics_topology.svg")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 SVG 失败: {e}")
    
    return True

def generate_redundancy_comparison():
    """生成冗余度对比图"""
    
    dot_content = '''
digraph Redundancy_Comparison {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];
    
    // 标题
    title [label="冗余运动学：问题与解决方案", 
           shape=plaintext, 
           fontsize=16, 
           fontname="Arial Bold"];
    
    // 问题描述
    subgraph cluster_problem {
        label="问题：无穷多解";
        style=filled;
        color="#ffebee";
        fontsize=13;
        fontname="Arial Bold";
        
        problem [label="给定足端位置 p = [x, y, z]ᵀ\\n求解关节角度 q = [s, θ_haa, θ_hfe, θ_kfe]ᵀ\\n━━━━━━━━━━━━━━━━━━━━━━━━━━\\n冗余度 r = 1 → 解空间是 1 维流形\\n存在无穷多组解满足约束条件", 
                 fillcolor="#ffcdd2",
                 fontsize=11];
        
        challenge [label="挑战:\\n1. 如何选择最优解？\\n2. 如何保证实时性？\\n3. 如何避免奇异位形？", 
                   fillcolor="#ef9a9a",
                   fontsize=11];
        
        problem -> challenge;
    }
    
    // 解决方案
    subgraph cluster_solutions {
        label="解决方案：降维思想";
        style=filled;
        color="#e8f5e9";
        fontsize=13;
        fontname="Arial Bold";
        
        sol1 [label="方案 1: 导轨锁定\\n━━━━━━━━━━━━━━━━\\n固定 s = 0.0m\\n降维为 3-DOF 标准问题\\n━━━━━━━━━━━━━━━━\\n✓ 解析解\\n✓ 实时性好 (0.05ms)\\n✓ 鲁棒性高\\n✗ 未充分利用导轨", 
              fillcolor="#a5d6a7",
              penwidth=2,
              fontsize=11];
        
        sol2 [label="方案 2: 零空间优化\\n━━━━━━━━━━━━━━━━\\nq̇ = J†ẋ + Nq̇_s\\n主任务 + 次级任务\\n━━━━━━━━━━━━━━━━\\n✓ 充分利用冗余度\\n✓ 优化次级目标\\n△ 计算量较大 (1.8ms)\\n△ 依赖初值", 
              fillcolor="#81c784",
              penwidth=2,
              fontsize=11];
        
        sol3 [label="方案 3: 任务优先级\\n━━━━━━━━━━━━━━━━\\n分层求解多个任务\\n严格的优先级保证\\n━━━━━━━━━━━━━━━━\\n✓ 处理复杂场景\\n✓ 灵活性高\\n✗ 实现复杂\\n✗ 计算量大", 
              fillcolor="#66bb6a",
              penwidth=2,
              fontsize=11];
    }
    
    // 实现路径
    subgraph cluster_roadmap {
        label="实现路径";
        style=filled;
        color="#e3f2fd";
        fontsize=13;
        fontname="Arial Bold";
        
        phase1 [label="第 1 阶段 (已完成)\\n━━━━━━━━━━━━━━━━\\n导轨锁定\\n验证系统稳定性", 
                fillcolor="#90caf9",
                penwidth=3,
                fontsize=11];
        
        phase2 [label="第 2 阶段 (规划中)\\n━━━━━━━━━━━━━━━━\\n零空间优化\\n提升性能", 
                fillcolor="#64b5f6",
                fontsize=11];
        
        phase3 [label="第 3 阶段 (未来)\\n━━━━━━━━━━━━━━━━\\n任务优先级\\n处理复杂场景", 
                fillcolor="#42a5f5",
                fontsize=11];
        
        phase1 -> phase2 [label="平滑过渡", penwidth=2];
        phase2 -> phase3 [label="逐步扩展", penwidth=2];
    }
    
    // 连接
    title -> problem [style=invis];
    challenge -> sol1 [label="降维", color=green, penwidth=2];
    challenge -> sol2 [label="优化", color=blue, penwidth=2];
    challenge -> sol3 [label="分层", color=purple, penwidth=2];
    
    sol1 -> phase1 [label="当前实现", color=green, penwidth=3];
    sol2 -> phase2 [label="未来扩展", color=blue, penwidth=2, style=dashed];
    sol3 -> phase3 [label="长期目标", color=purple, penwidth=2, style=dashed];
    
    // 性能对比表
    performance [label="性能对比\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n方法          | 计算时间 | 实时性 | 解唯一性 | 工作空间\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n导轨锁定      | 0.05ms   | ✓✓✓   | ✓✓✓     | ✓✓\\n零空间优化    | 1.8ms    | ✓✓    | ✓✓      | ✓✓✓\\n任务优先级    | 3.2ms    | ✓     | ✓       | ✓✓✓", 
                 shape=note,
                 fillcolor="#fff9c4",
                 fontsize=10,
                 fontname="Courier"];
    
    {rank=same; sol1; sol2; sol3;}
    {rank=same; phase1; phase2; phase3;}
}
'''
    
    with open('/tmp/redundancy_comparison.dot', 'w') as f:
        f.write(dot_content)
    
    try:
        subprocess.run([
            'dot', '-Tpng', '/tmp/redundancy_comparison.dot',
            '-o', 'redundancy_solution_comparison.png',
            '-Gdpi=300'
        ], check=True)
        print("✓ 成功生成冗余度对比图 PNG: redundancy_solution_comparison.png")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 PNG 失败: {e}")
        return False
    
    try:
        subprocess.run([
            'dot', '-Tsvg', '/tmp/redundancy_comparison.dot',
            '-o', 'redundancy_solution_comparison.svg'
        ], check=True)
        print("✓ 成功生成冗余度对比图 SVG: redundancy_solution_comparison.svg")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成 SVG 失败: {e}")
    
    return True

def main():
    print("=" * 60)
    print("单腿 4 自由度冗余运动学拓扑图生成工具")
    print("=" * 60)
    
    if not check_graphviz():
        print("\n✗ 错误: 未找到 Graphviz")
        print("请运行以下命令安装:")
        print("  Ubuntu/Debian: sudo apt-get install graphviz")
        sys.exit(1)
    
    print("✓ Graphviz 已安装\n")
    
    print("正在生成图表...")
    print("-" * 60)
    
    success = True
    
    # 生成运动学拓扑图
    print("\n[1/2] 生成运动学拓扑图...")
    if not generate_kinematics_topology():
        success = False
    
    # 生成冗余度对比图
    print("\n[2/2] 生成冗余度对比图...")
    if not generate_redundancy_comparison():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 所有图表生成完成！")
        print("\n生成的文件:")
        print("  1. redundant_kinematics_topology.png/svg - 运动学拓扑图")
        print("  2. redundancy_solution_comparison.png/svg - 冗余度对比图")
        print("\n推荐使用 SVG 格式插入 PPT，缩放不失真。")
        sys.exit(0)
    else:
        print("✗ 部分图表生成失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
