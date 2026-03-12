# 在Blender中打开URDF机器人模型指南

## 方法1：使用phobos插件（推荐）

### 安装步骤

1. **安装Blender** (如果还没有)
```bash
sudo snap install blender --classic
# 或者从官网下载：https://www.blender.org/download/
```

2. **安装phobos插件**
```bash
# 克隆phobos仓库
cd ~/Downloads
git clone https://github.com/dfki-ric/phobos.git
cd phobos

# 在Blender中安装：
# Edit → Preferences → Add-ons → Install
# 选择 phobos 文件夹中的 __init__.py
# 启用 "Import-Export: Phobos"
```

3. **导入URDF**
```bash
# 在Blender中：
# File → Import → URDF (.urdf)
# 选择文件：src/dog2_description/urdf/dog2.urdf
```

### 使用phobos的优势
- 保留关节层级结构
- 可以看到完整的机器人装配体
- 可以测试关节运动
- 修改后可以导出回URDF

---

## 方法2：转换URDF为COLLADA/OBJ

如果phobos安装困难，可以先转换格式：

### 使用ROS工具转换

```bash
# 安装转换工具
sudo apt-get install ros-humble-collada-urdf

# 转换URDF到COLLADA (.dae)
cd ~/your_workspace
rosrun collada_urdf urdf_to_collada src/dog2_description/urdf/dog2.urdf dog2.dae

# 然后在Blender中导入COLLADA
# File → Import → Collada (.dae)
```

---

## 方法3：使用Python脚本批量导入STL

创建一个Blender Python脚本，自动导入所有部件并按URDF定义的位置摆放：

```python
# blender_import_dog2.py
import bpy
import os

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置meshes路径
meshes_path = "/path/to/src/dog2_description/meshes/"

# 导入所有STL文件
stl_files = [
    "base_link.STL",
    "l1.STL", "l11.STL", "l111.STL",
    "l2.STL", "l21.STL", "l211.STL",
    "l3.STL", "l31.STL", "l311.STL",
    "l4.STL", "l41.STL", "l411.STL",
]

for stl_file in stl_files:
    filepath = os.path.join(meshes_path, stl_file)
    if os.path.exists(filepath):
        bpy.ops.import_mesh.stl(filepath=filepath)
        print(f"Imported: {stl_file}")

print("All parts imported!")
```

**使用方法：**
```bash
# 在Blender中运行脚本
# Scripting标签 → 新建脚本 → 粘贴代码 → 修改路径 → 运行
```

---

## 方法4：逐个导入STL文件（最简单但繁琐）

1. 打开Blender
2. File → Import → STL (.stl)
3. 逐个导入每个部件
4. 手动调整位置和旋转

**部件列表：**
- `base_link.STL` - 机身
- `l1.STL` - 左前腿髋关节
- `l11.STL` - 左前腿大腿
- `l111.STL` - 左前腿小腿
- `l2.STL` - 右前腿髋关节
- `l21.STL` - 右前腿大腿
- `l211.STL` - 右前腿小腿
- `l3.STL` - 左后腿髋关节
- `l31.STL` - 左后腿大腿
- `l311.STL` - 左后腿小腿
- `l4.STL` - 右后腿髋关节
- `l41.STL` - 右后腿大腿
- `l411.STL` - 右后腿小腿

---

## 修改后的工作流程

### 如果修改单个部件：
1. 在Blender中打开并修改STL
2. 导出为STL（保持原文件名）
3. 替换原文件
4. 重新构建ROS2工作空间

### 如果修改整体装配：
1. 使用phobos导入URDF
2. 在Blender中修改
3. 使用phobos导出URDF
4. 检查并更新惯性参数

---

## 推荐工作流程

**最佳实践：**
1. 先备份原始文件
2. 使用phobos插件导入完整URDF
3. 在Blender中进行修改
4. 导出修改后的部件
5. 更新URDF中的惯性参数（如果几何形状改变）
6. 在RViz/Gazebo中测试

---

## 需要帮助？

如果你想：
- 安装phobos插件
- 创建自动导入脚本
- 修改特定部件
- 更新URDF参数

请告诉我具体需求，我可以创建详细的实施计划！
