# 需求文档

## 简介

本规范旨在为DOG2四足机器人的每条腿添加球形足端（第5个Link），以改善在油箱环境中穿越障碍物时的接触稳定性。当前机器人腿部结构为4个Link（导轨、髋、大腿、小腿），需要在小腿末端添加球形足端，使运动链完整为5个Link，确保与地面和障碍物的接触始终是稳定的点接触。

## 术语表

- **Link**: 连杆 - 机器人运动链中的刚体部件
- **Joint**: 关节 - 连接两个Link的运动副
- **Foot_Link**: 足端连杆 - 机器人腿部末端与地面接触的部件
- **Spherical_Geometry**: 球形几何体 - 用于足端的几何形状，确保稳定的点接触
- **Fixed_Joint**: 固定关节 - 不允许相对运动的关节类型
- **Friction_Coefficient**: 摩擦系数 - 控制足端与地面之间的摩擦力
- **Inertial_Properties**: 惯性属性 - 包括质量、质心位置和转动惯量
- **URDF**: 统一机器人描述格式 - 描述机器人运动学和动力学的XML格式
- **Xacro**: XML宏语言 - 用于参数化和模块化URDF文件
- **Gazebo**: 机器人物理仿真环境
- **MPC**: 模型预测控制 - 用于机器人运动规划的控制算法
- **WBC**: 全身控制 - 计算关节力矩以实现期望运动的控制算法
- **Property_Test**: 属性测试 - 验证系统在所有输入下满足某个属性的测试方法

## 需求

### 需求 1: 球形足端几何定义

**用户故事:** 作为机器人工程师，我希望为每条腿定义球形足端几何体，以便在仿真中实现稳定的点接触。

#### 验收标准

1. WHEN 定义足端Link时，THE System SHALL 使用球形（sphere）几何体而非STL网格
2. THE System SHALL 为足端球体设置半径为0.02米（20mm）
3. THE System SHALL 在visual和collision标签中都使用相同的球形几何体
4. THE System SHALL 为足端设置灰色材质（Gazebo/Grey）以便在仿真中可视化
5. WHEN 机器人在Gazebo中加载时，THE System SHALL 显示球形足端而非网格模型

### 需求 2: 足端Link命名和层级结构

**用户故事:** 作为开发者，我希望足端Link遵循现有的命名规范，以便与测试和控制系统集成。

#### 验收标准

1. THE System SHALL 为每条腿（leg_num 1-4）创建名为 `l${leg_num}1111` 的足端Link
2. WHEN 生成URDF时，THE System SHALL 确保每条腿包含5个Link：
   - `l${leg_num}`: 导轨Link
   - `l${leg_num}1`: 髋Link
   - `l${leg_num}11`: 大腿Link
   - `l${leg_num}111`: 小腿Link
   - `l${leg_num}1111`: 足端Link
3. THE System SHALL 通过固定关节 `j${leg_num}1111` 将足端Link连接到小腿Link
4. THE System SHALL 确保足端Link是运动链的终点（没有子Link）

### 需求 3: 足端物理属性配置

**用户故事:** 作为控制工程师，我希望足端具有适当的物理属性，以便Gazebo物理引擎能够正确模拟接触力。

#### 验收标准

1. THE System SHALL 为足端Link设置质量为0.05kg（50克）
2. THE System SHALL 为足端Link计算并设置适合球形的转动惯量
3. THE System SHALL 将足端质心位置设置在球心
4. WHEN 足端质量为零或惯性矩阵奇异时，THEN THE System SHALL 拒绝该配置并报错
5. THE System SHALL 确保足端的惯性属性满足物理约束（正定矩阵）

### 需求 4: 足端摩擦力配置

**用户故事:** 作为仿真工程师，我希望为足端配置高摩擦系数，以便机器人在油箱环境中能够稳定站立和行走。

#### 验收标准

1. THE System SHALL 在Gazebo标签中为足端Link设置摩擦系数 mu1=1.5
2. THE System SHALL 在Gazebo标签中为足端Link设置摩擦系数 mu2=1.5
3. THE System SHALL 设置接触刚度 kp=1000000.0 以模拟硬接触
4. THE System SHALL 设置接触阻尼 kd=100.0 以稳定接触
5. THE System SHALL 设置最小穿透深度 minDepth=0.001 以提高接触检测精度
6. THE System SHALL 设置最大接触速度 maxVel=0.1 以防止数值不稳定

### 需求 5: 固定关节位置配置

**用户故事:** 作为运动学工程师，我希望正确设置足端关节的位置偏移，以便足端位于小腿末端的正确位置。

#### 验收标准

1. THE System SHALL 创建固定关节 `j${leg_num}1111` 连接小腿和足端
2. THE System SHALL 设置关节原点xyz偏移，使足端球心位于小腿末端下方0.02米处
3. THE System SHALL 设置关节原点rpy旋转为 (0, 0, 0)
4. WHEN 计算足端位置时，THE System SHALL 确保足端不与小腿几何体重叠
5. THE System SHALL 确保足端在机器人站立时能够接触地面

### 需求 6: 属性测试验证

**用户故事:** 作为质量保证工程师，我希望属性测试能够验证每条腿都有完整的5个Link结构，以便自动检测结构错误。

#### 验收标准

1. WHEN 运行属性测试时，THE System SHALL 验证每条腿（1-4）都有5个Link
2. THE System SHALL 验证Link命名遵循模式：`l${leg_num}`, `l${leg_num}1`, `l${leg_num}11`, `l${leg_num}111`, `l${leg_num}1111`
3. IF 任何腿缺少Link，THEN THE System SHALL 报告缺失的Link名称
4. IF 任何腿有额外的Link，THEN THE System SHALL 报告额外的Link名称
5. THE System SHALL 对所有4条腿运行至少100次随机测试迭代

### 需求 7: 控制接口隔离

**用户故事:** 作为控制系统工程师，我希望固定关节不出现在ros2_control配置中，以便控制器只管理主动关节。

#### 验收标准

1. THE System SHALL 确保固定关节 `j${leg_num}1111` 不在ros2_control块中定义
2. THE System SHALL 仅为前4个主动关节配置command_interface：
   - `j${leg_num}`: 导轨（prismatic）
   - `j${leg_num}1`: 髋外展/内收（revolute）
   - `j${leg_num}11`: 髋前屈/后伸（revolute）
   - `j${leg_num}111`: 膝关节（revolute）
3. WHEN WBC算法计算足端受力时，THE System SHALL 能够查询足端Link的位置和速度
4. THE System SHALL 确保固定关节不需要控制器或command接口

### 需求 8: Gazebo加载验证

**用户故事:** 作为开发者，我希望验证Gazebo能够成功加载带有球形足端的机器人，以便进行仿真测试。

#### 验收标准

1. WHEN 启动Gazebo仿真时，THE System SHALL 成功加载机器人而不出现错误
2. WHEN 机器人生成在Gazebo中时，THE System SHALL 显示所有4条腿的球形足端
3. THE System SHALL 确保足端能够与地面正确碰撞检测
4. WHEN 机器人站立时，THE System SHALL 确保足端与地面接触产生支撑力
5. THE System SHALL 确保物理引擎不会因为足端配置而崩溃或报错

### 需求 9: 文档和可视化

**用户故事:** 作为团队成员，我希望有清晰的文档说明足端的设计决策，以便理解为什么使用球形几何体。

#### 验收标准

1. THE System SHALL 在设计文档中说明选择球形足端的原因（稳定的点接触）
2. THE System SHALL 记录足端的物理参数（半径、质量、摩擦系数）
3. THE System SHALL 提供可视化脚本或launch文件以在RViz中查看足端
4. THE System SHALL 说明球形足端如何改善穿越障碍物时的稳定性
5. THE System SHALL 记录足端配置对MPC和WBC算法的影响
