# Design Document: Hip Joint Axis Change (Z to X)

## Overview

本设计文档描述了如何将 Dog2 四足机器人的髋关节（j11, j21, j31, j41）从 z 轴旋转改为 x 轴旋转。这是一个简单的参数修改任务，只需要更改 URDF Xacro 文件中的 `hip_axis` 参数，不涉及视觉模型、碰撞模型或其他几何结构的修改。

## Architecture

### 当前配置
- 髋关节 j11, j21, j31, j41 当前配置为绕 z 轴旋转（`axis="0 0 -1"`）
- 这使得髋关节在水平面内旋转（左右摆动）

### 目标配置
- 髋关节 j11, j21, j31, j41 将配置为绕 x 轴旋转（`axis="1 0 0"`）
- 这将使得髋关节前后摆动

### 修改范围
- **修改内容**：仅修改 `dog2.urdf.xacro` 文件中的 `hip_axis` 参数
- **不修改内容**：
  - 视觉模型（STL 文件）
  - 碰撞模型
  - 关节限位
  - 其他关节定义
  - 连杆惯性参数

## Components and Interfaces

### 1. URDF Xacro 文件结构

文件位置：`src/dog2_description/urdf/dog2.urdf.xacro`

#### Leg Macro 定义
```xml
<xacro:macro name="leg" params="... hip_axis:='0 0 -1'">
  ...
  <joint name="j${leg_num}1" type="revolute">
    <origin rpy="${hip_joint_rpy}" xyz="${hip_joint_xyz}"/>
    <parent link="l${leg_num}"/>
    <child link="l${leg_num}1"/>
    <axis xyz="${hip_axis}"/>
    <limit effort="${hip_effort}" lower="${hip_lower_limit}" 
           upper="${hip_upper_limit}" velocity="${hip_velocity}"/>
  </joint>
  ...
</xacro:macro>
```

#### Leg 实例化（需要修改的部分）
```xml
<!-- Leg 1: Front Left -->
<xacro:leg leg_num="1" 
           ...
           hip_axis="0 0 -1"/>  <!-- 需要改为 "1 0 0" -->

<!-- Leg 2: Front Right -->
<xacro:leg leg_num="2" 
           ...
           hip_axis="0 0 -1"/>  <!-- 需要改为 "1 0 0" -->

<!-- Leg 3: Rear Left -->
<xacro:leg leg_num="3" 
           ...
           hip_axis="0 0 -1"/>  <!-- 需要改为 "1 0 0" -->

<!-- Leg 4: Rear Right -->
<xacro:leg leg_num="4" 
           ...
           hip_axis="0 0 -1"/>  <!-- 需要改为 "1 0 0" -->
```

### 2. 修改策略

采用**最小化修改**策略：
1. 定位四个 leg 实例化语句
2. 将每个实例中的 `hip_axis` 参数从 `"0 0 -1"` 改为 `"1 0 0"`
3. 不修改任何其他参数

## Data Models

### 关节轴向定义

#### Z 轴旋转（当前配置）
```
axis="0 0 -1"
```
- 在局部坐标系中绕 z 轴负方向旋转
- 效果：髋关节在水平面内左右摆动

#### X 轴旋转（目标配置）
```
axis="1 0 0"
```
- 在局部坐标系中绕 x 轴正方向旋转
- 效果：髋关节前后摆动

### 关节限位（保持不变）
```xml
<limit effort="50" 
       lower="-2.618" 
       upper="2.618" 
       velocity="20"/>
```
- 位置限位：±150° (±2.618 rad)
- 力矩限位：50 Nm
- 速度限位：20 rad/s

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Hip Axis Configuration Consistency
*For any* leg instantiation (leg 1, 2, 3, 4), the `hip_axis` parameter SHALL be set to "1 0 0"

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: URDF Parsing Correctness
*For any* parsed URDF, when querying joint j11, j21, j31, or j41, the axis attribute SHALL return the vector [1, 0, 0]

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 3: Visual Model Preservation
*For any* hip link (l11, l21, l31, l41), the visual mesh filename and visual origin SHALL remain unchanged after the axis modification

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 4: Collision Model Preservation
*For any* hip link (l11, l21, l31, l41), the collision geometry and collision origin SHALL remain unchanged after the axis modification

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Joint Limits Preservation
*For any* hip joint (j11, j21, j31, j41), the effort, velocity, and position limits SHALL remain unchanged after the axis modification

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 6: Minimal Modification
*For any* line in the URDF file, if the line does not contain a `hip_axis` parameter for legs 1-4, then the line SHALL remain unchanged

**Validates: Requirements 5.3, 5.4**

## Error Handling

### 潜在问题和处理

1. **文件不存在**
   - 检查：验证 `src/dog2_description/urdf/dog2.urdf.xacro` 存在
   - 处理：如果文件不存在，报错并终止

2. **参数未找到**
   - 检查：确认四个 leg 实例化中都有 `hip_axis` 参数
   - 处理：如果某个 leg 缺少参数，报告具体是哪个 leg

3. **Xacro 语法错误**
   - 检查：修改后运行 `xacro` 命令验证语法
   - 处理：如果有语法错误，回滚修改并报告错误

4. **URDF 验证失败**
   - 检查：使用 `check_urdf` 验证生成的 URDF
   - 处理：如果验证失败，报告具体错误信息

## Testing Strategy

### Unit Tests

#### Test 1: 文件读取测试
- 验证能够正确读取 `dog2.urdf.xacro` 文件
- 验证文件包含四个 leg 实例化

#### Test 2: 参数定位测试
- 验证能够在每个 leg 实例化中找到 `hip_axis` 参数
- 验证当前值为 `"0 0 -1"` 或其他值

#### Test 3: 参数替换测试
- 验证能够正确替换 `hip_axis` 参数值
- 验证替换后的值为 `"1 0 0"`

#### Test 4: Xacro 编译测试
- 验证修改后的 xacro 文件可以成功编译为 URDF
- 命令：`xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/test.urdf`

#### Test 5: URDF 验证测试
- 验证生成的 URDF 通过 `check_urdf` 验证
- 命令：`check_urdf /tmp/test.urdf`

### Property-Based Tests

#### Property Test 1: Hip Axis Configuration Consistency
- 生成：解析修改后的 URDF
- 验证：对于每个髋关节（j11, j21, j31, j41），axis 属性为 [1, 0, 0]
- 迭代次数：100（虽然这是确定性测试，但保持一致性）

#### Property Test 2: Visual Model Preservation
- 生成：比较修改前后的 URDF
- 验证：所有 visual 标签的内容完全相同
- 迭代次数：100

#### Property Test 3: Collision Model Preservation
- 生成：比较修改前后的 URDF
- 验证：所有 collision 标签的内容完全相同
- 迭代次数：100

#### Property Test 4: Joint Limits Preservation
- 生成：解析修改前后的 URDF
- 验证：所有髋关节的 limit 标签内容完全相同
- 迭代次数：100

### Integration Tests

#### Test 1: RViz 可视化测试
- 启动 RViz 并加载修改后的 URDF
- 使用 joint_state_publisher_gui 控制髋关节
- 验证：髋关节绕 x 轴旋转（前后摆动）
- 验证：视觉外观与修改前一致

#### Test 2: Gazebo 仿真测试
- 启动 Gazebo 并加载修改后的机器人模型
- 通过 ROS 2 topic 发送关节命令
- 验证：髋关节绕 x 轴旋转
- 验证：碰撞检测正常工作

### 测试工具和库

- **Python**: 用于编写修改脚本和测试
- **pytest**: 单元测试框架
- **hypothesis**: Property-based testing 库
- **lxml**: XML 解析和修改
- **subprocess**: 调用 xacro 和 check_urdf 命令

### 测试配置

- 每个 property test 运行 100 次迭代
- 测试标签格式：`# Feature: hip-joint-z-axis-reversion, Property N: [property text]`

## Validation Plan

### 阶段 1：静态验证
1. 验证 xacro 文件语法正确
2. 验证生成的 URDF 格式正确
3. 验证所有四个髋关节的 axis 属性为 [1, 0, 0]

### 阶段 2：RViz 验证
1. 在 RViz 中加载机器人模型
2. 使用 joint_state_publisher_gui 测试髋关节运动
3. 确认髋关节绕 x 轴旋转
4. 确认视觉外观正确

### 阶段 3：Gazebo 验证
1. 在 Gazebo 中加载机器人模型
2. 通过 ROS 2 控制髋关节
3. 确认髋关节运动正确
4. 确认碰撞检测正常

## Implementation Notes

### 修改方法选择

有两种实现方法：

#### 方法 1：手动编辑（推荐用于简单修改）
- 直接在文本编辑器中修改四处 `hip_axis` 参数
- 优点：简单直接，易于理解
- 缺点：容易出错，不易自动化

#### 方法 2：脚本自动化（推荐用于可重复性）
- 编写 Python 脚本自动查找和替换
- 优点：可重复，可测试，不易出错
- 缺点：需要编写额外代码

**推荐使用方法 2**，因为：
1. 可以编写测试验证修改正确性
2. 可以在备份后安全执行
3. 可以轻松回滚
4. 为未来类似修改提供模板

### 备份策略

在修改前：
1. 创建 `dog2.urdf.xacro` 的备份
2. 备份文件命名：`dog2.urdf.xacro.backup_YYYYMMDD_HHMMSS`
3. 记录备份位置

### 回滚策略

如果修改失败：
1. 从备份恢复原文件
2. 报告失败原因
3. 不保留部分修改的文件

## Dependencies

### 系统依赖
- ROS 2 (Humble 或更高版本)
- xacro
- urdf_parser_py
- RViz2
- Gazebo Fortress

### Python 依赖
- lxml (XML 解析)
- pytest (测试框架)
- hypothesis (Property-based testing)

## Timeline Estimate

- 脚本开发：30 分钟
- 单元测试：30 分钟
- Property-based 测试：30 分钟
- RViz 验证：15 分钟
- Gazebo 验证：15 分钟
- 总计：约 2 小时

## Risks and Mitigations

### 风险 1：修改错误导致 URDF 无效
- 概率：低
- 影响：高
- 缓解：使用备份，运行 xacro 和 check_urdf 验证

### 风险 2：视觉外观意外改变
- 概率：极低（因为不修改视觉模型）
- 影响：中
- 缓解：在 RViz 中验证外观

### 风险 3：运动学行为不符合预期
- 概率：低
- 影响：中
- 缓解：在 RViz 和 Gazebo 中测试关节运动

## Conclusion

这是一个简单的参数修改任务，风险低，实现直接。通过自动化脚本和完善的测试，可以确保修改的正确性和可靠性。修改完成后，髋关节将从 z 轴旋转改为 x 轴旋转，实现前后摆动的运动模式。
