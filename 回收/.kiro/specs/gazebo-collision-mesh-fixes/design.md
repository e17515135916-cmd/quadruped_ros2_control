# 设计文档

## 概述

本设计文档详细说明如何修复 DOG2 机器人在 Gazebo 仿真中因碰撞网格重叠导致的"炸飞"问题。核心策略是：
1. 用简单的碰撞原语（cylinder/box）替换复杂的 STL Mesh
2. 截断小腿碰撞体以消除与球形足端的自我碰撞
3. 配置碰撞过滤和优化接触参数

**设计原则：**
- 保持视觉 Mesh 不变（用户看到的外观）
- 只修改碰撞几何体（物理引擎使用）
- 确保碰撞体之间有足够间隙（≥5mm）
- 使用 Gazebo 原生的碰撞过滤机制

## 架构

### 系统组件

```
URDF/Xacro 文件
├── Visual Geometry (保持不变)
│   └── STL Mesh 文件
├── Collision Geometry (修改)
│   ├── 大腿: Cylinder 原语
│   ├── 小腿: 截断的 Cylinder 原语
│   └── 足端: Sphere 原语
├── Gazebo 配置
│   ├── 碰撞过滤规则
│   └── 接触参数
└── 验证脚本
    ├── 碰撞体间隙检查
    └── Gazebo 稳定性测试
```

### 数据流

```
STL Mesh 测量
    ↓
计算碰撞体尺寸
    ↓
生成 Xacro 配置
    ↓
Gazebo 加载 URDF
    ↓
物理引擎碰撞检测
    ↓
验证稳定性
```


## 组件和接口

### 1. STL Mesh 测量工具

**功能：** 自动测量 STL 文件的边界框尺寸

**输入：**
- STL 文件路径（如 `meshes/l111.STL`）

**输出：**
- 边界框尺寸 (length, width, height)
- 质心位置 (x, y, z)

**实现：**
```python
def measure_stl_mesh(stl_path: str) -> dict:
    """
    测量 STL Mesh 的边界框
    
    Returns:
        {
            'length': float,  # 主轴长度（米）
            'width': float,   # 横截面宽度（米）
            'height': float,  # 横截面高度（米）
            'center': (x, y, z)  # 质心位置
        }
    """
```

### 2. 碰撞体生成器

**功能：** 根据 Mesh 尺寸生成碰撞原语配置

**输入：**
- Link 名称（如 `l111`）
- Mesh 测量结果
- 缩放因子（默认 0.85）

**输出：**
- 碰撞体类型（cylinder/box）
- 碰撞体尺寸
- 碰撞体偏移量

**实现：**
```python
def generate_collision_geometry(link_name: str, mesh_data: dict, scale: float = 0.85) -> dict:
    """
    生成碰撞几何体配置
    
    Returns:
        {
            'type': 'cylinder' | 'box',
            'dimensions': {...},
            'origin': {'xyz': (x, y, z), 'rpy': (r, p, y)}
        }
    """
```

### 3. Xacro 模板生成器

**功能：** 生成带有碰撞原语的 Xacro 代码

**输入：**
- 碰撞体配置
- Link 参数

**输出：**
- Xacro XML 代码片段


### 4. 碰撞过滤配置

**功能：** 禁用相邻 Link 之间的碰撞检测

**方法：** 使用 Gazebo 的 `<collision>` 标签配置

**配置示例：**
```xml
<gazebo>
  <plugin name="gazebo_ros_state" filename="libgazebo_ros_state.so">
    <update_rate>50</update_rate>
  </plugin>
  <!-- 禁用相邻 Link 碰撞 -->
  <disable_link_collision link1="l111" link2="l11"/>
  <disable_link_collision link1="l1111" link2="l111"/>
</gazebo>
```

### 5. 验证工具

**功能：** 检查碰撞体配置的正确性

**检查项：**
- 相邻 Link 间隙 ≥ 5mm
- 小腿与足端间隙 ≥ 10mm
- 碰撞体尺寸在合理范围内
- Gazebo 加载无错误

## 数据模型

### 碰撞体配置数据结构

```python
@dataclass
class CollisionGeometry:
    """碰撞几何体配置"""
    link_name: str
    geometry_type: str  # 'cylinder', 'box', 'sphere'
    dimensions: dict    # {'radius': float, 'length': float} 或 {'size': (x,y,z)}
    origin_xyz: tuple   # (x, y, z) 相对于 Link 原点的偏移
    origin_rpy: tuple   # (roll, pitch, yaw) 旋转

@dataclass
class LinkCollisionConfig:
    """Link 碰撞配置"""
    link_name: str
    visual_mesh: str    # STL 文件路径
    collision_geometry: CollisionGeometry
    gazebo_params: dict # {'mu1': float, 'mu2': float, 'kp': float, ...}
```

### 腿部结构配置

```python
@dataclass
class LegConfig:
    """单条腿的配置"""
    leg_num: int  # 1-4
    links: dict[str, LinkCollisionConfig]  # 'thigh', 'shin', 'foot'
    collision_filters: list[tuple[str, str]]  # 需要禁用碰撞的 Link 对
```


## 正确性属性

*属性（Property）是系统在所有有效执行中应该保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 碰撞原语使用

*对于任意* 腿部编号（1-4）和 Link 类型（大腿 l${leg_num}11 或小腿 l${leg_num}111），生成的 URDF 文件中该 Link 的 collision 标签应该使用 cylinder 或 box 几何体，而不是 mesh 几何体。

**验证方法：** 解析 URDF，检查所有大腿和小腿 Link 的 `<collision><geometry>` 标签是否包含 `<cylinder>` 或 `<box>`，而不包含 `<mesh>`。

**Validates: Requirements 1.1, 1.2**

### Property 2: Visual Mesh 保留

*对于任意* 腿部编号（1-4）和 Link 类型（大腿、小腿），生成的 URDF 文件中该 Link 的 visual 标签应该仍然使用原始的 STL mesh 文件。

**验证方法：** 解析 URDF，检查所有 Link 的 `<visual><geometry>` 标签是否包含 `<mesh filename="...STL"/>`。

**Validates: Requirements 1.4**

### Property 3: Scale 属性移除

*对于任意* 腿部编号（1-4）和 Link 类型（大腿、小腿），生成的 URDF 文件中该 Link 的 collision 标签不应该包含 scale 属性。

**验证方法：** 解析 URDF，检查所有 collision 标签的 `<geometry><mesh>` 是否不存在，或者如果存在则不包含 scale 属性。

**Validates: Requirements 1.5**

### Property 4: 碰撞体尺寸比例

*对于任意* 使用 cylinder 碰撞体的 Link，碰撞体的半径应该是 STL Mesh 最大横截面半径的 0.85-0.95 倍，长度应该是 Mesh 长度的 0.80-0.90 倍。

**验证方法：** 
1. 测量 STL Mesh 的边界框尺寸
2. 解析 URDF 获取碰撞体尺寸
3. 验证比例关系在指定范围内

**Validates: Requirements 1.3, 4.2, 4.3, 4.4**

### Property 5: 相邻 Link 间隙

*对于任意* 腿部编号（1-4）和相邻 Link 对（大腿-小腿），两个碰撞体之间的最小距离应该 >= 0.005 米（5mm）。

**验证方法：**
1. 解析 URDF 获取碰撞体几何和位置
2. 使用正向运动学计算碰撞体在世界坐标系中的位置
3. 计算两个碰撞体之间的最小距离
4. 验证距离 >= 5mm

**Validates: Requirements 1.6, 8.2**

### Property 6: 小腿足端间隙

*对于任意* 腿部编号（1-4），小腿碰撞体末端与球形足端之间的间隙应该 >= 0.01 米（10mm）。

**验证方法：**
1. 解析 URDF 获取小腿碰撞体和足端球体的几何参数
2. 计算小腿碰撞体末端位置
3. 计算足端球心位置
4. 验证距离 - 足端半径 >= 10mm

**Validates: Requirements 2.3, 8.3**

### Property 7: 小腿碰撞体截断

*对于任意* 腿部编号（1-4），小腿碰撞体的长度应该小于小腿 STL Mesh 的实际长度，且差值应该在 0.025-0.035 米范围内。

**验证方法：**
1. 测量小腿 STL Mesh 的长度
2. 解析 URDF 获取小腿碰撞体长度
3. 验证 Mesh长度 - 碰撞体长度 ∈ [0.025, 0.035]

**Validates: Requirements 2.1, 2.2**

### Property 8: 碰撞过滤配置

*对于任意* 腿部编号（1-4），碰撞过滤配置应该包含以下 Link 对：(大腿, 小腿) 和 (小腿, 足端)，且不应该包含非相邻 Link 对（如左右腿之间）。

**验证方法：**
1. 解析 URDF/Gazebo 配置中的碰撞过滤规则
2. 验证每条腿都有 (l${leg_num}11, l${leg_num}111) 和 (l${leg_num}111, l${leg_num}1111) 过滤规则
3. 验证不存在跨腿的过滤规则（如 l111 和 l211）

**Validates: Requirements 3.2, 3.5**


## 错误处理

### 1. STL Mesh 文件缺失

**场景：** 指定的 STL 文件不存在

**处理：**
- 抛出 `FileNotFoundError` 异常
- 错误消息包含缺失文件的完整路径
- 提供可能的文件位置建议

### 2. Mesh 测量失败

**场景：** STL 文件损坏或格式不正确

**处理：**
- 捕获解析异常
- 记录详细错误信息到日志
- 提供手动指定尺寸的回退选项

### 3. 碰撞体重叠检测

**场景：** 生成的碰撞体仍然重叠

**处理：**
- 验证脚本检测到重叠时立即报错
- 输出重叠的 Link 对和重叠量
- 建议调整缩放因子或偏移量

### 4. URDF 解析错误

**场景：** 生成的 URDF 文件格式不正确

**处理：**
- 使用 `urdf_parser_py` 验证 URDF 语法
- 报告具体的语法错误位置
- 回滚到备份文件

### 5. Gazebo 加载失败

**场景：** Gazebo 无法加载修改后的 URDF

**处理：**
- 捕获 Gazebo 错误日志
- 检查常见问题（文件路径、插件配置）
- 提供诊断命令和回滚选项

### 6. 间隙验证失败

**场景：** 碰撞体间隙小于最小要求

**处理：**
- 报告所有不满足间隙要求的 Link 对
- 输出当前间隙值和要求的最小值
- 建议增加缩放因子或调整偏移量

## 测试策略

### 单元测试

**目标：** 验证各个组件的功能正确性

**测试内容：**
1. **STL Mesh 测量**
   - 测试已知尺寸的简单 STL 文件
   - 验证边界框计算准确性
   - 测试边界情况（空文件、单点、单面）

2. **碰撞体生成**
   - 测试 cylinder 参数计算
   - 测试 box 参数计算
   - 验证缩放因子应用

3. **URDF 解析**
   - 测试 Link 提取
   - 测试几何体参数解析
   - 测试 Gazebo 配置解析

4. **间隙计算**
   - 测试简单几何体的距离计算
   - 测试旋转和平移变换
   - 测试边界情况（接触、重叠）

### 属性测试

**目标：** 验证系统在所有输入下满足正确性属性

**测试配置：**
- 最小迭代次数：100 次
- 使用 Python 的 `hypothesis` 库
- 每个属性对应一个独立的测试函数

**测试内容：**

1. **Property 1: 碰撞原语使用**
   ```python
   @given(leg_num=integers(min_value=1, max_value=4))
   def test_collision_primitives_used(leg_num):
       """
       Feature: gazebo-collision-mesh-fixes, Property 1
       验证大腿和小腿使用碰撞原语
       """
       urdf = parse_urdf("dog2.urdf.xacro")
       thigh = urdf.get_link(f"l{leg_num}11")
       shin = urdf.get_link(f"l{leg_num}111")
       
       assert thigh.collision.geometry.type in ['cylinder', 'box']
       assert shin.collision.geometry.type in ['cylinder', 'box']
   ```

2. **Property 2: Visual Mesh 保留**
   ```python
   @given(leg_num=integers(min_value=1, max_value=4))
   def test_visual_mesh_preserved(leg_num):
       """
       Feature: gazebo-collision-mesh-fixes, Property 2
       验证 visual 标签仍使用 STL Mesh
       """
       urdf = parse_urdf("dog2.urdf.xacro")
       for link_suffix in ['11', '111']:
           link = urdf.get_link(f"l{leg_num}{link_suffix}")
           assert link.visual.geometry.type == 'mesh'
           assert link.visual.geometry.filename.endswith('.STL')
   ```

3. **Property 5: 相邻 Link 间隙**
   ```python
   @given(leg_num=integers(min_value=1, max_value=4))
   def test_adjacent_link_clearance(leg_num):
       """
       Feature: gazebo-collision-mesh-fixes, Property 5
       验证相邻 Link 间隙 >= 5mm
       """
       urdf = parse_urdf("dog2.urdf.xacro")
       thigh = urdf.get_link(f"l{leg_num}11")
       shin = urdf.get_link(f"l{leg_num}111")
       
       clearance = compute_min_distance(thigh.collision, shin.collision)
       assert clearance >= 0.005  # 5mm
   ```

4. **Property 6: 小腿足端间隙**
   ```python
   @given(leg_num=integers(min_value=1, max_value=4))
   def test_shin_foot_clearance(leg_num):
       """
       Feature: gazebo-collision-mesh-fixes, Property 6
       验证小腿与足端间隙 >= 10mm
       """
       urdf = parse_urdf("dog2.urdf.xacro")
       shin = urdf.get_link(f"l{leg_num}111")
       foot = urdf.get_link(f"l{leg_num}1111")
       
       clearance = compute_shin_foot_clearance(shin, foot)
       assert clearance >= 0.01  # 10mm
   ```

### 集成测试

**目标：** 验证系统在 Gazebo 中的实际行为

**测试内容：**
1. **Gazebo 加载测试**
   - 启动 Gazebo
   - 加载修改后的 URDF
   - 验证无错误消息

2. **稳定性测试**
   - 机器人生成在 Gazebo 中
   - 运行 10 秒仿真
   - 验证基座高度在合理范围内
   - 验证无"炸飞"现象

3. **接触测试**
   - 验证只有足端与地面接触
   - 验证接触力在合理范围内
   - 验证无自我碰撞警告

### 测试工具

**验证脚本：**
```bash
# 检查碰撞体配置
python scripts/verify_collision_config.py

# 可视化碰撞体
ros2 launch dog2_description view_collision.launch.py

# 运行属性测试
pytest tests/test_collision_properties.py -v

# Gazebo 稳定性测试
./scripts/test_gazebo_stability.sh
```

