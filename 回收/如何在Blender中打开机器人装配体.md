# 如何在Blender中打开Dog2机器人完整装配体

## 🎯 问题解决

你之前遇到的问题：
- ❌ Phobos插件 - numpy兼容性错误
- ❌ 旧的导入脚本 - 部件位置不正确

## ✅ 解决方案

我已经创建了**改进版的导入脚本**，它能正确处理URDF的变换矩阵，显示完整的、正确装配的机器人。

## 🚀 快速开始

### 一键启动（推荐）

```bash
cd ~/aperfect/carbot_ws
./test_blender_import.sh
```

这个脚本会：
1. 检查所有必需文件
2. 自动启动Blender
3. 导入完整的机器人装配体

### 或者直接运行

```bash
cd ~/aperfect/carbot_ws
./scripts/open_dog2_in_blender.sh
```

## 📋 导入后你会看到

✅ **完整的机器人装配体**，所有部件都在正确的位置：
- 机身（base_link）
- 4条腿，每条腿包含：
  - 髋关节滑轨
  - 髋关节
  - 大腿
  - 小腿
  - 球形脚

✅ **正确的层级关系**，在Outliner面板中可以看到父子结构

## 🔧 如何修改部件位置

### 1. 选择部件
- 在3D视图中点击部件
- 或在右侧Outliner面板中选择

### 2. 移动/旋转
- 按 `G` = 移动
- 按 `R` = 旋转
- 按 `G` + `X`/`Y`/`Z` = 沿特定轴移动
- 按 `R` + `X`/`Y`/`Z` = 绕特定轴旋转

### 3. 精确输入
- `G` + `X` + `0.05` + `Enter` = 沿X轴移动0.05米
- `R` + `Z` + `90` + `Enter` = 绕Z轴旋转90度

### 4. 查看变换值
选中部件后，在右侧Properties面板查看：
- Location (位置): X, Y, Z
- Rotation (旋转): X, Y, Z

### 5. 更新到URDF
1. 记录Blender中的变换值
2. 将旋转角度转换为弧度（度 × π / 180）
3. 打开 `src/dog2_description/urdf/dog2.urdf.xacro`
4. 找到对应的joint，更新 `origin` 的 `xyz` 和 `rpy` 值
5. 重新编译：
```bash
colcon build --packages-select dog2_description
source install/setup.bash
```

## 📚 详细文档

查看 `BLENDER_导入完整装配体指南.md` 获取：
- 详细的使用说明
- Blender快捷键
- 完整的工作流程示例
- 常见问题解答

## 🎨 Blender基本操作

### 视图控制
- **旋转**: 鼠标中键拖动
- **缩放**: 鼠标滚轮
- **平移**: Shift + 鼠标中键
- **聚焦**: `Home` 键

### 变换操作
- **移动**: `G`
- **旋转**: `R`
- **缩放**: `S`
- **取消**: `Esc`
- **确认**: `Enter`

### 选择
- **单选**: 左键点击
- **多选**: Shift + 左键
- **全选**: `A`

## ⚠️ 重要提示

1. **不要进入Edit Mode** - 我们只修改位置/旋转，不修改mesh形状
2. **单位是米** - Blender和URDF都使用米作为单位
3. **角度转换** - Blender显示度，URDF使用弧度
4. **相对坐标** - 子部件的位置是相对于父部件的

## 🆘 遇到问题？

### 看不到机器人？
按 `Home` 键聚焦所有对象

### 部件还是散乱的？
确保使用的是改进后的脚本（我刚刚更新的）

### Blender未安装？
```bash
sudo snap install blender --classic
```

## 🎯 现在就试试！

```bash
cd ~/aperfect/carbot_ws
./test_blender_import.sh
```

等待Blender打开，你会看到完整的、正确装配的Dog2机器人！🚀
