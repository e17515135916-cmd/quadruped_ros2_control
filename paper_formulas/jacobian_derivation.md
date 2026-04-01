# dog2 单腿 4-DoF 雅可比推导（SymPy 自动生成）

本文档由 `generate_jacobian_derivation.py` 自动生成，用于论文中的运动学与 WBC 冗余控制推导。

## 1. 坐标与变量定义

- 机器人单腿广义坐标：\(\mathbf{q}=[s,\theta_1,\theta_2,\theta_3]^T\)。

- \(s\)：直线导轨位移（沿机身 x 方向）。

- \(\theta_1\)：髋侧摆角（影响足端在水平面内的方位）。

- \(\theta_2,\theta_3\)：大腿与小腿俯仰角（决定足端高度与前向伸展）。

- 连杆参数 \(l_1,l_2,l_3>0\) 分别对应髋偏置、股骨、胫骨等效长度。

### 公式 (1): 平面投影半径

$$
r = l_{1} + l_{2} \cos{\left(\theta_{2} \right)} + l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}
$$

**物理含义**：\(r\) 表示在给定俯仰构型 \(\theta_2,\theta_3\) 下，腿在水平面的等效伸展半径。

### 公式 (2): 足端正运动学（FK）

$$
\mathbf{p}_{foot} = \left[\begin{matrix}s + \left(l_{1} + l_{2} \cos{\left(\theta_{2} \right)} + l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}\right) \cos{\left(\theta_{1} \right)}\\\left(l_{1} + l_{2} \cos{\left(\theta_{2} \right)} + l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}\right) \sin{\left(\theta_{1} \right)}\\- l_{2} \sin{\left(\theta_{2} \right)} - l_{3} \sin{\left(\theta_{2} + \theta_{3} \right)}\end{matrix}\right]
$$

**物理含义**：

- 第 1 行（\(x\)）：由导轨平移 \(s\) 与旋转链投影 \(r\cos\theta_1\) 叠加得到。

- 第 2 行（\(y\)）：由侧摆角 \(\theta_1\) 产生的横向投影 \(r\sin\theta_1\)。

- 第 3 行（\(z\)）：由俯仰链 \(\theta_2,\theta_3\) 决定的垂向高度（向下取负号约定）。

### 公式 (3): 广义坐标向量

$$
\mathbf{q} = \left[\begin{matrix}s\\\theta_{1}\\\theta_{2}\\\theta_{3}\end{matrix}\right]
$$

**物理含义**：将导轨平移与三个旋转关节统一到同一优化变量中，为 MPC/WBC 联合求解提供统一决策空间。

## 2. 雅可比矩阵自动求导

### 公式 (4): 雅可比定义

$$
\mathbf{J} = \frac{\partial \mathbf{p}_{foot}}{\partial \mathbf{q}}
$$

**物理含义**：\(\mathbf{J}\) 建立足端速度 \(\dot{\mathbf{p}}_{foot}\) 与关节速度 \(\dot{\mathbf{q}}\) 的线性映射：\(\dot{\mathbf{p}}_{foot}=\mathbf{J}\dot{\mathbf{q}}\)。

### 公式 (5): 3x4 解析雅可比

$$
\mathbf{J}=\left[\begin{matrix}1 & - \left(l_{1} + l_{2} \cos{\left(\theta_{2} \right)} + l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}\right) \sin{\left(\theta_{1} \right)} & - \left(l_{2} \sin{\left(\theta_{2} \right)} + l_{3} \sin{\left(\theta_{2} + \theta_{3} \right)}\right) \cos{\left(\theta_{1} \right)} & - l_{3} \sin{\left(\theta_{2} + \theta_{3} \right)} \cos{\left(\theta_{1} \right)}\\0 & \left(l_{1} + l_{2} \cos{\left(\theta_{2} \right)} + l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}\right) \cos{\left(\theta_{1} \right)} & - \left(l_{2} \sin{\left(\theta_{2} \right)} + l_{3} \sin{\left(\theta_{2} + \theta_{3} \right)}\right) \sin{\left(\theta_{1} \right)} & - l_{3} \sin{\left(\theta_{1} \right)} \sin{\left(\theta_{2} + \theta_{3} \right)}\\0 & 0 & - l_{2} \cos{\left(\theta_{2} \right)} - l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)} & - l_{3} \cos{\left(\theta_{2} + \theta_{3} \right)}\end{matrix}\right]
$$

**物理含义（按列）**：

- 第 1 列：导轨平移对足端线速度的贡献。

- 第 2 列：侧摆角 \(\theta_1\) 对平面内切向速度的贡献。

- 第 3 列：大腿俯仰角 \(\theta_2\) 对前伸/抬落足速度分量的贡献。

- 第 4 列：小腿俯仰角 \(\theta_3\) 对末端精细姿态与高度调节的贡献。

### 公式 (6): 导轨列向量（第一列）

$$
\mathbf{j}_s = \left[\begin{matrix}1\\0\\0\end{matrix}\right]
$$

**学术意义（防侧翻与零空间避障）**：

1. 该列显示导轨 DOF 在笛卡尔空间提供了纯平移可控方向，使系统可在不显著改变腿部折叠姿态的情况下调整机身-落足相对位形。

2. 在窄窗框穿越中，该自由度可降低膝部扫掠体积，减少与上/下边缘干涉概率，从而提高防侧翻安全裕度。

3. 对 3x4 冗余系统，导轨列参与构成零空间：\(\dot{\mathbf{q}}=\mathbf{J}^+\dot{\mathbf{x}}+(\mathbf{I}-\mathbf{J}^+\mathbf{J})\dot{\mathbf{q}}_0\)。因此可将窗框间隙最大化、可操作度提升等次级目标注入 \(\dot{\mathbf{q}}_0\)，并在不破坏主任务（足端轨迹/受力）的前提下执行。

## 3. 论文撰写建议（章节归属与学术化表述）

### 建议章节放置

- **第 3 章：系统运动学建模**

  - 放置公式 (1)–(5)，强调导轨-旋转链解耦建模。

- **第 4 章：基于 WBC 的冗余分配与避障控制**

  - 放置公式 (6) 与零空间分解式，强调导轨自由度在次级任务优化中的作用。

### 可直接使用的学术化描述模板

本文针对 dog2 单腿 4-DoF 机构，构建了包含直线导轨平移量 \(s\) 与三旋转关节角 \(\theta_1,\theta_2,\theta_3\) 的统一运动学模型。通过符号求导获得 3x4 雅可比矩阵，揭示了导轨自由度在足端速度映射中的独立贡献。进一步地，基于冗余系统的零空间投影，将窗框间隙最大化与构型可操作度提升作为次级优化目标注入 WBC，从而在保持主任务可达性的同时显著降低狭窄环境中的碰撞与侧翻风险。

## 4. 复现说明

在仓库根目录执行：

```bash
python3 generate_jacobian_derivation.py
```

将自动生成：`paper_formulas/jacobian_derivation.md`。
