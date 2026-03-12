# Blender 凸包处理完全指南

## 为什么选择 Blender 凸包方案？

你做了一个非常明智的决定！相比简单的碰撞原语（box/cylinder），Blender 凸包方案有以下优势：

1. **更精确的碰撞检测**：凸包紧密包裹原始模型，比简单几何体更准确
2. **彻底解决"量子爆炸"**：凸包保证是凸多面体，物理引擎处理起来非常稳定
3. **专业工作流**：这是游戏和仿真行业的标准做法
4. **一劳永逸**：处理好的凸包模型可以长期使用

## 前置准备

### 1. 安装 Blender

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install blender

# 或者下载最新版本
# https://www.blender.org/download/
```

### 2. 找到你的 STL 文件

根据你的项目结构，STL 文件应该在：
```
src/dog2_description/meshes/
├── l111.STL   # 第1条腿大腿
├── l1111.STL  # 第1条腿小腿
├── l211.STL   # 第2条腿大腿
├── l2111.STL  # 第2条腿小腿
└── ...
```

## 步骤一：在 Blender 中打开 STL 文件

### 1. 启动 Blender
```bash
blender
```

### 2. 删除默认场景
- 选中默认的立方体、灯光、相机（按 `A` 全选）
- 按 `X` 删除
- 确认删除

### 3. 导入 STL 文件

- 菜单：`File` → `Import` → `STL (.stl)`
- 浏览到你的 mesh 文件夹
- 选择第一个文件（比如 `l111.STL`）
- 点击 `Import STL`

### 4. 检查导入的模型
- 按 `Numpad 7` 切换到顶视图
- 按 `Numpad 1` 切换到前视图
- 按 `Numpad 3` 切换到侧视图
- 滚动鼠标滚轮缩放查看模型

## 步骤二：生成凸包（Convex Hull）

### 方法 A：使用 Convex Hull 修改器（推荐）

1. **选中导入的模型**
   - 在 3D 视图中点击模型
   - 或在右侧 Outliner 中点击模型名称

2. **切换到编辑模式**
   - 按 `Tab` 键进入编辑模式
   - 或点击顶部的 `Edit Mode`

3. **全选所有顶点**
   - 按 `A` 键全选
   - 所有顶点应该变成橙色/黄色

4. **应用凸包操作**
   - 按 `Alt + M` 打开合并菜单
   - 或者菜单：`Mesh` → `Convex Hull`
   - 如果没有 Convex Hull 选项，使用下面的方法 B

### 方法 B：使用 Remesh 修改器（备选）

1. **选中模型，切换到对象模式**
   - 按 `Tab` 返回对象模式

2. **添加 Remesh 修改器**
   - 右侧属性面板 → 扳手图标（Modifiers）
   - 点击 `Add Modifier` → `Remesh`

3. **配置 Remesh 参数**
   - Mode: `Blocks` 或 `Smooth`
   - Octree Depth: `6` 或 `7`（数值越大越精细）
   - 点击 `Apply` 应用修改器

4. **简化网格（重要！）**
   - 再次添加修改器：`Add Modifier` → `Decimate`
   - Ratio: `0.3` - `0.5`（保留 30%-50% 的面）
   - 点击 `Apply`

## 步骤三：清理和优化凸包模型

### 1. 检查面数

- 右上角会显示顶点数和面数
- **目标**：碰撞网格应该在 **100-500 个面** 之间
- 如果面数太多（>1000），需要进一步简化

### 2. 进一步简化（如果需要）

如果面数太多：
1. 添加 `Decimate` 修改器
2. 调整 `Ratio` 参数（0.1 = 保留 10% 的面）
3. 预览效果，确保形状仍然合理
4. 点击 `Apply` 应用

### 3. 重新计算法线
- 进入编辑模式（`Tab`）
- 全选（`A`）
- 按 `Shift + N` 重新计算法线
- 或菜单：`Mesh` → `Normals` → `Recalculate Outside`

### 4. 移除重复顶点
- 仍在编辑模式
- 全选（`A`）
- 按 `M` → `By Distance`
- 或菜单：`Mesh` → `Merge` → `By Distance`

## 步骤四：导出凸包 STL 文件

### 1. 返回对象模式
- 按 `Tab` 返回对象模式

### 2. 导出为 STL
- 菜单：`File` → `Export` → `STL (.stl)`
- **重要命名规则**：
  - 原文件：`l111.STL`
  - 凸包文件：`l111_collision.STL` 或 `l111_convex.STL`

### 3. 导出设置
- **Scene Unit**: 保持默认
- **Forward**: Y Forward（重要！）
- **Up**: Z Up（重要！）
- **Scale**: 1.0
- **Apply Modifiers**: 勾选
- **Selection Only**: 勾选（只导出选中的模型）

### 4. 保存位置
- 保存到原 meshes 文件夹
- 或创建子文件夹 `meshes/collision/`

## 步骤五：批量处理所有 STL 文件

你需要对以下文件重复上述步骤：

```
大腿（Thigh）：
- l111.STL  → l111_collision.STL
- l211.STL  → l211_collision.STL
- l311.STL  → l311_collision.STL
- l411.STL  → l411_collision.STL

小腿（Shin）：
- l1111.STL → l1111_collision.STL
- l2111.STL → l2111_collision.STL
- l3111.STL → l3111_collision.STL
- l4111.STL → l4111_collision.STL
```

### 自动化脚本（高级）

如果你熟悉 Python，可以使用 Blender 的 Python API 批量处理：

```python
# blender_batch_convex_hull.py
import bpy
import os

# 配置
input_dir = "/path/to/meshes/"
output_dir = "/path/to/meshes/collision/"
files = ["l111.STL", "l211.STL", "l311.STL", "l411.STL",
         "l1111.STL", "l2111.STL", "l3111.STL", "l4111.STL"]

for filename in files:
    # 清空场景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # 导入 STL
    input_path = os.path.join(input_dir, filename)
    bpy.ops.import_mesh.stl(filepath=input_path)
    
    # 获取导入的对象
    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj
    
    # 进入编辑模式并应用凸包
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 简化网格
    bpy.ops.object.modifier_add(type='DECIMATE')
    obj.modifiers["Decimate"].ratio = 0.3
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    # 导出
    output_filename = filename.replace('.STL', '_collision.STL')
    output_path = os.path.join(output_dir, output_filename)
    bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True)
    
    print(f"Processed: {filename} → {output_filename}")
```

运行脚本：
```bash
blender --background --python blender_batch_convex_hull.py
```

## 步骤六：更新 URDF/Xacro 文件

### 1. 备份原文件
```bash
cp src/dog2_description/urdf/dog2.urdf.xacro \
   src/dog2_description/urdf/dog2.urdf.xacro.backup
```

### 2. 修改碰撞网格路径

找到类似这样的代码：

```xml
<!-- 原来的配置 -->
<link name="l${leg_num}11">
  <visual>
    <geometry>
      <mesh filename="package://dog2_description/meshes/l${leg_num}11.STL"/>
    </geometry>
  </visual>
  <collision>
    <geometry>
      <mesh filename="package://dog2_description/meshes/l${leg_num}11.STL" scale="0.95 0.95 0.95"/>
    </geometry>
  </collision>
</link>
```

修改为：
```xml
<!-- 使用凸包碰撞网格 -->
<link name="l${leg_num}11">
  <visual>
    <geometry>
      <mesh filename="package://dog2_description/meshes/l${leg_num}11.STL"/>
    </geometry>
  </visual>
  <collision>
    <geometry>
      <!-- 使用凸包文件，移除 scale -->
      <mesh filename="package://dog2_description/meshes/collision/l${leg_num}11_collision.STL"/>
    </geometry>
  </collision>
</link>
```

### 3. 关键修改点

对于**每条腿的大腿和小腿**，修改：
1. **移除 `scale` 属性**：凸包已经是优化过的
2. **更新 collision mesh 路径**：指向 `_collision.STL` 文件
3. **保持 visual mesh 不变**：用户看到的还是原始精细模型

## 步骤七：验证和测试

### 1. 检查文件结构
```bash
# 确认凸包文件存在
ls -lh src/dog2_description/meshes/collision/

# 应该看到：
# l111_collision.STL
# l211_collision.STL
# ...
```

### 2. 生成 URDF 并检查
```bash
cd src/dog2_description
xacro urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf
check_urdf /tmp/dog2_test.urdf
```

### 3. 在 RViz 中可视化
```bash
ros2 launch dog2_description view_robot.launch.py
```

在 RViz 中：
- 添加 `RobotModel` 显示
- 在左侧面板找到 `Visual Enabled` 和 `Collision Enabled`
- 切换查看 visual 和 collision 模型的区别

### 4. Gazebo 测试
```bash
ros2 launch dog2_gazebo spawn_dog2.launch.py
```

观察：
- ✅ 机器人应该平稳落地
- ✅ 不应该出现抖动或"炸飞"
- ✅ 腿部关节应该可以正常移动
- ✅ 没有 "collision penetration" 警告

## 常见问题和解决方案

### 问题 1：凸包太粗糙，丢失了细节

**解决方案**：
- 碰撞网格不需要完美匹配视觉模型
- 只要大致形状正确，物理仿真就会很准确
- 如果确实需要更精细，减少 Decimate 的 Ratio（比如 0.5 而不是 0.3）

### 问题 2：凸包面数太多（>1000 面）
**解决方案**：
- 增加 Decimate 修改器的强度（降低 Ratio）
- 或使用 Remesh 修改器先简化，再应用凸包
- 目标：100-500 面是最佳范围

### 问题 3：导出的 STL 文件方向不对
**解决方案**：
- 检查导出设置：Forward = Y Forward, Up = Z Up
- 或在 URDF 中添加旋转：
  ```xml
  <collision>
    <origin xyz="0 0 0" rpy="1.5708 0 0"/>  <!-- 旋转 90 度 -->
    <geometry>
      <mesh filename="..."/>
    </geometry>
  </collision>
  ```

### 问题 4：Gazebo 中仍然有碰撞问题
**解决方案**：
1. 检查凸包文件是否真的是凸的（在 Blender 中查看）
2. 确认移除了 `scale` 属性
3. 添加碰撞过滤（禁用相邻 Link 碰撞）：
   ```xml
   <gazebo>
     <self_collide>false</self_collide>
   </gazebo>
   ```

### 问题 5：小腿和足端仍然碰撞
**解决方案**：
- 在 Blender 中手动缩短小腿凸包
- 进入编辑模式，选择底部顶点，向上移动（`G` + `Z`）
- 或在 URDF 中调整 collision 的 origin 偏移

## 高级技巧

### 技巧 1：使用 V-HACD 算法（最专业）

V-HACD 是专门用于生成凸分解的算法，比简单凸包更精确：

```bash
# 安装 V-HACD
git clone https://github.com/kmammou/v-hacd.git
cd v-hacd/app
mkdir build && cd build
cmake ..
make

# 使用 V-HACD 处理 STL
./TestVHACD \
  --input /path/to/l111.STL \
  --output /path/to/l111_collision.obj \
  --resolution 100000 \
  --maxhulls 1
```

然后在 Blender 中导入 OBJ，导出为 STL。

### 技巧 2：为复杂形状使用多个凸包

如果一个部件形状很复杂（比如 L 形），可以分解为多个凸包：

```xml
<link name="l${leg_num}11">
  <collision name="collision_1">
    <geometry>
      <mesh filename=".../l${leg_num}11_collision_part1.STL"/>
    </geometry>
  </collision>
  <collision name="collision_2">
    <geometry>
      <mesh filename=".../l${leg_num}11_collision_part2.STL"/>
    </geometry>
  </collision>
</link>
```

### 技巧 3：可视化对比工具

创建一个脚本对比原始 mesh 和凸包：

```python
# compare_meshes.py
import trimesh
import numpy as np

def compare_meshes(original_stl, convex_stl):
    """对比原始 mesh 和凸包的差异"""
    original = trimesh.load(original_stl)
    convex = trimesh.load(convex_stl)
    
    print(f"原始模型：")
    print(f"  顶点数: {len(original.vertices)}")
    print(f"  面数: {len(original.faces)}")
    print(f"  体积: {original.volume:.6f} m³")
    
    print(f"\n凸包模型：")
    print(f"  顶点数: {len(convex.vertices)}")
    print(f"  面数: {len(convex.faces)}")
    print(f"  体积: {convex.volume:.6f} m³")
    
    volume_diff = abs(convex.volume - original.volume) / original.volume * 100
    print(f"\n体积差异: {volume_diff:.2f}%")
    
    if volume_diff > 20:
        print("⚠️  警告：体积差异较大，可能需要调整凸包")
    else:
        print("✅ 体积差异在合理范围内")

# 使用
compare_meshes("meshes/l111.STL", "meshes/collision/l111_collision.STL")
```

## 完整工作流程总结

```
1. 准备阶段
   ├── 安装 Blender
   ├── 找到所有 STL 文件
   └── 备份原始 URDF

2. Blender 处理（每个文件）
   ├── 导入 STL
   ├── 应用凸包操作
   ├── 简化网格（100-500 面）
   ├── 清理和优化
   └── 导出为 _collision.STL

3. 更新 URDF
   ├── 修改 collision mesh 路径
   ├── 移除 scale 属性
   └── 保持 visual mesh 不变

4. 验证测试
   ├── check_urdf 语法检查
   ├── RViz 可视化对比
   ├── Gazebo 稳定性测试
   └── 确认无碰撞警告
```

## 预期效果

完成后，你应该看到：

✅ **Gazebo 中机器人平稳落地**，不再"炸飞"  
✅ **没有 collision penetration 警告**  
✅ **关节运动流畅**，无异常抖动  
✅ **仿真性能提升**，碰撞检测更快  
✅ **视觉效果不变**，用户看到的还是精细模型  

## 下一步

完成凸包处理后，你可以：

1. **调整接触参数**：降低 kp、kd 获得更柔和的接触
2. **配置碰撞过滤**：禁用不需要的碰撞检测
3. **测试控制算法**：在稳定的仿真环境中测试你的控制器
4. **优化性能**：如果仿真仍然慢，进一步简化凸包

---

## 需要帮助？

如果在处理过程中遇到问题：

1. **Blender 操作问题**：查看 Blender 官方文档或教程
2. **URDF 配置问题**：我可以帮你修改 Xacro 文件
3. **Gazebo 仿真问题**：检查日志，我可以帮你分析

准备好开始了吗？从第一个 STL 文件开始，一步一步来！💪
