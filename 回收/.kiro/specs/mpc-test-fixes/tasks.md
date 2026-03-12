# Implementation Plan: MPC测试修复

## Overview

修复Dog2机器人MPC测试套件中的问题，确保所有测试使用正确的16维状态向量，修正重力补偿计算，并改进测试输出格式。

## Tasks

- [x] 1. 修复test_basic_mpc状态维度问题
  - [x] 1.1 将状态向量从12维改为16维
    - 修改x0初始化为Eigen::VectorXd(16)
    - 添加滑动副位置初始化（后4维设为0）
    - _Requirements: 1.1, 5.1_
  
  - [x] 1.2 修改参考轨迹为16维
    - 修改x_ref[k]为16维向量
    - 在参考轨迹中添加滑动副状态（设为0）
    - _Requirements: 1.2, 5.2_
  
  - [x] 1.3 更新Q权重矩阵为16×16
    - 修改Q矩阵维度从12×12到16×16
    - 添加滑动副权重（对角元素12-15）
    - _Requirements: 6.1, 6.3_
  
  - [x] 1.4 修改动力学积分保持16维状态
    - 确保x_next也是16维
    - 添加滑动副状态更新（保持为0，因为速度为0）
    - _Requirements: 4.4, 5.3_

- [x] 2. 添加测试辅助工具
  - [x] 2.1 创建状态向量辅助函数
    - 实现create16DState()函数
    - 简化16维状态创建
    - _Requirements: 1.1, 5.1_
  
  - [x] 2.2 创建TestConfig结构
    - 定义统一的测试配置参数
    - 包含质量、重力、时间步长等
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 2.3 实现GravityCompensationValidator类
    - 验证重力补偿是否正确
    - 输出详细的诊断信息
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 2.4 实现TestReporter类
    - 统一测试输出格式
    - 提供printHeader, printSuccess, printFailure等方法
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3. 修复test_16d_mpc重力补偿验证
  - [x] 3.1 更新重力补偿验证逻辑
    - 使用GravityCompensationValidator
    - 设置合理的容差（±10 N）
    - _Requirements: 2.1, 2.3_
  
  - [x] 3.2 改进诊断输出
    - 使用TestReporter格式化输出
    - 清晰显示期望值vs实际值
    - _Requirements: 3.1, 3.3, 8.3_

- [x] 4. 验证test_dynamics参数正确性
  - [x] 4.1 确认质量参数为11.8 kg
    - 检查代码中的质量值
    - 确保与URDF一致
    - _Requirements: 4.1_
  
  - [x] 4.2 确认重力加速度为9.81 m/s²
    - 检查重力常数
    - 确保计算正确
    - _Requirements: 4.2_

- [x] 5. 改进所有测试的输出格式
  - [x] 5.1 在test_basic_mpc中使用TestReporter
    - 添加清晰的测试头部
    - 使用✅/❌标记
    - _Requirements: 3.1, 3.3, 3.4_
  
  - [x] 5.2 在test_16d_mpc中使用TestReporter
    - 统一输出格式
    - 改进可读性
    - _Requirements: 3.1, 3.3, 3.4_
  
  - [x] 5.3 在test_dynamics中使用TestReporter
    - 保持一致的输出风格
    - _Requirements: 3.1, 3.3, 3.4_

- [ ] 6. 添加错误处理和诊断
  - [ ] 6.1 添加维度检查
    - 在solve()调用前检查状态维度
    - 输出详细的错误信息
    - _Requirements: 8.2_
  
  - [ ] 6.2 添加MPC求解失败处理
    - 输出OSQP状态码
    - 提供调试信息
    - _Requirements: 8.1_
  
  - [ ] 6.3 添加数值异常检查
    - 检查NaN和Inf
    - 及时终止异常测试
    - _Requirements: 8.4_

- [x] 7. Checkpoint - 编译和基本测试
  - 编译所有修改的测试文件
  - 运行test_dynamics验证基础功能
  - 确保没有编译错误
  - 如有问题，询问用户

- [x] 8. 运行和验证所有测试
  - [x] 8.1 运行test_dynamics
    - 验证动力学计算正确
    - 确认重力补偿测试通过
    - _Requirements: 7.1_
  
  - [x] 8.2 运行test_basic_mpc
    - 验证16维MPC基本功能
    - 确认MPC求解成功
    - 验证控制循环完成
    - _Requirements: 7.2_
  
  - [x] 8.3 运行test_16d_mpc
    - 验证16维MPC求解
    - 确认重力补偿验证通过
    - _Requirements: 7.3_
  
  - [x] 8.4 运行test_sliding_constraints
    - 验证滑动副约束正确
    - 确认所有子测试通过
    - _Requirements: 7.4_

- [x] 9. Final Checkpoint - 验证所有测试通过
  - 确认所有测试返回退出码0
  - 确认所有测试输出✅成功标记
  - 确认没有维度不匹配错误
  - 确认重力补偿验证通过
  - 如有问题，询问用户

- [ ] 10. 更新文档
  - [ ] 10.1 创建测试修复总结文档
    - 记录所有修改
    - 记录测试结果
    - 提供使用指南
  
  - [ ] 10.2 更新URDF_SYNC_FINAL_SUMMARY.md
    - 添加测试验证结果
    - 更新成功标准检查列表

## Notes

- 所有测试必须使用16维扩展状态，即使不使用滑动副功能
- 重力补偿是MPC正确性的关键指标，必须验证通过
- 测试输出应该清晰、一致、易于理解
- 修改后的测试应该能够独立运行，不依赖外部环境
- 编译命令: `colcon build --packages-select dog2_mpc`
- 测试命令: `./test_dynamics && ./build/dog2_mpc/test_basic_mpc && ./build/dog2_mpc/test_16d_mpc && ./build/dog2_mpc/test_sliding_constraints`
