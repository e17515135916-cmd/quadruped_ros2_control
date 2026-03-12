# Requirements Document: MPC测试修复

## Introduction

修复Dog2机器人MPC测试套件中的问题，确保所有测试都能正确运行并通过。当前测试存在状态维度不匹配和重力补偿计算问题。

## Glossary

- **MPC_Controller**: 模型预测控制器，负责计算最优控制输入
- **SRBD_Model**: 单刚体动力学模型，12维状态空间
- **Extended_SRBD_Model**: 扩展单刚体动力学模型，16维状态空间（包含4个滑动副）
- **State_Vector**: 状态向量，描述机器人的位置、姿态、速度等
- **Gravity_Compensation**: 重力补偿，足端力需要抵消机器人重力

## Requirements

### Requirement 1: 状态维度一致性

**User Story:** 作为MPC开发者，我希望所有测试使用正确的状态维度，以便测试能够正常运行。

#### Acceptance Criteria

1. WHEN test_basic_mpc初始化状态向量 THEN THE System SHALL使用16维扩展状态（12维SRBD + 4维滑动副）
2. WHEN test_basic_mpc设置参考轨迹 THEN THE System SHALL使用16维参考状态向量
3. WHEN test_basic_mpc调用solve方法 THEN THE System SHALL传递16维状态向量
4. WHEN 任何测试创建状态向量 THEN THE System SHALL确保维度与MPC控制器期望一致

### Requirement 2: 重力补偿正确性

**User Story:** 作为MPC开发者，我希望MPC求解器能够正确计算重力补偿，以便机器人能够稳定悬停。

#### Acceptance Criteria

1. WHEN MPC求解悬停状态 THEN THE System SHALL计算的总垂直力应接近机器人重量（115.758 N）
2. WHEN 机器人质量为11.8 kg THEN THE System SHALL每条腿的垂直力应约为28.9395 N（115.758/4）
3. WHEN MPC求解完成 THEN THE System SHALL净垂直力（总垂直力-重力）应小于10 N
4. WHEN 测试验证重力补偿 THEN THE System SHALL输出的垂直加速度应接近0

### Requirement 3: 测试输出清晰性

**User Story:** 作为MPC开发者，我希望测试输出清晰明确，以便快速识别问题。

#### Acceptance Criteria

1. WHEN 测试开始 THEN THE System SHALL输出测试名称和配置参数
2. WHEN 测试失败 THEN THE System SHALL输出详细的错误信息和失败原因
3. WHEN 测试成功 THEN THE System SHALL输出✅标记和关键性能指标
4. WHEN 测试完成 THEN THE System SHALL输出测试总结和通过/失败状态

### Requirement 4: 动力学积分一致性

**User Story:** 作为MPC开发者，我希望测试中的动力学积分与MPC内部模型一致，以便验证控制效果。

#### Acceptance Criteria

1. WHEN test_basic_mpc进行动力学积分 THEN THE System SHALL使用与MPC相同的质量参数（11.8 kg）
2. WHEN 计算加速度 THEN THE System SHALL正确应用重力（-9.81 m/s²）
3. WHEN 更新速度 THEN THE System SHALL使用正确的时间步长（dt）
4. WHEN 积分状态 THEN THE System SHALL保持16维状态向量的完整性

### Requirement 5: 滑动副状态初始化

**User Story:** 作为MPC开发者，我希望测试正确初始化滑动副状态，以便16维MPC能够正常工作。

#### Acceptance Criteria

1. WHEN 测试初始化16维状态 THEN THE System SHALL将滑动副位置初始化为0
2. WHEN 测试设置参考轨迹 THEN THE System SHALL在参考轨迹中包含滑动副状态
3. WHEN 测试不使用滑动副 THEN THE System SHALL保持滑动副位置为0但仍使用16维状态
4. WHEN 测试调用setSlidingVelocity THEN THE System SHALL传递4维滑动副速度向量

### Requirement 6: MPC权重矩阵配置

**User Story:** 作为MPC开发者，我希望测试使用合理的权重矩阵，以便MPC能够产生合理的控制输出。

#### Acceptance Criteria

1. WHEN 配置Q矩阵 THEN THE System SHALL使用16×16维度（不是12×12）
2. WHEN 设置位置权重 THEN THE System SHALL对z方向使用更高权重（保持高度）
3. WHEN 设置滑动副权重 THEN THE System SHALL使用适中权重（避免不必要的滑动）
4. WHEN 配置R矩阵 THEN THE System SHALL使用12×12维度（控制输入维度）

### Requirement 7: 测试覆盖完整性

**User Story:** 作为MPC开发者，我希望测试覆盖所有关键功能，以便确保系统可靠性。

#### Acceptance Criteria

1. WHEN 运行test_dynamics THEN THE System SHALL验证基本动力学计算正确
2. WHEN 运行test_basic_mpc THEN THE System SHALL验证16维MPC基本功能
3. WHEN 运行test_16d_mpc THEN THE System SHALL验证16维MPC求解和预测
4. WHEN 运行test_sliding_constraints THEN THE System SHALL验证滑动副约束正确性
5. WHEN 所有测试运行 THEN THE System SHALL全部通过并输出成功标记

### Requirement 8: 错误处理和诊断

**User Story:** 作为MPC开发者，我希望测试能够捕获和报告错误，以便快速定位问题。

#### Acceptance Criteria

1. WHEN MPC求解失败 THEN THE System SHALL输出OSQP求解器状态码
2. WHEN 状态维度不匹配 THEN THE System SHALL输出期望维度和实际维度
3. WHEN 重力补偿异常 THEN THE System SHALL输出期望值和实际值的差异
4. WHEN 测试异常终止 THEN THE System SHALL返回非零退出码

## Notes

- 所有测试必须使用16维扩展状态，即使不使用滑动副功能
- 重力补偿是MPC正确性的关键指标
- 测试应该能够独立运行，不依赖外部环境
- 测试输出应该清晰、一致、易于理解
