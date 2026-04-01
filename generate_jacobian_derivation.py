#!/usr/bin/env python3
"""
Generate symbolic FK and 3x4 Jacobian for dog2 single-leg 4-DoF model,
and export publication-ready formulas to paper_formulas/jacobian_derivation.md.

DoF definition:
- q1: rail translation s (along body x-axis)
- q2: hip side-swing theta1
- q3: hip pitch theta2
- q4: knee pitch theta3
"""

from __future__ import annotations

from pathlib import Path
import sympy as sp


def build_symbolic_model():
    # Generalized coordinates
    s, theta1, theta2, theta3 = sp.symbols("s theta_1 theta_2 theta_3", real=True)

    # Geometric parameters
    l1, l2, l3 = sp.symbols("l_1 l_2 l_3", positive=True, real=True)

    # Compact trigonometric helpers
    c1, s1 = sp.cos(theta1), sp.sin(theta1)
    c2, s2 = sp.cos(theta2), sp.sin(theta2)
    c23, s23 = sp.cos(theta2 + theta3), sp.sin(theta2 + theta3)

    # Radial projection in horizontal plane after pitch-chain folding
    r = l1 + l2 * c2 + l3 * c23

    # Forward kinematics: foot position in base frame
    p = sp.Matrix(
        [
            s + r * c1,
            r * s1,
            -(l2 * s2 + l3 * s23),
        ]
    )

    q = sp.Matrix([s, theta1, theta2, theta3])
    J = sp.simplify(p.jacobian(q))

    return {
        "symbols": {
            "s": s,
            "theta1": theta1,
            "theta2": theta2,
            "theta3": theta3,
            "l1": l1,
            "l2": l2,
            "l3": l3,
        },
        "r": sp.simplify(r),
        "p": sp.simplify(p),
        "q": q,
        "J": J,
    }


def equation_block(eq_latex: str) -> str:
    return f"$$\n{eq_latex}\n$$\n"


def generate_markdown(model: dict) -> str:
    s = model["symbols"]["s"]
    theta1 = model["symbols"]["theta1"]
    theta2 = model["symbols"]["theta2"]
    theta3 = model["symbols"]["theta3"]
    l1 = model["symbols"]["l1"]
    l2 = model["symbols"]["l2"]
    l3 = model["symbols"]["l3"]

    r = model["r"]
    p = model["p"]
    J = model["J"]

    # LaTeX equations
    r_latex = sp.latex(sp.Eq(sp.Symbol("r"), r))
    p_latex = sp.latex(sp.Eq(sp.MatrixSymbol("\\mathbf{p}_{foot}", 3, 1), p))
    q_latex = sp.latex(sp.Eq(sp.MatrixSymbol("\\mathbf{q}", 4, 1), sp.Matrix([s, theta1, theta2, theta3])))
    j_def_latex = sp.latex(
        sp.Eq(
            sp.MatrixSymbol("\\mathbf{J}", 3, 4),
            sp.MatrixSymbol("\\frac{\\partial \\mathbf{p}_{foot}}{\\partial \\mathbf{q}}", 3, 4),
        )
    )
    J_latex = sp.latex(J)

    # Extract the first Jacobian column (rail column)
    j_col1 = J[:, 0]
    j_col1_latex = sp.latex(sp.Eq(sp.MatrixSymbol("\\mathbf{j}_s", 3, 1), j_col1))

    md = []
    md.append("# dog2 单腿 4-DoF 雅可比推导（SymPy 自动生成）\n")
    md.append("本文档由 `generate_jacobian_derivation.py` 自动生成，用于论文中的运动学与 WBC 冗余控制推导。\n")

    md.append("## 1. 坐标与变量定义\n")
    md.append("- 机器人单腿广义坐标：\\(\\mathbf{q}=[s,\\theta_1,\\theta_2,\\theta_3]^T\\)。\n")
    md.append("- \\(s\\)：直线导轨位移（沿机身 x 方向）。\n")
    md.append("- \\(\\theta_1\\)：髋侧摆角（影响足端在水平面内的方位）。\n")
    md.append("- \\(\\theta_2,\\theta_3\\)：大腿与小腿俯仰角（决定足端高度与前向伸展）。\n")
    md.append("- 连杆参数 \\(l_1,l_2,l_3>0\\) 分别对应髋偏置、股骨、胫骨等效长度。\n")

    md.append("### 公式 (1): 平面投影半径\n")
    md.append(equation_block(r_latex))
    md.append("**物理含义**：\\(r\\) 表示在给定俯仰构型 \\(\\theta_2,\\theta_3\\) 下，腿在水平面的等效伸展半径。\n")

    md.append("### 公式 (2): 足端正运动学（FK）\n")
    md.append(equation_block(p_latex))
    md.append("**物理含义**：\n")
    md.append("- 第 1 行（\\(x\\)）：由导轨平移 \\(s\\) 与旋转链投影 \\(r\\cos\\theta_1\\) 叠加得到。\n")
    md.append("- 第 2 行（\\(y\\)）：由侧摆角 \\(\\theta_1\\) 产生的横向投影 \\(r\\sin\\theta_1\\)。\n")
    md.append("- 第 3 行（\\(z\\)）：由俯仰链 \\(\\theta_2,\\theta_3\\) 决定的垂向高度（向下取负号约定）。\n")

    md.append("### 公式 (3): 广义坐标向量\n")
    md.append(equation_block(q_latex))
    md.append("**物理含义**：将导轨平移与三个旋转关节统一到同一优化变量中，为 MPC/WBC 联合求解提供统一决策空间。\n")

    md.append("## 2. 雅可比矩阵自动求导\n")
    md.append("### 公式 (4): 雅可比定义\n")
    md.append(equation_block(j_def_latex))
    md.append("**物理含义**：\\(\\mathbf{J}\\) 建立足端速度 \\(\\dot{\\mathbf{p}}_{foot}\\) 与关节速度 \\(\\dot{\\mathbf{q}}\\) 的线性映射：\\(\\dot{\\mathbf{p}}_{foot}=\\mathbf{J}\\dot{\\mathbf{q}}\\)。\n")

    md.append("### 公式 (5): 3x4 解析雅可比\n")
    md.append(equation_block("\\mathbf{J}=" + J_latex))
    md.append("**物理含义（按列）**：\n")
    md.append("- 第 1 列：导轨平移对足端线速度的贡献。\n")
    md.append("- 第 2 列：侧摆角 \\(\\theta_1\\) 对平面内切向速度的贡献。\n")
    md.append("- 第 3 列：大腿俯仰角 \\(\\theta_2\\) 对前伸/抬落足速度分量的贡献。\n")
    md.append("- 第 4 列：小腿俯仰角 \\(\\theta_3\\) 对末端精细姿态与高度调节的贡献。\n")

    md.append("### 公式 (6): 导轨列向量（第一列）\n")
    md.append(equation_block(j_col1_latex))
    md.append("**学术意义（防侧翻与零空间避障）**：\n")
    md.append("1. 该列显示导轨 DOF 在笛卡尔空间提供了纯平移可控方向，使系统可在不显著改变腿部折叠姿态的情况下调整机身-落足相对位形。\n")
    md.append("2. 在窄窗框穿越中，该自由度可降低膝部扫掠体积，减少与上/下边缘干涉概率，从而提高防侧翻安全裕度。\n")
    md.append("3. 对 3x4 冗余系统，导轨列参与构成零空间：\\(\\dot{\\mathbf{q}}=\\mathbf{J}^+\\dot{\\mathbf{x}}+(\\mathbf{I}-\\mathbf{J}^+\\mathbf{J})\\dot{\\mathbf{q}}_0\\)。因此可将窗框间隙最大化、可操作度提升等次级目标注入 \\(\\dot{\\mathbf{q}}_0\\)，并在不破坏主任务（足端轨迹/受力）的前提下执行。\n")

    md.append("## 3. 论文撰写建议（章节归属与学术化表述）\n")
    md.append("### 建议章节放置\n")
    md.append("- **第 3 章：系统运动学建模**\n")
    md.append("  - 放置公式 (1)–(5)，强调导轨-旋转链解耦建模。\n")
    md.append("- **第 4 章：基于 WBC 的冗余分配与避障控制**\n")
    md.append("  - 放置公式 (6) 与零空间分解式，强调导轨自由度在次级任务优化中的作用。\n")

    md.append("### 可直接使用的学术化描述模板\n")
    md.append(
        "本文针对 dog2 单腿 4-DoF 机构，构建了包含直线导轨平移量 \\(s\\) 与三旋转关节角 \\(\\theta_1,\\theta_2,\\theta_3\\) 的统一运动学模型。"
        "通过符号求导获得 3x4 雅可比矩阵，揭示了导轨自由度在足端速度映射中的独立贡献。"
        "进一步地，基于冗余系统的零空间投影，将窗框间隙最大化与构型可操作度提升作为次级优化目标注入 WBC，"
        "从而在保持主任务可达性的同时显著降低狭窄环境中的碰撞与侧翻风险。\n"
    )

    md.append("## 4. 复现说明\n")
    md.append("在仓库根目录执行：\n")
    md.append("```bash\npython3 generate_jacobian_derivation.py\n```\n")
    md.append("将自动生成：`paper_formulas/jacobian_derivation.md`。\n")

    return "\n".join(md)


def main():
    model = build_symbolic_model()
    markdown = generate_markdown(model)

    output_dir = Path.cwd() / "paper_formulas"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "jacobian_derivation.md"
    output_file.write_text(markdown, encoding="utf-8")

    print(f"[OK] Wrote: {output_file}")


if __name__ == "__main__":
    main()
