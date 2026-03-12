# 棱柱关节行程问题报告

## 问题发现

在验证 URDF 时发现棱柱关节（导轨）的行程配置存在问题。

## 当前配置

```
j1 (Leg 1): lower=-0.111, upper=0.008  (119mm 行程，零点偏下 51.5mm)
j2 (Leg 2): lower=-0.008, upper=0.111  (119mm 行程，零点偏上 51.5mm)
j3 (Leg 3): lower=-0.111, upper=0.008  (119mm 行程，零点偏下 51.5mm)
j4 (Leg 4): lower=-0.008, upper=0.111  (119mm 行程，零点偏上 51.5mm)
```

## 问题分析

1. **行程被"腰斩"**
   - 预期设计: ±111mm (总行程 222mm)
   - 实际行程: 119mm
   - **损失: 103mm (46.4%)**

2. **零点不对称**
   - j1, j3: 只能向下伸 111mm，向上缩 8mm
   - j2, j4: 只能向下伸 8mm，向上缩 111mm
   - 零点偏移: ±51.5mm

3. **来源**
   - 这个配置来自原始 URDF 备份 (`dog2.urdf.backup_xacro_migration`)
   - 可能是 SolidWorks 导出时零点设置问题
   - 也可能是有意的机械限位设计

## 影响

- 垂直伸缩能力受限
- 越障高度可能不足
- 不同腿的伸缩方向不一致

## 建议修改方案

### 方案 A: 对称 ±111mm（推荐）

修改所有腿为对称配置：

```xml
<xacro:leg leg_num="1" 
           origin_xyz="1.1026 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0" 
           prismatic_lower="-0.111" 
           prismatic_upper="0.111"/>

<xacro:leg leg_num="2" 
           origin_xyz="1.3491 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0" 
           prismatic_lower="-0.111" 
           prismatic_upper="0.111"/>

<xacro:leg leg_num="3" 
           origin_xyz="1.3491 -0.68953 0.2649" 
           origin_rpy="1.5708 0 -3.1416" 
           prismatic_lower="-0.111" 
           prismatic_upper="0.111"/>

<xacro:leg leg_num="4" 
           origin_xyz="1.1071 -0.68953 0.2649" 
           origin_rpy="1.5708 0 -3.1416" 
           prismatic_lower="-0.111" 
           prismatic_upper="0.111"/>
```

**优点**:
- 恢复完整 222mm 行程
- 零点位于导轨中间
- 所有腿行为一致
- 向上/向下伸缩范围相同

**缺点**:
- 如果原始设计有机械限位，可能超出物理限制

### 方案 B: 保持原始配置

保持当前不对称配置。

**优点**:
- 符合原始 URDF 设计
- 如果有机械限位，不会超出

**缺点**:
- 行程损失 46.4%
- 零点不在中间
- 不同腿行为不一致

## 验证步骤

1. **检查机械设计图纸**
   - 确认导轨的实际物理行程
   - 确认零点位置设置

2. **测试修改后的配置**
   ```bash
   # 修改 Xacro 文件
   vim src/dog2_description/urdf/dog2.urdf.xacro
   
   # 重新构建
   colcon build --packages-select dog2_description
   
   # 分析配置
   python3 scripts/analyze_prismatic_joints.py src/dog2_description/urdf/dog2.urdf
   
   # 在 Gazebo 中测试
   ros2 launch dog2_description gazebo_dog2.launch.py
   ```

3. **观察行为**
   - 检查腿部是否能正常伸缩
   - 确认没有超出物理限制
   - 测试越障能力

## 当前状态

✅ **已修复宏参数传递问题**
- 棱柱关节限位现在正确使用 `${prismatic_lower}` 和 `${prismatic_upper}` 参数
- 不同腿的限位可以独立配置

⚠️ **等待用户决定**
- 是否修改为对称 ±111mm 配置
- 或保持原始不对称配置

## 相关文件

- Xacro 源文件: `src/dog2_description/urdf/dog2.urdf.xacro`
- 分析脚本: `scripts/analyze_prismatic_joints.py`
- 原始备份: `src/dog2_description/urdf/dog2.urdf.backup_xacro_migration`
