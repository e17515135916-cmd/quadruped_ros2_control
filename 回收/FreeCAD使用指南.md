# FreeCAD 使用指南 - 编辑Dog2机器人STL文件

## ✅ 安装成功！

FreeCAD 0.19 已成功安装在你的Ubuntu 22.04系统上。

## 🚀 快速启动

### 方法1：命令行启动
```bash
cd ~/aperfect/carbot_ws
freecad
```

### 方法2：图形界面启动
在应用程序菜单中搜索 "FreeCAD" 并点击启动

## 📁 STL文件位置

你的机器人mesh文件在这里：
```
~/aperfect/carbot_ws/src/dog2_description/meshes/
```

**髋关节相关文件（已旋转90度）：**
- `l1.STL`, `l11.STL` - 左前腿
- `l2.STL`, `l21.STL` - 右前腿  
- `l3.STL`, `l31.STL` - 左后腿
- `l4.STL`, `l41.STL` - 右后腿

**备份文件：**
- `*.STL.backup` - 原始文件备份

## 🔧 在FreeCAD中编辑STL文件

### 步骤1：导入STL文件

1. 启动FreeCAD
2. 点击 **File → Import**
3. 选择STL文件（例如：`l1.STL`）
4. 文件会以mesh对象导入

### 步骤2：查看和测量

- **旋转视图**：鼠标中键拖动
- **缩放**：鼠标滚轮
- **平移**：Shift + 中键拖动
- **测量**：Part → Measure → Distance

### 步骤3：编辑mesh

#### 选项A：直接编辑mesh（简单修改）

1. 选中导入的mesh对象
2. 点击 **Mesh Design** 工作台（顶部下拉菜单）
3. 使用mesh工具：
   - **Meshes → Analyze → Evaluate & Repair** - 修复mesh
   - **Meshes → Cutting** - 切割mesh
   - **Meshes → Boolean** - 布尔运算

#### 选项B：转换为实体后编辑（精确修改）

1. 选中mesh对象
2. **Part → Create shape from mesh**
3. 设置容差（Tolerance）：0.1
4. 点击OK，创建Shape对象
5. 切换到 **Part Design** 工作台
6. 现在可以使用CAD工具编辑

### 步骤4：旋转/移动对象

如果需要旋转或移动mesh：

1. 选中对象
2. 点击 **Edit → Placement**
3. 设置旋转角度：
   - **Rotation Axis**: 选择轴（X/Y/Z）
   - **Angle**: 输入角度（度）
4. 或者使用 **Draft** 工作台的旋转工具

### 步骤5：导出STL

1. 选中修改后的对象
2. 点击 **File → Export**
3. 选择文件类型：**STL Mesh (*.stl)**
4. 保存到原位置（会覆盖原文件）

⚠️ **重要**：导出前先备份原文件！

## 💡 实用技巧

### 1. 同时查看多个部件

```bash
# 在FreeCAD中依次导入多个文件
File → Import → l1.STL
File → Import → l11.STL
```

这样可以看到它们的相对位置关系。

### 2. 精确旋转

如果需要精确旋转90度：
1. 选中对象
2. Edit → Placement
3. Rotation Axis: Y
4. Angle: 90
5. 点击 Apply

### 3. 查看坐标系

- View → Toggle axis cross - 显示坐标轴

### 4. 测量尺寸

1. 切换到 **Part** 工作台
2. Part → Measure → Distance
3. 点击两个点测量距离

## 🔄 修改后的工作流程

1. **在FreeCAD中修改STL**
2. **导出STL文件**（覆盖原文件）
3. **重新编译URDF**：
   ```bash
   cd ~/aperfect/carbot_ws
   colcon build --packages-select dog2_description
   source install/setup.bash
   ```
4. **在RViz中查看效果**：
   ```bash
   ros2 launch dog2_description view_dog2.launch.py
   ```

## 📚 FreeCAD工作台说明

- **Start** - 起始页面
- **Part** - 基础实体建模
- **Part Design** - 参数化设计
- **Mesh Design** - mesh编辑
- **Draft** - 2D绘图和基础3D操作
- **Sketcher** - 草图绘制

## ⚠️ 注意事项

1. **始终备份原文件**
   ```bash
   cp l1.STL l1.STL.my_backup
   ```

2. **导出设置**
   - 使用ASCII格式（更通用）
   - 或使用Binary格式（文件更小）

3. **单位一致性**
   - URDF使用米（m）
   - 确保FreeCAD中的单位设置正确

4. **mesh质量**
   - 导出前检查mesh是否有错误
   - Mesh → Analyze → Evaluate & Repair

## 🎯 当前项目状态

你已经完成了髋关节改造（ZYY → XYY）：
- ✅ 8个mesh文件已旋转90度
- ✅ URDF joint axis已修改
- ✅ 编译成功

如果需要进一步微调mesh的形状或位置，现在可以在FreeCAD中精确编辑了！

## 🆘 常见问题

### Q: FreeCAD启动很慢？
A: 第一次启动会初始化，之后会快一些。

### Q: 导入STL后看不到对象？
A: 按 **V** 键然后按 **F** 键（View Fit All）

### Q: 如何撤销操作？
A: Ctrl+Z

### Q: 如何保存项目？
A: File → Save（保存为.FCStd格式，可以继续编辑）

## 📖 更多学习资源

- FreeCAD官方文档：https://wiki.freecad.org/
- FreeCAD中文教程：https://wiki.freecad.org/Getting_started/zh-cn
- YouTube教程搜索："FreeCAD STL editing"

---

**准备好了！现在你可以用FreeCAD自己修改机器人的mesh文件了！** 🎉
