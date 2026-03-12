# Requirements Document

## Introduction

本文档定义了一个用于机器人项目演示的数据采集与可视化系统。该系统旨在自动化生成工科 PPT 所需的专业图表、数据曲线和可视化内容，包括运动学简图、工作空间分析、ROS 通信图、状态机流转图、关键帧序列和实时数据曲线。

## Glossary

- **System**: 演示数据采集与可视化系统
- **Data_Collector**: 数据采集模块，负责从 ROS2 话题和 Gazebo 仿真中采集数据
- **Visualizer**: 可视化模块，负责生成图表和图像
- **Kinematic_Diagram_Generator**: 运动学简图生成器
- **Workspace_Analyzer**: 工作空间分析器
- **ROS_Graph_Generator**: ROS 节点通信图生成器
- **FSM_Visualizer**: 状态机可视化器
- **Keyframe_Extractor**: 关键帧提取器
- **Plot_Generator**: 数据曲线图生成器
- **Gazebo_Sim**: Gazebo Fortress 仿真环境
- **ROS2_Topic**: ROS2 话题数据流

## Requirements

### Requirement 1: 数据采集功能

**User Story:** 作为开发者，我想要自动采集机器人仿真运行时的关键数据，以便后续生成专业的数据可视化图表。

#### Acceptance Criteria

1. WHEN Gazebo_Sim 运行时，THE Data_Collector SHALL 订阅机器人的关节状态话题并记录数据
2. WHEN Gazebo_Sim 运行时，THE Data_Collector SHALL 订阅机器人的位姿话题并记录位置和姿态数据
3. WHEN Gazebo_Sim 运行时，THE Data_Collector SHALL 订阅 IMU 话题并记录加速度和角速度数据
4. WHEN 数据采集开始时，THE Data_Collector SHALL 记录时间戳以便时序分析
5. WHEN 数据采集完成时，THE Data_Collector SHALL 将数据保存为 CSV 格式文件

### Requirement 2: 运动学简图生成

**User Story:** 作为演示者，我想要生成机器人的运动学简图，以便在 PPT 中展示机器人的结构和关节配置。

#### Acceptance Criteria

1. WHEN 用户提供 URDF 文件路径时，THE Kinematic_Diagram_Generator SHALL 解析机器人的关节和连杆结构
2. WHEN 解析完成后，THE Kinematic_Diagram_Generator SHALL 生成侧视图的骨架简图
3. WHEN 生成简图时，THE Kinematic_Diagram_Generator SHALL 在髋关节位置标注坐标系
4. WHEN 生成简图时，THE Kinematic_Diagram_Generator SHALL 标注导轨的伸缩方向 d₁
5. WHEN 生成简图时，THE Kinematic_Diagram_Generator SHALL 标注旋转关节的角度 θ₁, θ₂, θ₃
6. WHEN 生成完成时，THE Kinematic_Diagram_Generator SHALL 输出高分辨率 PNG 图像

### Requirement 3: 工作空间对比分析

**User Story:** 作为演示者，我想要生成工作空间对比图，以便展示导轨扩展前后机器人腿部的活动范围差异。

#### Acceptance Criteria

1. WHEN 用户指定腿部参数时，THE Workspace_Analyzer SHALL 计算普通腿的可达工作空间
2. WHEN 用户指定导轨伸出距离时，THE Workspace_Analyzer SHALL 计算扩展后的可达工作空间
3. WHEN 计算完成后，THE Workspace_Analyzer SHALL 生成重叠的扇形对比图
4. WHEN 生成对比图时，THE Workspace_Analyzer SHALL 使用不同颜色区分普通工作空间和扩展工作空间
5. WHEN 生成对比图时，THE Workspace_Analyzer SHALL 添加 "Extended Workspace" 标注
6. WHEN 生成完成时，THE Workspace_Analyzer SHALL 输出高分辨率 PNG 图像

### Requirement 4: ROS 节点通信图生成

**User Story:** 作为演示者，我想要生成简洁的 ROS 节点通信图，以便展示系统的数据流动和闭环控制架构。

#### Acceptance Criteria

1. WHEN 用户指定节点列表时，THE ROS_Graph_Generator SHALL 创建节点框图
2. WHEN 用户指定话题连接时，THE ROS_Graph_Generator SHALL 绘制带标注的箭头连接
3. WHEN 生成通信图时，THE ROS_Graph_Generator SHALL 标注前向数据流（如 Target Velocity）
4. WHEN 生成通信图时，THE ROS_Graph_Generator SHALL 标注反馈数据流（如 Joint States, IMU）
5. WHEN 生成完成时，THE ROS_Graph_Generator SHALL 输出清晰的框图 PNG 图像

### Requirement 5: 状态机流转图生成

**User Story:** 作为演示者，我想要生成状态机流转图，以便展示机器人穿越窗框的控制策略。

#### Acceptance Criteria

1. WHEN 用户定义状态列表时，THE FSM_Visualizer SHALL 创建状态圆圈节点
2. WHEN 用户定义状态转换时，THE FSM_Visualizer SHALL 绘制带箭头的转换连线
3. WHEN 生成流转图时，THE FSM_Visualizer SHALL 为每个状态添加描述性标签
4. WHEN 生成流转图时，THE FSM_Visualizer SHALL 在状态旁边添加机器人姿态示意图
5. WHEN 生成完成时，THE FSM_Visualizer SHALL 输出专业的状态机图 PNG 图像

### Requirement 6: 关键帧序列提取

**User Story:** 作为演示者，我想要从仿真视频中自动提取关键帧，以便在 PPT 中展示机器人动作的连续过程。

#### Acceptance Criteria

1. WHEN 用户提供 Gazebo 仿真运行命令时，THE Keyframe_Extractor SHALL 自动截取屏幕画面
2. WHEN 用户指定时间点列表时，THE Keyframe_Extractor SHALL 在指定时刻截取关键帧
3. WHEN 截取关键帧时，THE Keyframe_Extractor SHALL 保存高质量的 PNG 图像
4. WHEN 截取完成后，THE Keyframe_Extractor SHALL 为每张图像添加时间戳标注
5. WHEN 所有关键帧提取完成时，THE Keyframe_Extractor SHALL 生成横向排列的组合图

### Requirement 7: 数据曲线图生成

**User Story:** 作为演示者，我想要生成专业的数据曲线图，以便展示机器人运动的稳定性和控制效果。

#### Acceptance Criteria

1. WHEN 用户提供 CSV 数据文件时，THE Plot_Generator SHALL 读取时序数据
2. WHEN 用户指定绘图变量时，THE Plot_Generator SHALL 生成对应的曲线图
3. WHEN 生成曲线图时，THE Plot_Generator SHALL 使用清晰的坐标轴标签和单位
4. WHEN 生成曲线图时，THE Plot_Generator SHALL 使用专业的配色方案（深灰背景 + 亮蓝线条）
5. WHEN 生成曲线图时，THE Plot_Generator SHALL 添加网格线以提高可读性
6. WHEN 生成完成时，THE Plot_Generator SHALL 输出高分辨率 PNG 图像

### Requirement 8: 批量生成与导出

**User Story:** 作为演示者，我想要一键生成所有可视化图表，以便快速准备演示材料。

#### Acceptance Criteria

1. WHEN 用户执行批量生成命令时，THE System SHALL 按顺序执行所有可视化模块
2. WHEN 批量生成过程中，THE System SHALL 显示当前进度和状态信息
3. WHEN 某个模块生成失败时，THE System SHALL 记录错误信息并继续执行其他模块
4. WHEN 所有生成完成后，THE System SHALL 将所有图像输出到指定的目录
5. WHEN 输出完成后，THE System SHALL 生成一个索引文件列出所有生成的图像及其用途

### Requirement 9: 配置文件支持

**User Story:** 作为开发者，我想要通过配置文件定制可视化参数，以便灵活调整图表样式和内容。

#### Acceptance Criteria

1. WHEN 系统启动时，THE System SHALL 读取 YAML 格式的配置文件
2. WHEN 配置文件包含颜色方案时，THE System SHALL 应用指定的配色
3. WHEN 配置文件包含字体设置时，THE System SHALL 使用指定的字体和大小
4. WHEN 配置文件包含数据源设置时，THE System SHALL 从指定的话题或文件读取数据
5. WHEN 配置文件不存在或格式错误时，THE System SHALL 使用默认配置并输出警告信息

### Requirement 10: 实时预览功能

**User Story:** 作为开发者，我想要在生成过程中实时预览图表，以便快速调整参数和样式。

#### Acceptance Criteria

1. WHEN 用户启用预览模式时，THE System SHALL 在生成图表后立即显示预览窗口
2. WHEN 预览窗口打开时，THE System SHALL 等待用户确认或调整参数
3. WHEN 用户调整参数后，THE System SHALL 重新生成图表并更新预览
4. WHEN 用户确认满意时，THE System SHALL 保存最终图像并继续下一个任务
5. WHEN 用户关闭预览窗口时，THE System SHALL 自动保存当前图像
