# MPC + WBC 分层控制架构与零空间冗余解析

## 四层控制架构图 (Hierarchical Control Architecture)

```mermaid
graph TB
    subgraph "规划层 Planning Layer - 10Hz"
        A[全局路径规划器<br/>Global Path Planner]
        B[窗框识别<br/>Window Detection]
        C[状态机<br/>State Machine]
        
        A --> C
        B --> C
        
        C1[平地 Trot 模式<br/>Trotting Gait]
        C2[穿窗 Crawl 模式<br/>Crawling Gait]
        
        C --> C1
        C --> C2
        
        style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
        style B fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
        style C fill:#bbdefb,stroke:#0d47a1,stroke-width:3px
        style C1 fill:#c5cae9,stroke:#283593,stroke-width:2px
        style C2 fill:#c5cae9,stroke:#283593,stroke-width:2px
    end

    subgraph "MPC 层 Model Predictive Control - 100Hz"
        D[MPC 优化器<br/>MPC Optimizer]
        E[动力学模型<br/>Dynamics Model]
        F[约束条件<br/>Constraints]
        
        D --> E
        D --> F
        
        G[地面反作用力 GRF<br/>Ground Reaction Forces<br/>未来 10 个周期]
        
        E --> G
        
        style D fill:#fff3e0,stroke:#e65100,stroke-width:3px
        style E fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px
        style F fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px
        style G fill:#ffcc80,stroke:#f57c00,stroke-width:3px
    end

    subgraph "WBC 层 Whole Body Control - 500Hz"
        H[全身控制器<br/>WBC Controller]
        I[任务优先级<br/>Task Hierarchy]
        
        H --> I
        
        subgraph "主任务 Primary Tasks"
            J1[足端轨迹跟踪<br/>Foot Trajectory Tracking]
            J2[质心稳定<br/>CoM Stabilization]
            J3[姿态控制<br/>Orientation Control]
        end
        
        subgraph "次级任务 Secondary Tasks - 零空间优化"
            K1[导轨优化<br/>Rail Optimization]
            K2[关节限位避让<br/>Joint Limit Avoidance]
            K3[能量最优<br/>Energy Minimization]
        end
        
        I --> J1
        I --> J2
        I --> J3
        I --> K1
        I --> K2
        I --> K3
        
        L[零空间投影<br/>Null Space Projection<br/>N = I - J†J]
        
        K1 --> L
        K2 --> L
        K3 --> L
        
        M[16 关节指令<br/>16-DOF Joint Commands<br/>4 导轨 + 12 旋转]
        
        J1 --> M
        J2 --> M
        J3 --> M
        L --> M
        
        style H fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
        style I fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
        style J1 fill:#a5d6a7,stroke:#43a047,stroke-width:2px
        style J2 fill:#a5d6a7,stroke:#43a047,stroke-width:2px
        style J3 fill:#a5d6a7,stroke:#43a047,stroke-width:2px
        style K1 fill:#ffccbc,stroke:#d84315,stroke-width:2px
        style K2 fill:#ffccbc,stroke:#d84315,stroke-width:2px
        style K3 fill:#ffccbc,stroke:#d84315,stroke-width:2px
        style L fill:#fff9c4,stroke:#f57f17,stroke-width:3px
        style M fill:#b2dfdb,stroke:#00695c,stroke-width:3px
    end

    subgraph "执行层 Execution Layer - 1000Hz"
        N[ros2_control 框架<br/>ROS 2 Control Framework]
        O[JointTrajectoryController<br/>关节轨迹控制器]
        P[ControllerManager<br/>控制器管理器]
        
        N --> O
        O --> P
        
        subgraph "双通道执行 Dual-Channel Execution"
            Q1[4 导轨静态锁定<br/>4 Rails: Static Lock<br/>位置: 0.0m]
            Q2[12 旋转关节动态执行<br/>12 Revolute: Dynamic<br/>力矩/位置指令]
        end
        
        P --> Q1
        P --> Q2
        
        R[Gazebo Fortress<br/>物理仿真引擎]
        
        Q1 --> R
        Q2 --> R
        
        style N fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px
        style O fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px
        style P fill:#ce93d8,stroke:#8e24aa,stroke-width:2px
        style Q1 fill:#ffebee,stroke:#c62828,stroke-width:2px
        style Q2 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
        style R fill:#bbdefb,stroke:#1976d2,stroke-width:3px
    end

    %% 层间数据流
    C1 -->|步态参数| D
    C2 -->|步态参数| D
    
    G -->|期望 GRF| H
    
    M -->|关节指令| N
    
    R -.->|状态反馈| H
    R -.->|状态反馈| D
    R -.->|状态反馈| C

    %% 频率标注
    note1[10 Hz<br/>规划周期]
    note2[100 Hz<br/>MPC 周期]
    note3[500 Hz<br/>WBC 周期]
    note4[1000 Hz<br/>执行周期]
    
    style note1 fill:#e1f5fe,stroke:#01579b
    style note2 fill:#fff3e0,stroke:#e65100
    style note3 fill:#f1f8e9,stroke:#33691e
    style note4 fill:#fce4ec,stroke:#880e4f
```

## 控制层级详细说明

### 第 1 层：规划层 (10Hz)
- **功能**：全局路径规划，环境感知，状态机切换
- **输入**：传感器数据（激光雷达、相机）
- **输出**：运动模式指令（Trot / Crawl）
- **关键技术**：
  - 窗框识别算法
  - 状态机设计（平地 ↔ 穿窗）
  - 路径规划算法

### 第 2 层：MPC 层 (100Hz)
- **功能**：预测未来轨迹，优化地面反作用力
- **输入**：期望速度、当前状态、步态模式
- **输出**：未来 10 个周期的 GRF
- **关键技术**：
  - 单刚体动力学模型
  - 二次规划（QP）求解器
  - 滚动时域优化

### 第 3 层：WBC 层 (500Hz) - 核心创新
- **功能**：全身控制，任务分配，冗余解析
- **输入**：期望 GRF、足端轨迹、当前状态
- **输出**：16 个关节的力矩/位置指令
- **关键技术**：
  - **任务优先级分层**
  - **零空间投影**（利用 4 个导轨的冗余自由度）
  - 动力学一致性控制

### 第 4 层：执行层 (1000Hz)
- **功能**：底层指令执行，硬件接口
- **输入**：关节指令
- **输出**：电机控制信号
- **关键技术**：
  - ros2_control 标准接口
  - 双通道物理隔离
  - 实时性保证

## 频率设计原理

| 层级 | 频率 | 原因 |
|------|------|------|
| 规划层 | 10Hz | 环境变化慢，降低计算负担 |
| MPC 层 | 100Hz | 平衡预测精度与实时性 |
| WBC 层 | 500Hz | 保证力控制的稳定性 |
| 执行层 | 1000Hz | 匹配电机控制器频率 |

## 数据流向与反馈

```
正向控制流：
规划层 → MPC 层 → WBC 层 → 执行层 → 物理仿真

反馈控制流：
物理仿真 → 状态估计 → WBC 层（闭环）
物理仿真 → 状态估计 → MPC 层（模型更新）
物理仿真 → 状态估计 → 规划层（任务完成检测）
```

## 创新点总结

1. **硬件创新**：4 个冗余导轨，增加工作空间
2. **算法创新**：零空间投影，优化导轨使用
3. **架构创新**：四层分层控制，职责清晰
4. **工程创新**：双通道物理隔离，提高鲁棒性

---

**适用场景**：PPT 幻灯片 3 - 分层控制架构
**展示重点**：MPC + WBC 理论深度 + 冗余导轨工程实践
