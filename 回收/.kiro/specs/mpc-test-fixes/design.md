# Design Document: MPC测试修复

## Overview

本设计文档描述了如何修复Dog2机器人MPC测试套件中的问题。主要问题包括：
1. test_basic_mpc使用12维状态，但MPC控制器期望16维扩展状态
2. test_16d_mpc中重力补偿计算不准确
3. 测试输出格式不够清晰

修复方案将确保所有测试使用正确的16维状态向量，修正重力补偿计算，并改进测试输出。

## Architecture

### 当前架构问题

```
test_basic_mpc.cpp
├── 创建12维状态向量 x0(12)  ❌ 错误
├── 创建12维参考轨迹 x_ref[k](12)  ❌ 错误
├── 调用 mpc_controller.solve(x0, u_optimal)  ❌ 维度不匹配
└── MPC控制器期望16维状态  ✅ 正确

test_16d_mpc.cpp
├── 创建16维状态向量 x0(16)  ✅ 正确
├── MPC求解成功  ✅ 正确
└── 重力补偿计算: 200N vs 115.758N  ❌ 过大
```

### 修复后架构

```
test_basic_mpc.cpp (修复后)
├── 创建16维状态向量 x0(16)  ✅
│   └── 前12维: SRBD状态
│   └── 后4维: 滑动副位置 (初始化为0)
├── 创建16维参考轨迹 x_ref[k](16)  ✅
│   └── 包含滑动副状态
├── 配置16×16 Q矩阵  ✅
├── 调用 mpc_controller.solve(x0, u_optimal)  ✅
└── 动力学积分保持16维  ✅

test_16d_mpc.cpp (修复后)
├── 创建16维状态向量  ✅
├── MPC求解  ✅
└── 重力补偿验证: ~115.758N ± 10N  ✅
```

## Components and Interfaces

### 1. 状态向量扩展工具

**功能**: 将12维SRBD状态扩展为16维扩展状态

```cpp
// 辅助函数：创建16维状态向量
Eigen::VectorXd create16DState(
    const Eigen::Vector3d& position,
    const Eigen::Vector3d& orientation,
    const Eigen::Vector3d& linear_velocity,
    const Eigen::Vector3d& angular_velocity,
    const Eigen::Vector4d& sliding_positions = Eigen::Vector4d::Zero()
) {
    Eigen::VectorXd x(16);
    x << position, orientation, linear_velocity, angular_velocity, sliding_positions;
    return x;
}
```

### 2. 测试配置结构

**功能**: 统一测试配置参数

```cpp
struct TestConfig {
    double mass = 11.8;  // kg
    double gravity = 9.81;  // m/s²
    double dt = 0.1;  // s
    int horizon = 6;
    
    // 权重矩阵 (16×16)
    Eigen::MatrixXd Q = Eigen::MatrixXd::Identity(16, 16);
    Eigen::MatrixXd R = Eigen::MatrixXd::Identity(12, 12);
    
    // 期望的重力补偿力
    double expected_hover_force() const {
        return mass * gravity;  // 115.758 N
    }
    
    double expected_leg_force() const {
        return expected_hover_force() / 4.0;  // 28.9395 N per leg
    }
};
```

### 3. 重力补偿验证器

**功能**: 验证MPC输出的力是否正确补偿重力

```cpp
struct GravityCompensationValidator {
    double mass;
    double gravity;
    double tolerance;  // 容差 (N)
    
    bool validate(const Eigen::VectorXd& u_optimal) {
        // 计算总垂直力
        double fz_total = 0.0;
        for (int i = 0; i < 4; ++i) {
            fz_total += u_optimal(i * 3 + 2);  // z分量
        }
        
        // 期望的重力补偿力
        double expected_force = mass * gravity;
        
        // 净垂直力（应该接近0）
        double net_force = fz_total - expected_force;
        
        // 输出诊断信息
        std::cout << "重力补偿验证:" << std::endl;
        std::cout << "  机器人重量: " << expected_force << " N" << std::endl;
        std::cout << "  总垂直力: " << fz_total << " N" << std::endl;
        std::cout << "  净垂直力: " << net_force << " N" << std::endl;
        std::cout << "  容差: ±" << tolerance << " N" << std::endl;
        
        bool valid = std::abs(net_force) < tolerance;
        std::cout << (valid ? "✅ 重力补偿正确" : "❌ 重力补偿错误") << std::endl;
        
        return valid;
    }
};
```

### 4. 测试输出格式化器

**功能**: 统一测试输出格式

```cpp
class TestReporter {
public:
    void printHeader(const std::string& test_name) {
        std::cout << "\n" << std::string(60, '=') << std::endl;
        std::cout << "  " << test_name << std::endl;
        std::cout << std::string(60, '=') << std::endl;
    }
    
    void printSection(const std::string& section_name) {
        std::cout << "\n--- " << section_name << " ---" << std::endl;
    }
    
    void printSuccess(const std::string& message) {
        std::cout << "✅ " << message << std::endl;
    }
    
    void printFailure(const std::string& message) {
        std::cout << "❌ " << message << std::endl;
    }
    
    void printWarning(const std::string& message) {
        std::cout << "⚠️  " << message << std::endl;
    }
    
    void printSummary(bool all_passed, int total_tests, int passed_tests) {
        std::cout << "\n" << std::string(60, '=') << std::endl;
        std::cout << "测试总结: " << passed_tests << "/" << total_tests << " 通过" << std::endl;
        if (all_passed) {
            std::cout << "✅ 所有测试通过！" << std::endl;
        } else {
            std::cout << "❌ 部分测试失败" << std::endl;
        }
        std::cout << std::string(60, '=') << std::endl;
    }
};
```

## Data Models

### 16维扩展状态向量

```
x ∈ ℝ¹⁶:
  x[0:3]   - 位置 [x, y, z] (m)
  x[3:6]   - 姿态 [roll, pitch, yaw] (rad)
  x[6:9]   - 线速度 [vx, vy, vz] (m/s)
  x[9:12]  - 角速度 [wx, wy, wz] (rad/s)
  x[12:16] - 滑动副位置 [j1, j2, j3, j4] (m)
```

### 控制输入向量

```
u ∈ ℝ¹²:
  u[0:3]   - 腿1足端力 [fx1, fy1, fz1] (N)
  u[3:6]   - 腿2足端力 [fx2, fy2, fz2] (N)
  u[6:9]   - 腿3足端力 [fx3, fy3, fz3] (N)
  u[9:12]  - 腿4足端力 [fx4, fy4, fz4] (N)
```

### 权重矩阵

```
Q ∈ ℝ¹⁶ˣ¹⁶ (状态权重):
  Q = diag([100, 100, 200,    // 位置权重 (z更高)
            50, 50, 50,        // 姿态权重
            10, 10, 10,        // 线速度权重
            5, 5, 5,           // 角速度权重
            20, 20, 20, 20])   // 滑动副权重

R ∈ ℝ¹²ˣ¹² (控制权重):
  R = 0.01 * I₁₂
```

## Correctness Properties

*属性是系统应该满足的特征或行为，本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 状态向量维度一致性

*For any* 测试中创建的状态向量、参考轨迹和权重矩阵，它们的维度必须与MPC控制器期望的维度一致：
- 状态向量和参考轨迹必须是16维
- Q矩阵必须是16×16
- R矩阵必须是12×12
- 控制输入必须是12维

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 6.1, 6.4**

### Property 2: 重力补偿正确性

*For any* 悬停状态（速度为0，加速度为0），MPC求解器输出的总垂直力应该在机器人重量的±10N范围内：
- 机器人重量 = 11.8 kg × 9.81 m/s² = 115.758 N
- 总垂直力 = Σ(fz_i) for i=1 to 4
- |总垂直力 - 115.758| < 10 N

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 3: 动力学参数一致性

*For any* 测试中的动力学积分，使用的物理参数必须与MPC控制器一致：
- 质量 = 11.8 kg
- 重力加速度 = 9.81 m/s²
- 时间步长 = dt (配置值)
- 惯性矩阵 = MPC使用的惯性矩阵

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 4: 滑动副状态初始化

*For any* 不使用滑动副功能的测试，16维状态向量的滑动副部分（x[12:16]）必须初始化为零向量，并在整个测试过程中保持为零（当滑动副速度为0时）。

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 5: 状态向量完整性

*For any* 动力学积分步骤，输入和输出的状态向量必须保持16维，且滑动副部分的更新必须正确：
- 输入状态维度 = 16
- 输出状态维度 = 16
- 滑动副位置更新: j_new = j_old + v_sliding * dt

**Validates: Requirements 4.4, 5.3**

## Error Handling

### 1. 维度不匹配错误

```cpp
if (x0.size() != 16) {
    std::cerr << "❌ 错误: 状态向量维度不匹配" << std::endl;
    std::cerr << "   期望维度: 16" << std::endl;
    std::cerr << "   实际维度: " << x0.size() << std::endl;
    return -1;
}
```

### 2. MPC求解失败

```cpp
if (!success) {
    std::cerr << "❌ MPC求解失败" << std::endl;
    std::cerr << "   OSQP状态码: " << mpc_controller.getSolveStatus() << std::endl;
    std::cerr << "   求解时间: " << mpc_controller.getSolveTime() << "ms" << std::endl;
    return -1;
}
```

### 3. 重力补偿异常

```cpp
if (!gravity_validator.validate(u_optimal)) {
    std::cerr << "⚠️  警告: 重力补偿可能不准确" << std::endl;
    std::cerr << "   这可能影响机器人的稳定性" << std::endl;
    // 不终止测试，但记录警告
}
```

### 4. 数值异常

```cpp
// 检查NaN或Inf
if (!x_current.allFinite()) {
    std::cerr << "❌ 错误: 状态向量包含NaN或Inf" << std::endl;
    std::cerr << "   状态: " << x_current.transpose() << std::endl;
    return -1;
}
```

## Testing Strategy

### 单元测试和属性测试的双重方法

本项目将使用单元测试和属性测试的组合来确保全面覆盖：

**单元测试**:
- 验证特定示例和边缘情况
- 测试集成点和错误条件
- 示例：测试特定的初始状态是否产生预期的控制输出

**属性测试**:
- 验证跨所有输入的通用属性
- 通过随机化提供全面的输入覆盖
- 示例：对于任何有效的16维状态，MPC求解器应该成功

### 属性测试配置

- 每个属性测试最少运行100次迭代（由于随机化）
- 每个测试必须引用其设计文档属性
- 标签格式: **Feature: mpc-test-fixes, Property {number}: {property_text}**

### 测试文件修改

#### test_basic_mpc.cpp
- **修改**: 将所有12维状态改为16维
- **单元测试**: 验证特定前进场景
- **属性测试**: 
  - Property 1: 状态维度一致性
  - Property 2: 重力补偿正确性
  - Property 3: 动力学参数一致性

#### test_16d_mpc.cpp
- **修改**: 修正重力补偿验证逻辑
- **单元测试**: 验证16维MPC基本功能
- **属性测试**:
  - Property 2: 重力补偿正确性
  - Property 4: 滑动副状态初始化

#### test_dynamics.cpp
- **验证**: 确认已使用正确参数（11.8 kg）
- **单元测试**: 验证动力学计算
- **属性测试**:
  - Property 3: 动力学参数一致性

#### test_sliding_constraints.cpp
- **验证**: 确认测试通过
- **单元测试**: 验证滑动副约束
- **属性测试**:
  - Property 4: 滑动副状态初始化
  - Property 5: 状态向量完整性

### 测试执行流程

```bash
# 1. 编译测试
colcon build --packages-select dog2_mpc

# 2. 运行所有测试
./test_dynamics
./build/dog2_mpc/test_basic_mpc
./build/dog2_mpc/test_16d_mpc
./build/dog2_mpc/test_sliding_constraints

# 3. 验证所有测试通过
# 期望输出: 所有测试都显示 ✅ 标记
```

### 成功标准

- 所有测试返回退出码0
- test_basic_mpc成功完成MPC控制循环
- test_16d_mpc的重力补偿验证通过
- 所有测试输出清晰的成功/失败标记
- 没有维度不匹配错误
- 没有NaN或Inf数值异常

## Implementation Notes

### 修改优先级

1. **P0 - 关键修复**:
   - test_basic_mpc.cpp: 状态向量维度修改
   - test_basic_mpc.cpp: 参考轨迹维度修改
   - test_basic_mpc.cpp: Q矩阵维度修改

2. **P1 - 重要改进**:
   - test_16d_mpc.cpp: 重力补偿验证逻辑
   - 所有测试: 添加TestReporter输出格式化

3. **P2 - 可选增强**:
   - 添加GravityCompensationValidator类
   - 添加create16DState辅助函数
   - 添加TestConfig结构

### 向后兼容性

- 修改后的测试仍然测试相同的功能
- 只是修正了状态维度和验证逻辑
- 不影响MPC控制器本身的实现

### 性能考虑

- 16维状态不会显著增加计算开销
- MPC求解时间应该保持在<10ms
- 测试执行时间应该保持在<5秒

## References

- URDF优化文档: `URDF_SYNC_FINAL_SUMMARY.md`
- MPC控制器实现: `src/dog2_mpc/src/mpc_controller.cpp`
- 扩展SRBD模型: `src/dog2_mpc/include/dog2_mpc/extended_srbd_model.hpp`
