# Blender导入Dog2完整装配体指南

## 🎯 目标

在Blender中打开Dog2机器人的**完整装配体**，所有部件都在正确的位置，这样你就可以：
- 查看整个机器人的装配关系
- 在装配体环境中调整部件的位置和旋转
- 修改部件之间的相对位置

## ✅ 改进的导入脚本

我已经改进了导入脚本 `scripts/urdf_to_blend_simple.py`，现在它能：
- ✅ 正确处理URDF中的复杂变换矩阵
- ✅ 计算每个部件的世界坐标
- ✅ 显示完整的、正确装配的机器人
- ✅ 保持父子层级关系

## 🚀 使用方法

### 方法1：使用启动脚本（推荐）

```bash
cd ~/aperfect/carbot_ws
./scripts/open_dog2_in_blender.sh
```

### 方法2：手动在Blender中运行

1. **打开Blender**
```bash
blender
```

2. **切换到Scripting标签**
   - 点击顶部的"Scripting"

3. **打开改进的脚本**
   - 点击"Open"按钮
   - 选择：`~/aperfect/carbot_ws/scripts/urdf_to_blend_simple.py`

4. **运行脚本**
   - 点击运行按钮（▶）或按 `Alt+P`

5. **查看结果**
   - 切换到"Layout"标签
   - 按 `Home` 键或 `Numpad .` 来聚焦整个机器人

## 📐 现在你应该看到什么

导入后，你会看到：
- ✅ 机身（base_link）在中心
- ✅ 4条腿在正确的位置
- ✅ 每条腿的所有关节都正确连接
- ✅ 球形脚在每条腿的末端

**机器人应该看起来像一个完整的四足机器人，而不是散落的零件！**

## 🔧 如何在装配体中修改部件

### 1. 选择要修改的部件

在右侧的"Outliner"面板中，你会看到层级结构：
```
base_link (机身)
├── l1 (左前腿 - 髋关节滑轨)
│   └── l11 (左前腿 - 髋关节)
│       └── l111 (左前腿 - 大腿)
│           └── l1111 (左前腿 - 小腿)
│               └── l11111 (左前腿 - 脚)
├── l2 (右前腿...)
├── l3 (左后腿...)
└── l4 (右后腿...)
```

点击任何部件来选择它。

### 2. 在Object Mode中调整位置/旋转

**重要：不要进入Edit Mode！**

在Object Mode中（默认模式）：
- 按 `G` 然后移动鼠标 = 移动部件
- 按 `R` 然后移动鼠标 = 旋转部件
- 按 `S` 然后移动鼠标 = 缩放部件

**约束到特定轴：**
- `G` + `X` = 只沿X轴移动
- `G` + `Y` = 只沿Y轴移动
- `G` + `Z` = 只沿Z轴移动
- `R` + `X` = 只绕X轴旋转
- `R` + `Y` = 只绕Y轴旋转
- `R` + `Z` = 只绕Z轴旋转

**精确输入数值：**
- `G` + `X` + `0.1` + `Enter` = 沿X轴移动0.1米
- `R` + `Z` + `90` + `Enter` = 绕Z轴旋转90度

### 3. 查看修改后的变换值

选中部件后，在右侧的"Properties"面板中：
- 找到"Transform"部分
- 你会看到：
  - Location (位置): X, Y, Z
  - Rotation (旋转): X, Y, Z (欧拉角，单位是度)
  - Scale (缩放): X, Y, Z

**这些值就是你需要更新到URDF文件中的值！**

## 📝 如何将修改应用到URDF

假设你修改了 `l11` (左前腿髋关节) 的位置：

### 1. 记录Blender中的变换值

在Blender中选中 `l11`，查看Transform面板：
- Location: X=0.05, Y=0.02, Z=0.06
- Rotation: X=0°, Y=0°, Z=95°

### 2. 转换旋转角度为弧度

Blender显示的是度，URDF使用弧度：
- 95° = 95 × π / 180 = 1.658 弧度

### 3. 找到URDF中对应的joint

打开 `src/dog2_description/urdf/dog2.urdf.xacro`，找到 `j11` joint：

```xml
<joint name="j11" type="revolute">
    <origin rpy="0 0 1.5708" xyz="-0.016 0.0199 0.055"/>
    <parent link="l1"/>
    <child link="l11"/>
    ...
</joint>
```

### 4. 更新origin值

将Blender中的值更新到URDF：

```xml
<joint name="j11" type="revolute">
    <origin rpy="0 0 1.658" xyz="0.05 0.02 0.06"/>
    <parent link="l1"/>
    <child link="l11"/>
    ...
</joint>
```

### 5. 重新编译URDF

```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description
source install/setup.bash
```

### 6. 在RViz中验证

```bash
ros2 launch dog2_description view_dog2.launch.py
```

## 🎨 Blender快捷键速查

### 视图控制
- **旋转视图**: 鼠标中键拖动
- **缩放**: 鼠标滚轮
- **平移**: Shift + 鼠标中键拖动
- **聚焦选中对象**: Numpad `.` 或 `Home`
- **查看所有对象**: `Home`

### 选择
- **选择对象**: 左键单击
- **多选**: Shift + 左键单击
- **全选**: `A`
- **取消全选**: Alt + `A`
- **框选**: `B`

### 变换
- **移动**: `G`
- **旋转**: `R`
- **缩放**: `S`
- **取消操作**: `Esc` 或 右键
- **确认操作**: `Enter` 或 左键

### 约束轴
- **X轴**: 按 `X`
- **Y轴**: 按 `Y`
- **Z轴**: 按 `Z`
- **局部坐标系**: 按两次（如 `X` `X`）

### 其他
- **撤销**: Ctrl + `Z`
- **重做**: Ctrl + Shift + `Z`
- **删除**: `X` 或 `Delete`
- **复制**: Shift + `D`

## ⚠️ 重要注意事项

### 1. 不要修改mesh几何形状

如果你想修改部件的**外形**（如添加孔洞、改变形状），那是另一个流程：
1. 导出单个STL文件
2. 在Edit Mode中修改
3. 重新导出STL
4. 替换原文件

**本指南只针对修改部件的位置和旋转！**

### 2. 坐标系统

- Blender使用Z轴向上
- URDF也使用Z轴向上
- 单位都是米

### 3. 旋转顺序

URDF的RPY（Roll-Pitch-Yaw）顺序：
1. 先绕X轴旋转（Roll）
2. 再绕Y轴旋转（Pitch）
3. 最后绕Z轴旋转（Yaw）

Blender的欧拉角默认也是XYZ顺序，所以可以直接对应。

### 4. 父子关系

修改子部件的位置时，它是相对于父部件的。例如：
- `l11` 的位置是相对于 `l1` 的
- `l111` 的位置是相对于 `l11` 的

## 🔄 完整工作流程示例

假设你想调整左前腿的髋关节位置：

### 步骤1：在Blender中打开装配体
```bash
cd ~/aperfect/carbot_ws
./scripts/open_dog2_in_blender.sh
```

### 步骤2：选择并调整部件
1. 在Outliner中选择 `l11`
2. 按 `G` + `Z` + `0.01` + `Enter` （向上移动1cm）
3. 按 `R` + `Z` + `5` + `Enter` （绕Z轴旋转5度）

### 步骤3：记录新的变换值
查看Transform面板，记录：
- Location: X, Y, Z
- Rotation: X, Y, Z

### 步骤4：转换并更新URDF
1. 将旋转角度转换为弧度
2. 打开 `src/dog2_description/urdf/dog2.urdf.xacro`
3. 找到对应的joint
4. 更新 `origin` 的 `xyz` 和 `rpy` 值

### 步骤5：测试
```bash
colcon build --packages-select dog2_description
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

## 🆘 常见问题

### Q: 导入后看不到机器人？
A: 按 `Home` 键来聚焦所有对象。

### Q: 机器人看起来还是散乱的？
A: 确保你使用的是改进后的脚本。检查终端输出是否有错误。

### Q: 如何知道哪个部件是哪条腿？
A: 
- `l1` 系列 = 左前腿
- `l2` 系列 = 右前腿
- `l3` 系列 = 左后腿
- `l4` 系列 = 右后腿

### Q: 修改后URDF在Gazebo中不正常？
A: 检查：
1. 是否更新了正确的joint
2. 旋转角度是否转换为弧度
3. 是否重新编译了工作空间

### Q: 我想修改mesh的形状，不是位置？
A: 那需要不同的流程：
1. 导出单个STL
2. 在Blender中修改几何形状
3. 重新导出
4. 替换原文件
参考 `BLENDER_MODIFICATION_WORKFLOW.md`

## 📚 相关文档

- `BLENDER_MODIFICATION_WORKFLOW.md` - 修改mesh几何形状的流程
- `BLENDER_URDF_IMPORT_GUIDE.md` - 其他导入方法
- `src/dog2_description/urdf/dog2.urdf.xacro` - URDF源文件

## 🎯 总结

现在你可以：
1. ✅ 在Blender中看到完整的、正确装配的Dog2机器人
2. ✅ 在装配体环境中调整部件的位置和旋转
3. ✅ 将修改应用回URDF文件
4. ✅ 在RViz/Gazebo中验证修改

**准备好了吗？运行这个命令开始：**
```bash
cd ~/aperfect/carbot_ws
./scripts/open_dog2_in_blender.sh
```

祝你修改顺利！🚀
