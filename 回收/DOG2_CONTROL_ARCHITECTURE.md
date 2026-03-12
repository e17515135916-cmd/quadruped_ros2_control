# Dog2机器人控制架构

## 系统架构流程图

```mermaid
graph TB
    %% 样式定义
    classDef decisionLayer fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    classDef dynamicsLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef kinematicsLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef outputLayer fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    
    %% 决策层 - 横向排列
    subgraph Decision["🎯 决策层 High-Level Decision"]
        direction LR
        D1["用户指令 Twist"]
        D2["跨越策略 FSM"]
        D3["输出: 目标速度 + 足端轨迹 + 导轨位置"]
        D1 --> D3
        D2 --> D3
    end
    
    %% 动力学层 - 横向排列
    subgraph Dynamics["🧠 动力学层 MPC Brain - Dynamics"]
        direction LR
        M1["Convex MPC<br/>预测优化"]
        M2["状态估计<br/>传感器融合"]
        M3["质心动力学<br/>CoM优化"]
        M4["输出: GRF<br/>地面反作用力"]
        M1 --> M3
        M2 --> M3
        M3 --> M4
    end
    
    %% 运动学层 - 横向排列
    subgraph Kinematics["🦾 运动学层 WBC/IK - Kinematics"]
        direction LR
        K1["解耦IK<br/>Decoupled"]
        K2["1-Prismatic<br/>工作空间拓展"]
        K3["3-Revolute<br/>XYY姿态"]
        K4["输出: 16关节指令<br/>位置/速度/力矩"]
        K1 --> K2
        K1 --> K3
        K2 --> K4
        K3 --> K4
    end
    
    %% 执行层 - 横向排列
    subgraph Execution["⚙️ 执行层 Hardware Execution"]
        direction LR
        E1["16关节电机<br/>4腿×4DOF"]
        E2["🤖 Dog2机器人"]
        E1 --> E2
    end
    
    %% 层间数据流
    Decision --> Dynamics
    Dynamics --> Kinematics
    Kinematics --> Execution
    
    %% 反馈回路
    E2 -.->|传感器反馈| M2
    
    %% 应用样式
    class D1,D2,D3 decisionLayer
    class M1,M2,M3,M4 dynamicsLayer
    class K1,K2,K3,K4 kinematicsLayer
    class E1,E2 outputLayer
```

## 三层架构说明

### 🎯 决策层 (1-10 Hz)
**输入**：用户指令 (Twist) + 跨越策略 (FSM)  
**输出**：目标速度、足端轨迹、导轨预置位  
**功能**：高层规划、步态切换、障碍跨越

### 🧠 动力学层 (10-50 Hz)
**输入**：目标速度、足端轨迹  
**输出**：地面反作用力 (GRF)  
**功能**：
- Convex MPC：预测优化
- 状态估计：传感器融合
- 质心动力学：力分配优化

### 🦾 运动学层 (100-1000 Hz)
**输入**：地面反作用力  
**输出**：16个关节位置/速度/力矩指令  
**功能**：
- 解耦式IK：降低计算复杂度
- 1-Prismatic：工作空间拓展 (X轴滑动)
- 3-Revolute：姿态调整 (XYY: Roll-Pitch-Pitch)

### ⚙️ 执行层 (1000+ Hz)
**组件**：16个关节电机 (4腿 × 4DOF)  
**反馈**：关节状态、IMU、接触力

## 数据流

```
用户指令 → 决策 → 动力学 → 运动学 → 执行 → 机器人
            ↑                              ↓
            └────────── 传感器反馈 ─────────┘
```

## 关键特性

| 特性 | 说明 |
|------|------|
| **分层架构** | 解耦设计、模块化、易扩展 |
| **4-DOF配置** | 1-P工作空间拓展 + 3-R姿态调整 |
| **实时性能** | MPC快速优化、解耦IK、并行计算 |
| **鲁棒性** | 多传感器融合、约束处理、故障恢复 |

## 实现文件

- **决策层**：`src/dog2_champ_config/`
- **动力学层**：`src/dog2_mpc/`
- **运动学层**：`src/dog2_kinematics/leg_ik_4dof.*`
- **执行层**：`src/dog2_description/`

## 总结

Dog2采用**三层控制架构**实现从用户指令到机器人执行的完整控制流程，核心创新是4-DOF腿部配置（1-Prismatic + 3-Revolute），提供更大工作空间和更好地形适应能力。
