# Dog2越障功能需求文档

## 简介

Dog2四足机器人越障功能使机器人能够穿越窗型障碍物。该功能利用机器人独特的纵向滑动副机构和肘/膝构型切换能力，实现了创新的混合构型动态行走越障策略。

## 术语表

- **System**: Dog2四足机器人越障控制系统
- **Sliding_Joint**: 纵向滑动副，允许腿部根部沿机身前后滑动的平移关节（j1, j2, j3, j4）
- **Elbow_Configuration**: 肘式构型，关节向后/外突出，工作空间偏前，适合正常行走
- **Knee_Configuration**: 膝式构型，关节向前/内收束，工作空间偏后，适合穿越障碍
- **Window_Obstacle**: 窗型障碍物，四周有墙的开口，机器人必须从开口穿过
- **Hybrid_Gait**: 混合构型步态，前腿膝式+后腿肘式的不对称行走模式
- **MPC_Controller**: 模型预测控制器，16维扩展状态（SRBD 12维 + 滑动副 4维）
- **Crossing_State_Machine**: 越障状态机，管理8个越障阶段的转换
- **SRBD_Model**: 单刚体动力学模型，描述机器人质心运动

## 需求

### 需求1：越障状态管理

**用户故事**：作为机器人控制系统，我需要管理越障过程的不同阶段，以便机器人能够有序地完成复杂的越障动作。

#### 验收标准

1. WHEN 系统初始化越障功能 THEN THE System SHALL 创建包含8个阶段的状态机（APPROACH, BODY_FORWARD_SHIFT, FRONT_LEGS_TRANSIT, HYBRID_GAIT_WALKING, RAIL_ALIGNMENT, REAR_LEGS_TRANSIT, ALL_KNEE_STATE, RECOVERY, CONTINUE_FORWARD）
2. WHEN 当前阶段完成条件满足 THEN THE System SHALL 自动转换到下一个阶段
3. WHEN 查询越障进度 THEN THE System SHALL 返回0到1之间的进度值
4. WHEN 查询当前状态 THEN THE System SHALL 返回当前所处的越障阶段

### 需求2：滑动副控制

**用户故事**：作为机器人控制系统，我需要精确控制滑动副位置，以便实现机身前探和腿部穿越动作。

#### 验收标准

1. WHEN 控制滑动副位置 THEN THE System SHALL 确保位置在限位范围内（j1: [-0.111m, 0.008m], j2: [-0.008m, 0.111m], j3: [-0.008m, 0.111m], j4: [-0.111m, 0.008m]）
2. WHEN 控制滑动副速度 THEN THE System SHALL 限制速度不超过1.0 m/s
3. WHEN 控制前后腿滑动副 THEN THE System SHALL 保持左右对称性（|d1 - d3| < 0.02m, |d2 - d4| < 0.02m）
4. WHEN 控制所有滑动副 THEN THE System SHALL 保持协调性（|d1 + d2 + d3 + d4| < 0.05m）

### 需求3：机身前探动作

**用户故事**：作为机器人，我需要在保持四腿接触地面的情况下将机身向前推进，以便让前腿滑动副穿过窗框。

#### 验收标准

1. WHEN 执行机身前探 THEN THE System SHALL 保持四条腿足端位置固定
2. WHEN 执行机身前探 THEN THE System SHALL 前腿滑动副向后伸展至-0.111m（相对机身）
3. WHEN 执行机身前探 THEN THE System SHALL 后腿滑动副向前伸展至0.111m（相对机身）
4. WHEN 机身前探完成 THEN THE System SHALL 使前腿滑动副前端穿过窗框位置
5. WHEN 机身前探过程中 THEN THE System SHALL 保持机身姿态稳定（|pitch| < 5°）

### 需求4：腿部穿越动作

**用户故事**：作为机器人，我需要逐条腿穿过窗框，并在穿越过程中切换构型，以便避开窗框边缘。

#### 验收标准

1. WHEN 穿越一条腿 THEN THE System SHALL 先抬起该腿离地（高度0.15m）
2. WHEN 腿部抬起后 THEN THE System SHALL 沿滑动副向前滑动0.119m
3. WHEN 腿部根部穿过窗框 THEN THE System SHALL 在空中切换构型（肘式→膝式）
4. WHEN 构型切换完成 THEN THE System SHALL 在窗框内侧落地
5. WHEN 穿越过程中 THEN THE System SHALL 保持其他三腿支撑稳定

### 需求5：混合构型行走

**用户故事**：作为机器人，我需要在前腿膝式+后腿肘式的混合构型下行走，以便在窗框约束下继续前进。

#### 验收标准

1. WHEN 进入混合构型行走 THEN THE System SHALL 前腿使用膝式构型，后腿使用肘式构型
2. WHEN 混合构型行走 THEN THE System SHALL 前腿步长为0.08m，后腿步长为0.12m
3. WHEN 混合构型行走 THEN THE System SHALL 使用Trot对角线步态
4. WHEN 混合构型行走 THEN THE System SHALL 保持腿间距离大于0.15m
5. WHEN 混合构型行走 THEN THE System SHALL 前进速度为0.1 m/s
6. WHEN 后腿滑动副前端穿过窗框 THEN THE System SHALL 停止行走

### 需求6：MPC控制器集成

**用户故事**：作为控制系统，我需要使用MPC控制器生成最优控制指令，以便实现稳定的越障运动。

#### 验收标准

1. WHEN MPC控制器初始化 THEN THE System SHALL 使用16维扩展状态（SRBD 12维 + 滑动副 4维）
2. WHEN MPC求解 THEN THE System SHALL 添加动力学约束（等式约束）
3. WHEN MPC求解 THEN THE System SHALL 添加滑动副约束（不等式约束）
4. WHEN MPC求解 THEN THE System SHALL 添加控制约束（足端力限制）
5. WHEN 越障模式启用 THEN THE System SHALL 根据当前越障状态生成参考轨迹
6. WHEN MPC求解成功 THEN THE System SHALL 返回12维控制向量（4条腿×3维力）

### 需求7：参考轨迹生成

**用户故事**：作为MPC控制器，我需要根据越障状态生成合适的参考轨迹，以便引导机器人完成越障动作。

#### 验收标准

1. WHEN 处于APPROACH状态 THEN THE System SHALL 生成正常Trot步态参考轨迹（速度0.2 m/s）
2. WHEN 处于BODY_FORWARD_SHIFT状态 THEN THE System SHALL 生成静态参考轨迹（速度为0）
3. WHEN 处于HYBRID_GAIT_WALKING状态 THEN THE System SHALL 生成混合构型步态参考轨迹（速度0.1 m/s）
4. WHEN 处于RAIL_ALIGNMENT状态 THEN THE System SHALL 生成精确停车参考轨迹
5. WHEN 生成参考轨迹 THEN THE System SHALL 输出16维扩展状态（包含滑动副目标位置）

### 需求8：构型恢复

**用户故事**：作为机器人，我需要在完全穿过窗框后恢复正常构型，以便继续正常行走。

#### 验收标准

1. WHEN 四条腿都穿过窗框 THEN THE System SHALL 进入全膝式状态
2. WHEN 全膝式状态稳定 THEN THE System SHALL 逐条腿切换回肘式构型
3. WHEN 所有腿恢复肘式 THEN THE System SHALL 收缩滑动副回到中立位置（d1=d2=d3=d4=0）
4. WHEN 构型恢复完成 THEN THE System SHALL 恢复正常Trot步态

### 需求9：安全约束

**用户故事**：作为机器人控制系统，我需要确保越障过程的安全性，以便避免碰撞和失稳。

#### 验收标准

1. WHEN 任何时刻 THEN THE System SHALL 保持质心投影在支撑多边形内
2. WHEN 任何时刻 THEN THE System SHALL 保持机身姿态角度在安全范围内（|roll| < 10°, |pitch| < 10°）
3. WHEN 混合构型行走 THEN THE System SHALL 保持前后腿工作空间不重叠
4. WHEN 穿越窗框 THEN THE System SHALL 保持机身与窗框距离大于0.05m
5. WHEN 三点支撑时 THEN THE System SHALL 确保支撑三角形稳定

### 需求10：测试验证

**用户故事**：作为开发者，我需要全面测试越障功能，以便确保系统可靠性。

#### 验收标准

1. WHEN 运行基础功能测试 THEN THE System SHALL 通过状态机测试、步态生成器测试
2. WHEN 运行MPC集成测试 THEN THE System SHALL 通过初始化测试、参考轨迹测试、求解测试、状态更新测试
3. WHEN 运行简化测试 THEN THE System SHALL 在简化场景下通过所有测试
4. WHEN 所有测试运行 THEN THE System SHALL 达到100%通过率
