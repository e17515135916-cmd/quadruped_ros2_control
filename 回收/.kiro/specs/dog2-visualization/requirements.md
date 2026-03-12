# Requirements Document: Dog2 可视化系统

## Introduction

为 Dog2 四足机器人添加完整的可视化功能，使用户能够在 RViz2 和 Gazebo 中清晰地看到机器人的行走、越障动作，以及实时的控制数据。

## Glossary

- **RViz2**: ROS 2 的 3D 可视化工具
- **Gazebo**: 物理仿真环境
- **TF**: ROS 的坐标变换系统
- **Marker**: RViz2 中的可视化标记
- **Trajectory**: 机器人的运动轨迹
- **Foot_Force**: 足端接触力
- **Sliding_Joint**: 滑动副关节
- **Contact_State**: 足端接触状态

## Requirements

### Requirement 1: RViz2 基础可视化

**User Story:** 作为开发者，我想在 RViz2 中看到机器人模型和关节状态，以便直观地了解机器人的姿态和运动。

#### Acceptance Criteria

1. WHEN RViz2 启动 THEN THE System SHALL 显示 Dog2 的完整 3D 模型
2. WHEN 机器人关节运动 THEN THE System SHALL 实时更新模型的关节角度
3. WHEN 滑动副移动 THEN THE System SHALL 显示滑动副的伸缩状态
4. THE System SHALL 显示所有坐标系（base_link, 腿部链接等）
5. THE System SHALL 提供预配置的 RViz2 配置文件

### Requirement 2: 足端力可视化

**User Story:** 作为开发者，我想看到足端力的大小和方向，以便验证 MPC 控制器的输出是否合理。

#### Acceptance Criteria

1. WHEN MPC 输出足端力 THEN THE System SHALL 在 RViz2 中显示力向量箭头
2. WHEN 足端力变化 THEN THE System SHALL 更新箭头的长度和颜色
3. THE System SHALL 使用颜色编码表示力的大小（绿色=小，黄色=中，红色=大）
4. WHEN 足端离地 THEN THE System SHALL 隐藏或淡化该足端的力箭头
5. THE System SHALL 在箭头旁显示力的数值标签

### Requirement 3: 轨迹可视化

**User Story:** 作为开发者，我想看到机器人的历史轨迹和规划轨迹，以便分析运动路径和跟踪性能。

#### Acceptance Criteria

1. WHEN 机器人移动 THEN THE System SHALL 在 RViz2 中绘制机身中心的历史轨迹
2. WHEN MPC 生成参考轨迹 THEN THE System SHALL 显示未来的规划路径
3. THE System SHALL 使用不同颜色区分历史轨迹（蓝色）和规划轨迹（绿色）
4. THE System SHALL 显示每个足端的运动轨迹
5. WHEN 轨迹过长 THEN THE System SHALL 自动清除旧的轨迹点（保留最近 100 个点）

### Requirement 4: 接触状态可视化

**User Story:** 作为开发者，我想看到哪些足端正在接触地面，以便验证步态规划是否正确。

#### Acceptance Criteria

1. WHEN 足端接触地面 THEN THE System SHALL 在足端位置显示绿色球体标记
2. WHEN 足端离地 THEN THE System SHALL 在足端位置显示红色球体标记
3. THE System SHALL 实时更新接触状态标记
4. THE System SHALL 在 RViz2 中显示接触状态文本（例如 "[1,0,0,1]"）
5. WHEN 步态切换 THEN THE System SHALL 平滑过渡标记颜色

### Requirement 5: Gazebo 环境增强

**User Story:** 作为开发者，我想在 Gazebo 中看到清晰的地面网格和障碍物，以便更好地理解机器人的运动环境。

#### Acceptance Criteria

1. THE System SHALL 在 Gazebo 中显示带网格的地面平面
2. WHEN 启动越障模式 THEN THE System SHALL 在场景中生成窗框障碍物模型
3. THE System SHALL 在地面上显示距离标记（每米一个标记）
4. THE System SHALL 提供可选的地形模型（平地、斜坡、台阶）
5. THE System SHALL 允许用户通过参数选择不同的环境场景

### Requirement 6: 滑动副状态可视化

**User Story:** 作为开发者，我想看到滑动副的位置和限位状态，以便验证滑动副约束是否正确工作。

#### Acceptance Criteria

1. THE System SHALL 在 RViz2 中显示每个滑动副的当前位置（数值）
2. WHEN 滑动副接近限位 THEN THE System SHALL 用黄色警告标记显示
3. WHEN 滑动副达到限位 THEN THE System SHALL 用红色标记显示
4. THE System SHALL 显示滑动副的运动范围（-0.1m ~ 0.1m）
5. THE System SHALL 显示前后腿滑动副的对称性状态

### Requirement 7: 实时数据图表

**User Story:** 作为开发者，我想看到实时的数据曲线（高度、姿态、速度等），以便分析控制性能。

#### Acceptance Criteria

1. THE System SHALL 提供启动 PlotJuggler 或 rqt_plot 的配置
2. THE System SHALL 预配置常用的数据曲线（高度、roll、pitch、yaw）
3. THE System SHALL 支持显示 MPC 求解时间曲线
4. THE System SHALL 支持显示足端力曲线
5. THE System SHALL 允许用户保存和加载图表配置

### Requirement 8: 一键启动可视化

**User Story:** 作为用户，我想通过一个命令启动完整的可视化系统，以便快速开始测试。

#### Acceptance Criteria

1. THE System SHALL 提供单一的 launch 文件启动所有可视化组件
2. WHEN 用户启动可视化 THEN THE System SHALL 自动打开 Gazebo、RViz2 和数据图表
3. THE System SHALL 支持通过参数选择可视化模式（行走/越障）
4. THE System SHALL 在启动时自动加载预配置的 RViz2 视角
5. THE System SHALL 提供清晰的终端输出，说明如何控制机器人

### Requirement 9: 越障过程可视化

**User Story:** 作为开发者，我想看到越障过程的每个阶段，以便理解和调试越障算法。

#### Acceptance Criteria

1. WHEN 越障开始 THEN THE System SHALL 在 RViz2 中显示当前阶段名称
2. THE System SHALL 用不同颜色标记不同阶段（阶段 1=蓝色，阶段 2=绿色等）
3. THE System SHALL 显示窗框的位置和尺寸
4. WHEN 前腿穿越 THEN THE System SHALL 高亮显示正在穿越的腿
5. THE System SHALL 显示混合构型状态（肘式/膝式）

### Requirement 10: 性能监控面板

**User Story:** 作为开发者，我想在 RViz2 中看到关键性能指标，以便快速评估系统状态。

#### Acceptance Criteria

1. THE System SHALL 在 RViz2 中显示文本面板，包含以下信息：
   - MPC 求解时间
   - 控制频率
   - 当前高度
   - 当前速度
   - 接触状态
2. THE System SHALL 每秒更新一次性能数据
3. WHEN MPC 求解失败 THEN THE System SHALL 在面板中显示红色警告
4. THE System SHALL 显示滑动副约束满足状态
5. THE System SHALL 显示系统运行时间
