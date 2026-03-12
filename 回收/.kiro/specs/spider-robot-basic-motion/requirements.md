# 需求文档

## 简介

为蜘蛛式四足机器人开发基础运动算法，使机器人能够在Gazebo仿真环境中实现简单的步态运动。机器人具有4条腿，每条腿有3个旋转关节（HAA髋关节外展/内收、HFE髋关节屈伸、KFE膝关节屈伸），需要实现协调的腿部运动以产生稳定的行走步态。

## 术语表

- **System**: 蜘蛛机器人运动控制系统
- **HAA_Joint**: Hip Abduction/Adduction Joint（髋关节外展/内收关节），绕局部X轴旋转（axis="-1 0 0"），由于腿部坐标系旋转，在base_link坐标系下控制腿部的侧向张开/收回
- **HFE_Joint**: Hip Flexion/Extension Joint（髋关节屈伸关节），绕局部X轴旋转，控制大腿的前后摆动
- **KFE_Joint**: Knee Flexion/Extension Joint（膝关节屈伸关节），绕局部X轴旋转，控制小腿的屈伸
- **Leg_Coordinate_Frame**: 腿部局部坐标系，前腿绕X轴旋转90度（rpy="1.5708 0 0"），后腿绕X轴旋转90度再绕Z轴旋转180度（rpy="1.5708 0 -3.1416"）
- **Gait**: 步态，机器人腿部运动的协调模式
- **Stance_Phase**: 支撑相，脚接触地面的阶段
- **Swing_Phase**: 摆动相，脚离开地面向前移动的阶段
- **Leg_Prefix**: 腿部前缀标识（lf=前左leg1，rf=前右leg4，lh=后左leg2，rh=后右leg3）
- **Joint_Command**: 关节命令，发送给关节控制器的位置或力矩指令

## 需求

### 需求 1: 关节控制接口

**用户故事:** 作为开发者，我希望能够控制机器人的所有关节，以便实现各种运动模式。

#### 验收标准

1. WHEN 系统启动时 THEN THE System SHALL 初始化所有12个旋转关节的控制接口（4条腿 × 3个关节）
2. WHEN 发送关节位置命令时 THEN THE System SHALL 在100ms内将命令传递给对应的关节控制器
3. WHEN 关节达到目标位置时 THEN THE System SHALL 报告关节状态为"已到达"
4. IF 关节命令超出安全限位 THEN THE System SHALL 将命令限制在安全范围内并记录警告

### 需求 2: 基础步态生成

**用户故事:** 作为用户，我希望机器人能够执行简单的步态，以便验证运动算法的基本功能。

#### 验收标准

1. WHEN 用户启动步态时 THEN THE System SHALL 生成对角线步态（trot gait）的关节轨迹
2. WHEN 执行步态时 THEN THE System SHALL 确保至少有两条腿始终处于支撑相
3. WHEN 腿部处于摆动相时 THEN THE System SHALL 抬起脚部至少0.05米离开地面
4. WHEN 腿部处于支撑相时 THEN THE System SHALL 保持脚部与地面接触
5. WHEN 步态周期完成时 THEN THE System SHALL 平滑过渡到下一个周期

### 需求 3: 运动学计算

**用户故事:** 作为开发者，我希望系统能够进行运动学计算，以便将笛卡尔空间的脚部位置转换为关节角度。

#### 验收标准

1. WHEN 提供目标脚部位置（x, y, z）时 THEN THE System SHALL 计算对应的三个关节角度
2. WHEN 目标位置在工作空间内时 THEN THE System SHALL 返回有效的关节角度解
3. IF 目标位置超出工作空间 THEN THE System SHALL 返回错误并提供最近的可达位置
4. WHEN 计算逆运动学时 THEN THE System SHALL 在10ms内完成计算

### 需求 4: 轨迹规划

**用户故事:** 作为开发者，我希望系统能够生成平滑的关节轨迹，以便实现流畅的运动。

#### 验收标准

1. WHEN 生成摆动腿轨迹时 THEN THE System SHALL 使用三次样条插值确保速度连续
2. WHEN 脚部抬起时 THEN THE System SHALL 生成抛物线轨迹避免拖地
3. WHEN 关节速度超过限制时 THEN THE System SHALL 自动调整轨迹时间以满足速度约束
4. WHEN 轨迹生成完成时 THEN THE System SHALL 验证所有关节角度在安全范围内

### 需求 5: ROS 2 集成

**用户故事:** 作为用户，我希望通过ROS 2接口控制机器人，以便与其他ROS 2节点集成。

#### 验收标准

1. WHEN 系统启动时 THEN THE System SHALL 创建ROS 2节点并发布关节命令到`/joint_trajectory_controller/joint_trajectory`话题
2. WHEN 接收到速度命令（cmd_vel）时 THEN THE System SHALL 调整步态参数以实现期望的移动速度
3. WHEN 系统运行时 THEN THE System SHALL 以50Hz频率发布关节状态
4. WHEN 接收到停止命令时 THEN THE System SHALL 在一个步态周期内平滑停止运动

### 需求 6: 稳定性保证

**用户故事:** 作为用户，我希望机器人在运动时保持稳定，以便避免摔倒。

#### 验收标准

1. WHEN 机器人运动时 THEN THE System SHALL 确保质心投影始终在支撑多边形内
2. WHEN 检测到不稳定状态时 THEN THE System SHALL 自动调整步态以恢复稳定
3. WHEN 身体倾斜角度超过15度时 THEN THE System SHALL 停止运动并报警
4. WHEN 执行步态时 THEN THE System SHALL 保持身体高度在0.15米到0.25米之间

### 需求 7: 参数配置

**用户故事:** 作为开发者，我希望能够配置步态参数，以便调整机器人的运动特性。

#### 验收标准

1. WHEN 系统启动时 THEN THE System SHALL 从配置文件加载步态参数（步长、步高、频率等）
2. WHEN 参数更新时 THEN THE System SHALL 在下一个步态周期应用新参数
3. WHEN 参数无效时 THEN THE System SHALL 使用默认值并记录错误
4. WHERE 调试模式启用时 THEN THE System SHALL 发布详细的步态状态信息

### 需求 8: 错误处理

**用户故事:** 作为用户，我希望系统能够处理异常情况，以便保护机器人硬件。

#### 验收标准

1. IF 关节控制器连接丢失 THEN THE System SHALL 停止发送命令并尝试重新连接
2. IF 逆运动学无解 THEN THE System SHALL 记录错误并使用上一个有效的关节配置
3. IF 检测到关节卡死 THEN THE System SHALL 降低该关节的命令力矩并报警
4. WHEN 发生严重错误时 THEN THE System SHALL 将机器人切换到安全姿态（蹲下）
