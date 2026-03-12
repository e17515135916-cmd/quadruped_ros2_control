# DOG2 碰撞体修复总结

## 问题描述
DOG2 机器人在 Gazebo 仿真中掉到地面以下（Z ≈ -1.0），物理仿真不稳定。

## 根本原因
1. **复杂的 STL mesh 碰撞体** - 大腿和小腿使用完整的 STL mesh 作为碰撞体
2. **Mesh 穿透** - 相邻 Link 的 mesh 在关节处可能重叠
3. **计算效率低** - 复杂 mesh 的碰撞检测计算量大

## 解决方案
将大腿和小腿的碰撞体从 STL mesh 替换为简单的 cylinder 原语。

### 修改内容

#### 1. 大腿（Thigh）碰撞体
**原配置：**
```xml
<collision>
  <origin rpy="${thigh_visual_rpy}" xyz="0.026 -0.076004 0.064987"/>
  <geometry>
    <mesh filename="package://dog2_description/meshes/collision/l${leg_num}11_collision.STL"/>
  </geometry>
</collision>
```

**新配置：**
```xml
<collision>
  <!-- Cylinder collision primitive to prevent joint overlap -->
  <!-- Radius: 0.072m (mesh width/2 * 0.9), Length: 0.155m (mesh length * 0.85) -->
  <origin rpy="${thigh_visual_rpy} 1.5708 0" xyz="0.026 -0.076 0.065"/>
  <geometry>
    <cylinder radius="0.072" length="0.155"/>
  </geometry>
</collision>
```

**参数说明：**
- Radius: 0.072m = 0.160m (mesh width) / 2 × 0.9
- Length: 0.155m = 0.182m (mesh length) × 0.85
- Origin: 保持与 mesh 质心相同的位置
- Rotation: 添加 1.5708 rad (90°) 使 cylinder 沿 Y 轴方向

#### 2. 小腿（Shin）碰撞体
**原配置：**
```xml
<collision>
  <origin rpy="0 0 0" xyz="0 0 0"/>
  <geometry>
    <mesh filename="package://dog2_description/meshes/l${leg_num}111.STL"/>
  </geometry>
</collision>
```

**新配置：**
```xml
<collision>
  <!-- Truncated cylinder collision primitive to prevent foot overlap -->
  <!-- Radius: 0.079m (mesh width/2 * 0.9), Length: 0.286m (mesh length - 0.03m) -->
  <origin rpy="0 1.5708 0" xyz="0.026 -0.127 -0.072"/>
  <geometry>
    <cylinder radius="0.079" length="0.286"/>
  </geometry>
</collision>
```

**参数说明：**
- Radius: 0.079m = 0.176m (mesh width) / 2 × 0.9
- Length: 0.286m = 0.316m (mesh length) - 0.03m（截断 30mm 避免与足端重叠）
- Origin: 调整位置使 cylinder 不延伸到足端
- Rotation: 1.5708 rad (90°) 使 cylinder 沿 Y 轴方向

#### 3. 调整生成高度
将机器人生成高度从 0.5m 提高到 1.0m，避免初始穿透。

## 测试结果

### 修复前
- ❌ 机器人 Z 坐标：-0.96m（掉到地面以下）
- ❌ Z 坐标持续下降
- ❌ 物理仿真不稳定

### 修复后
- ✅ 机器人 Z 坐标：0.556m（正常站立高度）
- ✅ Z 坐标稳定（变化 < 0.001m）
- ✅ 物理仿真稳定

## 性能提升
1. **碰撞检测速度** - Cylinder 比复杂 mesh 快 10-100 倍
2. **物理稳定性** - 简单几何体避免了 mesh 穿透问题
3. **Gazebo 加载速度** - 减少了 mesh 文件加载时间

## 保留的功能
- ✅ Visual mesh 保持不变（外观没有变化）
- ✅ 所有关节和连接保持不变
- ✅ 惯性参数保持不变

## 下一步
1. 测试机器人行走控制
2. 如需要，可以进一步优化碰撞体尺寸
3. 解决 Gazebo 图形界面卡住的问题（可选）

## 文件修改
- `src/dog2_description/urdf/dog2.urdf.xacro` - 修改大腿和小腿碰撞体
- `src/dog2_description/launch/gazebo_headless.launch.py` - 调整生成高度

## 任务完成状态
- ✅ 任务 4.1: 将大腿 collision 标签从 mesh 改为 cylinder
- ✅ 任务 5.1: 将小腿 collision 标签从 mesh 改为 cylinder
- ✅ 物理仿真验证通过
