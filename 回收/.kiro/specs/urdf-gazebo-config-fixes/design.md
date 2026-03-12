# 设计文档

## 概述

本设计文档描述了如何修复 dog2_visual.urdf 和 dog2_gazebo.urdf 文件中的严重 Gazebo 配置错误。这些错误包括 ROS 版本不兼容、配置路径错误、物理参数失真、传感器配置错误和仿真稳定性问题。

修复策略采用最小侵入性原则：
- 只修改必要的配置项
- 保留所有正确的配置
- 创建备份以便回滚
- 提供验证脚本确保修复成功

## 架构

### 文件结构

```
src/panda_description/urdf/
├── dog2.urdf                    # 原始 URDF（参考用）
├── dog2_gazebo.urdf             # Gazebo 仿真用（需要修复）
├── dog2_visual.urdf             # 当前用于可视化（需要修复或废弃）
├── dog2_gazebo_fixed.urdf       # 修复后的 Gazebo 仿真文件（新建）
└── dog2_rviz.urdf               # RViz2 可视化专用（新建，可选）
```

### 修复流程

```
1. 备份原始文件
   ↓
2. 读取原始 URDF 获取真实惯性参数
   ↓
3. 应用所有修复
   ↓
4. 验证修复后的文件
   ↓
5. 更新 Launch 文件引用
```

## 组件和接口

### 1. URDF 修复器 (URDF Fixer)

**职责**: 读取、修改和写入 URDF 文件

**接口**:
```python
class URDFFixer:
    def __init__(self, urdf_path: str):
        """初始化修复器"""
        
    def remove_ros1_plugin(self) -> None:
        """移除 ROS 1 gazebo_ros_control 插件"""
        
    def fix_ros2_control_config(self) -> None:
        """修复 ROS 2 控制器配置路径"""
        
    def restore_inertia_parameters(self, reference_urdf: str) -> None:
        """从参考 URDF 恢复真实惯性参数"""
        
    def fix_contact_sensor_names(self) -> None:
        """修复接触传感器碰撞体名称"""
        
    def adjust_contact_stiffness(self, new_kp: float = 10000.0) -> None:
        """调整接触刚度参数"""
        
    def fix_joint_types_and_limits(self) -> None:
        """修复关节类型并添加物理限位"""
        
    def save(self, output_path: str) -> None:
        """保存修复后的 URDF"""
```

### 2. 惯性参数提取器 (Inertia Extractor)

**职责**: 从参考 URDF 文件提取真实的惯性参数

**接口**:
```python
class InertiaExtractor:
    def __init__(self, urdf_path: str):
        """初始化提取器"""
        
    def extract_link_inertia(self, link_name: str) -> Dict:
        """提取指定 link 的惯性参数
        
        Returns:
            {
                'mass': float,
                'origin': {'xyz': [x, y, z], 'rpy': [r, p, y]},
                'inertia': {'ixx': float, 'ixy': float, ...}
            }
        """
        
    def get_all_inertias(self) -> Dict[str, Dict]:
        """获取所有 link 的惯性参数"""
```

### 3. 关节配置管理器 (Joint Configuration Manager)

**职责**: 管理关节类型和限位配置

**接口**:
```python
class JointConfigManager:
    def __init__(self, urdf_path: str):
        """初始化关节配置管理器"""
        
    def get_joint_type(self, joint_name: str) -> str:
        """获取关节类型（continuous, revolute, prismatic 等）"""
        
    def set_joint_type(self, joint_name: str, joint_type: str) -> None:
        """设置关节类型"""
        
    def add_joint_limits(self, joint_name: str, lower: float, upper: float, 
                        effort: float, velocity: float) -> None:
        """为关节添加限位
        
        Args:
            joint_name: 关节名称
            lower: 下限（弧度）
            upper: 上限（弧度）
            effort: 最大力矩（N·m）
            velocity: 最大速度（rad/s）
        """
        
    def get_recommended_limits(self, joint_name: str) -> Dict:
        """根据关节名称获取推荐的限位值
        
        Returns:
            {
                'lower': float,
                'upper': float,
                'effort': float,
                'velocity': float
            }
        """
```

### 4. URDF 验证器 (URDF Validator)

**职责**: 验证修复后的 URDF 文件是否正确

**接口**:
```python
class URDFValidator:
    def __init__(self, urdf_path: str):
        """初始化验证器"""
        
    def check_syntax(self) -> Tuple[bool, str]:
        """检查 XML 语法是否正确"""
        
    def check_no_ros1_plugins(self) -> Tuple[bool, str]:
        """检查是否移除了 ROS 1 插件"""
        
    def check_ros2_control_config(self) -> Tuple[bool, str]:
        """检查 ROS 2 控制器配置是否正确"""
        
    def check_inertia_parameters(self, reference_urdf: str) -> Tuple[bool, str]:
        """检查惯性参数是否恢复"""
        
    def check_contact_sensors(self) -> Tuple[bool, str]:
        """检查接触传感器配置"""
        
    def check_contact_stiffness(self, max_kp: float = 50000.0) -> Tuple[bool, str]:
        """检查接触刚度是否在合理范围"""
        
    def check_joint_types_and_limits(self) -> Tuple[bool, str]:
        """检查关节类型和限位配置"""
        
    def validate_all(self) -> Tuple[bool, List[str]]:
        """运行所有验证检查"""
```

## 数据模型

### URDF 元素定位

```python
# 需要修复的 XML 元素路径
ELEMENTS_TO_FIX = {
    'ros1_plugin': '//gazebo/plugin[@name="gazebo_ros_control"]',
    'ros2_control_params': '//gazebo/plugin[@name="gazebo_ros2_control"]/parameters',
    'base_link_inertial': '//link[@name="base_link"]/inertial',
    'leg_link_inertials': [
        '//link[@name="l1"]/inertial',
        '//link[@name="l11"]/inertial',
        '//link[@name="l111"]/inertial',
        '//link[@name="l1111"]/inertial',
        # ... 其他腿部 links
    ],
    'contact_sensors': [
        '//gazebo[@reference="l1111"]/sensor[@type="contact"]',
        '//gazebo[@reference="l2111"]/sensor[@type="contact"]',
        '//gazebo[@reference="l3111"]/sensor[@type="contact"]',
        '//gazebo[@reference="l4111"]/sensor[@type="contact"]',
    ],
    'contact_physics': [
        '//gazebo[@reference="l1111"]/kp',
        '//gazebo[@reference="l2111"]/kp',
        '//gazebo[@reference="l3111"]/kp',
        '//gazebo[@reference="l4111"]/kp',
    ],
    'hip_joints': [
        '//joint[@name="j11"]',
        '//joint[@name="j21"]',
        '//joint[@name="j31"]',
        '//joint[@name="j41"]',
    ],
    'knee_joints': [
        '//joint[@name="j111"]',
        '//joint[@name="j211"]',
        '//joint[@name="j311"]',
        '//joint[@name="j411"]',
    ],
    'shoulder_joints': [
        '//joint[@name="j1"]',
        '//joint[@name="j2"]',
        '//joint[@name="j3"]',
        '//joint[@name="j4"]',
    ]
}
```

### 惯性参数数据结构

```python
@dataclass
class InertiaParameters:
    """惯性参数数据类"""
    mass: float
    origin_xyz: List[float]  # [x, y, z]
    origin_rpy: List[float]  # [roll, pitch, yaw]
    ixx: float
    ixy: float
    ixz: float
    iyy: float
    iyz: float
    izz: float
    
    def to_xml(self) -> str:
        """转换为 URDF XML 格式"""
        return f"""<inertial>
      <origin xyz="{' '.join(map(str, self.origin_xyz))}" rpy="{' '.join(map(str, self.origin_rpy))}" />
      <mass value="{self.mass}" />
      <inertia ixx="{self.ixx}" ixy="{self.ixy}" ixz="{self.ixz}" 
               iyy="{self.iyy}" iyz="{self.iyz}" izz="{self.izz}" />
    </inertial>"""
```

### 关节限位数据结构

```python
@dataclass
class JointLimits:
    """关节限位数据类"""
    lower: float  # 下限（弧度）
    upper: float  # 上限（弧度）
    effort: float  # 最大力矩（N·m）
    velocity: float  # 最大速度（rad/s）
    
    def to_xml(self) -> str:
        """转换为 URDF XML 格式"""
        return f"""<limit lower="{self.lower}" upper="{self.upper}" 
             effort="{self.effort}" velocity="{self.velocity}" />"""

# 推荐的关节限位配置
RECOMMENDED_JOINT_LIMITS = {
    'hip': JointLimits(
        lower=-1.57,  # -90°
        upper=1.57,   # +90°
        effort=50.0,  # 50 N·m
        velocity=10.0  # 10 rad/s
    ),
    'knee': JointLimits(
        lower=-2.5,   # -143°（膝盖只能向一个方向弯曲）
        upper=0.0,    # 0°（完全伸直）
        effort=50.0,
        velocity=10.0
    ),
    'shoulder': JointLimits(
        lower=-0.785,  # -45°
        upper=0.785,   # +45°
        effort=30.0,
        velocity=8.0
    )
}
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: ROS 1 插件完全移除

*对于任何* 修复后的 URDF 文件，解析该文件不应该找到任何名为 "gazebo_ros_control" 的插件元素

**验证: 需求 1.1, 1.2, 1.3, 1.4**

### 属性 2: ROS 2 控制器配置路径不包含占位符

*对于任何* 修复后的 URDF 文件，gazebo_ros2_control 插件不应该包含 `<parameters>` 子元素

**验证: 需求 2.1, 2.3, 2.4**

### 属性 3: 惯性参数恢复一致性

*对于任何* link 名称，如果参考 URDF 中存在该 link，则修复后的 URDF 中该 link 的惯性参数应该与参考 URDF 中的值匹配（允许浮点误差 < 0.1%）

**验证: 需求 3.1, 3.2, 3.5**

### 属性 4: 接触传感器碰撞体名称简化

*对于任何* 足端接触传感器，其碰撞体名称应该遵循简化格式 "{link_name}_collision"，而不是包含 "lump" 或重复的 "collision" 字样

**验证: 需求 4.2, 4.4**

### 属性 5: 接触刚度在安全范围内

*对于任何* 足端碰撞配置，其接触刚度 kp 值应该小于或等于 50000.0

**验证: 需求 5.2, 5.4**

### 属性 6: XML 语法有效性

*对于任何* 修复后的 URDF 文件，使用 XML 解析器解析该文件应该成功且不产生语法错误

**验证: 需求 6.1**

### 属性 7: 文件备份存在性

*对于任何* 被修复的 URDF 文件，在修复操作完成后，应该存在一个带有时间戳的备份文件

**验证: 需求 6.6**

## 错误处理

### 错误类型

1. **文件不存在错误**
   - 场景: 指定的 URDF 文件不存在
   - 处理: 抛出 FileNotFoundError，提供清晰的错误消息

2. **XML 解析错误**
   - 场景: URDF 文件包含无效的 XML 语法
   - 处理: 捕获解析异常，报告错误位置和原因

3. **参考文件缺失错误**
   - 场景: 用于恢复惯性参数的参考 URDF 不存在
   - 处理: 提示用户指定正确的参考文件路径

4. **元素未找到错误**
   - 场景: 预期的 XML 元素在文件中不存在
   - 处理: 记录警告，跳过该修复项，继续其他修复

5. **备份失败错误**
   - 场景: 无法创建备份文件（权限问题等）
   - 处理: 中止修复操作，不修改原始文件

### 错误恢复策略

```python
def fix_urdf_with_rollback(urdf_path: str) -> bool:
    """带回滚功能的 URDF 修复"""
    backup_path = None
    try:
        # 1. 创建备份
        backup_path = create_backup(urdf_path)
        
        # 2. 应用修复
        fixer = URDFFixer(urdf_path)
        fixer.apply_all_fixes()
        fixer.save(urdf_path)
        
        # 3. 验证修复
        validator = URDFValidator(urdf_path)
        success, errors = validator.validate_all()
        
        if not success:
            # 验证失败，回滚
            restore_from_backup(backup_path, urdf_path)
            raise ValidationError(f"修复验证失败: {errors}")
            
        return True
        
    except Exception as e:
        # 发生错误，回滚
        if backup_path and os.path.exists(backup_path):
            restore_from_backup(backup_path, urdf_path)
        raise
```

## 测试策略

### 单元测试

测试各个组件的功能：

1. **URDFFixer 测试**
   - 测试移除 ROS 1 插件
   - 测试移除配置路径占位符
   - 测试惯性参数替换
   - 测试接触传感器名称修复
   - 测试接触刚度调整

2. **InertiaExtractor 测试**
   - 测试从有效 URDF 提取惯性参数
   - 测试处理缺失的 link
   - 测试处理格式错误的惯性数据

3. **URDFValidator 测试**
   - 测试检测 ROS 1 插件
   - 测试检测占位符语法
   - 测试验证惯性参数
   - 测试验证接触传感器配置

### 集成测试

测试完整的修复流程：

1. **端到端修复测试**
   - 输入: dog2_visual.urdf（包含所有错误）
   - 输出: dog2_gazebo_fixed.urdf（所有错误已修复）
   - 验证: 所有验证检查通过

2. **Gazebo 加载测试**
   - 在 Gazebo 中加载修复后的 URDF
   - 验证: 无错误消息，模型成功加载

3. **控制器连接测试**
   - 启动 ros2_control 控制器
   - 验证: 所有关节控制器成功连接

4. **传感器数据测试**
   - 运行仿真，机器人足端接触地面
   - 验证: 接触传感器产生有效数据

### 属性测试

使用属性测试验证通用正确性：

1. **属性 1 测试: ROS 1 插件移除**
   ```python
   def test_no_ros1_plugin(urdf_path):
       """验证修复后的 URDF 不包含 ROS 1 插件"""
       tree = ET.parse(urdf_path)
       root = tree.getroot()
       ros1_plugins = root.findall('.//plugin[@name="gazebo_ros_control"]')
       assert len(ros1_plugins) == 0, "发现 ROS 1 插件"
   ```

2. **属性 3 测试: 惯性参数一致性**
   ```python
   def test_inertia_consistency(fixed_urdf, reference_urdf):
       """验证惯性参数与参考文件一致"""
       extractor_fixed = InertiaExtractor(fixed_urdf)
       extractor_ref = InertiaExtractor(reference_urdf)
       
       for link_name in extractor_ref.get_all_link_names():
           inertia_fixed = extractor_fixed.extract_link_inertia(link_name)
           inertia_ref = extractor_ref.extract_link_inertia(link_name)
           
           # 允许 0.1% 的浮点误差
           assert abs(inertia_fixed['mass'] - inertia_ref['mass']) / inertia_ref['mass'] < 0.001
   ```

3. **属性 5 测试: 接触刚度范围**
   ```python
   def test_contact_stiffness_range(urdf_path, max_kp=50000.0):
       """验证接触刚度在安全范围内"""
       tree = ET.parse(urdf_path)
       root = tree.getroot()
       
       for kp_elem in root.findall('.//gazebo/kp'):
           kp_value = float(kp_elem.text)
           assert kp_value <= max_kp, f"接触刚度 {kp_value} 超过最大值 {max_kp}"
   ```

### 测试配置

- 单元测试: 使用 pytest，每个测试独立运行
- 集成测试: 使用 pytest + ROS 2 launch 测试框架
- 属性测试: 每个属性至少运行 100 次迭代
- 测试数据: 使用真实的 dog2 URDF 文件作为测试输入
- CI/CD: 所有测试在提交前必须通过
