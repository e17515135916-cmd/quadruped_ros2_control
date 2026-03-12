# Implementation Plan: Prismatic Coordinate System Fix

## Overview

修复 Dog2 机器人 Prismatic joint 坐标系问题的实施计划。核心任务是移除 Prismatic joint 的 `rpy="1.5708 0 0"` 旋转，重新计算所有后续关节的 origin，确保 HAA 关节垂直于 HFE/KFE 平面，实现 CHAMP 框架要求的正交关节配置。

## Tasks

- [ ] 1. 备份当前配置并设置开发环境
  - 创建 dog2.urdf.xacro 的备份文件（带时间戳）
  - 创建 Python 虚拟环境
  - 安装依赖：scipy, numpy, urdf_parser_py, lxml
  - 验证 RViz2 可以正常加载当前 URDF
  - _Requirements: All_

- [ ] 2. 分析当前坐标系配置
  - [ ] 2.1 编写脚本解析当前 URDF
    - 读取 dog2.urdf.xacro 并展开 xacro
    - 提取所有 Prismatic joints 的 origin（xyz 和 rpy）
    - 提取所有 HAA、HFE、KFE joints 的 origin
    - 保存当前配置到 JSON 文件
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.2 计算当前关节在世界坐标系中的位置
    - 使用 scipy.spatial.transform 计算变换矩阵
    - 对每条腿计算 HAA、HFE、KFE 在世界坐标系中的位置
    - 计算每个关节轴向在世界坐标系中的方向
    - 保存结果到 JSON 文件（作为参考基准）
    - _Requirements: 2.3, 3.3, 4.3_
  
  - [ ] 2.3 验证当前配置的问题
    - 计算 HAA 和 HFE 轴向的点积（应该不为 0，说明不正交）
    - 计算 HAA 和 KFE 轴向的点积（应该不为 0）
    - 生成诊断报告，确认问题存在
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 3. 计算新的坐标变换
  - [ ] 3.1 编写坐标变换计算脚本
    - 实现 JointOrigin 和 LegConfiguration 数据类
    - 实现坐标变换矩阵计算函数
    - 实现旋转补偿计算函数
    - _Requirements: 1.1, 2.1, 3.1, 4.1_
  
  - [ ] 3.2 计算 Leg 1 (Front Left) 的新配置
    - 移除 Prismatic rpy（设为 0 0 0）
    - 计算 HAA joint 的新 xyz（考虑坐标轴交换）
    - 计算 HAA joint 的新 rpy（移除补偿旋转）
    - 计算 HFE joint 的新 xyz 和 rpy
    - 计算 KFE joint 的新 xyz 和 rpy（如需要）
    - 验证计算结果：HAA axis 在世界坐标系中应为 (0, 0, 1)
    - _Requirements: 1.1, 2.1, 2.2, 2.4, 3.1, 3.2, 3.4, 4.1, 4.2, 4.4_
  
  - [ ] 3.3 计算 Leg 2 (Front Right) 的新配置
    - 应用与 Leg 1 相同的变换逻辑
    - 考虑左右对称性（mirror 参数）
    - 验证计算结果
    - _Requirements: 1.1, 2.1, 2.2, 2.4, 3.1, 3.2, 3.4, 4.1, 4.2, 4.4, 7.4_
  
  - [ ] 3.4 计算 Leg 3 (Rear Left) 的新配置
    - 注意后腿的特殊配置（hip_joint_rpy="0 0 0"）
    - 应用坐标变换
    - 验证计算结果
    - _Requirements: 1.1, 2.1, 2.2, 2.4, 3.1, 3.2, 3.4, 4.1, 4.2, 4.4, 7.5_
  
  - [ ] 3.5 计算 Leg 4 (Rear Right) 的新配置
    - 应用与 Leg 3 相同的变换逻辑
    - 考虑左右对称性
    - 验证计算结果
    - _Requirements: 1.1, 2.1, 2.2, 2.4, 3.1, 3.2, 3.4, 4.1, 4.2, 4.4, 7.5_
  
  - [ ] 3.6 生成新配置摘要报告
    - 列出所有变更的 joint origins
    - 对比修改前后的世界坐标系位置
    - 验证所有关节位置误差 < 1mm
    - 保存报告到文件
    - _Requirements: 6.2, 7.1, 7.2, 7.3_

- [ ] 4. 修改 URDF 文件
  - [ ] 4.1 更新 leg macro 的 Prismatic joint
    - 在 leg macro 中找到 Prismatic joint 定义
    - 将 `<origin rpy="${origin_rpy}" .../>` 改为 `<origin rpy="0 0 0" .../>`
    - 注意：保持 xyz 不变
    - _Requirements: 1.1, 1.2_
  
  - [ ] 4.2 更新 leg macro 的 HAA joint
    - 更新 HAA joint 的 origin xyz（使用计算结果）
    - 更新 HAA joint 的 origin rpy（使用计算结果）
    - 保持 axis="0 0 1" 不变
    - 保持 limits 不变
    - _Requirements: 2.1, 2.2, 2.4, 2.5_
  
  - [ ] 4.3 更新 leg macro 的 HFE joint
    - 更新 HFE joint 的 origin xyz（如需要）
    - 更新 HFE joint 的 origin rpy（使用计算结果）
    - 保持 axis="-1 0 0" 不变
    - 保持 limits 不变
    - _Requirements: 3.1, 3.2, 3.4, 3.5_
  
  - [ ] 4.4 更新 leg macro 的 KFE joint
    - 更新 KFE joint 的 origin xyz（如需要）
    - 更新 KFE joint 的 origin rpy（如需要）
    - 保持 axis="-1 0 0" 不变
    - 保持 limits 不变
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  
  - [ ] 4.5 更新所有 leg 实例化
    - 更新 Leg 1 实例化：移除 origin_rpy 参数或设为 "0 0 0"
    - 更新 Leg 2 实例化：移除 origin_rpy 参数或设为 "0 0 0"
    - 更新 Leg 3 实例化：移除 origin_rpy 参数或设为 "0 0 0"
    - 更新 Leg 4 实例化：移除 origin_rpy 参数或设为 "0 0 0"
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 4.6 验证 URDF 语法
    - 运行 `xacro dog2.urdf.xacro > /tmp/dog2_fixed.urdf`
    - 运行 `check_urdf /tmp/dog2_fixed.urdf`
    - 确认没有语法错误
    - _Requirements: All_

- [ ] 5. Checkpoint - RViz 初步验证
  - 启动 RViz 并加载修改后的 URDF
  - 检查零位姿态是否与原设计相似
  - 如果姿态完全错误，回到步骤 3 重新计算
  - 如果姿态基本正确但有偏差，继续到步骤 6 进行微调
  - _Requirements: 6.1, 8.1_

- [ ] 6. 编写单元测试
  - [ ] 6.1 测试 Prismatic RPY 移除
    - 解析修改后的 URDF
    - 验证所有 Prismatic joints 的 rpy 为 (0, 0, 0)
    - _Requirements: 1.1_
  
  - [ ] 6.2 测试关节轴向
    - 计算每个关节在世界坐标系中的轴向
    - 验证 HAA axis ≈ (0, 0, 1)，误差 < 0.01
    - 验证 HFE axis ≈ (±1, 0, 0)，误差 < 0.01
    - 验证 KFE axis ≈ (±1, 0, 0)，误差 < 0.01
    - _Requirements: 2.4, 3.4, 4.4_
  
  - [ ] 6.3 测试关节正交性
    - 计算 HAA 和 HFE 轴向的点积
    - 验证点积 ≈ 0，误差 < 0.01（正交）
    - 计算 HAA 和 KFE 轴向的点积
    - 验证点积 ≈ 0，误差 < 0.01（正交）
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.4 测试关节位置保持
    - 计算每个关节在世界坐标系中的位置
    - 与原始配置（步骤 2.2 的结果）对比
    - 验证误差 < 1mm
    - _Requirements: 6.2_
  
  - [ ] 6.5 测试 ROS 2 Control 配置
    - 验证所有 joint names 未改变
    - 验证所有 joint limits 未改变
    - 验证所有 joint interfaces 未改变
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 7. 编写基于属性的测试
  - [ ] 7.1 Property Test: Prismatic RPY Removed
    - **Property 1: Prismatic RPY Removed**
    - 解析 URDF 并验证所有 Prismatic joints 的 rpy = (0, 0, 0)
    - _Requirements: 1.1_
  
  - [ ] 7.2 Property Test: Joint Axes Orthogonality
    - **Property 4-6: Joint orthogonality**
    - 对每条腿计算 HAA、HFE、KFE 在世界坐标系中的轴向
    - 验证 HAA ⊥ HFE（点积 ≈ 0）
    - 验证 HAA ⊥ KFE（点积 ≈ 0）
    - 验证 HFE ∥ KFE（点积 ≈ ±1）
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 7.3 Property Test: Joint Position Preservation
    - **Property 7: Joint position preservation**
    - 对每条腿计算所有关节在世界坐标系中的位置
    - 与原始配置对比
    - 验证误差 < 1mm
    - _Requirements: 2.3, 3.3, 4.3, 6.2_
  
  - [ ] 7.4 Property Test: Joint Names Unchanged
    - **Property 12: Joint names unchanged**
    - 解析 URDF 并验证所有 joint names 未改变
    - _Requirements: 9.1, 10.1_
  
  - [ ] 7.5 Property Test: Joint Limits Unchanged
    - **Property 13: Joint limits unchanged**
    - 解析 URDF 并验证所有 joint limits 未改变
    - _Requirements: 9.4, 9.5_

- [ ] 8. Checkpoint - 确保所有测试通过
  - 运行所有单元测试
  - 运行所有基于属性的测试
  - 确认所有测试通过，如有问题请询问用户

- [ ] 9. RViz 详细验证和微调
  - [ ] 9.1 验证零位姿态
    - 在 RViz 中加载修改后的 URDF
    - 设置所有关节为零位
    - 对比原始设计的零位姿态
    - 如有偏差，记录需要调整的参数
    - _Requirements: 6.1, 8.1_
  
  - [ ] 9.2 验证 HAA 关节运动
    - 使用 joint_state_publisher_gui 控制 HAA 关节
    - 验证腿部左右摆动（abduction/adduction）
    - 验证运动方向正确（正值 = 外展）
    - 如运动方向错误，调整 axis 或 origin rpy
    - _Requirements: 2.5, 8.2_
  
  - [ ] 9.3 验证 HFE 关节运动
    - 使用 joint_state_publisher_gui 控制 HFE 关节
    - 验证腿部前后摆动（flexion/extension）
    - 验证运动方向正确
    - 如运动方向错误，调整 axis 或 origin rpy
    - _Requirements: 3.5, 8.3_
  
  - [ ] 9.4 验证 KFE 关节运动
    - 使用 joint_state_publisher_gui 控制 KFE 关节
    - 验证小腿折叠运动
    - 验证运动方向正确
    - 如运动方向错误，调整 axis 或 origin rpy
    - _Requirements: 4.5, 8.4_
  
  - [ ] 9.5 验证关节独立性
    - 同时移动 HAA 和 HFE
    - 验证运动相互独立（正交）
    - 验证没有意外的耦合
    - _Requirements: 8.5_
  
  - [ ] 9.6 微调 origin 参数（如需要）
    - 如果视觉外观或运动方向有偏差
    - 逐步调整 joint origin xyz 或 rpy
    - 每次调整后重新加载 URDF 验证
    - 记录最终的调整值
    - _Requirements: 6.1, 6.3_

- [ ] 10. TF Tree 分析
  - 发布 robot_description 到 ROS 2
  - 运行 `ros2 run tf2_tools view_frames`
  - 生成 TF tree PDF
  - 验证坐标系关系正确
  - 验证没有断裂的 TF 链
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 11. Gazebo 集成测试
  - 在 Gazebo 中加载修改后的机器人
  - 验证物理仿真正常
  - 测试关节控制
  - 验证碰撞检测正常
  - _Requirements: 6.4_

- [ ] 12. 生成迁移文档
  - 记录所有修改的 joint origins
  - 创建修改前后对比表
  - 说明坐标变换计算方法
  - 提供 RViz 验证步骤
  - 记录遇到的问题和解决方案
  - _Requirements: All_

- [ ] 13. 最终验证
  - 运行完整的测试套件
  - 在 RViz 中进行最终验证
  - 生成测试报告
  - 确认所有 requirements 都已满足
  - _Requirements: All_

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快开发
- 每个任务都引用了具体的需求以便追溯
- Checkpoint 任务确保增量验证
- 坐标变换计算是关键步骤，需要仔细验证
- RViz 验证是必须的，用于确认视觉外观和运动方向
- 如果计算结果不正确，可以在 RViz 中实验性地调整参数
- 保持备份，以便随时回退

## 关键提示

1. **坐标轴交换**：移除 Prismatic 的 `Rot_x(90°)` 后，原来的 y 和 z 轴会交换
   - 原 HAA xyz: `(-0.016, 0.0199, 0.080)`
   - 新 HAA xyz: `(-0.016, -0.080, 0.0199)` （y 和 z 交换，y 取负）

2. **RPY 补偿**：移除 Prismatic 的旋转后，需要调整后续关节的 rpy
   - 原 HAA rpy: `(-1.5708, 0, 0)` 用于抵消 Prismatic 的旋转
   - 新 HAA rpy: `(0, 0, 0)` 或其他值（需要实验确定）

3. **验证方法**：使用 RViz 是最直观的验证方法
   - 零位姿态应该与原设计匹配
   - 关节运动方向应该正确
   - 如有偏差，逐步调整 origin 参数

4. **前后腿差异**：前腿和后腿的配置可能不同
   - 前腿：`hip_joint_rpy="-1.5708 0 0"`
   - 后腿：`hip_joint_rpy="0 0 0"`
   - 需要分别计算和验证
