# Implementation Plan: Dog2 可视化系统

## Overview

实现完整的 Dog2 可视化系统，包括 RViz2 3D 可视化、Gazebo 环境增强、实时数据图表和性能监控。使用 Python 实现可视化节点，利用 ROS 2 的 visualization_msgs 和 RViz2 Marker API。

## Tasks

- [x] 1. 创建项目结构和基础配置
  - 创建 dog2_visualization 包
  - 设置 package.xml 和 setup.py
  - 创建 RViz2 配置文件目录
  - 创建 Gazebo 世界文件目录
  - _Requirements: 1.5, 5.1, 5.4_

- [x] 2. 实现核心可视化节点
  - [x] 2.1 创建 VisualizationNode 基类
    - 初始化 ROS 2 节点
    - 设置订阅器（odom, joint_states, foot_forces）
    - 设置发布器（MarkerArray）
    - 实现定时器回调（20Hz）
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 2.2 编写 VisualizationNode 单元测试
    - 测试节点初始化
    - 测试订阅器创建
    - 测试发布器创建
    - _Requirements: 1.1_

- [x] 3. 实现足端力可视化
  - [x] 3.1 实现 FootForceVisualizer 类
    - 创建力箭头 Marker
    - 实现力到颜色的映射（绿/黄/红）
    - 实现力数值标签
    - 处理非接触状态（隐藏/淡化）
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 3.2 编写足端力可视化属性测试
    - **Property 2: Foot force arrow visualization**
    - **Property 3: Force color encoding**
    - **Property 4: Non-contact force hiding**
    - **Property 5: Force value labels**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [ ] 4. 实现轨迹可视化
  - [ ] 4.1 实现 TrajectoryVisualizer 类
    - 创建轨迹点缓冲区（最大100点）
    - 实现历史轨迹绘制（蓝色）
    - 实现规划轨迹绘制（绿色）
    - 实现足端轨迹绘制
    - 实现缓冲区管理（FIFO）
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 4.2 编写轨迹可视化属性测试
    - **Property 6: Trajectory point accumulation**
    - **Property 7: Reference trajectory visualization**
    - **Property 8: Trajectory color distinction**
    - **Property 9: Foot trajectory tracking**
    - **Property 10: Trajectory buffer management**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [ ] 5. 检查点 - 基础可视化测试
  - 确保所有测试通过，询问用户是否有问题

- [ ] 6. 实现接触状态可视化
  - [ ] 6.1 实现 ContactMarkerVisualizer 类
    - 创建接触状态球体标记（绿色/红色）
    - 实现接触状态文本显示
    - 实现实时更新
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 6.2 编写接触状态属性测试
    - **Property 11: Contact marker color**
    - **Property 12: Contact state updates**
    - **Validates: Requirements 4.1, 4.2, 4.3_

- [ ] 7. 实现滑动副状态可视化
  - [ ] 7.1 实现 SlidingJointVisualizer 类
    - 创建滑动副位置文本标记
    - 实现警告级别计算（正常/警告/危险）
    - 实现颜色编码（绿/黄/红）
    - 显示运动范围指示器
    - 显示对称性状态
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 7.2 编写滑动副可视化属性测试
    - **Property 13: Sliding joint position display**
    - **Property 14: Sliding joint warning colors**
    - **Validates: Requirements 6.1, 6.2, 6.3**

- [ ] 8. 实现性能监控面板
  - [ ] 8.1 实现 PerformanceMonitor 类
    - 订阅性能相关话题
    - 创建文本面板 Marker
    - 实现 1Hz 更新
    - 实现 MPC 失败警告（红色）
    - 显示所有性能指标
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 8.2 编写性能监控属性测试
    - **Property 17: Performance metrics update rate**
    - **Property 18: MPC failure warning**
    - **Validates: Requirements 10.2, 10.3**

- [ ] 9. 检查点 - 核心功能测试
  - 确保所有测试通过，询问用户是否有问题

- [ ] 10. 实现越障可视化
  - [ ] 10.1 实现 CrossingVisualizationNode 类
    - 订阅越障状态话题
    - 创建阶段文本标记
    - 实现阶段颜色编码
    - 创建窗框模型标记
    - 实现腿部高亮
    - 显示混合构型状态
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 10.2 编写越障可视化属性测试
    - **Property 15: Crossing stage visualization**
    - **Property 16: Leg highlight during crossing**
    - **Validates: Requirements 9.1, 9.2, 9.4**

- [ ] 11. 创建 RViz2 配置文件
  - [ ] 11.1 创建 dog2_walking.rviz
    - 配置机器人模型显示
    - 配置 TF 显示
    - 配置 Marker 显示
    - 设置俯视图相机
    - _Requirements: 1.5, 8.4_

  - [ ] 11.2 创建 dog2_crossing.rviz
    - 基于 walking 配置
    - 添加越障特定的 Marker
    - 调整相机视角
    - _Requirements: 1.5, 8.4_

  - [ ] 11.3 创建 dog2_debug.rviz
    - 显示所有可用的可视化
    - 添加调试面板
    - _Requirements: 1.5_

- [ ] 12. 创建 Gazebo 世界文件
  - [ ] 12.1 创建 dog2_flat.world
    - 添加网格地面
    - 添加距离标记
    - 设置光照
    - _Requirements: 5.1, 5.3_

  - [ ] 12.2 创建 dog2_crossing.world
    - 基于 flat world
    - 添加窗框障碍物模型
    - _Requirements: 5.2_

  - [ ] 12.3 创建 dog2_terrain.world
    - 添加斜坡和台阶
    - _Requirements: 5.4_

- [ ] 13. 创建启动文件
  - [ ] 13.1 创建 visualization.launch.py
    - 启动 Gazebo（可选世界文件）
    - 启动 RViz2（可选配置文件）
    - 启动可视化节点
    - 启动 PlotJuggler（可选）
    - 支持模式参数（walking/crossing）
    - 打印使用说明
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 13.2 编写启动文件测试
    - 测试参数解析
    - 测试节点启动
    - _Requirements: 8.1, 8.3_

- [ ] 14. 创建 PlotJuggler 配置
  - [ ] 14.1 创建 dog2_performance.xml
    - 配置高度曲线
    - 配置姿态曲线（roll, pitch, yaw）
    - 配置 MPC 求解时间曲线
    - 配置足端力曲线
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 15. 集成测试
  - [ ]* 15.1 完整系统集成测试
    - 启动完整可视化系统
    - 验证所有节点正常运行
    - 验证 RViz2 显示正确
    - 验证 Gazebo 加载正确
    - _Requirements: 8.1, 8.2_

  - [ ]* 15.2 行走模式集成测试
    - 启动行走模式
    - 发送速度命令
    - 验证轨迹绘制
    - 验证接触标记交替
    - _Requirements: 3.1, 4.1, 4.2_

  - [ ]* 15.3 越障模式集成测试
    - 启动越障模式
    - 触发越障序列
    - 验证阶段标记更新
    - 验证窗框可见
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 16. 文档和示例
  - [ ] 16.1 创建 README.md
    - 安装说明
    - 快速开始指南
    - 使用示例
    - 故障排查

  - [ ] 16.2 创建示例脚本
    - test_visualization.sh
    - record_demo.sh

- [ ] 17. 最终检查点
  - 确保所有测试通过，询问用户是否有问题

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求，便于追溯
- 检查点确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证特定示例和边界情况
