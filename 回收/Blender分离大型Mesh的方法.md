# Blender分离大型Mesh的高效方法

## 🎯 问题

L1 mesh面数太多，无法一次性框选所有面进行分离。

## ✅ 解决方案（从简单到高级）

---

## 方法1：使用Bisect工具（最简单，推荐！）

这个方法不需要选择任何面，直接用平面切割！

### 步骤：

1. **打开L1文件**
   ```bash
   blender src/dog2_description/meshes/l1.STL
   ```

2. **进入编辑模式**
   - 选中对象
   - 按 `Tab` 进入编辑模式

3. **使用Bisect工具**
   - 按 `3` 切换到面选择模式
   - 在顶部菜单：`Mesh` → `Bisect`
   - 或者按 `空格` 搜索 "Bisect"

4. **设置切割平面**
   - 在左下角会出现Bisect选项
   - 设置 Plane Point（平面位置）：
     - X: 0
     - Y: 0
     - Z: 0.05（你想分离的高度）
   - 设置 Plane Normal（平面法向）：
     - X: 0
     - Y: 0
     - Z: 1（表示垂直切割）

5. **勾选 "Clear Inner" 或 "Clear Outer"**
   - 先勾选 "Clear Inner" 删除下半部分
   - 导出上半部分为 `l1_upper.STL`
   - 然后 `Ctrl + Z` 撤销
   - 勾选 "Clear Outer" 删除上半部分
   - 导出下半部分为 `l1_lower.STL`

---

## 方法2：使用Python脚本按Z坐标自动选择

这个方法完全自动化，不需要手动选择！

### 在Blender中运行脚本：

1. **打开L1文件**
   ```bash
   blender src/dog2_description/meshes/l1.STL
   ```

2. **切换到Scripting标签**
   - 点击顶部的 "Scripting"

3. **粘贴以下脚本**：

```python
import bpy
import bmesh

# 设置分离高度（米）
SPLIT_HEIGHT = 0.05

# 获取当前对象
obj = bpy.context.active_object

if obj and obj.type == 'MESH':
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 使用bmesh
    bm = bmesh.from_edit_mesh(obj.data)
    
    # 取消所有选择
    for v in bm.verts:
        v.select = False
    
    # 选择Z坐标大于SPLIT_HEIGHT的所有顶点
    for v in bm.verts:
        world_co = obj.matrix_world @ v.co
        if world_co.z >= SPLIT_HEIGHT:
            v.select = True
    
    # 更新mesh
    bmesh.update_edit_mesh(obj.data)
    
    # 切换到面选择模式
    bpy.ops.mesh.select_mode(type='FACE')
    
    print(f"✓ 已选择Z >= {SPLIT_HEIGHT}m的所有顶点")
    print("现在按 P → Selection 来分离")
else:
    print("✗ 请先选择一个mesh对象")
```

4. **点击运行按钮（▶）**

5. **分离选中的部分**
   - 按 `P` 键
   - 选择 "Selection"

6. **导出两个部分**

---

## 方法3：使用Boolean Modifier（适合复杂情况）

这个方法使用一个立方体作为"切刀"来分离mesh。

### 步骤：

1. **添加一个立方体作为切割工具**
   - `Shift + A` → Mesh → Cube
   - 按 `S` 缩放立方体，让它足够大能覆盖整个L1
   - 按 `G` + `Z` 移动立方体到分离位置

2. **使用Boolean Modifier分离上半部分**
   - 选中L1对象
   - 在右侧Properties面板，找到 Modifier Properties（扳手图标）
   - Add Modifier → Boolean
   - Operation: Intersect（交集）
   - Object: 选择刚才创建的Cube
   - Apply Modifier
   - 导出为 `l1_upper.STL`

3. **撤销并分离下半部分**
   - `Ctrl + Z` 撤销
   - 再次添加Boolean Modifier
   - Operation: Difference（差集）
   - Object: Cube
   - Apply Modifier
   - 导出为 `l1_lower.STL`

---

## 方法4：使用命令行脚本（完全自动化）

我已经创建了一个Python脚本，可以完全自动化这个过程！

### 使用方法：

```bash
# 直接运行
./分离l1部件.sh

# 或者手动指定参数
blender --background --python scripts/split_l1_mesh.py -- ~/aperfect/carbot_ws 0.05
```

这个脚本会：
- ✅ 自动按Z坐标选择顶点
- ✅ 自动分离mesh
- ✅ 自动导出两个文件
- ✅ 自动创建碰撞mesh
- ✅ 自动备份原文件

---

## 方法5：使用Knife Project（精确控制）

如果你想精确控制分离线的形状：

### 步骤：

1. **创建一个平面作为切割线**
   - `Shift + A` → Mesh → Plane
   - 按 `S` 缩放到足够大
   - 按 `G` + `Z` 移动到分离高度
   - 按 `R` + `X` + `90` 旋转平面（如果需要）

2. **使用Knife Project**
   - 选中L1对象
   - 按 `Tab` 进入编辑模式
   - 在顶视图（小键盘7）
   - 选择平面（在对象模式下）
   - 回到L1的编辑模式
   - `Mesh` → `Knife Project`

3. **选择并分离**
   - 现在会有一条切割线
   - 选择切割线上方的所有面
   - 按 `P` → Selection 分离

---

## 🎯 推荐方案对比

| 方法 | 难度 | 速度 | 精确度 | 适用场景 |
|------|------|------|--------|----------|
| Bisect工具 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 简单的平面切割 |
| Python脚本（手动） | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 需要自定义选择逻辑 |
| Boolean Modifier | ⭐⭐ | ⭐⭐ | ⭐⭐ | 复杂形状切割 |
| 命令行脚本 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 批量处理，自动化 |
| Knife Project | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | 需要精确控制切割线 |

---

## 🚀 最快速的方法（推荐）

### 使用Bisect工具：

```
1. 打开Blender
2. 导入L1.STL
3. Tab进入编辑模式
4. 空格搜索"Bisect"
5. 设置Z=0.05
6. 勾选"Clear Inner"
7. 导出上半部分
8. Ctrl+Z撤销
9. 勾选"Clear Outer"
10. 导出下半部分
```

**总耗时：2-3分钟！**

---

## 🔧 Bisect工具详细使用

### 在Blender中的操作：

1. **进入编辑模式**
   - 选中L1对象
   - 按 `Tab`

2. **激活Bisect工具**
   - 顶部菜单：`Mesh` → `Bisect`
   - 或按 `空格` 搜索 "Bisect"

3. **在3D视图中画一条线**
   - 鼠标左键点击并拖动
   - 这条线定义了切割平面

4. **调整参数（左下角）**
   ```
   Plane Point (平面位置):
   - X: 0.0
   - Y: 0.0  
   - Z: 0.05  ← 你想分离的高度
   
   Plane Normal (平面法向):
   - X: 0.0
   - Y: 0.0
   - Z: 1.0  ← 垂直切割
   
   选项:
   ☑ Fill        ← 填充切口
   ☐ Clear Inner ← 删除下半部分
   ☐ Clear Outer ← 删除上半部分
   ```

5. **分离上半部分**
   - 勾选 "Clear Inner"
   - `Tab` 退出编辑模式
   - `File` → `Export` → `STL`
   - 保存为 `l1_upper.STL`

6. **撤销并分离下半部分**
   - `Ctrl + Z` 撤销
   - 重新执行Bisect
   - 勾选 "Clear Outer"
   - 导出为 `l1_lower.STL`

---

## 💡 小技巧

### 1. 查看mesh的Z范围

在Blender中运行这个脚本查看mesh的高度范围：

```python
import bpy

obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)
    mid_z = (min_z + max_z) / 2
    
    print(f"Z范围: {min_z:.4f}m 到 {max_z:.4f}m")
    print(f"高度: {max_z - min_z:.4f}m")
    print(f"中点: {mid_z:.4f}m")
    print(f"建议分离高度: {mid_z:.4f}m")
```

### 2. 预览切割位置

在使用Bisect之前，可以添加一个平面来预览切割位置：

```
1. Shift + A → Mesh → Plane
2. S → 放大平面
3. G + Z + 0.05 → 移动到分离高度
4. 在X-Ray模式下查看（Alt + Z）
```

### 3. 批量处理多个部件

如果要分离所有4条腿的L1部件：

```bash
# 修改脚本处理l1, l2, l3, l4
for leg in l1 l2 l3 l4; do
    blender --background --python scripts/split_l1_mesh.py -- ~/aperfect/carbot_ws 0.05 $leg
done
```

---

## ⚠️ 常见问题

### Q: Bisect后mesh有破洞？
A: 勾选 "Fill" 选项来填充切口

### Q: 切割位置不准确？
A: 
1. 先运行查看Z范围的脚本
2. 使用精确的数值输入
3. 在侧视图（小键盘3）中操作更准确

### Q: 分离后mesh的原点位置不对？
A: 
```
1. 选中对象
2. Object → Set Origin → Origin to Geometry
3. 或 Object → Set Origin → Origin to 3D Cursor
```

### Q: 导出的STL文件太大？
A: 
1. 使用Decimate Modifier减少面数
2. 在导出设置中调整精度
3. 碰撞mesh可以更简化

---

## 🎯 总结

**最推荐的方法：**

1. **新手**：使用Bisect工具（最直观）
2. **进阶**：使用Python脚本（最灵活）
3. **批量**：使用命令行脚本（最高效）

**现在就试试Bisect工具！**

```bash
blender src/dog2_description/meshes/l1.STL
```

然后按照上面的步骤操作，2-3分钟就能完成！
