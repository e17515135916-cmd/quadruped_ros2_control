# 设计文档：球形足端

## 概述

本设计为DOG2四足机器人的每条腿添加球形足端（第5个Link），替换当前使用STL网格的足端几何体。球形足端提供稳定的点接触，改善机器人在油箱环境中穿越障碍物时的物理稳定性。设计包括几何体定义、物理属性配置、摩擦力参数和测试验证。

### 设计目标

1. **稳定接触**: 使用球形几何体确保与地面和障碍物的接触始终是点接触
2. **物理真实性**: 配置适当的质量、惯性和摩擦参数以实现真实的物理仿真
3. **结构完整性**: 确保每条腿有完整的5个Link结构（导轨→髋→大腿→小腿→足端）
4. **控制兼容性**: 保持与现有MPC和WBC控制算法的兼容性
5. **可测试性**: 通过属性测试自动验证结构完整性

## 架构

### 系统组件

```
DOG2 Robot
├── Base Link (base_link)
└── 4 × Leg Assembly
    ├── Prismatic Link (l${leg_num})        - 导轨
    ├── Hip Link (l${leg_num}1)             - 髋关节
    ├── Thigh Link (l${leg_num}11)          - 大腿
    ├── Shin Link (l${leg_num}111)          - 小腿
    └── Foot Link (l${leg_num}1111)         - 足端 [球形]
```

### 关节连接

```
j${leg_num}      : base_link → l${leg_num}      (prismatic, 导轨)
j${leg_num}1     : l${leg_num} → l${leg_num}1   (revolute, 髋外展/内收)
j${leg_num}11    : l${leg_num}1 → l${leg_num}11 (revolute, 髋前屈/后伸)
j${leg_num}111   : l${leg_num}11 → l${leg_num}111 (revolute, 膝关节)
j${leg_num}1111  : l${leg_num}111 → l${leg_num}1111 (fixed, 足端固定)
```

### 数据流

```
URDF/Xacro → Gazebo Physics Engine → Contact Forces → MPC/WBC Controller
     ↓              ↓                      ↓                ↓
  几何定义      碰撞检测              摩擦力计算        关节力矩命令
```

## 组件和接口

### 1. 足端Link定义 (Foot Link)

**组件**: `l${leg_num}1111`

**几何体**:
- **类型**: 球体 (sphere)
- **半径**: 0.02米 (20mm)
- **材质**: Gazebo/Grey

**接口**:
- **输入**: 来自小腿Link的固定连接
- **输出**: 与地面/障碍物的接触力

**实现细节**:
```xml
<link name="l${leg_num}1111">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="0.05"/>
    <inertia ixx="8e-6" ixy="0" ixz="0" 
             iyy="8e-6" iyz="0" 
             izz="8e-6"/>
  </inertial>
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.02"/>
    </geometry>
    <material name="">
      <color rgba="0.5 0.5 0.5 1"/>
    </material>
  </visual>
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <sphere radius="0.02"/>
    </geometry>
  </collision>
</link>
```

**设计决策**:
- 使用球体而非STL网格：球体提供完美的点接触，无论机器人姿态如何
- 半径20mm：足够小以穿过狭窄空间，足够大以提供稳定支撑
- 质心在球心：简化动力学计算

### 2. 足端关节定义 (Foot Joint)

**组件**: `j${leg_num}1111`

**类型**: 固定关节 (fixed)

**位置偏移**:
- **xyz**: `(0, -0.22, 0)` - 小腿末端下方22cm
- **rpy**: `(0, 0, 0)` - 无旋转

**实现细节**:
```xml
<joint name="j${leg_num}1111" type="fixed">
  <origin xyz="0 -0.22 0" rpy="0 0 0"/>
  <parent link="l${leg_num}111"/>
  <child link="l${leg_num}1111"/>
</joint>
```

**设计决策**:
- 固定关节：足端不需要主动控制，简化控制系统
- 偏移量计算：小腿长度(~20cm) + 球体半径(2cm) = 22cm
- 不在ros2_control中定义：减少控制器复杂度

### 3. Gazebo摩擦配置

**组件**: Gazebo材质属性

**参数**:
- **mu1**: 1.5 (主摩擦系数)
- **mu2**: 1.5 (次摩擦系数)
- **kp**: 1000000.0 (接触刚度)
- **kd**: 100.0 (接触阻尼)
- **minDepth**: 0.001 (最小穿透深度)
- **maxVel**: 0.1 (最大接触速度)

**实现细节**:
```xml
<gazebo reference="l${leg_num}1111">
  <mu1>1.5</mu1>
  <mu2>1.5</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
  <minDepth>0.001</minDepth>
  <maxVel>0.1</maxVel>
  <material>Gazebo/Grey</material>
</gazebo>
```

**设计决策**:
- 高摩擦系数(1.5)：模拟油箱内的防滑表面
- 高刚度：模拟硬接触，防止足端"陷入"地面
- 适度阻尼：稳定接触，防止振荡

### 4. 惯性属性计算

**球体惯性公式**:
对于质量为 m、半径为 r 的实心球体：
```
I = (2/5) * m * r²
```

**参数**:
- 质量 m = 0.05 kg
- 半径 r = 0.02 m

**计算**:
```
I = (2/5) * 0.05 * (0.02)²
I = 0.4 * 0.05 * 0.0004
I = 0.000008 kg·m²
I = 8e-6 kg·m²
```

**惯性矩阵**:
```
Ixx = Iyy = Izz = 8e-6
Ixy = Ixz = Iyz = 0 (球体对称)
```

**设计决策**:
- 轻量化设计(50g)：减少腿部末端质量，改善动态响应
- 精确惯性：使用物理公式而非估算，确保仿真准确性
- 对称性：球体的对称性简化了惯性矩阵

## 数据模型

### Link结构

```python
class FootLink:
    name: str                    # "l${leg_num}1111"
    geometry_type: str           # "sphere"
    radius: float                # 0.02 m
    mass: float                  # 0.05 kg
    inertia: InertiaMatrix       # 对角矩阵 [8e-6, 8e-6, 8e-6]
    center_of_mass: Vector3      # [0, 0, 0] (球心)
    material: str                # "Gazebo/Grey"
```

### Joint结构

```python
class FootJoint:
    name: str                    # "j${leg_num}1111"
    type: str                    # "fixed"
    parent: str                  # "l${leg_num}111"
    child: str                   # "l${leg_num}1111"
    origin_xyz: Vector3          # [0, -0.22, 0]
    origin_rpy: Vector3          # [0, 0, 0]
```

### Gazebo属性

```python
class GazeboFriction:
    link_reference: str          # "l${leg_num}1111"
    mu1: float                   # 1.5
    mu2: float                   # 1.5
    kp: float                    # 1000000.0
    kd: float                    # 100.0
    min_depth: float             # 0.001
    max_vel: float               # 0.1
    material: str                # "Gazebo/Grey"
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 属性 1: 球形足端几何体完整性

*对于任意* 腿编号（1-4），生成的URDF中足端Link应该在visual和collision标签中都使用球形几何体，半径为0.02米，且两者几何体类型和参数一致。

**验证需求: 1.1, 1.2, 1.3**

### 属性 2: 足端Link结构完整性

*对于任意* 腿编号（1-4），该腿应该包含恰好5个Link，命名遵循模式 `l${leg_num}`, `l${leg_num}1`, `l${leg_num}11`, `l${leg_num}111`, `l${leg_num}1111`，且足端Link是运动链的终点（没有子Link）。

**验证需求: 2.1, 2.2, 2.4**

### 属性 3: 固定关节连接正确性

*对于任意* 腿编号（1-4），应该存在固定关节 `j${leg_num}1111`，连接小腿Link `l${leg_num}111` 到足端Link `l${leg_num}1111`，关节类型为fixed，且原点旋转为(0, 0, 0)。

**验证需求: 2.3, 5.1, 5.3**

### 属性 4: 球形惯性属性正确性

*对于任意* 足端Link，其惯性属性应该满足：
- 质量 = 0.05 kg
- 质心位置 = (0, 0, 0)
- 转动惯量 Ixx = Iyy = Izz = (2/5) × 0.05 × (0.02)² = 8e-6 kg·m²
- 非对角元素 Ixy = Ixz = Iyz = 0
- 所有对角元素 > 0（正定矩阵）

**验证需求: 3.1, 3.2, 3.3, 3.5**

### 属性 5: Gazebo摩擦参数完整性

*对于任意* 足端Link，Gazebo配置应该包含：
- mu1 = 1.5
- mu2 = 1.5
- kp = 1000000.0
- kd = 100.0
- minDepth = 0.001
- maxVel = 0.1
- material = "Gazebo/Grey"

**验证需求: 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

### 属性 6: 关节偏移量合理性

*对于任意* 足端固定关节，其xyz偏移的y分量应该为负值（向下），且绝对值应该在合理范围内（0.15m到0.25m之间），以确保足端位于小腿末端下方。

**验证需求: 5.2**

### 属性 7: 控制接口隔离

*对于任意* 腿编号（1-4），ros2_control块中不应该包含固定关节 `j${leg_num}1111` 的定义，只应该包含4个主动关节：`j${leg_num}`, `j${leg_num}1`, `j${leg_num}11`, `j${leg_num}111`。

**验证需求: 7.1, 7.2**

## 错误处理

### 1. URDF生成错误

**错误场景**: xacro处理失败或生成无效URDF

**处理策略**:
- 在测试中捕获subprocess异常
- 记录详细的错误信息（stderr输出）
- 提供清晰的错误消息指示问题位置

**示例**:
```python
try:
    result = subprocess.run(["xacro", xacro_path], 
                          capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Failed to generate URDF: {e.stderr}")
```

### 2. XML解析错误

**错误场景**: 生成的URDF不是有效的XML

**处理策略**:
- 使用xml.etree.ElementTree进行解析
- 捕获ParseError异常
- 提供URDF内容的前几行以便调试

**示例**:
```python
try:
    root = ET.fromstring(urdf_content)
except ET.ParseError as e:
    preview = urdf_content[:500]
    raise RuntimeError(f"Invalid URDF XML: {e}\nPreview: {preview}")
```

### 3. 缺失元素错误

**错误场景**: 期望的Link或Joint不存在

**处理策略**:
- 明确报告缺失的元素名称
- 列出实际找到的元素
- 提供期望的命名模式

**示例**:
```python
missing_links = expected_links - actual_links
if missing_links:
    raise AssertionError(
        f"Leg {leg_num} missing links: {missing_links}. "
        f"Expected: {expected_links}, Found: {actual_links}"
    )
```

### 4. 参数值错误

**错误场景**: 物理参数不在有效范围内

**处理策略**:
- 验证数值范围（质量>0，半径>0等）
- 检查惯性矩阵的正定性
- 报告实际值和期望值的差异

**示例**:
```python
if mass <= 0:
    raise ValueError(f"Invalid mass {mass} for link {link_name}: must be > 0")
if not is_positive_definite(inertia_matrix):
    raise ValueError(f"Inertia matrix for {link_name} is not positive definite")
```

### 5. Gazebo加载失败

**错误场景**: Gazebo无法加载机器人模型

**处理策略**:
- 这是集成测试层面的错误，不在单元测试范围内
- 建议：提供launch文件测试脚本
- 记录Gazebo日志以便诊断

## 测试策略

### 双重测试方法

本项目采用**单元测试**和**基于属性的测试**相结合的方法，以确保全面覆盖：

- **单元测试**: 验证特定示例、边界情况和错误条件
- **属性测试**: 验证所有输入下的通用属性
- 两者互补：单元测试捕获具体错误，属性测试验证通用正确性

### 单元测试

**目标**: 验证特定配置和边界情况

**测试用例**:

1. **test_foot_link_exists**: 验证每条腿的足端Link存在
2. **test_foot_geometry_is_sphere**: 验证足端使用球形几何体
3. **test_foot_mass_correct**: 验证足端质量为0.05kg
4. **test_foot_joint_is_fixed**: 验证足端关节类型为fixed
5. **test_gazebo_friction_configured**: 验证Gazebo摩擦参数存在

**边界情况**:
- 腿编号边界（leg_num = 1 和 4）
- 零质量检测（应该失败）
- 负半径检测（应该失败）

### 基于属性的测试

**测试库**: Hypothesis (Python)

**配置**: 每个属性测试最少100次迭代

**属性测试实现**:

#### 属性测试 1: 球形足端几何体完整性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_spherical_foot_geometry_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 1: 球形足端几何体完整性
    Validates: Requirements 1.1, 1.2, 1.3
    
    对于任意腿编号，足端Link应该使用球形几何体，半径0.02m，
    visual和collision几何体一致。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    foot_link = root.find(f".//link[@name='l{leg_num}1111']")
    assert foot_link is not None
    
    # 检查visual几何体
    visual_geom = foot_link.find(".//visual/geometry/sphere")
    assert visual_geom is not None
    assert float(visual_geom.get("radius")) == 0.02
    
    # 检查collision几何体
    collision_geom = foot_link.find(".//collision/geometry/sphere")
    assert collision_geom is not None
    assert float(collision_geom.get("radius")) == 0.02
```

#### 属性测试 2: 足端Link结构完整性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_foot_link_structure_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 2: 足端Link结构完整性
    Validates: Requirements 2.1, 2.2, 2.4
    
    对于任意腿编号，应该有5个Link，且足端是运动链终点。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    # 验证5个Link存在
    expected_links = {
        f"l{leg_num}", f"l{leg_num}1", f"l{leg_num}11",
        f"l{leg_num}111", f"l{leg_num}1111"
    }
    actual_links = {link.get("name") for link in root.findall("link")
                   if link.get("name") in expected_links}
    assert actual_links == expected_links
    
    # 验证足端是终点（没有以它为parent的关节）
    foot_as_parent = root.find(f".//joint/parent[@link='l{leg_num}1111']")
    assert foot_as_parent is None
```

#### 属性测试 3: 固定关节连接正确性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_fixed_joint_connection_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 3: 固定关节连接正确性
    Validates: Requirements 2.3, 5.1, 5.3
    
    对于任意腿编号，固定关节应该正确连接小腿和足端。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    joint = root.find(f".//joint[@name='j{leg_num}1111']")
    assert joint is not None
    assert joint.get("type") == "fixed"
    
    parent = joint.find("parent")
    child = joint.find("child")
    assert parent.get("link") == f"l{leg_num}111"
    assert child.get("link") == f"l{leg_num}1111"
    
    origin = joint.find("origin")
    rpy = origin.get("rpy").split()
    assert all(float(x) == 0.0 for x in rpy)
```

#### 属性测试 4: 球形惯性属性正确性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_spherical_inertia_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 4: 球形惯性属性正确性
    Validates: Requirements 3.1, 3.2, 3.3, 3.5
    
    对于任意足端Link，惯性属性应该符合球体物理公式。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    foot_link = root.find(f".//link[@name='l{leg_num}1111']")
    inertial = foot_link.find("inertial")
    
    # 验证质量
    mass = float(inertial.find("mass").get("value"))
    assert abs(mass - 0.05) < 1e-6
    
    # 验证质心
    origin = inertial.find("origin")
    xyz = [float(x) for x in origin.get("xyz").split()]
    assert all(abs(x) < 1e-6 for x in xyz)
    
    # 验证惯性矩阵
    inertia = inertial.find("inertia")
    expected_I = (2/5) * 0.05 * (0.02)**2  # 8e-6
    
    ixx = float(inertia.get("ixx"))
    iyy = float(inertia.get("iyy"))
    izz = float(inertia.get("izz"))
    
    assert abs(ixx - expected_I) < 1e-9
    assert abs(iyy - expected_I) < 1e-9
    assert abs(izz - expected_I) < 1e-9
    
    # 验证非对角元素为0
    assert abs(float(inertia.get("ixy"))) < 1e-9
    assert abs(float(inertia.get("ixz"))) < 1e-9
    assert abs(float(inertia.get("iyz"))) < 1e-9
    
    # 验证正定性
    assert ixx > 0 and iyy > 0 and izz > 0
```

#### 属性测试 5: Gazebo摩擦参数完整性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_gazebo_friction_parameters_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 5: Gazebo摩擦参数完整性
    Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
    
    对于任意足端Link，Gazebo配置应该包含所有必需的摩擦参数。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    gazebo = root.find(f".//gazebo[@reference='l{leg_num}1111']")
    assert gazebo is not None
    
    # 验证所有参数
    assert float(gazebo.find("mu1").text) == 1.5
    assert float(gazebo.find("mu2").text) == 1.5
    assert float(gazebo.find("kp").text) == 1000000.0
    assert float(gazebo.find("kd").text) == 100.0
    assert float(gazebo.find("minDepth").text) == 0.001
    assert float(gazebo.find("maxVel").text) == 0.1
    assert gazebo.find("material").text == "Gazebo/Grey"
```

#### 属性测试 6: 关节偏移量合理性

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_joint_offset_reasonableness_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 6: 关节偏移量合理性
    Validates: Requirements 5.2
    
    对于任意足端关节，偏移量应该在合理范围内。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    joint = root.find(f".//joint[@name='j{leg_num}1111']")
    origin = joint.find("origin")
    xyz = [float(x) for x in origin.get("xyz").split()]
    
    # y分量应该为负（向下）
    assert xyz[1] < 0
    
    # 绝对值应该在合理范围内（15cm到25cm）
    assert 0.15 <= abs(xyz[1]) <= 0.25
```

#### 属性测试 7: 控制接口隔离

```python
@settings(max_examples=100)
@given(leg_num=st.integers(min_value=1, max_value=4))
def test_control_interface_isolation_property(leg_num):
    """
    Feature: dog2-spherical-foot, Property 7: 控制接口隔离
    Validates: Requirements 7.1, 7.2
    
    对于任意腿编号，ros2_control不应该包含固定关节。
    """
    urdf_content = generate_urdf_from_xacro()
    root = parse_urdf(urdf_content)
    
    ros2_control = root.find(".//ros2_control")
    
    # 固定关节不应该在ros2_control中
    fixed_joint = ros2_control.find(f".//joint[@name='j{leg_num}1111']")
    assert fixed_joint is None
    
    # 应该只有4个主动关节
    expected_joints = {
        f"j{leg_num}", f"j{leg_num}1", 
        f"j{leg_num}11", f"j{leg_num}111"
    }
    actual_joints = {
        joint.get("name") for joint in ros2_control.findall("joint")
        if joint.get("name") and joint.get("name").startswith(f"j{leg_num}")
    }
    assert actual_joints == expected_joints
```

### 测试执行

**运行所有测试**:
```bash
# 运行属性测试
python3 src/dog2_description/test/test_spherical_foot_properties.py

# 运行单元测试
pytest src/dog2_description/test/test_spherical_foot_unit.py

# 运行现有的Link结构测试
python3 src/dog2_description/test/test_link_structure_property.py
```

**持续集成**:
- 在每次URDF修改后自动运行测试
- 测试失败时阻止提交
- 生成测试覆盖率报告

### 测试数据生成

**Hypothesis策略**:
```python
# 腿编号生成器
leg_numbers = st.integers(min_value=1, max_value=4)

# 物理参数生成器（用于边界测试）
masses = st.floats(min_value=0.001, max_value=1.0)
radii = st.floats(min_value=0.005, max_value=0.1)
friction_coefficients = st.floats(min_value=0.1, max_value=2.0)
```

## 实施计划

### 阶段 1: URDF修改

1. 修改 `dog2.urdf.xacro` 中的leg宏
2. 将足端Link的几何体从STL mesh改为sphere
3. 更新惯性属性为球体公式计算值
4. 调整Gazebo摩擦参数

### 阶段 2: 测试实现

1. 创建属性测试文件 `test_spherical_foot_properties.py`
2. 实现7个属性测试
3. 创建单元测试文件 `test_spherical_foot_unit.py`
4. 实现边界情况测试

### 阶段 3: 验证

1. 运行所有测试确保通过
2. 生成URDF并在RViz中可视化
3. 在Gazebo中加载并验证物理行为
4. 测试与MPC/WBC控制器的集成

### 阶段 4: 文档

1. 更新README说明球形足端设计
2. 记录物理参数选择的理由
3. 提供可视化和测试指南
4. 创建故障排除文档

## 依赖关系

### 外部依赖

- **xacro**: URDF宏处理器
- **Gazebo**: 物理仿真环境
- **RViz**: 可视化工具
- **ros2_control**: 控制框架
- **Hypothesis**: 属性测试库

### 内部依赖

- **dog2_mpc**: MPC控制器（需要足端位置信息）
- **dog2_wbc**: WBC控制器（需要足端接触力）
- **dog2_description**: URDF定义（本项目修改的目标）

### 版本要求

- ROS 2 Humble
- Gazebo 11+
- Python 3.8+
- Hypothesis 6.0+

## 性能考虑

### 仿真性能

- **球形几何体**: 比STL mesh计算更快，减少碰撞检测时间
- **简化惯性**: 对称惯性矩阵简化动力学计算
- **固定关节**: 减少自由度，提高仿真速度

### 测试性能

- **属性测试**: 100次迭代约需5-10秒
- **URDF生成**: 每次约0.5秒
- **XML解析**: 每次约0.1秒

### 优化建议

1. 缓存生成的URDF以避免重复xacro处理
2. 并行运行独立的属性测试
3. 使用Gazebo的快速碰撞检测模式

## 安全性和鲁棒性

### 物理约束验证

- 质量必须 > 0
- 半径必须 > 0
- 惯性矩阵必须正定
- 摩擦系数必须 >= 0

### 数值稳定性

- 避免极小的质量（< 0.001 kg）
- 避免极小的半径（< 0.005 m）
- 使用合理的接触参数防止振荡

### 错误恢复

- URDF生成失败时提供清晰的错误消息
- 测试失败时报告具体的不匹配项
- Gazebo加载失败时记录详细日志

## 未来扩展

### 可能的改进

1. **可配置足端形状**: 支持半球体或椭球体
2. **自适应摩擦**: 根据地形类型调整摩擦系数
3. **足端传感器**: 添加接触力传感器模拟
4. **磨损模型**: 模拟足端随时间的磨损

### 兼容性

- 设计应该与未来的ROS 2版本兼容
- 保持与现有控制算法的接口稳定
- 支持不同的仿真环境（Gazebo, Isaac Sim等）
