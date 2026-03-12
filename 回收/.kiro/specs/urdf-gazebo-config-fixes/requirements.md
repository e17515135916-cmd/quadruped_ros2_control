# 需求文档

## 简介

本文档定义了修复 dog2_visual.urdf 文件中严重 Gazebo 配置错误的需求。这些错误会导致仿真无法正常启动、控制器无法加载、物理计算不准确以及传感器数据无效。

**背景**: dog2_visual.urdf 文件包含以下致命错误：
1. ROS 1 插件 (gazebo_ros_control) 在 ROS 2 环境中不兼容
2. 配置文件路径使用了无效的占位符语法 {ROS_CONTROL_CONFIG_PATH}
3. 惯性参数被缩放 0.3 倍，导致 MPC/WBC 控制算法失效
4. 接触传感器使用了可能不匹配的碰撞体名称
5. 接触刚度 (kp=1000000) 过高，可能导致仿真不稳定

## 术语表

- **URDF**: 统一机器人描述格式（Unified Robot Description Format）
- **Gazebo**: 机器人仿真环境
- **ROS2_Control**: ROS 2 的硬件抽象层和控制器框架
- **Inertia_Tensor**: 惯性张量，描述物体旋转惯性的 3x3 矩阵
- **Contact_Sensor**: 接触传感器，检测机器人足端与地面的接触
- **Collision_Geometry**: 碰撞几何体，用于物理仿真中的碰撞检测
- **Contact_Stiffness**: 接触刚度，控制碰撞时的力响应特性

## 需求

### 需求 1: 移除 ROS 1 插件

**用户故事:** 作为仿真工程师，我希望 URDF 文件只包含 ROS 2 兼容的插件，以便仿真能够在 ROS 2 Humble 环境中正常启动。

#### 验收标准

1. WHEN 解析 URDF 文件时 THEN THE System SHALL 不包含 gazebo_ros_control 插件
2. WHEN 启动 Gazebo 仿真时 THEN THE System SHALL 不报告找不到 libgazebo_ros_control.so 的错误
3. WHEN 加载机器人模型时 THEN THE System SHALL 只使用 gazebo_ros2_control 插件
4. THE URDF_File SHALL 移除包含 "gazebo_ros_control" 的整个 `<gazebo>` 标签块
5. THE URDF_File SHALL 保留 gazebo_ros2_control 插件配置

### 需求 2: 修复控制器配置路径

**用户故事:** 作为控制工程师，我希望 ROS 2 控制器配置能够正确加载，以便电机能够上电并响应控制命令。

#### 验收标准

1. WHEN gazebo_ros2_control 插件初始化时 THEN THE Plugin SHALL 不使用无效的占位符语法
2. WHEN 加载控制器配置时 THEN THE System SHALL 通过 Launch 文件参数传递配置路径
3. WHEN URDF 文件被解析时 THEN THE gazebo_ros2_control 插件 SHALL 不包含 `<parameters>` 标签
4. THE URDF_File SHALL 移除 `<parameters>{ROS_CONTROL_CONFIG_PATH}</parameters>` 行
5. THE Launch_File SHALL 负责通过节点参数加载 YAML 配置文件

### 需求 3: 恢复真实惯性参数

**用户故事:** 作为控制算法工程师，我希望 URDF 文件包含真实的惯性参数，以便 MPC 和 WBC 算法能够计算出正确的控制力矩。

#### 验收标准

1. WHEN MPC 控制器读取机器人模型时 THEN THE URDF_File SHALL 提供未缩放的真实惯性参数
2. WHEN WBC 控制器计算关节力矩时 THEN THE System SHALL 使用与物理机器人一致的质量和惯性值
3. WHEN 仿真运行时 THEN THE Robot SHALL 不出现由于惯性参数错误导致的剧烈抖动
4. THE URDF_File SHALL 移除文件开头关于"质量值已缩放 0.3 倍"的警告注释
5. THE URDF_File SHALL 使用原始 dog2.urdf 或 dog2_gazebo.urdf 中的真实惯性参数
6. IF 需要可视化专用文件 THEN THE System SHALL 创建单独的 dog2_rviz.urdf 文件用于 RViz2

### 需求 4: 修复接触传感器碰撞体名称

**用户故事:** 作为传感器工程师，我希望接触传感器能够正确检测足端接触，以便步态规划器知道哪些脚在地面上。

#### 验收标准

1. WHEN 机器人足端接触地面时 THEN THE Contact_Sensor SHALL 能够检测到接触事件
2. WHEN 传感器配置碰撞体名称时 THEN THE System SHALL 使用 Gazebo 实际生成的碰撞体名称
3. WHEN 碰撞体名称不匹配时 THEN THE System SHALL 在启动时报告警告或错误
4. THE Contact_Sensor SHALL 使用简化的碰撞体名称格式（如 "l1111_collision" 而非 "l1111_fixed_joint_lump__l1111_collision_collision"）
5. IF 简化名称不工作 THEN THE System SHALL 通过 Gazebo 日志验证实际的碰撞体名称

### 需求 5: 调整接触刚度参数

**用户故事:** 作为仿真工程师，我希望接触物理参数能够保证仿真稳定性，以便机器人不会出现"爆炸"或弹飞现象。

#### 验收标准

1. WHEN 机器人足端接触地面时 THEN THE System SHALL 保持数值稳定性
2. WHEN 接触刚度过高导致不稳定时 THEN THE System SHALL 使用更合理的刚度值
3. WHEN 调整刚度参数后 THEN THE Robot SHALL 能够稳定站立和行走
4. THE Contact_Parameters SHALL 将 kp 值从 1000000.0 降低到 10000.0 或更低
5. THE Contact_Parameters SHALL 保持 kd 值在合理范围内（如 100.0）
6. THE Contact_Parameters SHALL 保持摩擦系数 mu1 和 mu2 在 1.0-2.0 范围内

### 需求 6: 验证修复后的 URDF 文件

**用户故事:** 作为系统集成工程师，我希望修复后的 URDF 文件能够通过所有验证测试，以便确保仿真能够正常运行。

#### 验收标准

1. WHEN 运行 URDF 验证工具时 THEN THE URDF_File SHALL 通过语法检查
2. WHEN 在 Gazebo 中加载机器人时 THEN THE System SHALL 成功加载模型且无错误
3. WHEN 启动控制器时 THEN THE Controllers SHALL 成功连接到所有关节
4. WHEN 运行仿真时 THEN THE Robot SHALL 能够响应控制命令
5. THE System SHALL 提供验证脚本来检查所有修复是否正确应用
6. THE System SHALL 在修复前备份原始 URDF 文件

### 需求 7: 修复关节类型和添加物理限位

**用户故事:** 作为控制算法工程师，我希望关节配置符合真实机器人的物理约束，以便 MPC/WBC 求解器不会计算出不可行的关节角度。

#### 验收标准

1. WHEN MPC 求解器计算最优轨迹时 THEN THE Joint_Limits SHALL 防止求解器输出超出物理范围的关节角度
2. WHEN WBC 控制器计算关节力矩时 THEN THE System SHALL 考虑关节的物理限位约束
3. WHEN 关节类型为 continuous 时 THEN THE System SHALL 允许 360° 无限旋转
4. WHEN 关节类型为 revolute 时 THEN THE System SHALL 强制执行 lower 和 upper 限位
5. THE Hip_Joints (j11, j21, j31, j41) SHALL 使用 type="revolute" 并设置合理的限位范围（如 -1.57 到 1.57 弧度）
6. THE Knee_Joints (j111, j211, j311, j411) SHALL 使用 type="revolute" 并设置合理的限位范围（如 -2.5 到 0 弧度）
7. THE Shoulder_Joints (j1, j2, j3, j4) SHALL 根据实际机械设计设置限位
8. IF 关节有机械限位或线缆限制 THEN THE Joint SHALL 不使用 continuous 类型
9. THE Joint_Limits SHALL 包含 effort 和 velocity 限制以防止电机过载

### 需求 8: 文档和注释更新

**用户故事:** 作为开发者，我希望 URDF 文件包含清晰的注释说明，以便理解配置的目的和使用场景。

#### 验收标准

1. WHEN 查看 URDF 文件时 THEN THE File SHALL 包含说明其用途的注释（Gazebo 仿真用）
2. WHEN 文件被修改时 THEN THE Comments SHALL 解释关键参数的选择原因
3. WHEN 存在多个 URDF 文件时 THEN THE System SHALL 提供文档说明每个文件的用途
4. THE URDF_File SHALL 在文件开头包含用途说明（如"用于 Gazebo 仿真，包含真实物理参数"）
5. THE Documentation SHALL 说明 dog2_visual.urdf 和 dog2_gazebo.urdf 的区别和使用场景
