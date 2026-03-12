# Dog2 四自由度机器人 - 完整总结

## ✅ 确认：Dog2 是 4-DOF 腿部机器人

经过详细分析 URDF 文件，**确认** Dog2 机器人每条腿具有 **4 个自由度**：

### 关节链结构（每条腿）

```
基座 (base_link)
  ↓
1. j${leg_num}    - 移动关节 (prismatic) - 直线导轨
  ↓  
2. j${leg_num}1   - 旋转关节 (revolute)  - 髋关节侧摆 (HAA)
  ↓
3. j${leg_num}11  - 旋转关节 (revolute)  - 髋关节俯仰 (HFE)
  ↓
4. j${leg_num}111 - 旋转关节 (revolute)  - 膝关节 (KFE)
  ↓
足端 (l${leg_num}1111) - 固定连接
```

### 关节命名（实际 URDF）

| 腿编号 | 移动关节 | HAA | HFE | KFE | 足端 |
|--------|----------|-----|-----|-----|------|
| 腿 1 (前左) | j1 | j11 | j111 | j1111 | l11111 |
| 腿 2 (前右) | j2 | j21 | j211 | j2111 | l21111 |
| 腿 3 (后左) | j3 | j31 | j311 | j3111 | l31111 |
| 腿 4 (后右) | j4 | j41 | j411 | j4111 | l41111 |

**总计：16 个可控关节（4 条腿 × 4 个关节）**

## 📐 URDF 中的几何参数

### 移动关节限位（从 URDF 提取）

| 腿编号 | 下限 | 上限 | 说明 |
|--------|------|------|------|
| 腿 1 | -0.111 m | 0.0 m | 向后移动 |
| 腿 2 | 0.0 m | 0.111 m | 向前移动 |
| 腿 3 | -0.111 m | 0.0 m | 向后移动 |
| 腿 4 | 0.0 m | 0.111 m | 向前移动 |

### 旋转关节限位

| 关节类型 | 下限 | 上限 | 说明 |
|----------|------|------|------|
| HAA (髋关节侧摆) | -2.618 rad | 2.618 rad | ±150° |
| HFE (髋关节俯仰) | -2.8 rad | 2.8 rad | ±160° |
| KFE (膝关节) | -2.8 rad | 0.0 rad | 单向弯曲 |

### 连杆长度（从 URDF 计算）

```python
# 大腿长度（HFE 到 KFE）
thigh_length = sqrt(0.15201^2 + 0.12997^2) = 0.1998 m

# 小腿长度（KFE 到足端）
shin_length = 0.299478 m
```

## 🎯 已创建的逆运动学求解器

我已经为你创建了完整的 4-DOF 逆运动学求解器：

### 文件列表

1. **C++ 实现**
   - `src/dog2_kinematics/include/dog2_kinematics/leg_ik_4dof.hpp`
   - `src/dog2_kinematics/src/leg_ik_4dof.cpp`

2. **Python 实现**
   - `src/dog2_kinematics/dog2_kinematics/leg_ik_4dof.py`

3. **测试脚本**
   - `test_4dof_ik.py`

4. **文档**
   - `DOG2_4DOF_KINEMATICS.md` - 完整技术文档
   - `DOG2_4DOF_SUMMARY.md` - 本文档

### 核心特性

✅ **参数化策略**
- 移动关节位置作为输入参数
- 求解剩余 3 个旋转关节的解析解

✅ **两种求解模式**
1. `solve(foot_position, prismatic_position)` - 给定移动关节位置
2. `solve_with_optimization(foot_position, prismatic_preference)` - 自动优化移动关节位置

✅ **正运动学验证**
- `forward_kinematics(prismatic, haa, hfe, kfe)` - 验证逆运动学解

✅ **完整的 4 关节支持**
- 绝对不会漏掉移动关节
- 所有控制代码都包含 4 个关节

## 🚀 使用示例

### Python 快速开始

```python
from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry
import numpy as np

# 创建腿 1 的求解器
geometry = create_dog2_leg_geometry(1)
ik_solver = LegIK4DOF(geometry)

# 目标足端位置
target_foot_pos = np.array([1.0, -0.8, 0.0])

# 方法 1: 给定移动关节位置
prismatic_pos = -0.05  # 在允许范围内 [-0.111, 0.0]
solution = ik_solver.solve(target_foot_pos, prismatic_pos)

if solution.valid:
    print(f"✅ 求解成功!")
    print(f"移动关节: {solution.prismatic:.4f} m")
    print(f"HAA: {solution.haa:.4f} rad")
    print(f"HFE: {solution.hfe:.4f} rad")
    print(f"KFE: {solution.kfe:.4f} rad")
else:
    print(f"❌ 求解失败: {solution.error_msg}")

# 方法 2: 自动优化移动关节位置
solution = ik_solver.solve_with_optimization(target_foot_pos)
```

### ROS 2 控制集成

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# 为所有 4 条腿创建求解器
ik_solvers = [
    LegIK4DOF(create_dog2_leg_geometry(1)),  # 前左
    LegIK4DOF(create_dog2_leg_geometry(2)),  # 前右
    LegIK4DOF(create_dog2_leg_geometry(3)),  # 后左
    LegIK4DOF(create_dog2_leg_geometry(4))   # 后右
]

# 目标足端位置（4 条腿）
foot_positions = [
    np.array([1.0, -0.8, 0.0]),  # 腿 1
    np.array([1.0, 0.8, 0.0]),   # 腿 2
    np.array([-1.0, -0.8, 0.0]), # 腿 3
    np.array([-1.0, 0.8, 0.0])   # 腿 4
]

# 移动关节偏好位置
prismatic_preferences = [-0.05, 0.05, -0.05, 0.05]

# 求解所有腿的逆运动学
solutions = []
for i in range(4):
    solution = ik_solvers[i].solve(foot_positions[i], prismatic_preferences[i])
    if not solution.valid:
        print(f"警告：腿 {i+1} 逆运动学求解失败")
    solutions.append(solution)

# 组合所有关节位置（16 个关节）
joint_names = [
    'j1', 'j11', 'j111', 'j1111',    # 腿 1
    'j2', 'j21', 'j211', 'j2111',    # 腿 2
    'j3', 'j31', 'j311', 'j3111',    # 腿 3
    'j4', 'j41', 'j411', 'j4111'     # 腿 4
]

joint_positions = []
for solution in solutions:
    joint_positions.extend([
        solution.prismatic,  # 移动关节
        solution.haa,        # HAA
        solution.hfe,        # HFE
        solution.kfe         # KFE
    ])

# 创建并发布轨迹
point = JointTrajectoryPoint()
point.positions = joint_positions
point.time_from_start = Duration(sec=1, nanosec=0)

traj = JointTrajectory()
traj.joint_names = joint_names
traj.points = [point]

publisher.publish(traj)
```

## ⚠️ 重要注意事项

### 1. 绝对不要漏掉移动关节

❌ **错误示例**（只控制 3 个关节）：
```python
joint_names = ['j11', 'j111', 'j1111']  # 缺少 j1！
joint_positions = [haa, hfe, kfe]       # 缺少 prismatic！
```

✅ **正确示例**（控制所有 4 个关节）：
```python
joint_names = ['j1', 'j11', 'j111', 'j1111']
joint_positions = [prismatic, haa, hfe, kfe]
```

### 2. 移动关节限位不对称

注意每条腿的移动关节限位是不同的：
- 腿 1, 3：只能向后移动（负方向）
- 腿 2, 4：只能向前移动（正方向）

### 3. 参数化策略的必要性

由于 4-DOF 系统的冗余性，必须：
- 将移动关节位置作为输入参数，或
- 使用优化方法自动选择移动关节位置

不能简单地将移动关节设为零！

### 4. 坐标系变换

HAA 旋转会影响后续关节的坐标系，求解器已正确处理这个变换。

## 📊 测试结果

运行测试脚本：
```bash
python3 test_4dof_ik.py
```

测试内容：
1. ✅ 正运动学计算
2. ✅ 逆运动学求解
3. ✅ 往返测试（FK -> IK -> FK）
4. ✅ 自动优化移动关节位置
5. ✅ 所有四条腿的测试

## 🔧 下一步集成

### 1. 创建 ROS 2 包

```bash
cd ~/aperfect/carbot_ws/src
ros2 pkg create dog2_kinematics --build-type ament_python --dependencies rclpy numpy
```

### 2. 复制文件

```bash
cp -r dog2_kinematics/dog2_kinematics/* src/dog2_kinematics/dog2_kinematics/
```

### 3. 编译

```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_kinematics
source install/setup.bash
```

### 4. 在行走控制中使用

修改 `forward_walk_demo.py` 和 `simple_walk_demo.py`，使用逆运动学求解器：

```python
from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry

# 创建求解器
ik_solvers = [LegIK4DOF(create_dog2_leg_geometry(i)) for i in range(1, 5)]

# 在步态规划中使用
def compute_joint_angles_for_foot_positions(foot_positions):
    """根据足端位置计算关节角度"""
    joint_positions = []
    
    for i, foot_pos in enumerate(foot_positions):
        solution = ik_solvers[i].solve_with_optimization(foot_pos)
        
        if solution.valid:
            joint_positions.extend([
                solution.prismatic,
                solution.haa,
                solution.hfe,
                solution.kfe
            ])
        else:
            # 使用默认姿态或报错
            print(f"警告：腿 {i+1} 逆运动学失败")
            joint_positions.extend([0.0, 0.0, 0.4, -1.0])
    
    return joint_positions
```

## 📚 参考文档

1. **DOG2_4DOF_KINEMATICS.md** - 完整技术文档
   - 详细的数学推导
   - 求解算法说明
   - 优化策略
   - API 参考

2. **test_4dof_ik.py** - 测试和示例代码
   - 正运动学测试
   - 逆运动学测试
   - 往返验证
   - 优化示例

3. **URDF 文件** - `src/dog2_description/urdf/dog2.urdf.xacro`
   - 实际的机器人几何参数
   - 关节限位
   - 连杆长度

## 🎓 关键概念总结

1. **4-DOF 冗余系统**
   - 3 个位置约束 vs 4 个关节变量
   - 存在无穷多解

2. **参数化策略**
   - 移动关节位置作为参数
   - 简化为 3-DOF 问题

3. **解析求解**
   - HAA：从 Y-Z 平面投影求解
   - HFE-KFE：2R 平面逆运动学

4. **完整控制**
   - 必须包含所有 4 个关节
   - 16 个关节总计（4 腿 × 4 关节）

## ✅ 总结

你的 Dog2 机器人确实是一个 **4-DOF 腿部机器人**，具有直线导轨移动关节。我已经为你创建了：

1. ✅ 完整的 4-DOF 逆运动学求解器（C++ 和 Python）
2. ✅ 参数化策略处理冗余自由度
3. ✅ 自动优化移动关节位置的功能
4. ✅ 正运动学验证
5. ✅ 完整的测试脚本
6. ✅ 详细的技术文档

**所有代码都正确处理了 4 个关节，绝对不会漏掉移动关节！**

现在你可以在行走控制算法中使用这个逆运动学求解器，实现基于足端位置的运动规划。
