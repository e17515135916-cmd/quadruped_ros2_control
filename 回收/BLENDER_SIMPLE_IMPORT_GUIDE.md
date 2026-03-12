# Blender简单导入指南 - 无需Phobos

由于Phobos插件有numpy兼容性问题，我创建了一个简单的Python脚本来直接导入URDF。

## 🚀 快速开始

### 方法1：使用启动脚本（最简单）

```bash
cd ~/aperfect/carbot_ws
./scripts/open_dog2_in_blender.sh
```

这会自动：
1. ✅ 打开Blender
2. ✅ 运行导入脚本
3. ✅ 加载你的Dog2机器人模型
4. ✅ 显示所有部件

### 方法2：手动在Blender中运行

1. **打开Blender**
```bash
blender
```

2. **切换到Scripting标签**
   - 点击顶部的"Scripting"

3. **打开脚本**
   - 点击"Open"按钮
   - 选择：`~/aperfect/carbot_ws/scripts/urdf_to_blend_simple.py`

4. **修改URDF路径（如果需要）**
   - 找到脚本最后的这一行：
   ```python
   urdf_path = os.path.expanduser("~/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf")
   ```
   - 确保路径正确

5. **运行脚本**
   - 点击运行按钮（▶）或按 `Alt+P`

6. **查看结果**
   - 切换到"Layout"标签
   - 你应该能看到完整的机器人模型

---

## 📋 脚本功能

这个脚本会：
- ✅ 解析URDF文件
- ✅ 找到所有STL mesh文件
- ✅ 自动导入所有部件
- ✅ 根据URDF设置正确的位置和旋转
- ✅ 建立父子关节关系
- ✅ 自动调整视图以显示整个机器人

---

## 🎨 导入后的操作

### 查看模型
- **旋转视图**: 鼠标中键拖动
- **缩放**: 鼠标滚轮
- **平移**: Shift + 鼠标中键拖动
- **聚焦对象**: 选中对象后按 `Numpad .`

### 选择部件
- **单击**: 选择单个部件
- **Shift + 单击**: 多选
- **A**: 全选/取消全选
- **Alt + A**: 取消选择

### 修改部件
1. **选择要修改的部件**
   - 在3D视图中单击
   - 或在右侧"Outliner"中选择

2. **进入编辑模式**
   - 按 `Tab` 键
   - 或点击顶部的"Edit Mode"

3. **基础编辑操作**
   - `G`: 移动（Grab）
   - `S`: 缩放（Scale）
   - `R`: 旋转（Rotate）
   - `E`: 挤出（Extrude）
   - `X`: 删除

4. **退出编辑模式**
   - 再次按 `Tab`

### 导出修改后的部件

1. **选择修改的部件**
2. **File → Export → STL (.stl)**
3. **重要设置**:
   - ✅ 勾选 "Selection Only"（只导出选中的）
   - ✅ 勾选 "Apply Modifiers"
   - ✅ 保持 "Scene Unit"
4. **保存位置**:
   - 覆盖原文件：`src/dog2_description/meshes/[部件名].STL`
   - 或保存为新文件

---

## 🔍 部件名称对照

导入后，你会看到这些部件：

| Blender中的名称 | 说明 | 文件 |
|----------------|------|------|
| base_link | 机身 | base_link.STL |
| l1_link | 左前腿髋关节 | l1.STL |
| l11_link | 左前腿大腿 | l11.STL |
| l111_link | 左前腿小腿 | l111.STL |
| l2_link | 右前腿髋关节 | l2.STL |
| l21_link | 右前腿大腿 | l21.STL |
| l211_link | 右前腿小腿 | l211.STL |
| l3_link | 左后腿髋关节 | l3.STL |
| l31_link | 左后腿大腿 | l31.STL |
| l311_link | 左后腿小腿 | l311.STL |
| l4_link | 右后腿髋关节 | l4.STL |
| l41_link | 右后腿大腿 | l41.STL |
| l411_link | 右后腿小腿 | l411.STL |

---

## 🛠️ 修改工作流程示例

### 示例1：给机身添加传感器支架

```bash
1. 运行导入脚本
2. 选择 "base_link"
3. Tab 进入编辑模式
4. 选择要添加支架的面
5. E 挤出
6. S 缩放调整大小
7. Tab 退出编辑模式
8. File → Export → STL
9. 保存为 base_link.STL（覆盖原文件）
```

### 示例2：修改腿部形状

```bash
1. 运行导入脚本
2. 选择 "l111_link"（左前腿小腿）
3. Tab 进入编辑模式
4. 选择要修改的顶点/边/面
5. G + Z 沿Z轴移动
6. Tab 退出编辑模式
7. File → Export → STL
8. 保存为 l111.STL
```

---

## ⚠️ 注意事项

### 修改后必须做的事

1. **备份原文件**
```bash
cp src/dog2_description/meshes/base_link.STL \
   src/dog2_description/meshes/base_link.STL.backup
```

2. **更新碰撞模型**（如果修改了形状）
```bash
cp src/dog2_description/meshes/base_link.STL \
   src/dog2_description/meshes/collision/base_link_collision.STL
```

3. **重新构建工作空间**
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description
source install/setup.bash
```

4. **测试**
```bash
# 在RViz中查看
ros2 launch dog2_description view_dog2.launch.py

# 在Gazebo中测试
ros2 launch dog2_description dog2_fortress_with_gui.launch.py
```

### 常见问题

**Q: 导入后看不到模型？**
A: 按 `Home` 键或 `Numpad .` 来聚焦视图

**Q: 部件位置不对？**
A: 这是正常的，URDF中的关节变换可能很复杂。重点关注单个部件的形状修改。

**Q: 导出的STL文件太大？**
A: 在导出前，可以使用 Decimate modifier 减少面数：
   - 选择对象
   - Modifiers → Add Modifier → Decimate
   - 调整 Ratio（例如0.5 = 减少50%）
   - Apply Modifier

**Q: 修改后机器人在Gazebo中行为异常？**
A: 需要更新URDF中的惯性参数。使用trimesh计算新的质量和惯性矩阵。

---

## 🎯 快速命令参考

```bash
# 打开Blender并导入模型
./scripts/open_dog2_in_blender.sh

# 备份meshes文件夹
cp -r src/dog2_description/meshes src/dog2_description/meshes_backup_$(date +%Y%m%d)

# 重新构建
colcon build --packages-select dog2_description

# 测试
ros2 launch dog2_description view_dog2.launch.py
```

---

## 📚 Blender快捷键速查

| 操作 | 快捷键 |
|------|--------|
| 进入/退出编辑模式 | Tab |
| 移动 | G |
| 缩放 | S |
| 旋转 | R |
| 挤出 | E |
| 删除 | X |
| 全选 | A |
| 框选 | B |
| 撤销 | Ctrl+Z |
| 重做 | Ctrl+Shift+Z |
| 保存 | Ctrl+S |
| 聚焦选中对象 | Numpad . |
| 视图旋转 | 鼠标中键 |
| 视图缩放 | 滚轮 |
| 视图平移 | Shift+鼠标中键 |

---

## 🆘 需要帮助？

如果遇到问题：
1. 检查终端输出的错误信息
2. 确保URDF路径正确
3. 确保所有STL文件都存在
4. 查看Blender的System Console（Window → Toggle System Console）

**准备好了吗？** 运行这个命令开始：
```bash
./scripts/open_dog2_in_blender.sh
```
