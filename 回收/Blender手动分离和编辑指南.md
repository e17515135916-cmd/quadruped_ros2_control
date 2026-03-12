# Blender手动分离和编辑L1部件 - 完整指南

## 🎯 目标

在Blender中打开L1，使用Bisect工具分离上下两部分，不需要手动选择面。

---

## 🚀 步骤1：打开L1文件

```bash
cd ~/aperfect/carbot_ws
blender src/dog2_description/meshes/l1.STL
```

---

## 📋 步骤2：确认切割位置（重要！）

在执行分离之前，先确认切割位置是否正确：

### 方法1：使用脚本查看建议位置

```bash
./查看l1信息.sh
```

这会显示：
- mesh的Z范围（最低点到最高点）
- 建议的分离位置（通常是中点）
- 其他可选的分离位置（1/4、1/3、2/3、3/4高度）

### 方法2：在Blender中可视化预览

**步骤A：添加预览平面**
1. 打开Blender后，按 `Shift + A` 添加对象
2. 选择 `Mesh` → `Plane`（平面）
3. 按 `S` 键缩放平面，让它比L1大一些
4. 按 `G` 然后 `Z` 移动平面到你想切割的高度
5. 直接输入数字（例如 `0.05`）然后按 `Enter`

**步骤B：使用X-Ray模式查看**
1. 按 `Alt + Z` 切换到X-Ray模式（透视模式）
2. 现在你可以看到平面穿过mesh的位置
3. 如果位置不对，选中平面，按 `G` + `Z` 重新调整
4. 按 `N` 键打开侧边栏，在"Transform"部分可以看到精确的Z坐标

**步骤C：记录Z坐标**
- 确认位置满意后，记下平面的Z坐标值
- 删除预览平面（选中后按 `X` → `Delete`）
- 这个Z值就是你要在Bisect中使用的值

---

## 📋 步骤3：使用Bisect工具分离

### 3.1 进入编辑模式
- 选中L1对象（左键点击）
- 按 `Tab` 键进入编辑模式

### 3.2 激活Bisect工具
- 顶部菜单：`Mesh` → `Bisect`
- 或者按 `空格` 键，搜索 "Bisect"

### 3.3 画一条切割线
- 在3D视图中，**鼠标左键点击并拖动**画一条线
- 这条线定义了切割平面的方向
- 建议在**侧视图**操作（按小键盘 `3`）

### 3.4 调整Bisect参数

在左下角会出现Bisect工具面板：

```
Plane Point (平面位置):
  X: 0.0
  Y: 0.0
  Z: 0.05  ← 输入你在步骤2中确认的Z值

Plane Normal (平面法向):
  X: 0.0
  Y: 0.0
  Z: 1.0  ← 垂直切割（沿Z轴）

选项:
  ☑ Fill          ← 先勾选这个，预览切割线
  ☐ Clear Inner   ← 先不勾选
  ☐ Clear Outer   ← 先不勾选
```

### 3.5 预览切割效果（再次确认）

1. 只勾选 `Fill` 选项，不勾选 Clear Inner/Outer
2. 你会看到一条切割线出现在mesh上
3. 按 `Alt + Z` 使用X-Ray模式查看切割位置
4. 如果位置不对，调整 "Plane Point Z" 的值
5. 确认满意后，继续下一步

### 3.6 分离上半部分

1. **勾选 "Clear Inner"**（删除下半部分）
2. 按 `Tab` 退出编辑模式
3. `File` → `Export` → `STL (.stl)`
4. 保存为：`src/dog2_description/meshes/l1_upper.STL`

### 3.7 撤销并分离下半部分

1. 按 `Ctrl + Z` 撤销（恢复完整mesh）
2. 按 `Tab` 进入编辑模式
3. 再次执行Bisect（`Mesh` → `Bisect`）
4. 设置相同的参数
5. **勾选 "Clear Outer"**（删除上半部分）
6. 导出为：`src/dog2_description/meshes/l1_lower.STL`

---

## 🎨 Bisect工具快捷操作

### 视图切换
- `小键盘 1` = 前视图
- `小键盘 3` = 侧视图（推荐用于Bisect）
- `小键盘 7` = 顶视图
- `小键盘 0` = 相机视图

### 精确输入
在Bisect面板中直接输入数值：
- 点击 "Plane Point Z" 输入框
- 输入精确的高度值（例如：0.05）
- 按 `Enter` 确认

### 查看切割效果
- 按 `Alt + Z` = 切换X-Ray模式（透视）
- 可以看到切割平面的位置

---

## 💡 如何确认切割位置

### 方法1：查看mesh信息（推荐）

```bash
./查看l1信息.sh
```

会显示：
```
Z范围：0.0000m 到 0.1000m
高度：0.1000m
建议分离位置：0.0500m（中点）

其他可能的分离位置：
  1/4高度：0.0250m
  1/3高度：0.0333m
  1/2高度：0.0500m
  2/3高度：0.0667m
  3/4高度：0.0750m
```

### 方法2：在Blender中查看尺寸

1. 选中对象
2. 按 `N` 键打开侧边栏
3. 查看 "Dimensions" 部分
4. 看 Z 值就是高度

### 方法3：添加预览平面（最直观）

**在Blender中可视化切割位置：**

1. 打开L1文件后，按 `Shift + A`
2. 选择 `Mesh` → `Plane`
3. 按 `S` 缩放平面（让它比L1大）
4. 按 `G` + `Z` + `0.05` 移动到切割高度
5. 按 `Alt + Z` 开启X-Ray模式
6. 现在你可以看到平面穿过mesh的位置！
7. 调整满意后，记下Z坐标
8. 删除平面（`X` → `Delete`）
9. 使用这个Z值进行Bisect

**这个方法让你在切割前就能看到效果！**

---

## 🔧 常见问题

### Q: 如何在切割前确认位置？
A: 
1. **最佳方法**：添加预览平面（Shift+A → Plane）
2. 移动平面到切割高度（G + Z + 数值）
3. 使用X-Ray模式（Alt+Z）查看平面穿过mesh的位置
4. 确认满意后记下Z坐标，删除平面
5. 使用这个Z值进行Bisect

### Q: Bisect后看不到效果？
A: 
1. 确保勾选了 "Fill" 选项
2. 确保勾选了 "Clear Inner" 或 "Clear Outer"
3. 检查 Plane Normal 是否正确（Z轴切割应该是 0, 0, 1）

### Q: 切割位置不对？
A: 
1. 在侧视图操作更准确（小键盘 3）
2. 直接在面板中输入精确的 Z 值
3. 使用 `./查看l1信息.sh` 查看建议的分离位置
4. 先用预览平面确认位置再切割

### Q: 想要重新切割？
A: 
1. 按 `Ctrl + Z` 撤销
2. 重新执行Bisect
3. 调整参数

### Q: 导出的文件在哪里？
A: 
默认在你的home目录，建议：
1. 在导出对话框中，导航到正确的路径
2. 或者导出后手动移动文件

---

## 📝 完整工作流程示例（带预览）

```bash
# 1. 查看L1信息，获取建议的分离位置
./查看l1信息.sh

# 输出：建议分离位置：0.0500m

# 2. 打开Blender
blender src/dog2_description/meshes/l1.STL

# 3. 在Blender中预览切割位置：
#    - Shift+A → Mesh → Plane（添加预览平面）
#    - S 缩放平面
#    - G + Z + 0.05 移动到切割高度
#    - Alt+Z 开启X-Ray模式查看
#    - 确认位置后，X 删除平面
#
# 4. 执行Bisect分离：
#    - Tab 进入编辑模式
#    - Mesh → Bisect
#    - 画一条切割线
#    - 设置 Plane Point Z = 0.05
#    - 勾选 Fill（先预览切割线）
#    - 确认后勾选 Clear Inner
#    - Tab 退出，导出 l1_upper.STL
#    
#    - Ctrl+Z 撤销
#    - 再次 Bisect
#    - 勾选 Clear Outer
#    - 导出 l1_lower.STL

# 5. 测试
colcon build --packages-select dog2_description
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

---

## 🎯 为什么用Bisect而不是手动选择？

| 方法 | 优点 | 缺点 |
|------|------|------|
| **手动选择面** | 精确控制 | 面数太多无法操作 ❌ |
| **Bisect工具** | 不需要选择面 ✅ | 只能平面切割 |
| **Python脚本** | 完全自动化 ✅ | 需要命令行 |

**Bisect是最适合你的方法！**

---

## 🚀 现在就试试

**推荐的完整流程（带预览）：**

```bash
# 步骤1：查看mesh信息
./查看l1信息.sh
```

**步骤2：在Blender中预览**
```bash
blender src/dog2_description/meshes/l1.STL
```

在Blender中：
1. `Shift + A` → `Mesh` → `Plane`（添加预览平面）
2. `S` 缩放平面，让它比L1大
3. `G` + `Z` + `0.05`（移动到建议的切割高度）
4. `Alt + Z`（开启X-Ray透视模式）
5. 查看平面位置是否满意
6. 如果不满意，按 `G` + `Z` 重新调整
7. 满意后，按 `N` 查看精确的Z坐标
8. `X` → `Delete` 删除预览平面

**步骤3：执行Bisect分离**
1. `Tab` 进入编辑模式
2. `Mesh` → `Bisect`
3. 画一条切割线
4. 在左下角面板输入刚才确认的Z值
5. 先勾选 `Fill` 预览切割线
6. 确认后勾选 `Clear Inner`，导出上半部分
7. `Ctrl + Z` 撤销，重新Bisect
8. 勾选 `Clear Outer`，导出下半部分

**不需要选择任何面，Bisect会自动处理！**

**关键优势：预览平面让你在切割前就能看到效果！**

---

## 🔄 方法2：使用Python脚本切分，然后在Blender中编辑和合并

如果你已经使用脚本切分了mesh，现在想要旋转一部分然后合并回去：

### 步骤1：运行切分脚本

```bash
# 在Z=0.02m位置切分
./分离l1部件.sh
# 输入分离高度：0.02
```

这会生成：
- `src/dog2_description/meshes/l1_upper.STL`
- `src/dog2_description/meshes/l1_lower.STL`

### 步骤2：在Blender中导入两个部分

```bash
# 同时导入两个STL文件
blender src/dog2_description/meshes/l1_upper.STL src/dog2_description/meshes/l1_lower.STL
```

或者在Blender中：
1. `File` → `Import` → `STL (.stl)`
2. 选择 `l1_upper.STL`，点击 `Import STL`
3. 再次 `File` → `Import` → `STL (.stl)`
4. 选择 `l1_lower.STL`，点击 `Import STL`

### 步骤3：旋转其中一个部分

**选择要旋转的对象：**
1. 在3D视图中左键点击选择对象（或在右侧Outliner中选择）
2. 对象会显示为橙色边框

**旋转对象：**
- 按 `R` 键进入旋转模式
- 然后按轴向键：
  - `R` + `X` = 绕X轴旋转
  - `R` + `Y` = 绕Y轴旋转
  - `R` + `Z` = 绕Z轴旋转
- 移动鼠标调整角度
- 或直接输入角度数字（例如：`R` + `Z` + `90` = 绕Z轴旋转90度）
- 按 `Enter` 确认

**精确旋转（推荐）：**
1. 选择对象
2. 按 `N` 键打开侧边栏
3. 在 "Transform" 部分找到 "Rotation"
4. 直接输入精确的旋转角度（单位：度）

### 步骤4：合并两个对象

**重要：合并前确保两个对象位置正确！**

1. 按住 `Shift` 键，依次点击两个对象（都选中）
2. 最后点击的对象会是"活动对象"（颜色更亮）
3. 按 `Ctrl + J` 合并对象

现在两个对象已经合并成一个了！

### 步骤5：合并重复的顶点

合并对象后，切割线上会有重复的顶点，需要合并它们：

1. 确保对象被选中
2. 按 `Tab` 进入编辑模式
3. 按 `A` 全选所有顶点
4. 按 `M` 键（Merge菜单）
5. 选择 "按距离"（By Distance）或 "合并重复项"
   - 中文界面：选择 "按距离"
   - 英文界面：选择 "By Distance"
6. 在左下角可以调整合并距离（默认0.0001m通常就够了）

你会看到提示信息，例如："已移除 1234 个顶点"

### 步骤6：导出合并后的mesh

1. 按 `Tab` 退出编辑模式
2. `File` → `Export` → `STL (.stl)`
3. 保存为：`src/dog2_description/meshes/l1_modified.STL`

### 步骤7：测试新的mesh

```bash
# 备份原文件
cp src/dog2_description/meshes/l1.STL src/dog2_description/meshes/l1_original_backup.STL

# 使用新文件
cp src/dog2_description/meshes/l1_modified.STL src/dog2_description/meshes/l1.STL

# 重新编译
colcon build --packages-select dog2_description
source install/setup.bash

# 在RViz中查看
ros2 launch dog2_description view_dog2.launch.py
```

---

## 🎨 Blender合并操作快捷键总结

### 对象模式（Object Mode）操作：
- `Shift + 左键点击` = 多选对象
- `Ctrl + J` = 合并选中的对象
- `R` = 旋转
- `R` + `X`/`Y`/`Z` = 绕指定轴旋转
- `R` + `数字` = 旋转指定角度
- `G` = 移动（Grab）
- `S` = 缩放（Scale）
- `N` = 打开/关闭侧边栏（查看精确数值）

### 编辑模式（Edit Mode）操作：
- `Tab` = 切换编辑模式/对象模式
- `A` = 全选
- `Alt + A` = 取消全选
- `M` = 合并菜单（Merge）
- `M` → "按距离" = 合并重复顶点

### 视图操作：
- `鼠标中键拖动` = 旋转视图
- `Shift + 鼠标中键` = 平移视图
- `鼠标滚轮` = 缩放
- `Alt + Z` = X-Ray透视模式
- `小键盘 1` = 前视图
- `小键盘 3` = 侧视图
- `小键盘 7` = 顶视图

---

## 💡 合并操作的关键提示

### 1. 确保对象位置正确
在合并前，确保两个部分的相对位置是你想要的：
- 使用 `G` + `Z` 移动对象
- 按 `N` 查看精确坐标
- 使用 `Alt + Z` 透视模式查看对齐情况

### 2. 合并顺序很重要
- 最后选择的对象会成为"父对象"
- 合并后的对象会使用父对象的名称
- 建议：先选择要保留名称的对象

### 3. 合并重复顶点是必须的
- 切割线上会有完全重叠的顶点
- 不合并会导致mesh不连续
- 使用 `M` → "按距离" 自动处理

### 4. 检查合并结果
合并后检查：
- 顶点数是否合理（应该比两个对象的总和少）
- 是否有孔洞或缝隙
- 使用 `Alt + Z` 透视模式检查内部

### 5. 导出设置
导出STL时：
- 确保 "Selection Only" 已勾选（如果只想导出选中对象）
- 或取消勾选导出所有对象
- 检查单位设置（通常使用米）

---

## 🔧 完整工作流程示例（脚本切分 + Blender编辑）

```bash
# 1. 使用脚本在Z=0.02m切分
./分离l1部件.sh
# 输入：0.02

# 2. 在Blender中打开两个部分
blender src/dog2_description/meshes/l1_upper.STL \
        src/dog2_description/meshes/l1_lower.STL
```

**在Blender中：**

```
# 3. 旋转下半部分（例如绕Z轴旋转90度）
- 点击选择 l1_lower 对象
- 按 R + Z + 90 + Enter

# 4. 合并两个对象
- Shift + 点击选择两个对象
- Ctrl + J 合并

# 5. 合并重复顶点
- Tab 进入编辑模式
- A 全选
- M → "按距离"
- Tab 退出编辑模式

# 6. 导出
- File → Export → STL
- 保存为 l1_modified.STL
```

```bash
# 7. 测试
cp src/dog2_description/meshes/l1.STL src/dog2_description/meshes/l1_backup.STL
cp src/dog2_description/meshes/l1_modified.STL src/dog2_description/meshes/l1.STL

colcon build --packages-select dog2_description
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

**这个方法结合了脚本的精确性和Blender的灵活性！**
