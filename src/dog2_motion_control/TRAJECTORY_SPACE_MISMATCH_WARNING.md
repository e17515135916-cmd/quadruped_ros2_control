# 轨迹空间不匹配警告

## 日期
2026-03-01

## ⚠️ 关键架构问题

### 问题描述

`TrajectoryPlanner` 存在一个**空间不匹配**问题：

**轨迹生成（笛卡尔空间）：**
```python
plan_swing_trajectory(...) -> Callable[[float], np.ndarray]
plan_stance_trajectory(...) -> Callable[[float], np.ndarray]
# 返回：(x, y, z) 笛卡尔坐标
```

**安全检查（关节空间）：**
```python
check_joint_velocity_constraints(
    joint_trajectory: Callable[[float], Dict[str, float]],  # ← 期望关节角度！
    ...
)

verify_trajectory_safety(
    joint_trajectory: Callable[[float], Dict[str, float]],  # ← 期望关节角度！
    ...
)
```

### 为什么这不是 Bug？

这是**有意的设计分离**：
- 轨迹规划器在**笛卡尔空间**工作（更直观，更容易规划脚部运动）
- 安全检查在**关节空间**工作（电机限位、速度限制都是关节空间的）

### 🚨 在 Task 9 主控制器中必须解决

## 解决方案：包装函数（Wrapper）

在主控制器中，**不能直接**将 `plan_swing_trajectory` 的返回值传给 `check_joint_velocity_constraints`。

必须创建一个**包装函数**，将笛卡尔轨迹转换为关节轨迹：

```python
class SpiderRobotController:
    def __init__(self):
        self.kinematics_solver = KinematicsSolver(leg_params)
        self.trajectory_planner = TrajectoryPlanner()
    
    def create_joint_trajectory_wrapper(
        self,
        leg_id: str,
        cartesian_trajectory: Callable[[float], np.ndarray]
    ) -> Callable[[float], Dict[str, float]]:
        """
        将笛卡尔空间轨迹包装为关节空间轨迹
        
        这是连接轨迹规划器和安全检查器的关键桥梁！
        
        Args:
            leg_id: 腿部标识 ('lf', 'rf', 'lh', 'rh')
            cartesian_trajectory: 笛卡尔轨迹函数 f(t) -> (x, y, z)
        
        Returns:
            关节轨迹函数 f(t) -> {'rail': pos, 'haa': angle, ...}
        """
        def joint_trajectory(t: float) -> Dict[str, float]:
            # 1. 获取笛卡尔空间的目标位置
            foot_pos = cartesian_trajectory(t)
            
            # 2. 调用逆运动学求解器
            joint_positions = self.kinematics_solver.solve_ik(leg_id, foot_pos)
            
            if joint_positions is None:
                # IK 无解时的错误处理
                raise ValueError(f"IK failed for leg {leg_id} at t={t}, pos={foot_pos}")
            
            # 3. 转换为字典格式
            rail_pos_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad = joint_positions
            
            return {
                'rail': rail_pos_m,
                'haa': theta_haa_rad,
                'hfe': theta_hfe_rad,
                'kfe': theta_kfe_rad,
            }
        
        return joint_trajectory
```

## 完整使用流程

```python
# 在主控制器的 update() 方法中：

def update(self, dt: float):
    for leg_id in ['lf', 'rf', 'lh', 'rh']:
        # 1. 获取脚部目标位置（来自步态生成器）
        foot_target = self.gait_generator.get_foot_target(leg_id)
        foot_current = self.get_current_foot_position(leg_id)
        
        # 2. 生成笛卡尔空间轨迹
        if self.gait_generator.is_stance_phase(leg_id):
            cartesian_traj = self.trajectory_planner.plan_stance_trajectory(
                foot_current, foot_target, duration=0.5
            )
        else:
            cartesian_traj = self.trajectory_planner.plan_swing_trajectory(
                foot_current, foot_target, duration=0.5, height=0.05
            )
        
        # 3. 【关键步骤】包装为关节空间轨迹
        joint_traj = self.create_joint_trajectory_wrapper(leg_id, cartesian_traj)
        
        # 4. 现在可以安全地进行速度检查
        is_valid, ratio = self.trajectory_planner.check_joint_velocity_constraints(
            joint_traj, duration=0.5
        )
        
        if not is_valid:
            # 自动调整时间
            adjusted_duration = self.trajectory_planner.adjust_trajectory_duration(
                joint_traj, initial_duration=0.5
            )
            # 重新生成轨迹...
        
        # 5. 进行安全性验证
        leg_params = get_leg_parameters(leg_id)
        is_safe, violations = self.trajectory_planner.verify_trajectory_safety(
            joint_traj,
            leg_params.joint_limits,
            duration=0.5
        )
        
        if not is_safe:
            # 错误处理...
            pass
        
        # 6. 执行轨迹
        for t in np.linspace(0, 0.5, 25):  # 50Hz
            joint_positions = joint_traj(t)
            self.joint_controller.send_joint_commands(leg_id, joint_positions)
```

## 为什么不在 TrajectoryPlanner 中直接集成？

**设计原则：单一职责**

1. **TrajectoryPlanner** 只负责轨迹规划（笛卡尔空间）
   - 不依赖运动学求解器
   - 可以独立测试
   - 可以用于其他机器人

2. **KinematicsSolver** 只负责运动学计算
   - 不依赖轨迹规划器
   - 可以独立测试

3. **SpiderRobotController** 负责组装和协调
   - 连接各个模块
   - 处理空间转换
   - 实现完整的控制逻辑

## 测试建议

在实现主控制器时，务必测试：

```python
def test_joint_trajectory_wrapper():
    """测试笛卡尔轨迹到关节轨迹的转换"""
    controller = SpiderRobotController()
    
    # 创建简单的笛卡尔轨迹
    start = np.array([0.0, 0.0, -0.3])
    end = np.array([0.1, 0.0, -0.3])
    cartesian_traj = controller.trajectory_planner.plan_stance_trajectory(
        start, end, duration=1.0
    )
    
    # 包装为关节轨迹
    joint_traj = controller.create_joint_trajectory_wrapper('lf', cartesian_traj)
    
    # 验证：起点和终点的关节角度应该对应正确的笛卡尔位置
    joints_0 = joint_traj(0.0)
    joints_1 = joint_traj(1.0)
    
    # 通过正运动学验证
    fk_0 = controller.kinematics_solver.solve_fk('lf', 
        (joints_0['rail'], joints_0['haa'], joints_0['hfe'], joints_0['kfe'])
    )
    fk_1 = controller.kinematics_solver.solve_fk('lf',
        (joints_1['rail'], joints_1['haa'], joints_1['hfe'], joints_1['kfe'])
    )
    
    assert np.allclose(fk_0, start, atol=0.001)
    assert np.allclose(fk_1, end, atol=0.001)
    
    print("✅ 包装函数测试通过！")
```

## 相关任务

- **Task 6**: 实现轨迹规划器 ✅（已完成，但需要注意接口）
- **Task 9**: 实现主控制器 ⚠️（必须实现包装函数）

## 总结

这不是一个 Bug，而是一个**需要在集成时特别注意的架构设计点**。

关键要点：
1. ✅ 轨迹规划器在笛卡尔空间工作（正确）
2. ✅ 安全检查在关节空间工作（正确）
3. ⚠️ 主控制器必须提供空间转换包装函数（待实现）

**在 Task 9 实现主控制器时，务必参考本文档！**
