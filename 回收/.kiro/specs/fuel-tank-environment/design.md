# Design Document: Fuel Tank Environment

## Overview

本设计文档描述了为Dog2四足机器人创建飞机油箱内部仿真环境的技术方案。该环境将在Gazebo中实现，包含底部桁条网格和竖直穿越孔，用于测试机器人在受限空间内的穿越能力。

### 设计目标

1. 创建可配置的油箱环境生成器（Python脚本）
2. 生成标准Gazebo SDF世界文件
3. 与现有Dog2 ROS2启动系统集成
4. 提供直观的视觉效果和物理交互

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Fuel Tank Environment                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────────────────┐  │
│  │  Python Generator │───▶│  fuel_tank.world (SDF)       │  │
│  │  (配置参数输入)    │    │  - 地面/底板                  │  │
│  └──────────────────┘    │  - 桁条网格                    │  │
│                          │  - 穿越孔面板                  │  │
│                          │  - 灯光/相机                   │  │
│                          └──────────────────────────────┘  │
│                                     │                       │
│                                     ▼                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ROS2 Launch System                       │  │
│  │  dog2_fuel_tank.launch.py                            │  │
│  │  - 加载 fuel_tank.world                              │  │
│  │  - 启动 Dog2 机器人                                   │  │
│  │  - 配置控制器                                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. 环境生成器 (generate_fuel_tank_world.py)

Python脚本，根据配置参数生成Gazebo世界文件。

```python
class FuelTankWorldGenerator:
    """油箱环境世界文件生成器"""
    
    def __init__(self, config: FuelTankConfig):
        self.config = config
    
    def generate(self) -> str:
        """生成完整的SDF世界文件内容"""
        pass
    
    def generate_base_plate(self) -> str:
        """生成底板SDF模型"""
        pass
    
    def generate_stringers(self) -> List[str]:
        """生成桁条网格SDF模型列表"""
        pass
    
    def generate_access_panels(self) -> List[str]:
        """生成带穿越孔的面板SDF模型列表"""
        pass
    
    def save(self, output_path: str) -> None:
        """保存世界文件到指定路径"""
        pass
```

### 2. 配置数据结构

```python
@dataclass
class FuelTankConfig:
    """油箱环境配置参数"""
    
    # 整体尺寸
    tank_length: float = 2.0      # 油箱长度 (X方向)
    tank_width: float = 1.5       # 油箱宽度 (Y方向)
    
    # 桁条参数
    stringer_height: float = 0.03  # 桁条高度
    stringer_width: float = 0.02   # 桁条宽度
    stringer_spacing_x: float = 0.15  # X方向间距
    stringer_spacing_y: float = 0.15  # Y方向间距
    
    # 穿越孔参数（窗型障碍物）
    hole_width: float = 0.25       # 穿越孔宽度（固定）
    hole_height: float = 0.20      # 穿越孔高度（固定）
    panel_thickness: float = 0.02  # 面板厚度
    panel_total_width: float = 0.40  # 面板总宽度（包含框架）
    panel_total_height: float = 0.40  # 面板总高度（包含框架）
    panel_elevation: float = 0.20  # 穿越孔底部离地高度（悬空）
    num_panels: int = 2            # 窗型面板数量
    
    # 机器人起始位置
    robot_start_x: float = -0.5    # 起始X位置（桁条区域前方）
    robot_start_z: float = 0.15    # 起始高度
```

### 3. SDF模型结构

#### 3.1 底板模型
```xml
<model name='fuel_tank_floor'>
  <static>true</static>
  <link name='floor_link'>
    <collision name='floor_collision'>
      <geometry>
        <box><size>{length} {width} 0.01</size></box>
      </geometry>
      <surface>
        <friction>
          <ode><mu>0.8</mu><mu2>0.8</mu2></ode>
        </friction>
      </surface>
    </collision>
    <visual name='floor_visual'>
      <geometry>
        <box><size>{length} {width} 0.01</size></box>
      </geometry>
      <material>
        <ambient>0.6 0.6 0.7 1</ambient>  <!-- 金属灰色 -->
      </material>
    </visual>
  </link>
</model>
```

#### 3.2 桁条模型
```xml
<model name='stringer_{i}_{j}'>
  <static>true</static>
  <pose>{x} {y} {z} 0 0 {rotation}</pose>
  <link name='link'>
    <collision name='collision'>
      <geometry>
        <box><size>{length} {width} {height}</size></box>
      </geometry>
    </collision>
    <visual name='visual'>
      <geometry>
        <box><size>{length} {width} {height}</size></box>
      </geometry>
      <material>
        <ambient>0.3 0.3 0.35 1</ambient>  <!-- 深灰色 -->
      </material>
    </visual>
  </link>
</model>
```

#### 3.3 窗型穿越障碍物面板模型

窗型面板是悬空的框架结构，由4个box组成框架，中间留出穿越孔：

```
        侧视图                     正视图
    
    ┌─────────────┐         ┌───────────────────┐
    │  上框架     │         │    上框架          │
    ├──┐     ┌───┤         ├───┬───────┬───────┤
    │左│     │右 │         │左 │       │  右   │
    │框│ 孔  │框 │  悬空   │框 │  孔   │  框   │
    │架│     │架 │  ↑     │架 │       │  架   │
    ├──┘     └───┤  |     ├───┴───────┴───────┤
    │  下框架     │  地面   │    下框架          │
    └─────────────┘         └───────────────────┘
```

每个窗型面板由4个独立的box模型组成：

```xml
<!-- 上框架 -->
<model name='window_panel_{i}_top'>
  <static>true</static>
  <pose>{x} {y} {z_top} 0 0 0</pose>
  <link name='link'>
    <collision name='collision'>
      <geometry>
        <box><size>{panel_width} {panel_thickness} {frame_height}</size></box>
      </geometry>
    </collision>
    <visual name='visual'>
      <geometry>
        <box><size>{panel_width} {panel_thickness} {frame_height}</size></box>
      </geometry>
      <material>
        <ambient>0.4 0.4 0.45 1</ambient>  <!-- 框架颜色 -->
      </material>
    </visual>
  </link>
</model>

<!-- 下框架 -->
<model name='window_panel_{i}_bottom'>
  <!-- 类似结构，位置在 z_bottom -->
</model>

<!-- 左框架 -->
<model name='window_panel_{i}_left'>
  <!-- 竖直框架，连接上下 -->
</model>

<!-- 右框架 -->
<model name='window_panel_{i}_right'>
  <!-- 竖直框架，连接上下 -->
</model>
```

**关键尺寸计算：**
- 穿越孔底部高度：`panel_elevation` (例如 0.20m)
- 穿越孔顶部高度：`panel_elevation + hole_height` (例如 0.40m)
- 框架厚度：`(panel_total_height - hole_height) / 2` (上下各一半)
- 框架宽度：`(panel_total_width - hole_width) / 2` (左右各一半)

### 4. Launch文件接口

```python
# dog2_fuel_tank.launch.py
def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', 
            default_value='fuel_tank.world'),
        DeclareLaunchArgument('robot_start_x', 
            default_value='-0.5'),
        DeclareLaunchArgument('robot_start_z', 
            default_value='0.15'),
        # ... 包含现有dog2_gazebo启动配置
    ])
```

## Data Models

### 世界文件结构

```
fuel_tank.world
├── <world name='fuel_tank'>
│   ├── <light name='sun'>           # 主光源
│   ├── <light name='spot_light'>    # 聚光灯（照亮油箱内部）
│   ├── <model name='ground_plane'>  # 地面
│   ├── <model name='fuel_tank_floor'> # 油箱底板
│   ├── <model name='stringer_0_0'>  # 桁条网格
│   ├── <model name='stringer_0_1'>
│   ├── ...
│   ├── <model name='access_panel_0'> # 穿越孔面板
│   ├── <model name='access_panel_1'>
│   ├── <physics>                    # 物理引擎配置
│   └── <gui>                        # 相机视角
└── </world>
```

### 桁条网格布局

```
Y
^
|   ═══════════════════════════  (横向桁条)
|   ║   ║   ║   ║   ║   ║   ║   (纵向桁条)
|   ═══════════════════════════
|   ║   ║   ║   ║   ║   ║   ║
|   ═══════════════════════════
|   ║   ║   ║   ║   ║   ║   ║
|   ═══════════════════════════
+---------------------------------> X
    机器人起始位置 →  桁条区域  →  窗型障碍物(悬空)
    
侧视图 (X-Z平面):
    
    窗型障碍物1      窗型障碍物2
    ┌───────┐        ┌───────┐
    │ ┌───┐ │        │ ┌───┐ │
    │ │孔 │ │ 悬空   │ │孔 │ │ 悬空
    │ └───┘ │        │ └───┘ │
    └───────┘        └───────┘
    ════════════════════════════  ← 地面/桁条
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Round-Trip

*For any* valid FuelTankConfig, generating a world file and parsing the stringer/hole dimensions from it SHALL produce values matching the original configuration parameters.

**Validates: Requirements 1.3, 4.1, 4.2, 4.3**

### Property 2: Stringer Grid Pattern Validity

*For any* generated fuel tank environment with N×M stringer grid, the stringers SHALL be positioned at regular intervals where:
- X positions differ by exactly `stringer_spacing_x`
- Y positions differ by exactly `stringer_spacing_y`
- All stringers are within the tank boundary

**Validates: Requirements 1.2, 2.4, 5.2**

### Property 3: Element Count Correctness

*For any* configuration specifying `num_stringers_x`, `num_stringers_y`, and `num_panels`, the generated world file SHALL contain exactly:
- `num_stringers_x * num_stringers_y` stringer models (for grid pattern)
- `num_panels` access panel models

**Validates: Requirements 4.4, 4.5**

### Property 4: SDF Structure Validity

*For any* generated world file, parsing it as XML SHALL succeed and the document SHALL contain:
- Exactly one `<world>` element
- At least one `<light>` element
- At least one `<model>` element with collision and visual children

**Validates: Requirements 3.1, 3.4, 3.5**

## Error Handling

### 配置验证错误

| 错误条件 | 处理方式 |
|---------|---------|
| 桁条间距 < 桁条宽度 | 抛出 ValueError，提示间距过小 |
| 穿越孔尺寸 > 面板尺寸 | 抛出 ValueError，提示孔尺寸无效 |
| 负数参数 | 抛出 ValueError，提示参数必须为正 |
| 油箱尺寸过小 | 警告并调整为最小可用尺寸 |

### 文件操作错误

| 错误条件 | 处理方式 |
|---------|---------|
| 输出目录不存在 | 自动创建目录 |
| 文件写入权限不足 | 抛出 PermissionError，提示检查权限 |
| 磁盘空间不足 | 抛出 IOError，提示磁盘空间问题 |

## Testing Strategy

### 单元测试

1. **配置验证测试**
   - 测试有效配置被接受
   - 测试无效配置被拒绝并给出正确错误信息

2. **SDF生成测试**
   - 测试生成的XML结构有效
   - 测试各组件（底板、桁条、面板）正确生成

3. **边界条件测试**
   - 最小配置（1个桁条，1个面板）
   - 最大合理配置

### 属性测试

使用 `hypothesis` 库进行属性测试：

1. **Property 1 测试**: 生成随机有效配置，验证round-trip
2. **Property 2 测试**: 生成随机网格配置，验证间距一致性
3. **Property 3 测试**: 生成随机数量配置，验证元素计数
4. **Property 4 测试**: 生成随机配置，验证SDF结构有效性

### 集成测试

1. **Gazebo加载测试**: 验证生成的世界文件能被Gazebo正确加载
2. **机器人生成测试**: 验证Dog2能在环境中正确生成
3. **碰撞测试**: 验证机器人与环境结构的碰撞检测正常工作

### 测试框架

- 单元测试: pytest
- 属性测试: hypothesis
- 集成测试: 手动验证（需要Gazebo环境）
