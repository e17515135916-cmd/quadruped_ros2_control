# 需求文档

## 简介

本文档定义了修复 DOG2 机器人在 Gazebo 仿真中因碰撞网格重叠和足端物理冲突导致"炸飞"问题的需求。当前 URDF 配置存在两个致命问题：(1) 大腿和小腿 Mesh 在关节处内部重叠，导致物理引擎产生巨大排斥力；(2) 小腿 Mesh 碰撞体与球形足端发生自我碰撞，导致机器人抖动和弹飞。

**背景**: 
- 当前配置对大腿（l${leg_num}11）和小腿（l${leg_num}111）应用了 scale="0.95 0.95 0.95"
- 缩放 Mesh 并不能消除关节轴心处的碰撞穿透
- 小腿 Mesh 延伸到地面，与固定在小腿末端的球形足端发生自我碰撞
- Gazebo ODE 物理引擎检测到重叠后产生排斥力，导致能量累积和"爆炸"

## 术语表

- **Collision_Mesh**: 碰撞网格 - 用于物理引擎碰撞检测的几何体
- **Visual_Mesh**: 视觉网格 - 用于渲染显示的几何体
- **Self_Collision**: 自我碰撞 - 机器人自身不同部件之间的碰撞
- **Mesh_Penetration**: 网格穿透 - 两个碰撞体在空间中重叠
- **ODE**: Open Dynamics Engine - Gazebo 使用的物理引擎
- **Collision_Primitive**: 碰撞原语 - 简单几何体（box、cylinder、sphere）用于碰撞检测
- **Joint_Axis**: 关节轴 - 关节旋转或平移的中心线
- **Contact_Force**: 接触力 - 碰撞时物理引擎计算的作用力
- **Repulsion_Force**: 排斥力 - 物理引擎为分离重叠物体产生的力
- **Fixed_Joint**: 固定关节 - 不允许相对运动的关节
- **Collision_Margin**: 碰撞边距 - 碰撞检测的安全距离

## 需求

### 需求 1: 用碰撞原语替换 Mesh 碰撞体

**用户故事:** 作为仿真工程师，我希望使用简单的碰撞原语（box、cylinder）替换复杂的 STL Mesh，以便消除关节处的碰撞穿透并提高物理计算效率。

#### 验收标准

1. THE System SHALL 为大腿（l${leg_num}11）使用 cylinder 或 box 碰撞几何体
2. THE System SHALL 为小腿（l${leg_num}111）使用 cylinder 或 box 碰撞几何体
3. WHEN 定义碰撞原语时，THE System SHALL 确保碰撞体尺寸略小于实际 Link 尺寸
4. THE System SHALL 保留 STL Mesh 用于 visual 标签（视觉显示）
5. THE System SHALL 移除 collision 标签中的 scale 属性
6. WHEN 两个 Link 通过关节连接时，THE System SHALL 确保碰撞体之间有至少 0.005 米的间隙

### 需求 2: 截断小腿碰撞体

**用户故事:** 作为控制工程师，我希望小腿的碰撞体不延伸到足端位置，以便消除小腿与球形足端之间的自我碰撞。

#### 验收标准

1. THE System SHALL 将小腿碰撞体的长度设置为小于小腿实际长度
2. WHEN 小腿实际长度为 L 米时，THE System SHALL 将碰撞体长度设置为 (L - 0.03) 米
3. THE System SHALL 确保小腿碰撞体末端与球形足端之间有至少 0.01 米的间隙
4. THE System SHALL 将小腿碰撞体的原点偏移，使其不与足端球体重叠
5. WHEN 机器人站立时，THE System SHALL 确保只有球形足端与地面接触

### 需求 3: 配置自我碰撞过滤

**用户故事:** 作为仿真工程师，我希望显式禁用相邻 Link 之间的碰撞检测，以便防止关节处的误检测。

#### 验收标准

1. THE System SHALL 在 Gazebo 配置中禁用相邻 Link 之间的碰撞检测
2. THE System SHALL 禁用以下 Link 对的碰撞：
   - 大腿（l${leg_num}11）与小腿（l${leg_num}111）
   - 小腿（l${leg_num}111）与足端（l${leg_num}1111）
3. WHEN 使用 URDF 时，THE System SHALL 通过 `<disable_collisions>` 标签配置碰撞过滤
4. WHEN 使用 Xacro 时，THE System SHALL 通过 Gazebo 插件参数配置碰撞过滤
5. THE System SHALL 保留非相邻 Link 之间的碰撞检测（如左右腿之间）

### 需求 4: 优化碰撞几何体尺寸

**用户故事:** 作为机器人工程师，我希望碰撞几何体尺寸基于实际 STL Mesh 测量，以便准确反映机器人的物理形状。

#### 验收标准

1. THE System SHALL 提供脚本测量 STL Mesh 的边界框尺寸
2. WHEN 定义 cylinder 碰撞体时，THE System SHALL 设置半径为 Mesh 最大横截面半径的 0.9 倍
3. WHEN 定义 cylinder 碰撞体时，THE System SHALL 设置长度为 Mesh 长度的 0.85 倍
4. WHEN 定义 box 碰撞体时，THE System SHALL 设置尺寸为 Mesh 边界框的 0.9 倍
5. THE System SHALL 记录每个 Link 的碰撞体尺寸和偏移量

### 需求 5: 调整足端位置和尺寸

**用户故事:** 作为控制工程师，我希望球形足端的位置和尺寸能够确保稳定接触，以便机器人能够正常站立和行走。

#### 验收标准

1. THE System SHALL 将球形足端半径设置为 0.015 米（15mm）
2. THE System SHALL 将足端关节偏移设置为小腿长度加上足端半径
3. WHEN 机器人在 Gazebo 中生成时，THE System SHALL 确保足端球心位于小腿末端下方
4. THE System SHALL 确保足端球体不与小腿碰撞体重叠
5. WHEN 机器人站立时，THE System SHALL 确保所有 4 个足端同时接触地面

### 需求 6: 降低接触刚度参数

**用户故事:** 作为仿真工程师，我希望使用合理的接触刚度参数，以便防止数值不稳定和"爆炸"现象。

#### 验收标准

1. THE System SHALL 将足端接触刚度 kp 从 1000000.0 降低到 10000.0
2. THE System SHALL 将接触阻尼 kd 设置为 100.0
3. THE System SHALL 将摩擦系数 mu1 和 mu2 设置为 1.0
4. THE System SHALL 将最小穿透深度 minDepth 设置为 0.001
5. THE System SHALL 将最大接触速度 maxVel 设置为 0.1
6. WHEN 机器人接触地面时，THE System SHALL 不出现剧烈抖动或弹飞

### 需求 7: 验证碰撞配置

**用户故事:** 作为质量保证工程师，我希望有自动化测试验证碰撞配置的正确性，以便在部署前发现问题。

#### 验收标准

1. THE System SHALL 提供脚本检查相邻 Link 碰撞体是否重叠
2. THE System SHALL 提供脚本验证碰撞体尺寸是否在合理范围内
3. WHEN 检测到碰撞体重叠时，THE System SHALL 报告重叠的 Link 对和重叠量
4. THE System SHALL 提供可视化工具在 RViz 中显示碰撞几何体
5. THE System SHALL 在 Gazebo 中测试机器人能够稳定站立至少 10 秒

### 需求 8: 属性测试 - 碰撞体间隙

**用户故事:** 作为测试工程师，我希望属性测试能够验证所有相邻 Link 之间都有足够间隙，以便自动检测配置错误。

#### 验收标准

1. THE System SHALL 对每条腿的所有相邻 Link 对运行间隙检查
2. FOR ALL 相邻 Link 对，THE System SHALL 验证碰撞体之间的最小距离 >= 0.005 米
3. FOR ALL 腿（1-4），THE System SHALL 验证小腿与足端之间的间隙 >= 0.01 米
4. IF 任何 Link 对间隙不足，THE System SHALL 报告具体的 Link 名称和实际间隙
5. THE System SHALL 运行至少 100 次测试迭代以验证配置一致性

### 需求 9: Gazebo 稳定性测试

**用户故事:** 作为系统集成工程师，我希望验证修复后的机器人在 Gazebo 中能够稳定运行，以便确保仿真可用于控制算法测试。

#### 验收标准

1. WHEN 机器人在 Gazebo 中生成时，THE System SHALL 在 5 秒内稳定到静止状态
2. WHEN 机器人站立时，THE System SHALL 的基座高度保持在 0.3 ± 0.05 米范围内
3. WHEN 仿真运行 60 秒时，THE System SHALL 不出现任何 Link 的位置或速度发散
4. THE System SHALL 记录基座位置、速度和加速度数据用于分析
5. IF 机器人出现"炸飞"现象，THE System SHALL 在日志中记录触发时刻和相关 Link 状态

### 需求 10: 文档和回滚机制

**用户故事:** 作为开发者，我希望有清晰的文档说明碰撞配置的修改，以便理解设计决策并在需要时回滚。

#### 验收标准

1. THE System SHALL 在修改 URDF 前创建带时间戳的备份文件
2. THE System SHALL 记录每个碰撞体的尺寸、偏移和类型选择理由
3. THE System SHALL 提供对比文档说明修改前后的差异
4. THE System SHALL 提供回滚脚本恢复到修改前的配置
5. THE System SHALL 在设计文档中说明为什么使用碰撞原语而非 Mesh
