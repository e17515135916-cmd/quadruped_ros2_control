# Implementation Plan: Presentation Visualization System

## Overview

本实现计划将演示数据采集与可视化系统分解为离散的编码任务。系统采用模块化设计，每个可视化功能独立实现，可单独调用或批量执行。实现顺序遵循依赖关系：首先建立基础设施（配置管理、数据模型），然后实现各个可视化模块，最后集成批量执行和预览功能。

## Tasks

- [x] 1. 建立项目结构和基础设施
  - 创建 Python 包结构 `presentation_viz/`
  - 设置依赖管理（requirements.txt 或 pyproject.toml）
  - 创建配置文件模板（config.yaml）
  - 实现日志系统
  - _Requirements: 9.1, 9.5_

- [x] 1.1 编写项目结构单元测试
  - 测试包导入
  - 测试配置文件模板生成
  - _Requirements: 9.1_

- [x] 2. 实现配置管理模块
  - [x] 2.1 实现 ConfigManager 类
    - 实现 YAML 配置文件加载
    - 实现默认配置值
    - 实现配置验证（颜色代码、文件路径、数值范围）
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 2.2 编写 ConfigManager 属性测试
    - **Property 19: Configuration Loading Robustness**
    - **Validates: Requirements 9.1**

  - [x] 2.3 编写 ConfigManager 属性测试
    - **Property 20: Configuration Application**
    - **Validates: Requirements 9.2, 9.3, 9.4**

  - [x] 2.4 编写 ConfigManager 属性测试
    - **Property 21: Default Configuration Fallback**
    - **Validates: Requirements 9.5**

  - [x] 2.5 编写 ConfigManager 单元测试
    - 测试加载有效配置文件
    - 测试处理缺失配置文件
    - 测试处理无效 YAML 语法
    - 测试配置值验证
    - _Requirements: 9.1, 9.5_

- [x] 3. 实现数据模型
  - [x] 3.1 实现 URDFModel 数据类
    - 定义 Joint 和 Link dataclass
    - 实现 URDFModel 容器类
    - _Requirements: 2.1_

  - [x] 3.2 实现 TimeSeriesData 数据类
    - 定义 TimeSeriesData dataclass
    - 实现数据访问方法（get_variable, get_time_range）
    - 实现重采样方法
    - _Requirements: 1.4, 1.5_

  - [x] 3.3 实现 WorkspaceData 数据类
    - 定义 WorkspaceData dataclass
    - 实现平面投影方法
    - _Requirements: 3.1, 3.2_

  - [x] 3.4 编写数据模型单元测试
    - 测试数据类创建和访问
    - 测试数据转换方法
    - _Requirements: 2.1, 3.1_

- [x] 4. 实现 ROS2 数据采集模块
  - [x] 4.1 实现 ROS2DataCollector 类
    - 初始化 ROS2 节点
    - 实现话题订阅功能
    - 实现数据缓冲和时间戳记录
    - 实现 CSV 导出功能
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 4.2 编写 ROS2DataCollector 属性测试
    - **Property 1: Topic Subscription Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - **PBT Status: ✅ PASSED (8/8 tests)**

  - [x] 4.3 编写 ROS2DataCollector 属性测试
    - **Property 2: Timestamp Monotonicity**
    - **Validates: Requirements 1.4**

  - [x] 4.4 编写 ROS2DataCollector 属性测试
    - **Property 3: Data Persistence Round-Trip**
    - **Validates: Requirements 1.5**
    - **PBT Status: ✅ PASSED (5/5 tests)**

  - [x] 4.5 编写 ROS2DataCollector 单元测试
    - 测试话题订阅失败处理
    - 测试数据缓冲溢出保护
    - 测试 CSV 文件格式
    - _Requirements: 1.1, 1.5_

- [x] 5. 检查点 - 确保基础设施测试通过
  - 确保所有测试通过，如有问题请询问用户
  - **Status: ✅ ALL TESTS PASSED (113/113 tests)**

- [ ] 6. 实现运动学简图生成器
  - [ ] 6.1 实现 URDF 解析功能
    - 使用 urdfpy 或 xml.etree 解析 URDF/Xacro
    - 提取关节和连杆信息
    - 构建关节树结构
    - _Requirements: 2.1_

  - [ ] 6.2 实现正运动学计算
    - 实现 DH 参数或变换矩阵方法
    - 计算各连杆在世界坐标系中的位置
    - _Requirements: 2.2_

  - [ ] 6.3 实现 2D 投影和绘图
    - 实现 3D 到 2D 投影（侧视图、俯视图）
    - 使用 Matplotlib 绘制骨架线条
    - 绘制关节圆圈和标注
    - 添加坐标系标注
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

  - [ ] 6.4 实现 KinematicDiagramGenerator 主类
    - 整合解析、计算和绘图功能
    - 实现配置应用（样式、视角）
    - 实现图像输出
    - _Requirements: 2.1, 2.2, 2.6_

  - [ ]* 6.5 编写 KinematicDiagramGenerator 属性测试
    - **Property 4: URDF Parsing Completeness**
    - **Validates: Requirements 2.1**

  - [ ]* 6.6 编写 KinematicDiagramGenerator 属性测试
    - **Property 5: Image Generation Success**
    - **Validates: Requirements 2.2**

  - [ ]* 6.7 编写 KinematicDiagramGenerator 单元测试
    - 测试解析 Dog2 URDF
    - 测试坐标系标注
    - 测试关节角度标注
    - _Requirements: 2.1, 2.3, 2.5_

- [ ] 7. 实现工作空间分析器
  - [ ] 7.1 实现工作空间计算
    - 实现网格搜索算法
    - 计算可达工作空间点云
    - 计算凸包边界
    - _Requirements: 3.1, 3.2_

  - [ ] 7.2 实现工作空间对比可视化
    - 绘制普通工作空间和扩展工作空间
    - 使用不同颜色和透明度
    - 添加标注和图例
    - _Requirements: 3.3, 3.4, 3.5_

  - [ ] 7.3 实现 WorkspaceAnalyzer 主类
    - 整合计算和可视化功能
    - 实现配置应用
    - 实现图像输出
    - _Requirements: 3.1, 3.2, 3.3, 3.6_

  - [ ]* 7.4 编写 WorkspaceAnalyzer 属性测试
    - **Property 7: Workspace Extension Property**
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 7.5 编写 WorkspaceAnalyzer 单元测试
    - 测试工作空间计算
    - 测试边界提取
    - 测试颜色区分
    - _Requirements: 3.1, 3.4_

- [ ] 8. 实现 ROS 通信图生成器
  - [ ] 8.1 实现节点和连接管理
    - 实现节点添加和定位
    - 实现连接添加和路由
    - _Requirements: 4.1, 4.2_

  - [ ] 8.2 实现图形绘制
    - 绘制节点框
    - 绘制连接箭头和标签
    - 实现自动布局算法
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 8.3 实现 ROSGraphGenerator 主类
    - 整合节点管理和绘图功能
    - 实现配置应用
    - 实现图像输出
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ]* 8.4 编写 ROSGraphGenerator 属性测试
    - **Property 8: Graph Connectivity Preservation**
    - **Validates: Requirements 4.1, 4.2**

  - [ ]* 8.5 编写 ROSGraphGenerator 单元测试
    - 测试节点创建
    - 测试连接绘制
    - 测试标签添加
    - _Requirements: 4.1, 4.3_

- [ ] 9. 实现状态机可视化器
  - [ ] 9.1 实现状态和转换管理
    - 实现状态添加和定位
    - 实现转换添加
    - 实现圆形布局算法
    - _Requirements: 5.1, 5.2_

  - [ ] 9.2 实现状态机绘制
    - 绘制状态圆圈和标签
    - 绘制转换箭头
    - 添加机器人姿态图标（可选）
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 9.3 实现 FSMVisualizer 主类
    - 整合状态管理和绘图功能
    - 实现配置应用
    - 实现图像输出
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ]* 9.4 编写 FSMVisualizer 属性测试
    - **Property 9: FSM State Completeness**
    - **Validates: Requirements 5.1, 5.3**

  - [ ]* 9.5 编写 FSMVisualizer 属性测试
    - **Property 10: FSM Transition Completeness**
    - **Validates: Requirements 5.2**

  - [ ]* 9.6 编写 FSMVisualizer 单元测试
    - 测试状态创建
    - 测试转换绘制
    - 测试标签添加
    - _Requirements: 5.1, 5.3_

- [ ] 10. 检查点 - 确保所有可视化器测试通过
  - 确保所有测试通过，如有问题请询问用户

- [ ] 11. 实现关键帧提取器
  - [ ] 11.1 实现窗口查找和截图功能
    - 使用 python-xlib 或 pyautogui 查找 Gazebo 窗口
    - 实现屏幕截图功能
    - _Requirements: 6.1_

  - [ ] 11.2 实现定时截图调度
    - 实现 ROS2 时钟同步
    - 在指定时间点触发截图
    - _Requirements: 6.2_

  - [ ] 11.3 实现图像后处理
    - 添加时间戳标注
    - 实现关键帧拼接
    - _Requirements: 6.3, 6.4, 6.5_

  - [ ] 11.4 实现 KeyframeExtractor 主类
    - 整合截图和后处理功能
    - 实现配置应用
    - 实现图像输出
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 11.5 编写 KeyframeExtractor 属性测试
    - **Property 11: Keyframe Timestamp Correspondence**
    - **Validates: Requirements 6.2, 6.4**

  - [ ]* 11.6 编写 KeyframeExtractor 属性测试
    - **Property 12: Keyframe Strip Composition**
    - **Validates: Requirements 6.5**

  - [ ]* 11.7 编写 KeyframeExtractor 单元测试
    - 测试窗口查找
    - 测试时间戳标注
    - 测试图像拼接
    - _Requirements: 6.1, 6.4_

- [ ] 12. 实现数据曲线图生成器
  - [ ] 12.1 实现 CSV 数据加载
    - 使用 Pandas 读取 CSV
    - 实现数据验证
    - _Requirements: 7.1_

  - [ ] 12.2 实现曲线图绘制
    - 绘制时序曲线
    - 添加坐标轴标签和单位
    - 添加网格线
    - 应用专业配色方案
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [ ] 12.3 实现 PlotGenerator 主类
    - 整合数据加载和绘图功能
    - 实现多变量对比图
    - 实现配置应用
    - 实现图像输出
    - _Requirements: 7.1, 7.2, 7.6_

  - [ ]* 12.4 编写 PlotGenerator 属性测试
    - **Property 13: CSV Data Integrity**
    - **Validates: Requirements 7.1**

  - [ ]* 12.5 编写 PlotGenerator 属性测试
    - **Property 14: Plot Variable Correspondence**
    - **Validates: Requirements 7.2**

  - [ ]* 12.6 编写 PlotGenerator 属性测试
    - **Property 15: Plot Axis Labeling**
    - **Validates: Requirements 7.3, 7.5**

  - [ ]* 12.7 编写 PlotGenerator 单元测试
    - 测试 CSV 加载
    - 测试空文件处理
    - 测试配色方案应用
    - _Requirements: 7.1, 7.4_

- [ ] 13. 实现输出管理模块
  - [ ] 13.1 实现 ExportManager 类
    - 创建输出目录结构
    - 实现图像保存功能
    - 实现索引文件生成
    - 实现临时文件清理
    - _Requirements: 8.4, 8.5_

  - [ ]* 13.2 编写 ExportManager 属性测试
    - **Property 6: Output Format Consistency**
    - **Validates: Requirements 2.6, 3.6, 4.5, 5.5, 6.3, 7.6**

  - [ ]* 13.3 编写 ExportManager 属性测试
    - **Property 18: Index File Completeness**
    - **Validates: Requirements 8.5**

  - [ ]* 13.4 编写 ExportManager 单元测试
    - 测试目录创建
    - 测试文件保存
    - 测试索引生成
    - _Requirements: 8.4, 8.5_

- [ ] 14. 实现批量执行系统
  - [ ] 14.1 实现批量执行协调器
    - 实现模块执行顺序管理
    - 实现错误隔离机制
    - 实现进度跟踪
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 14.2 创建命令行接口
    - 实现 argparse 命令行参数
    - 支持单模块执行和批量执行
    - 支持配置文件指定
    - _Requirements: 8.1_

  - [ ]* 14.3 编写批量执行属性测试
    - **Property 16: Batch Execution Completeness**
    - **Validates: Requirements 8.1, 8.4**

  - [ ]* 14.4 编写批量执行属性测试
    - **Property 17: Error Isolation**
    - **Validates: Requirements 8.3**

  - [ ]* 14.5 编写批量执行单元测试
    - 测试模块执行顺序
    - 测试错误处理
    - 测试进度显示
    - _Requirements: 8.1, 8.3_

- [ ] 15. 实现预览窗口（可选）
  - [ ] 15.1 实现 PreviewWindow 类
    - 使用 Matplotlib 或 Tkinter 显示图像
    - 实现用户确认界面
    - 实现参数调整界面
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 15.2 编写 PreviewWindow 单元测试
    - 测试窗口显示
    - 测试用户交互
    - _Requirements: 10.1_

- [ ] 16. 集成测试和文档
  - [ ] 16.1 编写集成测试
    - 测试完整的批量执行流程
    - 测试 ConfigManager 与所有模块的集成
    - 测试 DataCollector → PlotGenerator 流程
    - _Requirements: 所有需求_

  - [ ] 16.2 编写用户文档
    - 创建 README.md
    - 编写配置文件说明
    - 编写使用示例
    - _Requirements: 所有需求_

  - [ ] 16.3 创建示例配置和脚本
    - 创建 Dog2 机器人的示例配置
    - 创建快速启动脚本
    - 创建演示数据文件
    - _Requirements: 所有需求_

- [ ] 17. 最终检查点 - 确保所有测试通过
  - 运行完整的测试套件
  - 验证所有 21 个属性测试通过
  - 验证测试覆盖率达标（>80% 行覆盖率）
  - 如有问题请询问用户

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求以便追溯
- 检查点任务确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边界情况
