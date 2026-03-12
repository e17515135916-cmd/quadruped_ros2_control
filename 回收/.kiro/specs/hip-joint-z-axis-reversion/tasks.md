# Implementation Plan: Hip Joint Axis Change (Z to X)

## Overview

本实施计划将髋关节（j11, j21, j31, j41）从 z 轴旋转改为 x 轴旋转。实施策略是通过 Python 脚本自动修改 URDF Xacro 文件中的 `hip_axis` 参数，并通过完整的测试验证修改的正确性。

## Tasks

- [x] 1. 创建备份和准备工作
  - 创建 `dog2.urdf.xacro` 的时间戳备份
  - 验证源文件存在且可读
  - 创建测试输出目录
  - _Requirements: 5.3, 5.4_

- [x] 2. 实现参数修改脚本
  - [x] 2.1 编写 Python 脚本读取和解析 xacro 文件
    - 使用 lxml 解析 XML
    - 定位四个 leg 实例化语句
    - _Requirements: 5.1, 5.2_

  - [x] 2.2 实现 hip_axis 参数查找和替换逻辑
    - 查找每个 leg 的 `hip_axis` 参数
    - 将值从 "0 0 -1" 替换为 "1 0 0"
    - 保持其他所有内容不变
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.2_

  - [x] 2.3 实现文件写入和备份功能
    - 写入修改后的内容到原文件
    - 保留原始文件权限和格式
    - _Requirements: 5.3_

  - [x] 2.4 编写单元测试验证脚本功能
    - 测试文件读取
    - 测试参数定位
    - 测试参数替换
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. 验证 URDF 语法和结构
  - [x] 3.1 运行 xacro 编译生成 URDF
    - 命令：`xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf`
    - 验证编译成功无错误
    - _Requirements: 1.5_

  - [x] 3.2 运行 check_urdf 验证 URDF 有效性
    - 命令：`check_urdf /tmp/dog2_test.urdf`
    - 验证 URDF 结构正确
    - _Requirements: 1.5_

  - [x] 3.3 解析生成的 URDF 验证 axis 属性
    - 使用 urdf_parser_py 解析 URDF
    - 验证 j11, j21, j31, j41 的 axis 为 [1, 0, 0]
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 3.4 编写 property test 验证 hip axis 配置一致性
    - **Property 1: Hip Axis Configuration Consistency**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [x] 3.5 编写 property test 验证视觉模型保持不变
    - **Property 3: Visual Model Preservation**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

  - [x] 3.6 编写 property test 验证碰撞模型保持不变
    - **Property 4: Collision Model Preservation**
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [x] 3.7 编写 property test 验证关节限位保持不变
    - **Property 5: Joint Limits Preservation**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 4. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

- [x] 5. 在 RViz 中验证修改
  - [x] 5.1 启动 RViz 加载修改后的机器人模型
    - 使用 robot_state_publisher 发布机器人状态
    - 在 RViz 中显示机器人模型
    - _Requirements: 6.1_

  - [x] 5.2 使用 joint_state_publisher_gui 测试髋关节运动
    - 调整 j11, j21, j31, j41 的角度
    - 观察髋关节是否绕 x 轴旋转（前后摆动）
    - _Requirements: 6.2_

  - [x] 5.3 验证视觉外观保持不变
    - 对比修改前后的视觉外观
    - 确认视觉模型没有变化
    - _Requirements: 6.5, 2.3_

  - [x] 5.4 创建 RViz 验证脚本
    - 自动化 RViz 验证过程
    - 生成验证报告
    - _Requirements: 6.1, 6.2_

- [ ] 6. 在 Gazebo 中验证修改
  - [ ] 6.1 启动 Gazebo 加载修改后的机器人模型
    - 使用 ros2 launch 启动 Gazebo 仿真
    - 确认机器人模型正确加载
    - _Requirements: 6.3_

  - [ ] 6.2 通过 ROS 2 topic 控制髋关节
    - 发布关节命令到 /joint_trajectory_controller/joint_trajectory
    - 观察髋关节运动
    - _Requirements: 6.4_

  - [ ] 6.3 验证髋关节绕 x 轴旋转
    - 确认髋关节前后摆动
    - 确认运动范围符合限位
    - _Requirements: 6.4_

  - [ ] 6.4 验证碰撞检测正常工作
    - 测试髋关节在运动范围内无异常碰撞
    - 确认碰撞模型保持不变
    - _Requirements: 3.2, 3.3_

  - [ ] 6.5 创建 Gazebo 验证脚本
    - 自动化 Gazebo 验证过程
    - 生成验证报告
    - _Requirements: 6.3, 6.4_

- [ ] 7. Final checkpoint - 确保所有验证通过
  - 确保所有测试和验证通过，如有问题请询问用户

## Notes

- 所有任务都是必需的，确保全面测试和验证
- 每个任务都引用了具体的需求以确保可追溯性
- Checkpoint 任务确保增量验证
- Property tests 验证通用正确性属性
- Unit tests 验证特定示例和边界情况
