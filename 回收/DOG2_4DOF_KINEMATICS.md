# Dog2 四自由度腿部运动学

## 概述

Dog2 机器人每条腿具有 **4 个自由度**，这是一个冗余构型，比标准的 3-DOF 四足机器人多一个自由度。

## 关节链结构

每条腿的关节链从基座出发，按以下顺序连接：

```
基座 (base_link)
  ↓
1. j${leg_num}    - 移动关节 (prismatic) - 直线导轨，沿 X 轴移动
  ↓
2. j${leg_num}1   - 旋转关节 (revolute)  - 髋关节侧摆 (HAA - Hip Abduction/Adduction)
  ↓
3. j${leg_num}11  - 旋转关节 (revolute)  - 髋关节俯仰 (HFE - Hip Flexion/Extension)
  ↓
4. j${leg_num}111 - 旋转关节 (revolute)  - 膝关节 (KFE - Knee Flexion/Extension)
  ↓
足端 (foot)
```

### 关节详细说明

#### 1. 移动关节（Prismatic Joint）- j${leg_num}

- **类型**: 移动关节（prismatic）
- **轴向**: 沿 X 轴（`axis="-1 0 0"`）
- **功能**: 直线导轨，改变整条腿相对于躯干的位置
- **作用**: 扩展落足点工作空间，增加机器人的灵活性
- **限位**: 根据 URDF 配置（建议 ±0.1m）

#### 2. 髋关节侧摆（HAA）- j${leg_num}1

- **类型**: 旋转关节（revolute）
- **轴向**: 绕 X 轴旋转
- **功能**: 控制腿的侧向摆动（内收/外展）
- **限位**: ±150° (±2.618 rad)

#### 3. 髋关节俯仰（HFE）- j${leg_num}11

- **类型**: 旋转关节（revolute）
- **轴向**: 绕 X 轴旋转（在 HAA 旋转后的坐标系中）
- **功能**: 控制大腿的前后摆动
- **限位**: ±160° (±2.8 rad)

#### 4. 膝关节（KFE）- j${leg_num}111

- **类型**: 旋转关节（revolute）
- **轴向**: 绕 X 轴旋转
- **功能**: 控制小腿的弯曲
- **限位**: -160° ~ 0° (-2.8 ~ 0.0 rad)（单向弯曲）

## 逆运动学求解策略

### 冗余自由度问题

从三维足端位置 (x, y, z) 求解四个关节角度存在 **无穷多解**。这是因为：
- 输入：3 个约束（足端的 x, y, z 坐标）
- 输出：4 个关节变量（prismatic, HAA, HFE, KFE）
- 自由度：4 - 3 = 1（一个冗余自由度）

### 参数化策略

我们采用 **参数化策略** 来处理冗余：

1. **将移动关节位置作为输入参数**
   - 移动关节位置可以是：
     - 给定的固定值
     - 优化变量（通过搜索找到最优值）
     - 从上层规划器传入的期望值

2. **求解剩余 3 个旋转关节**
   - 给定移动关节位置后，问题简化为标准的 3-DOF 逆运动学
   - 使用解析方法求解 HAA, HFE, KFE

### 求解步骤

#### 步骤 1: 计算移动关节位置

```
prismatic_pos = base_to_prismatic_offset + [prismatic_position, 0, 0]
```

#### 步骤 2: 计算 HAA 轴位置

```
haa_pos = prismatic_pos + prismatic_to_haa_offset
```

#### 步骤 3: 求解 HAA（髋关节侧摆）

```
haa_to_foot = foot_position - haa_pos
haa = atan2(haa_to_foot.z, haa_to_foot.y)
```

HAA 控制腿在 Y-Z 平面的侧向摆动。

#### 步骤 4: 计算 HFE 轴位置

考虑 HAA 旋转后的坐标变换：

```
hfe_offset_rotated = rotate_around_x(haa_to_hfe_offset, haa)
hfe_pos = haa_pos + hfe_offset_rotated
```

#### 步骤 5: 投影到 HFE-KFE 平面

将问题投影到 HFE-KFE 平面，得到 2R 平面机械臂问题：

```
hfe_to_foot = foot_position - hfe_pos
plane_x = hfe_to_foot.x
plane_y = hfe_to_foot.y * cos(haa) + hfe_to_foot.z * sin(haa)
```

#### 步骤 6: 求解 2R 平面逆运动学

使用余弦定理求解：

```
distance = sqrt(plane_x^2 + plane_y^2)

# 膝关节角度
cos_kfe = (l1^2 + l2^2 - distance^2) / (2 * l1 * l2)
kfe = -acos(cos_kfe)  # 肘向下配置

# 髋关节俯仰角度
alpha = atan2(plane_y, plane_x)
beta = acos((l1^2 + distance^2 - l2^2) / (2 * l1 * distance))
hfe = alpha - beta
```

其中：
- `l1` = 大腿长度（thigh_length）
- `l2` = 小腿长度（shin_length）

#### 步骤 7: 检查关节限位

验证所有关节角度是否在允许范围内。

## 正运动学

正运动学用于验证逆运动学解的正确性：

```python
def forward_kinematics(prismatic, haa, hfe, kfe):
    # 1. 移动关节位置
    prismatic_pos = base_to_prismatic_offset + [prismatic, 0, 0]
    
    # 2. HAA 位置
    haa_pos = prismatic_pos + prismatic_to_haa_offset
    
    # 3. HFE 位置（考虑 HAA 旋转）
    hfe_offset_rotated = rotate_around_x(haa_to_hfe_offset, haa)
    hfe_pos = haa_pos + hfe_offset_rotated
    
    # 4. 在 HFE 平面内计算足端位置
    plane_x = l1 * cos(hfe) + l2 * cos(hfe + kfe)
    plane_y = l1 * sin(hfe) + l2 * sin(hfe + kfe)
    
    # 5. 转换回基座坐标系
    foot_x = hfe_pos.x + plane_x
    foot_y = hfe_pos.y + plane_y * cos(haa)
    foot_z = hfe_pos.z + plane_y * sin(haa)
    
    return [foot_x, foot_y, foot_z]
```

## 使用方法

### Python 接口

```python
from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# 创建腿 1 的几何参数
geometry = create_dog2_leg_geometry(1)
ik_solver = LegIK4DOF(geometry)

# 方法 1: 给定移动关节位置求解
target_foot_pos = np.array([1.0, -0.8, 0.0])
prismatic_position = 0.0  # 移动关节位置
solution = ik_solver.solve(target_foot_pos, prismatic_position)

if solution.valid:
    print(f"移动关节: {solution.prismatic}")
    print(f"HAA: {solution.haa}")
    print(f"HFE: {solution.hfe}")
    print(f"KFE: {solution.kfe}")
else:
    print(f"求解失败: {solution.error_msg}")

# 方法 2: 自动优化移动关节位置
solution = ik_solver.solve_with_optimization(target_foot_pos, prismatic_preference=0.0)

# 验证：正运动学
foot_pos_verify = ik_solver.forward_kinematics(
    solution.prismatic, solution.haa, solution.hfe, solution.kfe
)
```

### 测试脚本

```bash
cd ~/aperfect/carbot_ws
python3 test_4dof_ik.py
```

测试内容：
1. 正运动学验证
2. 逆运动学求解
3. 往返测试（FK -> IK -> FK）
4. 自动优化移动关节位置
5. 所有四条腿的测试

## 几何参数（基于 URDF）

### 腿 1（前左）

```python
base_to_prismatic_offset = [1.1026, -0.80953, 0.2649]
prismatic_to_haa_offset = [-0.016, 0.0199, 0.055]
haa_to_hfe_offset = [-0.0233, -0.055, 0.0274]
thigh_length = 0.1998  # sqrt(0.15201^2 + 0.12997^2)
shin_length = 0.299478
```

### 腿 2（前右）

```python
base_to_prismatic_offset = [1.1026, 0.80953, 0.2649]
# 其他参数与腿 1 相同
```

### 腿 3（后左）

```python
base_to_prismatic_offset = [-1.1026, -0.80953, 0.2649]
# 其他参数与腿 1 相同
```

### 腿 4（后右）

```python
base_to_prismatic_offset = [-1.1026, 0.80953, 0.2649]
# 其他参数与腿 1 相同
```

## 控制代码集成

### 完整的四关节控制

在生成控制命令时，**必须包含所有 4 个关节**：

```python
# ❌ 错误：只控制 3 个旋转关节
joint_names = ['j1_1', 'j1_11', 'j1_111']  # 缺少移动关节！

# ✅ 正确：控制所有 4 个关节
joint_names = ['j1', 'j1_1', 'j1_11', 'j1_111']
joint_positions = [prismatic, haa, hfe, kfe]
```

### ROS 2 轨迹控制示例

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# 为所有 4 条腿创建轨迹
joint_names = [
    # 腿 1 (前左) - 4 个关节
    'j1', 'j11', 'j111', 'j1111',
    # 腿 2 (前右) - 4 个关节
    'j2', 'j21', 'j211', 'j2111',
    # 腿 3 (后左) - 4 个关节
    'j3', 'j31', 'j311', 'j3111',
    # 腿 4 (后右) - 4 个关节
    'j4', 'j41', 'j411', 'j4111'
]

# 求解每条腿的逆运动学
leg1_solution = ik_solver_leg1.solve(foot_pos_leg1, prismatic_leg1)
leg2_solution = ik_solver_leg2.solve(foot_pos_leg2, prismatic_leg2)
leg3_solution = ik_solver_leg3.solve(foot_pos_leg3, prismatic_leg3)
leg4_solution = ik_solver_leg4.solve(foot_pos_leg4, prismatic_leg4)

# 组合所有关节位置
joint_positions = [
    # 腿 1
    leg1_solution.prismatic, leg1_solution.haa, leg1_solution.hfe, leg1_solution.kfe,
    # 腿 2
    leg2_solution.prismatic, leg2_solution.haa, leg2_solution.hfe, leg2_solution.kfe,
    # 腿 3
    leg3_solution.prismatic, leg3_solution.haa, leg3_solution.hfe, leg3_solution.kfe,
    # 腿 4
    leg4_solution.prismatic, leg4_solution.haa, leg4_solution.hfe, leg4_solution.kfe
]

# 创建轨迹点
point = JointTrajectoryPoint()
point.positions = joint_positions
point.time_from_start = Duration(sec=1, nanosec=0)

# 发布轨迹
traj = JointTrajectory()
traj.joint_names = joint_names
traj.points = [point]
publisher.publish(traj)
```

## 优化策略

### 移动关节位置优化

移动关节的位置可以根据不同的优化目标选择：

1. **最小化关节角度**
   - 选择使 HAA, HFE, KFE 接近零位的 prismatic 值

2. **最大化操作性**
   - 选择使雅可比矩阵条件数最小的 prismatic 值

3. **避免关节限位**
   - 选择使所有关节远离限位的 prismatic 值

4. **能量最优**
   - 选择使关节力矩最小的 prismatic 值

5. **保持偏好位置**
   - 选择接近给定偏好值的 prismatic 值（例如保持在中间位置）

### 实现示例

```python
def optimize_prismatic_position(foot_position, optimization_goal='min_joint_angles'):
    """优化移动关节位置"""
    best_solution = None
    best_cost = float('inf')
    
    # 在允许范围内搜索
    for prismatic in np.linspace(prismatic_lower, prismatic_upper, 20):
        solution = ik_solver.solve(foot_position, prismatic)
        
        if not solution.valid:
            continue
        
        # 计算代价函数
        if optimization_goal == 'min_joint_angles':
            cost = abs(solution.haa) + abs(solution.hfe) + abs(solution.kfe)
        elif optimization_goal == 'center_preference':
            cost = abs(prismatic)
        # ... 其他优化目标
        
        if cost < best_cost:
            best_cost = cost
            best_solution = solution
    
    return best_solution
```

## 注意事项

1. **绝对不要漏掉移动关节**
   - 在所有控制代码中必须包含移动关节的控制通道
   - 关节数量：每条腿 4 个，总共 16 个关节

2. **参数化策略的重要性**
   - 移动关节位置必须作为输入参数或优化变量
   - 不能简单地忽略移动关节，设为零

3. **坐标系变换**
   - 注意 HAA 旋转对后续关节的影响
   - 正确处理坐标系变换

4. **关节限位检查**
   - 始终检查所有 4 个关节是否在限位范围内
   - 特别注意膝关节的单向限位

5. **数值稳定性**
   - 在求解反三角函数时进行数值裁剪
   - 检查工作空间边界

## 文件结构

```
src/dog2_kinematics/
├── include/dog2_kinematics/
│   └── leg_ik_4dof.hpp          # C++ 头文件
├── src/
│   └── leg_ik_4dof.cpp          # C++ 实现
└── dog2_kinematics/
    └── leg_ik_4dof.py           # Python 实现

test_4dof_ik.py                  # 测试脚本
DOG2_4DOF_KINEMATICS.md          # 本文档
```

## 参考资料

- URDF 文件: `src/dog2_description/urdf/dog2.urdf.xacro`
- 关节配置: `src/dog2_description/config/ros2_controllers.yaml`
- 测试脚本: `test_4dof_ik.py`

## 总结

Dog2 机器人的 4-DOF 腿部设计提供了额外的灵活性，但也带来了冗余自由度的求解挑战。通过参数化移动关节位置，我们将问题简化为标准的 3-DOF 逆运动学，同时保留了优化移动关节位置的能力。

在实现控制算法时，**务必记住包含所有 4 个关节的控制逻辑**，这是确保机器人正确运动的关键。
