# Dog2越障功能设计文档（开发指导）

> 来源：`回收/.kiro/specs/dog2-crossing/design.md`
> 说明：该文件用于主开发目录下的工程指导。

## 概述

Dog2越障功能实现了四足机器人穿越窗型障碍物的能力。该系统利用机器人独特的纵向滑动副机构和肘/膝构型切换能力，通过8个精心设计的阶段，实现了创新的混合构型动态行走越障策略。

核心创新点：
- **滑动副辅助穿越**：利用滑动副实现机身前探和腿部快速穿越
- **空中变构技术**：在腿部穿越过程中切换构型，避开窗框边缘
- **混合构型动态行走**：前腿膝式+后腿肘式的不对称步态，实现窗框约束下的行走

## 架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Dog2越障控制系统                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │ Crossing State   │      │ Hybrid Gait      │            │
│  │ Machine          │◄────►│ Generator        │            │
│  │ (9 stages)       │      │ (Mixed config)   │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                         │                        │
│           │ constraints             │ reference              │
│           │ target state            │ trajectory             │
│           ▼                         ▼                        │
│  ┌──────────────────────────────────────────┐               │
│  │      MPC Controller (16D Extended)       │               │
│  │  ┌────────────────────────────────────┐  │               │
│  │  │  Extended SRBD Model               │  │               │
│  │  │  (12D SRBD + 4D Sliding Joints)    │  │               │
│  │  └────────────────────────────────────┘  │               │
│  │  ┌────────────────────────────────────┐  │               │
│  │  │  OSQP Solver                       │  │               │
│  │  │  - Dynamics constraints            │  │               │
│  │  │  - Sliding joint constraints       │  │               │
│  │  │  - Control constraints             │  │               │
│  │  └────────────────────────────────────┘  │               │
│  └──────────────────┬───────────────────────┘               │
│                     │                                         │
│                     ▼                                         │
│           ┌──────────────────┐                               │
│           │  Optimal Control │                               │
│           │  (12D forces)    │                               │
│           └──────────────────┘                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
Sensor Data → Robot State → Crossing State Machine → Constraints
                    ↓                                      ↓
              Hybrid Gait Generator → Reference Trajectory
                                            ↓
                                    MPC Controller
                                            ↓
                                   Optimal Control → Actuators
```

## 组件和接口

### 1. CrossingStateMachine

**职责**：管理越障过程的9个阶段转换，为每个阶段提供约束和目标状态。

**接口**：
```cpp
class CrossingStateMachine {
public:
    // 初始化越障功能
    void initialize(const RobotState& initial_state, 
                   const WindowObstacle& window);
    
    // 更新状态机（检查转换条件）
    bool update(const RobotState& current_state, double dt);
    
    // 获取当前状态
    CrossingState getCurrentState() const;
    
    // 获取目标状态
    RobotState getTargetState() const;
    
    // 获取当前阶段的约束
    StageConstraints getCurrentConstraints() const;
    
    // 获取越障进度（0-1）
    double getProgress() const;
};
```

**9个越障阶段**：
1. **APPROACH**：初始接近（正常Trot步态，速度0.2 m/s）
2. **BODY_FORWARD_SHIFT**：机身前探（滑动副伸展，机身前移0.111m）
3. **FRONT_LEGS_TRANSIT**：前腿穿越（腿1和腿4逐一穿越，肘式→膝式）
4. **HYBRID_GAIT_WALKING**：混合构型行走（前腿膝式+后腿肘式，速度0.1 m/s）
5. **RAIL_ALIGNMENT**：精确停车定位（后腿滑动副前端穿过窗框）
6. **REAR_LEGS_TRANSIT**：后腿穿越（腿2和腿3逐一穿越，肘式→膝式）
7. **ALL_KNEE_STATE**：全膝式状态（临时状态，准备恢复）
8. **RECOVERY**：恢复常态（膝式→肘式，滑动副收缩）
9. **CONTINUE_FORWARD**：继续前进（恢复正常Trot步态）

### 2. HybridGaitGenerator

**职责**：生成混合构型步态，处理前后腿不同的运动参数。

**接口**：
```cpp
class HybridGaitGenerator {
public:
    // 初始化步态生成器
    void initialize(const RobotState& initial_state);
    
    // 生成正常Trot步态
    GaitState generateNormalTrotGait(
        const RobotState& current_state,
        const Eigen::Vector3d& desired_velocity,
        double dt);
    
    // 生成混合构型Trot步态（核心创新）
    GaitState generateHybridTrotGait(
        const RobotState& current_state,
        const Eigen::Vector3d& desired_velocity,
        double dt);
};
```

**混合构型参数**：
- 前腿（膝式）：步长0.08m，步高0.08m，工作空间偏后
- 后腿（肘式）：步长0.12m，步高0.10m，工作空间偏前
- 步态类型：Trot对角线步态
- 腿间最小距离：0.15m

### 3. MPCController (16维扩展)

**职责**：使用模型预测控制生成最优足端力，支持16维扩展状态。

**接口**：
```cpp
class MPCController {
public:
    // 初始化越障功能
    void initializeCrossing(
        const CrossingStateMachine::RobotState& initial_state,
        const CrossingStateMachine::WindowObstacle& window);
    
    // 更新越障状态
    bool updateCrossing(
        const CrossingStateMachine::RobotState& current_state, 
        double dt);
    
    // 求解MPC（16维扩展状态）
    bool solve(const Eigen::VectorXd& x0, Eigen::VectorXd& u_optimal);
    
    // 获取当前越障状态
    CrossingState getCurrentCrossingState() const;
    
    // 获取越障进度
    double getCrossingProgress() const;
    
private:
    // 生成越障参考轨迹（12维SRBD）
    std::vector<Eigen::VectorXd> generateCrossingReference(
        const CrossingStateMachine::RobotState& current_state, 
        double dt);
    
    // 更新越障状态（扩展12维→16维）
    void updateCrossingState(const Eigen::VectorXd& x0);
};
```

**16维扩展状态**：
```
x = [x, y, z,           // 位置 (3)
     roll, pitch, yaw,  // 姿态 (3)
     vx, vy, vz,        // 线速度 (3)
     wx, wy, wz,        // 角速度 (3)
     d1, d2, d3, d4]    // 滑动副位置 (4)
```

**12维控制**：
```
u = [f1x, f1y, f1z,     // 腿1足端力 (3)
     f2x, f2y, f2z,     // 腿2足端力 (3)
     f3x, f3y, f3z,     // 腿3足端力 (3)
     f4x, f4y, f4z]     // 腿4足端力 (3)
```

### 4. ExtendedSRBDModel

**职责**：扩展的单刚体动力学模型，包含滑动副。

**接口**：
```cpp
class ExtendedSRBDModel {
public:
    // 离散动力学：x_{k+1} = f(x_k, u_k, v_k)
    void discreteDynamics(
        const Eigen::VectorXd& x,      // 16维状态
        const Eigen::VectorXd& u,      // 12维控制
        const Eigen::MatrixXd& foot_positions,
        const Eigen::Vector4d& sliding_velocity,
        double dt,
        Eigen::VectorXd& x_next);
    
    // 线性化：A, B, C矩阵
    void linearize(
        const Eigen::VectorXd& x,
        const Eigen::VectorXd& u,
        const Eigen::MatrixXd& foot_positions,
        const Eigen::Vector4d& sliding_velocity,
        double dt,
        Eigen::MatrixXd& A,  // 16×16
        Eigen::MatrixXd& B,  // 16×12
        Eigen::MatrixXd& C); // 16×4
};
```

## 数据模型

### RobotState
```cpp
struct RobotState {
    Eigen::Vector3d position;              // 质心位置
    Eigen::Vector3d orientation;           // 姿态（roll, pitch, yaw）
    Eigen::Vector3d velocity;              // 线速度
    Eigen::Vector3d angular_velocity;      // 角速度
    Eigen::Vector4d sliding_positions;     // 滑动副位置
    Eigen::Vector4d sliding_velocities;    // 滑动副速度
    std::array<LegConfiguration, 4> leg_configs;  // 腿部构型
    std::array<Eigen::Vector3d, 4> foot_positions; // 足端位置
    std::array<bool, 4> foot_contacts;     // 足端接触状态
};
```

### WindowObstacle
```cpp
struct WindowObstacle {
    double x_position;    // 窗框x位置
    double width;         // 宽度
    double height;        // 高度
    double bottom_height; // 底部高度
    double top_height;    // 顶部高度
};
```

### StageConstraints
```cpp
struct StageConstraints {
    Eigen::Vector4d sliding_min;      // 滑动副最小位置
    Eigen::Vector4d sliding_max;      // 滑动副最大位置
    Eigen::Vector4d sliding_vel_max;  // 滑动副最大速度
    double min_leg_distance;          // 腿间最小距离
    Eigen::Vector3d com_min;          // 质心最小位置
    Eigen::Vector3d com_max;          // 质心最大位置
    std::array<Eigen::Vector3d, 4> foot_workspace_min;  // 足端工作空间最小
    std::array<Eigen::Vector3d, 4> foot_workspace_max;  // 足端工作空间最大
};
```

## 正确性属性

*正确性属性是系统应该满足的形式化规范，通过属性测试来验证。*

### 属性1：状态转换单调性
*对于任意*越障过程，状态机只能向前转换，不能回退到之前的状态。

**验证**: 需求1.2

### 属性2：滑动副位置限位
*对于任意*滑动副控制指令，滑动副位置必须在限位范围内。

**验证**: 需求2.1

### 属性3：滑动副对称性
*对于任意*时刻，左右对称的滑动副位置差值必须小于容差（|d1-d3| < 0.02m, |d2-d4| < 0.02m）。

**验证**: 需求2.3

### 属性4：MPC求解成功性
*对于任意*有效的16维初始状态和参考轨迹，MPC求解器应该返回成功状态。

**验证**: 需求6.6

### 属性5：参考轨迹维度一致性
*对于任意*越障状态，生成的参考轨迹必须是16维扩展状态。

**验证**: 需求7.5

### 属性6：混合构型腿间距离
*对于任意*混合构型行走时刻，前后腿之间的距离必须大于安全距离0.15m。

**验证**: 需求5.4

### 属性7：质心稳定性
*对于任意*越障时刻，质心投影必须在支撑多边形内。

**验证**: 需求9.1

### 属性8：姿态角度限制
*对于任意*越障时刻，机身姿态角度必须在安全范围内（|roll| < 10°, |pitch| < 10°）。

**验证**: 需求9.2

## 错误处理

### MPC求解失败
- **检测**：OSQP求解器返回非成功状态码
- **处理**：记录错误信息，返回失败状态，保持上一次的控制输出
- **恢复**：调整约束参数，重新尝试求解

### 状态转换条件不满足
- **检测**：长时间停留在同一状态
- **处理**：记录警告信息，继续等待条件满足
- **恢复**：提供手动强制转换接口

### 滑动副超限
- **检测**：滑动副位置或速度超出限制
- **处理**：限幅到安全范围内
- **恢复**：调整控制指令，逐步恢复到正常范围

### 腿间碰撞风险
- **检测**：前后腿距离小于安全距离
- **处理**：调整足端轨迹，增大腿间距离
- **恢复**：重新规划步态

## 测试策略

### 单元测试
- **CrossingStateMachine测试**：
  - 状态转换逻辑
  - 完成条件检查
  - 约束生成
  
- **HybridGaitGenerator测试**：
  - 正常步态生成
  - 混合步态生成
  - 足端轨迹计算

- **MPCController测试**：
  - 越障初始化
  - 参考轨迹生成
  - MPC求解
  - 状态更新

### 属性测试
每个正确性属性都应该有对应的属性测试：

- **属性1测试**：生成随机越障序列，验证状态只能向前转换
- **属性2测试**：生成随机滑动副指令，验证位置在限位内
- **属性3测试**：生成随机滑动副状态，验证对称性
- **属性4测试**：生成随机初始状态，验证MPC求解成功
- **属性5测试**：生成随机越障状态，验证参考轨迹维度
- **属性6测试**：生成随机混合构型状态，验证腿间距离
- **属性7测试**：生成随机越障状态，验证质心稳定性
- **属性8测试**：生成随机越障状态，验证姿态角度

### 集成测试
- **完整越障流程测试**：
  - 从APPROACH到CONTINUE_FORWARD的完整流程
  - 验证所有阶段转换正确
  - 验证最终状态符合预期

- **简化场景测试**：
  - 简化参数（horizon=5, dt=0.1）
  - 快速验证核心功能
  - 用于回归测试

### 测试配置
- **属性测试迭代次数**：最少100次
- **测试标签格式**：`Feature: dog2-crossing, Property N: [property_text]`
- **测试覆盖率目标**：100%

## 实现注意事项

### 数值稳定性
- 避免等式约束，使用不等式约束并留出余量
- BODY_FORWARD_SHIFT状态：前腿滑动副约束留出11mm余量
- 滑动副速度限制使用软约束

### 维度一致性
- `generateCrossingReference`返回12维SRBD状态
- `updateCrossingState`负责扩展为16维（添加滑动副目标）
- MPC内部统一使用16维扩展状态

### 性能优化
- 约束矩阵使用稀疏存储（稀疏度<2%）
- 线性化矩阵缓存复用
- OSQP求解器参数调优

### 安全保障
- 所有约束都有安全余量
- 关键状态转换需要多个条件同时满足
- 提供紧急停止和手动干预接口
