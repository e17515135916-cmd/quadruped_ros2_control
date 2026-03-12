# Blender修改机器人模型完整工作流程

## 🎯 修改流程总览

```
1. 备份原文件
2. 在Blender中打开并修改
3. 导出修改后的模型
4. 更新URDF参数（如果需要）
5. 测试验证
```

---

## 📋 方案A：修改单个部件（推荐新手）

### 适用场景
- 修改机身外形
- 调整腿部形状
- 添加传感器支架
- 修改某个零件的细节

### 详细步骤

#### 1. 备份原文件
```bash
# 备份你要修改的STL文件
cp src/dog2_description/meshes/base_link.STL src/dog2_description/meshes/base_link.STL.backup

# 或者备份整个meshes文件夹
cp -r src/dog2_description/meshes src/dog2_description/meshes_backup_$(date +%Y%m%d)
```

#### 2. 在Blender中打开单个STL
```bash
# 启动Blender
blender

# 在Blender中：
# File → Import → STL (.stl)
# 选择文件，例如：src/dog2_description/meshes/base_link.STL
```

#### 3. 修改模型
在Blender中可以做的修改：

**基础操作：**
- `Tab` - 进入编辑模式
- `G` - 移动（Grab）
- `S` - 缩放（Scale）
- `R` - 旋转（Rotate）
- `E` - 挤出（Extrude）
- `X` - 删除

**常见修改：**
- 添加孔洞（用于安装传感器）
- 修改外形
- 平滑表面
- 添加凸起或凹陷

#### 4. 导出修改后的模型
```bash
# 在Blender中：
# File → Export → STL (.stl)
# 
# 重要设置：
# ✅ Scene Unit - 保持原始单位
# ✅ Apply Modifiers - 应用所有修改器
# ✅ Selection Only - 如果只想导出选中的部分
# 
# 保存到原位置，覆盖原文件：
# src/dog2_description/meshes/base_link.STL
```

#### 5. 更新碰撞模型（如果需要）
```bash
# 如果你修改了视觉模型，也需要更新碰撞模型
# 碰撞模型在：src/dog2_description/meshes/collision/

# 可以直接复制视觉模型作为碰撞模型
cp src/dog2_description/meshes/base_link.STL \
   src/dog2_description/meshes/collision/base_link_collision.STL
```

#### 6. 测试
```bash
# 重新构建工作空间
cd ~/your_workspace
colcon build --packages-select dog2_description

# 在RViz中查看
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py

# 在Gazebo中测试
ros2 launch dog2_description dog2_fortress_with_gui.launch.py
```

---

## 📋 方案B：使用Phobos修改整个机器人

### 适用场景
- 调整关节位置
- 修改多个部件的相对位置
- 重新设计整体结构
- 需要保持关节层级关系

### 详细步骤

#### 1. 安装Phobos（如果还没安装）
```bash
# 下载phobos
cd ~/Downloads
git clone https://github.com/dfki-ric/phobos.git

# 在Blender中安装：
# Edit → Preferences → Add-ons → Install
# 选择 ~/Downloads/phobos/__init__.py
# 勾选启用 "Import-Export: Phobos"
```

#### 2. 导入URDF
```bash
# 启动Blender
blender

# 在Blender中：
# File → Import → URDF (.urdf)
# 选择：src/dog2_description/urdf/dog2.urdf
```

#### 3. 在Blender中修改
```bash
# 你会看到完整的机器人装配体
# 每个部件都是独立的对象
# 可以：
# - 选择某个部件进行修改
# - 调整关节位置
# - 修改部件形状
# - 添加新部件
```

#### 4. 导出修改后的模型

**选项1：导出整个URDF（推荐）**
```bash
# 在Blender中：
# File → Export → URDF (.urdf)
# 这会导出整个机器人定义
```

**选项2：只导出修改的部件**
```bash
# 选择修改的部件
# File → Export → STL (.stl)
# 保存到对应的meshes文件夹
```

#### 5. 更新URDF参数
如果你修改了几何形状，需要更新惯性参数：

```python
# 创建脚本：update_inertia.py
import trimesh
import numpy as np

# 加载修改后的STL
mesh = trimesh.load('src/dog2_description/meshes/base_link.STL')

# 计算质量属性（假设密度为1000 kg/m³）
density = 1000
mass = mesh.volume * density
inertia = mesh.moment_inertia * density

print(f"Mass: {mass}")
print(f"Inertia:\n{inertia}")
print(f"Center of mass: {mesh.center_mass}")
```

然后手动更新URDF文件中的inertial标签。

---

## 📋 方案C：快速修改（不用Phobos）

### 如果Phobos安装困难，用这个方法

#### 1. 创建Blender导入脚本
```python
# 保存为：import_dog2_to_blender.py
import bpy
import os

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置meshes路径（修改为你的实际路径）
meshes_path = "/home/your_username/your_workspace/src/dog2_description/meshes/"

# 定义所有部件及其位置（从URDF中提取）
parts = {
    "base_link": {"file": "base_link.STL", "location": (0, 0, 0)},
    "l1": {"file": "l1.STL", "location": (0.1881, 0.04675, 0)},
    "l11": {"file": "l11.STL", "location": (0.1881, 0.04675, 0)},
    # ... 添加其他部件
}

# 导入所有STL
for name, data in parts.items():
    filepath = os.path.join(meshes_path, data["file"])
    if os.path.exists(filepath):
        bpy.ops.import_mesh.stl(filepath=filepath)
        obj = bpy.context.selected_objects[0]
        obj.name = name
        obj.location = data["location"]
        print(f"Imported: {name}")

print("All parts imported!")
```

#### 2. 在Blender中运行脚本
```bash
# 启动Blender
blender

# 切换到 Scripting 标签
# 点击 New 创建新脚本
# 粘贴上面的代码
# 修改 meshes_path 为你的实际路径
# 点击运行按钮（▶）
```

---

## 🔧 常见修改场景示例

### 场景1：给机身添加传感器支架

```bash
1. 打开 base_link.STL
2. 在Blender中：
   - Tab 进入编辑模式
   - 选择要添加支架的面
   - E 挤出
   - S 缩放调整大小
3. 导出为 base_link.STL
4. 测试
```

### 场景2：修改腿部长度

```bash
1. 打开 l111.STL（小腿）
2. 在Blender中：
   - Tab 进入编辑模式
   - 选择需要拉长的部分
   - G + Z 沿Z轴移动
   - S + Z 沿Z轴缩放
3. 导出
4. 更新URDF中的关节位置参数
```

### 场景3：简化模型（减少面数）

```bash
1. 打开STL文件
2. 在Blender中：
   - 选择对象
   - 添加 Modifier → Decimate
   - 调整 Ratio（例如0.5 = 减少50%的面）
   - Apply Modifier
3. 导出
```

---

## ⚠️ 重要注意事项

### 修改后必须检查的事项：

1. **单位一致性**
   - Blender默认单位是米
   - 确保导出时单位设置正确

2. **原点位置**
   - STL的原点应该在关节位置
   - 如果原点错了，机器人会错位

3. **文件名**
   - 必须保持原文件名
   - 大小写要一致（Linux区分大小写）

4. **碰撞模型**
   - 修改视觉模型后，记得更新碰撞模型
   - 碰撞模型可以更简单（减少计算量）

5. **惯性参数**
   - 如果改变了形状或大小，必须更新URDF中的惯性参数
   - 否则物理模拟会不准确

---

## 🧪 测试流程

### 每次修改后都要测试：

```bash
# 1. 重新构建
cd ~/your_workspace
colcon build --packages-select dog2_description

# 2. 在RViz中检查外观
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py

# 3. 在Gazebo中测试物理
ros2 launch dog2_description dog2_fortress_with_gui.launch.py

# 4. 检查是否有碰撞问题
# 观察机器人是否能正常站立
# 腿部是否穿模
```

---

## 🆘 遇到问题怎么办

### 问题1：导出的模型在RViz中看不到
```bash
# 检查文件路径
ls -lh src/dog2_description/meshes/base_link.STL

# 检查文件大小（不应该是0）
# 重新导出，确保选中了对象
```

### 问题2：机器人位置错乱
```bash
# 检查STL的原点
# 在Blender中：Object → Set Origin → Origin to Geometry
# 重新导出
```

### 问题3：Gazebo中机器人掉落或抖动
```bash
# 需要更新惯性参数
# 使用trimesh计算新的质量和惯性
# 更新URDF文件
```

---

## 📚 推荐学习资源

- Blender基础教程：https://www.blender.org/support/tutorials/
- Phobos文档：https://github.com/dfki-ric/phobos
- URDF教程：http://wiki.ros.org/urdf/Tutorials

---

## 🎯 快速开始建议

**如果你是第一次修改，建议：**

1. 先从简单的开始：修改机身颜色或添加小装饰
2. 只修改一个STL文件
3. 修改前先备份
4. 每次只做一个小改动，立即测试
5. 熟悉流程后再做复杂修改

**需要我帮你：**
- 创建自动化脚本？
- 修改特定部件？
- 解决具体问题？

告诉我你想修改什么，我可以给你更具体的指导！
