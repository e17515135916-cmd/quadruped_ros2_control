# 设计文档：蜘蛛机器人基础运动算法

## 概述

本设计实现了一个简单但功能完整的四足机器人运动控制系统，使蜘蛛式机器人能够在Gazebo仿真环境中执行基础的爬行步态（crawl gait）。系统采用模块化设计，包含运动学求解器、步态生成器、轨迹规划器和ROS 2接口层。

### 设计目标

- **静态稳定性**: 使用爬行步态确保至少三条腿始终着地，质心投影在支撑三角形内
- **安全性**: 适用于狭窄的油箱内部环境，避免动态失稳导致撞击
- **简单性**: 使用最简单的算法让机器人快速动起来
- **模块化**: 各组件独立，便于测试和扩展
- **实时性**: 满足50Hz控制频率要求

### 技术栈

- **语言**: Python 3
- **框架**: ROS 2 Humble
- **仿真**: Gazebo Fortress
- **数学库**: NumPy, SciPy
- **控制接口**: ros2_control

## 架构

系统采用分层架构，从上到下分为四层：

```
┌─────────────────────────────────────┐
│      ROS 2 Interface Layer          │  ← 接收cmd_vel，发布joint commands
├─────────────────────────────────────┤
│      Gait Generator Layer           │  ← 生成步态相位和脚部轨迹
├─────────────────────────────────────┤
│   Kinematics & Trajectory Layer     │  ← 逆运动学求解和轨迹插值
├─────────────────────────────────────┤
│      Joint Controller Layer         │  ← 发送命令到ros2_control
└─────────────────────────────────────┘
```

### 16通道架构实现策略

机器人物理上具有16个关节通道（4条腿 × 4个关节），但当前阶段采用"锁定导轨"策略：

**1. 接口层（JointController）**
- 发送16个通道的关节命令
- 对于4个直线导轨（leg{1-4}_j1），永远发送恒定设定值0.0
- 相当于用高增益PD控制器将导轨"锁死"在初始位置
- 对于12个旋转关节，发送动态计算的目标位置

**2. 运动学层（KinematicsSolver）**
- IK函数接受4-DOF参数：`solve_ik(leg_id, foot_pos, rail_offset=0.0)`
- 预留了导轨位移`rail_offset`参数接口
- 当前阶段调用时强制传入`rail_offset=0.0`
- 返回4个关节值：(s, θ_HAA, θ_HFE, θ_KFE)，其中s恒为0.0

**3. 步态层（GaitGenerator）**
- 纯3自由度规划，完全不考虑导轨移动
- 只生成脚端在(x, y, z)坐标系下的抛物线摆动轨迹
- 算法与普通四足机器人完全相同，简单易实现

**设计优势**:
- ✅ 简化初期开发，快速验证基础步态
- ✅ 接口已预留，未来可平滑扩展到4-DOF动态规划
- ✅ 物理仿真中导轨被可靠锁定，不会产生意外移动
- ✅ 降低调试复杂度，专注于旋转关节的协调控制

### 数据流

1. 用户通过`/cmd_vel`发送速度命令
2. Gait Generator根据速度生成步态相位
3. 对于每条腿，计算脚部目标位置（3D坐标）
4. Kinematics Solver将脚部位置转换为4个关节角度（导轨固定为0）
5. Trajectory Planner生成平滑的关节轨迹
6. Joint Controller发送16通道命令到ros2_control（导轨通道恒为0）

## 组件和接口

### 1. SpiderRobotController (主控制器)

**职责**: 协调所有子系统，实现主控制循环

**接口**:
```python
class SpiderRobotController:
    def __init__(self, node: rclpy.node.Node)
    def start(self) -> None
    def stop(self) -> None
    def update(self, dt: float) -> None  # 主控制循环，50Hz调用
```

**属性**:
- `gait_generator`: GaitGenerator实例
- `kinematics_solver`: KinematicsSolver实例
- `trajectory_planner`: TrajectoryPlanner实例
- `joint_controller`: JointController实例
- `current_velocity`: (vx, vy, omega) 当前期望速度
- `robot_state`: 机器人当前状态（关节角度、位置等）

**时间同步设计**:

在Gazebo仿真环境中，系统必须使用ROS 2仿真时间而非系统墙钟时间，以确保步态时序与物理引擎同步。

**问题**: 使用`time.time()`（墙钟时间）会导致：
- 当仿真速度慢于实时（Real Time Factor < 1.0）时，控制算法运行过快
- 步态相位与物理引擎完全错位
- 机器人运动不稳定或失败

**解决方案**: 使用ROS 2节点的时钟API
```python
class SpiderRobotController(Node):
    def __init__(self):
        super().__init__('spider_robot_controller')
        # 使用节点时钟而非time.time()
        self.last_time = self.get_clock().now()
    
    def _timer_callback(self):
        # 获取当前ROS时间
        current_time = self.get_clock().now()
        # 计算时间增量（自动适应仿真时间）
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time
        
        self.update(dt)
```

**优势**:
- ✅ 自动适应仿真速度变化
- ✅ 与Gazebo物理引擎完美同步
- ✅ 支持时间加速/减速
- ✅ 兼容真实硬件（使用系统时间）

**需求**: 验证需求 5.5, 5.6

### 2. GaitGenerator (步态生成器)

**职责**: 生成爬行步态的相位和脚部轨迹（纯3自由度规划，不考虑导轨移动）

**接口**:
```python
class GaitGenerator:
    def __init__(self, config: GaitConfig)
    def update(self, dt: float, velocity: Tuple[float, float, float]) -> None
    def get_foot_target(self, leg_id: str) -> Tuple[float, float, float]
    def is_stance_phase(self, leg_id: str) -> bool
    def get_support_triangle(self) -> List[str]  # 返回当前支撑腿列表
```

**参数**:
- `stride_length`: 步长（米）
- `stride_height`: 步高（米）
- `cycle_time`: 步态周期时间（秒）
- `duty_factor`: 支撑相占比（0.75表示75%时间支撑，确保至少3腿着地）

**步态模式 - 爬行步态（Crawl Gait）**:
- **静态稳定**: 每次只有一条腿摆动，其余三条腿保持支撑
- **腿部顺序**: leg1 → leg3 → leg2 → leg4（或其他合理顺序）
- **相位分布**: 4条腿相位均匀分布，相位差90度
- **支撑三角形**: 任何时刻都有3条腿着地，形成稳定的支撑三角形

**实现策略**:
- **纯3自由度规划**: 只生成脚端在(x, y, z)坐标系下的抛物线摆动轨迹
- **不考虑导轨**: 完全忽略直线导轨的移动
- **静态稳定保证**: 在切换摆动腿之前，验证质心投影在新的支撑三角形内

### 3. KinematicsSolver (运动学求解器)

**职责**: 计算腿部的逆运动学（当前阶段为3自由度，预留4自由度接口）

**接口**:
```python
class KinematicsSolver:
    def __init__(self, leg_params: Dict[str, LegParameters])
    def solve_ik(self, leg_id: str, foot_pos: Tuple[float, float, float], rail_offset: float = 0.0) -> Optional[Tuple[float, float, float, float]]
    def solve_fk(self, leg_id: str, joint_positions: Tuple[float, float, float, float]) -> Tuple[float, float, float]
```

**返回值说明**:
- 返回类型：`Tuple[float, float, float, float]`
- 元素含义：`(rail_position_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad)`
- `rail_position_m`: 导轨位移，单位：米（m），当前阶段固定为0.0
- `theta_haa_rad`: HAA关节角度，单位：弧度（rad）
- `theta_hfe_rad`: HFE关节角度，单位：弧度（rad）
- `theta_kfe_rad`: KFE关节角度，单位：弧度（rad）

**实现策略**:
- **当前阶段**: 函数接受4自由度参数（3个旋转关节 + 1个直线导轨），但`rail_offset`参数固定传入0.0
- **未来扩展**: 接口已预留，可在后续版本中实现动态导轨规划
- **单位明确**: 代码中使用带单位后缀的变量名（如`rail_pos_m`, `theta_rad`）避免混淆

**算法**: 
- 使用几何法求解3-DOF腿部逆运动学
- HAA角度：根据脚部y坐标计算侧向角度
- HFE和KFE角度：使用2R平面机械臂逆运动学公式
- 导轨位移：当前阶段始终返回0.0

**坐标系转换**:
- 考虑每条腿的局部坐标系旋转（rpy参数）
- 将base_link坐标系下的目标位置转换到腿部局部坐标系

### 4. TrajectoryPlanner (轨迹规划器)

**职责**: 生成平滑的关节角度轨迹

**接口**:
```python
class TrajectoryPlanner:
    def __init__(self)
    def plan_swing_trajectory(self, start_pos: np.ndarray, end_pos: np.ndarray, 
                             duration: float, height: float) -> Callable[[float], np.ndarray]
    def plan_stance_trajectory(self, start_pos: np.ndarray, end_pos: np.ndarray,
                              duration: float) -> Callable[[float], np.ndarray]
```

**算法**:
- **摆动相**: 使用抛物线轨迹，确保脚部抬起到指定高度
- **支撑相**: 使用线性插值或三次样条
- 速度连续性：确保相位切换时速度平滑过渡

### 5. JointController (关节控制器)

**职责**: 与ros2_control接口通信，发送16通道关节命令（12个旋转关节 + 4个锁定的直线导轨）

**接口**:
```python
class JointController:
    def __init__(self, node: rclpy.node.Node)
    def send_joint_commands(self, joint_positions: Dict[str, float]) -> None
    def get_joint_states(self) -> Dict[str, JointState]
    def check_joint_limits(self, joint_name: str, position: float) -> float
    def monitor_rail_positions(self) -> bool  # 监控导轨是否发生滑动
    def lock_rails_with_max_effort(self) -> None  # 以最大力矩锁定导轨
```

**16通道架构**:
- **12个旋转关节**: 动态控制，根据步态生成器和运动学求解器计算的目标位置（单位：弧度）
- **4个直线导轨**: 恒定设定值（0.0米），通过高增益PD控制器"锁死"在初始位置
- 关节命名规范：
  - 导轨：`leg{1-4}_j1` (prismatic joints, 单位：米)
  - HAA：`leg{1-4}_j2` (revolute joints, 单位：弧度)
  - HFE：`leg{1-4}_j3` (revolute joints, 单位：弧度)
  - KFE：`leg{1-4}_j4` (revolute joints, 单位：弧度)

**实现细节**:
```python
def send_joint_commands(self, joint_positions: Dict[str, float]) -> None:
    """
    发送16通道关节命令
    
    参数:
        joint_positions: 字典，键为关节名，值为关节位置
                        - 导轨关节：位置单位为米（m）
                        - 旋转关节：位置单位为弧度（rad）
    """
    trajectory_msg = JointTrajectory()
    
    # 构建16个关节的命令
    for leg_id in ['leg1', 'leg2', 'leg3', 'leg4']:
        # 直线导轨：恒定锁定在0.0米
        trajectory_msg.joint_names.append(f'{leg_id}_j1')
        trajectory_msg.points[0].positions.append(0.0)  # 单位：米
        
        # 旋转关节：动态控制
        for joint_suffix in ['j2', 'j3', 'j4']:
            joint_name = f'{leg_id}_{joint_suffix}'
            trajectory_msg.joint_names.append(joint_name)
            # 单位：弧度
            trajectory_msg.points[0].positions.append(joint_positions[joint_name])
    
    self.publisher.publish(trajectory_msg)
```

**单位管理**:
- 在代码中使用明确的变量命名：`rail_pos_m`, `theta_rad`
- 在注释中标注单位：`# position in meters` 或 `# angle in radians`
- 在限位检查时分别处理不同类型的关节

**导轨安全监控**:
```python
def monitor_rail_positions(self) -> bool:
    """
    监控导轨位置，检测被动滑动
    
    返回:
        True: 所有导轨位置正常（±0.5mm内）
        False: 检测到导轨滑动，需要报警
    """
    SLIP_THRESHOLD_M = 0.0005  # 0.5mm
    
    for leg_id in ['leg1', 'leg2', 'leg3', 'leg4']:
        rail_joint = f'{leg_id}_j1'
        actual_pos_m = self.get_joint_position(rail_joint)
        
        if abs(actual_pos_m) > SLIP_THRESHOLD_M:
            self.log_error(
                f"Rail slip detected on {rail_joint}: "
                f"{actual_pos_m*1000:.2f}mm (threshold: ±0.5mm)"
            )
            return False
    
    return True

def lock_rails_with_max_effort(self) -> None:
    """
    以最大保持力矩锁定导轨
    
    用于紧急情况和安全姿态切换时
    确保导轨在受力情况下不会滑动
    """
    for leg_id in ['leg1', 'leg2', 'leg3', 'leg4']:
        rail_joint = f'{leg_id}_j1'
        # 发送位置指令并设置最大effort
        self.send_position_with_effort(
            joint_name=rail_joint,
            position_m=0.0,
            effort_max=True  # 使用最大保持力矩
        )
```

**话题**:
- 发布: `/joint_trajectory_controller/joint_trajectory` (trajectory_msgs/JointTrajectory)
- 订阅: `/joint_states` (sensor_msgs/JointState)

## 数据模型

### GaitConfig
```python
@dataclass
class GaitConfig:
    stride_length: float = 0.08     # 步长（米），爬行步态较小
    stride_height: float = 0.05     # 步高（米）
    cycle_time: float = 2.0         # 步态周期（秒），爬行步态较慢
    duty_factor: float = 0.75       # 支撑相占比（75%确保3腿着地）
    body_height: float = 0.2        # 身体高度（米）
    gait_type: str = "crawl"        # 步态类型
```

### LegParameters
```python
@dataclass
class LegParameters:
    leg_id: str                     # 腿部标识: lf, rf, lh, rh
    leg_num: int                    # 腿部编号: 1, 2, 3, 4
    base_position: np.ndarray       # 腿部基座在base_link中的位置
    base_rotation: np.ndarray       # 腿部坐标系旋转（rpy）
    link_lengths: Tuple[float, float, float, float]  # 导轨范围, HAA到HFE, HFE到KFE, KFE到foot的长度
    joint_limits: Dict[str, Tuple[float, float]]  # 关节限位（包含导轨和3个旋转关节）
    rail_locked: bool = True        # 导轨是否锁定（当前阶段为True）
```

### RobotState
```python
@dataclass
class RobotState:
    joint_positions: Dict[str, float]  # 关节位置（导轨：米，旋转：弧度）
    joint_velocities: Dict[str, float]  # 关节速度（导轨：米/秒，旋转：弧度/秒）
    base_position: np.ndarray          # 机身位置（米）
    base_orientation: np.ndarray       # 机身姿态（四元数）
    timestamp: float                   # 时间戳（秒）
```

### FootTrajectory
```python
@dataclass
class FootTrajectory:
    leg_id: str
    phase: float                    # 当前相位 [0, 1]
    is_stance: bool                 # 是否处于支撑相
    current_position: np.ndarray    # 当前脚部位置
    target_position: np.ndarray     # 目标脚部位置
```

## 运动学详细设计

### 16通道系统架构

机器人具有16个关节通道：
- **4个直线导轨** (prismatic joints): leg1_j1, leg2_j1, leg3_j1, leg4_j1
- **12个旋转关节** (revolute joints): 每条腿3个（HAA, HFE, KFE）

**当前阶段实现策略**:
1. **接口层**: JointController发送16个通道命令，导轨通道恒定为0.0
2. **运动学层**: IK函数接受4-DOF参数（包含导轨位移s），但调用时强制传入s=0.0
3. **步态层**: 纯3-DOF规划，完全不考虑导轨移动

这种设计使得：
- 导轨被"锁死"在初始位置（通过物理引擎的高增益PD控制器）
- 运动学算法与普通四足机器人相同，简单易实现
- 接口已预留，未来可扩展为动态导轨规划

### 腿部几何参数

根据URDF分析，每条腿的几何参数：

```python
# 从URDF提取的关键尺寸
L0 = 0.0    # 导轨位移（当前阶段固定为0）
L1 = 0.055  # HAA关节到HFE关节的距离（近似）
L2 = 0.152  # HFE关节到KFE关节的距离（大腿长度）
L3 = 0.299  # KFE关节到脚部的距离（小腿长度）
```

### 逆运动学求解

对于当前阶段的3-DOF腿部（导轨锁定在s=0），逆运动学分解为两步：

**函数签名**:
```python
def solve_ik(leg_id: str, foot_pos: Tuple[float, float, float], rail_offset: float = 0.0) -> Optional[Tuple[float, float, float, float]]:
    """
    求解逆运动学
    
    参数:
        leg_id: 腿部标识 (lf, rf, lh, rh)
        foot_pos: 脚部目标位置 (x, y, z) 在base_link坐标系，单位：米
        rail_offset: 导轨位移（当前阶段固定传入0.0），单位：米
    
    返回:
        (s_m, θ_haa_rad, θ_hfe_rad, θ_kfe_rad) 或 None（如果无解）
        - s_m: 导轨位移，单位：米
        - θ_haa_rad: HAA关节角度，单位：弧度
        - θ_hfe_rad: HFE关节角度，单位：弧度
        - θ_kfe_rad: KFE关节角度，单位：弧度
    """
    # 当前阶段：s = 0.0米（导轨锁定）
    s_m = 0.0
    
    # 转换到腿部局部坐标系
    foot_pos_local = transform_to_leg_frame(foot_pos, leg_id)
    px, py, pz = foot_pos_local  # 单位：米
    
    # 步骤1: 计算HAA角度（弧度）
    theta_haa_rad = atan2(py, pz)
    
    # 步骤2: 计算HFE和KFE角度（2R平面机械臂）
    r = sqrt(py² + pz²) - L1  # 单位：米
    d = sqrt(r² + px²)        # 单位：米
    
    # 检查工作空间
    if d > L2 + L3 or d < abs(L2 - L3):
        return None  # 无解
    
    # 使用余弦定理
    cos_theta_kfe = (d² - L2² - L3²) / (2 * L2 * L3)
    theta_kfe_rad = acos(cos_theta_kfe)  # 单位：弧度
    
    # 计算HFE
    alpha = atan2(px, r)
    beta = atan2(L3 * sin(theta_kfe_rad), L2 + L3 * cos(theta_kfe_rad))
    theta_hfe_rad = alpha - beta  # 单位：弧度
    
    return (s_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad)
```

**步骤1: 计算HAA角度（θ_HAA）**
```
θ_HAA = atan2(py, pz)  # 返回弧度
```
其中(px, py, pz)是脚部在腿部局部坐标系中的位置（单位：米）

**步骤2: 计算HFE和KFE角度（θ_HFE, θ_KFE）**

将问题简化为2R平面机械臂：
```
r = sqrt(py² + pz²) - L1  # 投影到平面后的径向距离（米）
d = sqrt(r² + px²)        # 到目标点的距离（米）

# 使用余弦定理
cos_θ_KFE = (d² - L2² - L3²) / (2 * L2 * L3)
θ_KFE = acos(cos_θ_KFE)  # 弧度

# 计算θ_HFE
α = atan2(px, r)  # 弧度
β = atan2(L3 * sin(θ_KFE), L2 + L3 * cos(θ_KFE))  # 弧度
θ_HFE = α - β  # 弧度
```

### 坐标系转换

每条腿的局部坐标系相对于base_link有旋转：
- 前腿: rpy = (90°, 0°, 0°)
- 后腿: rpy = (90°, 0°, 180°)

转换矩阵：
```python
def get_leg_transform(rpy: Tuple[float, float, float]) -> np.ndarray:
    """返回从base_link到腿部局部坐标系的旋转矩阵"""
    R = rotation_matrix_from_rpy(rpy)
    return R
```

## 步态生成详细设计

### 爬行步态时序（Crawl Gait）

```
时间轴:     0%        25%       50%       75%      100%
           ├─────────┼─────────┼─────────┼─────────┤
leg1 (lf): [摆动相──][支撑相────────────────────────]
leg2 (rf): [支撑相────────────][摆动相──][支撑相────]
leg3 (lh): [支撑相──][摆动相──][支撑相────────────────]
leg4 (rh): [支撑相────────────────────────][摆动相──]

支撑腿数:    3         3         3         3
```

**关键特性**:
- 每个时刻都有3条腿着地（75% duty factor）
- 腿部按顺序摆动：leg1 → leg3 → leg2 → leg4
- 相位差：90度（360°/4腿）
- 支撑三角形始终存在

**稳定性验证**:
```python
def verify_stability(swing_leg: str, com_position: np.ndarray) -> bool:
    """验证切换摆动腿后是否保持静态稳定"""
    support_legs = [leg for leg in ['leg1', 'leg2', 'leg3', 'leg4'] if leg != swing_leg]
    support_triangle = compute_triangle(support_legs)
    return point_in_triangle(com_position[:2], support_triangle)
```

### 脚部轨迹生成

**支撑相轨迹**:
```python
def stance_trajectory(t: float, t_start: float, t_end: float,
                     pos_start: np.ndarray, pos_end: np.ndarray) -> np.ndarray:
    """线性插值"""
    alpha = (t - t_start) / (t_end - t_start)
    return pos_start + alpha * (pos_end - pos_start)
```

**摆动相轨迹**:
```python
def swing_trajectory(t: float, t_start: float, t_end: float,
                    pos_start: np.ndarray, pos_end: np.ndarray,
                    height: float) -> np.ndarray:
    """抛物线轨迹"""
    alpha = (t - t_start) / (t_end - t_start)
    
    # 水平方向线性插值
    pos_xy = pos_start[:2] + alpha * (pos_end[:2] - pos_start[:2])
    
    # 垂直方向抛物线
    z = pos_start[2] + 4 * height * alpha * (1 - alpha)
    
    return np.array([pos_xy[0], pos_xy[1], z])
```

### 步态参数自适应

根据cmd_vel调整步态参数：
```python
def adapt_gait_parameters(vx: float, vy: float, omega: float) -> GaitConfig:
    """根据期望速度调整爬行步态参数"""
    config = GaitConfig()
    
    # 步长与速度成正比（爬行步态步长较小）
    velocity_magnitude = sqrt(vx² + vy²)
    config.stride_length = min(velocity_magnitude * config.cycle_time, 0.10)
    
    # 爬行步态保持较低的步高以增加稳定性
    config.stride_height = 0.05
    
    # 速度较快时可以适当缩短周期，但仍保持静态稳定
    if velocity_magnitude > 0.15:
        config.cycle_time = 1.5
    else:
        config.cycle_time = 2.0
    
    # 始终保持75% duty factor确保3腿着地
    config.duty_factor = 0.75
    
    return config
```


## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: 系统初始化完整性

*对于任意*系统配置，当系统启动时，所有16个关节通道（12个旋转关节 + 4个直线导轨）的控制接口都应该被成功初始化，并且ROS 2节点应该正确创建。

**验证: 需求 1.1, 5.1**

### 属性 2: 关节限位保护

*对于任意*关节命令，如果命令值超出该关节的安全限位范围，系统应该将命令限制在安全范围内，并且记录警告信息。

**验证: 需求 1.4**

### 属性 3: 关节状态报告准确性

*对于任意*关节和目标位置，当关节实际位置与目标位置的误差小于阈值时，系统应该报告该关节状态为"已到达"。

**验证: 需求 1.3**

### 属性 4: 爬行步态顺序性

*对于任意*时刻，在爬行步态执行过程中，4条腿应该按照预定顺序（leg1 → leg3 → leg2 → leg4）依次进入摆动相，相邻腿的相位差应该为90度。

**验证: 需求 2.1**

### 属性 5: 静态稳定性不变量

*对于任意*步态执行时刻，至少有三条腿应该处于支撑相，这三条腿的着地点应该形成一个支撑三角形，并且机器人质心的投影应该在该支撑三角形内，身体高度应该在0.15米到0.25米之间。

**验证: 需求 2.2, 2.6, 6.1, 6.4, 6.5**

### 属性 6: 脚部轨迹约束

*对于任意*腿部，当处于摆动相时，脚部轨迹上的所有点的高度应该至少为0.05米；当处于支撑相时，脚部应该保持与地面接触（z坐标接近0）。

**验证: 需求 2.3, 2.4**

### 属性 7: 步态周期连续性

*对于任意*步态周期，周期结束时的关节位置和速度应该与下一个周期开始时的关节位置和速度平滑连接，速度变化率应该有界。

**验证: 需求 2.5**

### 属性 8: 逆运动学正确性（Round-trip）

*对于任意*在工作空间内的脚部目标位置，逆运动学求解器计算出的关节位置（导轨位移[米] + 三个旋转关节角度[弧度]），通过正运动学计算后应该得到与目标位置等价的脚部位置（误差小于1mm）。

**验证: 需求 3.1, 3.3**

### 属性 9: 工作空间外错误处理

*对于任意*超出工作空间的脚部目标位置，逆运动学求解器应该返回错误状态，并提供一个在工作空间内的最近可达位置。

**验证: 需求 3.3**

### 属性 10: 轨迹平滑性

*对于任意*起止点，生成的摆动腿轨迹应该在所有点都具有连续的速度（一阶导数存在且有界），并且轨迹上的所有点都应该高于地面。

**验证: 需求 4.1, 4.2**

### 属性 11: 速度约束满足

*对于任意*轨迹，所有关节的速度应该不超过其速度限制，如果初始轨迹违反速度约束，系统应该自动延长轨迹时间以满足约束。

**验证: 需求 4.3**

### 属性 12: 轨迹安全性

*对于任意*生成的轨迹，轨迹上所有时刻的关节位置都应该在该关节的安全限位范围内（导轨位移限位和旋转关节角度限位分别检查）。

**验证: 需求 4.4**

### 属性 13: 仿真时间同步

*对于任意*控制循环迭代，系统应该使用ROS 2节点时钟（而非系统墙钟时间）计算时间增量dt，确保当仿真速度慢于实时（Real Time Factor < 1.0）时，步态相位更新与物理引擎保持同步。

**验证: 需求 5.5, 5.6**

### 属性 14: 速度命令响应性

*对于任意*cmd_vel命令（vx, vy, omega），系统应该相应地调整步态参数（步长、步高、周期时间），使得机器人的实际移动速度趋向于期望速度。

**验证: 需求 5.2**

### 属性 15: 平滑停止

*对于任意*步态执行时刻，当接收到停止命令时，系统应该在不超过一个步态周期的时间内将所有腿部移动到支撑相并停止运动，且停止过程中速度应该平滑衰减。

**验证: 需求 5.4**

### 属性 16: 配置参数加载

*对于任意*有效的配置文件，系统应该正确加载所有步态参数（步长、步高、频率等），加载后的参数值应该与配置文件中的值一致。

**验证: 需求 7.1**

### 属性 17: 参数更新时序

*对于任意*运行时参数更新，新参数应该在当前步态周期结束后的下一个周期开始时生效，不应该在周期中间突变。

**验证: 需求 7.2**

### 属性 18: 无效参数处理

*对于任意*无效的参数值（负数、超出合理范围等），系统应该拒绝该参数，使用预定义的默认值，并记录错误信息。

**验证: 需求 7.3**

### 属性 19: 调试信息发布

*对于任意*系统状态，当调试模式启用时，系统应该发布包含详细步态状态信息的消息，包括当前相位、脚部位置、关节角度等。

**验证: 需求 7.4**

### 属性 20: 逆运动学失败恢复

*对于任意*导致逆运动学无解的情况，系统应该记录错误，保持使用上一个有效的关节位置配置，并且不应该发送无效的关节命令。

**验证: 需求 8.2**

### 属性 21: 紧急安全姿态

*对于任意*严重错误（如多个关节失效、通信中断等），系统应该立即切换到安全姿态（所有腿部弯曲，身体降低），在整个切换过程中持续向4个直线导轨发送0.0米位置指令并维持最大保持力矩，确保导轨滑块不发生任何被动位移，并停止所有运动命令。

**验证: 需求 8.4, 8.5, 8.6**

### 属性 22: 导轨锁定持续性

*对于任意*系统运行时刻（包括正常运动、错误恢复、安全姿态切换），系统应该持续向4个直线导轨发送0.0米位置指令，并且导轨的实际位移应该始终保持在±0.5mm范围内，如果检测到超出此范围的滑动应该立即触发硬件报警。

**验证: 需求 1.3, 8.5, 8.6**

## 错误处理

### 错误类型

1. **运动学错误**
   - 目标位置超出工作空间
   - 逆运动学无解
   - 奇异点附近的数值不稳定

2. **通信错误**
   - ROS 2节点连接丢失
   - 关节控制器无响应
   - 消息发布/订阅失败

3. **参数错误**
   - 配置文件格式错误
   - 参数值超出合理范围
   - 必需参数缺失

4. **运行时错误**
   - 关节卡死或失效
   - 传感器数据异常
   - 稳定性检测失败

### 错误处理策略

**分级响应**:
- **警告级**: 记录日志，继续运行（如单次IK无解）
- **错误级**: 降级运行，使用fallback策略（如使用上一个有效配置）
- **严重级**: 立即停止，切换到安全姿态（如多关节失效）

**恢复机制**:
```python
class ErrorRecovery:
    def handle_ik_failure(self, leg_id: str) -> None:
        """IK失败时使用上一个有效配置"""
        self.use_last_valid_config(leg_id)
        self.log_warning(f"IK failed for {leg_id}, using last valid config")
    
    def handle_joint_stuck(self, joint_name: str) -> None:
        """关节卡死时降低力矩并报警"""
        self.reduce_effort(joint_name, factor=0.5)
        self.trigger_alarm(f"Joint {joint_name} may be stuck")
    
    def handle_critical_error(self) -> None:
        """
        严重错误时切换到安全姿态
        
        关键安全措施：
        1. 立即停止所有运动规划
        2. 持续锁定4个直线导轨在0.0米位置
        3. 缓慢降低身体高度（蹲下）
        4. 在整个过程中维持导轨最大保持力矩
        5. 监控导轨位置，确保无被动滑动
        """
        self.stop_all_motion()
        
        # 关键：在整个安全姿态切换过程中持续锁定导轨
        self.lock_rails_continuously()
        
        # 缓慢蹲下，避免冲击
        self.move_to_safe_posture_slowly()
        
        # 触发紧急停止
        self.trigger_emergency_stop()
    
    def lock_rails_continuously(self) -> None:
        """
        持续锁定直线导轨
        
        实现细节：
        - 以高频率（>50Hz）持续发送导轨位置指令（0.0米）
        - 设置最大保持力矩/增益
        - 监控实际导轨位置，检测任何偏差
        - 如果检测到滑动（>0.5mm），立即报警
        """
        for leg_id in ['leg1', 'leg2', 'leg3', 'leg4']:
            rail_joint = f'{leg_id}_j1'
            # 持续发送0.0米位置指令
            self.send_rail_lock_command(rail_joint, position_m=0.0, max_effort=True)
            
            # 监控实际位置
            actual_pos = self.get_joint_position(rail_joint)
            if abs(actual_pos) > 0.0005:  # 0.5mm阈值
                self.log_error(f"Rail {rail_joint} slipped: {actual_pos*1000:.2f}mm")
                self.trigger_hardware_alarm()
```

**超时保护**:
- 关节命令发送超时: 100ms
- 关节状态更新超时: 200ms
- IK计算超时: 10ms

## 测试策略

### 双重测试方法

本系统采用单元测试和基于属性的测试相结合的方法：

- **单元测试**: 验证特定示例、边界情况和错误条件
- **属性测试**: 通过随机输入验证通用属性

两者是互补的，共同提供全面的测试覆盖。

### 单元测试重点

单元测试应该专注于：
- 特定示例，展示正确行为
- 组件之间的集成点
- 边界情况和错误条件（如工作空间边界、关节限位）
- ROS 2接口的mock测试

避免编写过多的单元测试——基于属性的测试已经覆盖了大量输入组合。

### 基于属性的测试配置

**测试库**: 使用Python的`hypothesis`库进行基于属性的测试

**配置要求**:
- 每个属性测试最少运行100次迭代（由于随机化）
- 每个测试必须引用其对应的设计文档属性
- 标签格式: `# Feature: spider-robot-basic-motion, Property N: [property_text]`

**示例测试结构**:
```python
from hypothesis import given, settings, strategies as st
import numpy as np

# Feature: spider-robot-basic-motion, Property 8: 逆运动学正确性（Round-trip）
@settings(max_examples=100)  # 控制迭代次数
@given(
    x=st.floats(min_value=-0.3, max_value=0.3),
    y=st.floats(min_value=-0.3, max_value=0.3),
    z=st.floats(min_value=-0.4, max_value=-0.1)
)
def test_ik_fk_roundtrip(x, y, z):
    """对于任意工作空间内的位置，IK->FK应该返回原始位置"""
    solver = KinematicsSolver(leg_params)
    target_pos = np.array([x, y, z])
    
    # 逆运动学
    joint_angles = solver.solve_ik("lf", target_pos)
    assert joint_angles is not None
    
    # 正运动学
    result_pos = solver.solve_fk("lf", joint_angles)
    
    # 验证round-trip
    assert np.allclose(result_pos, target_pos, atol=0.001)
```

### 测试覆盖目标

- **代码覆盖率**: >80%
- **属性测试覆盖**: 所有20个正确性属性
- **边界测试**: 所有关节限位、工作空间边界
- **错误路径**: 所有错误处理分支

### 持续集成

- 每次提交自动运行所有测试
- 属性测试失败时保存反例用于调试
- 性能回归测试（IK计算时间、控制循环频率）

### 仿真测试

除了单元测试和属性测试，还需要在Gazebo中进行集成测试：
- 完整步态执行测试
- 不同速度命令响应测试
- 障碍物环境测试
- 长时间运行稳定性测试

这些测试验证系统在真实仿真环境中的行为，补充单元测试无法覆盖的物理交互。
