# Phobos插件安装指南 - 让Blender支持URDF导入

## 🚀 快速安装（推荐）

运行自动安装脚本：

```bash
cd ~/aperfect/carbot_ws
./scripts/install_phobos_for_blender.sh
```

这个脚本会自动：
1. ✅ 检查并安装Blender（如果需要）
2. ✅ 下载Phobos插件
3. ✅ 安装到Blender插件目录
4. ✅ 安装Python依赖
5. ✅ 测试安装是否成功

---

## 📋 手动安装步骤

如果自动脚本失败，按以下步骤手动安装：

### 1. 安装Blender
```bash
sudo snap install blender --classic
```

### 2. 下载Phobos
```bash
cd ~/Downloads
git clone https://github.com/dfki-ric/phobos.git
```

### 3. 找到Blender配置目录
```bash
# 查看Blender版本
blender --version

# Blender配置目录通常在：
# ~/.config/blender/[版本号]/scripts/addons/
# 例如：~/.config/blender/4.0/scripts/addons/
```

### 4. 安装Phobos插件

**方法A：创建符号链接（推荐）**
```bash
# 假设Blender版本是4.0
BLENDER_VERSION="4.0"
mkdir -p ~/.config/blender/${BLENDER_VERSION}/scripts/addons/
ln -s ~/Downloads/phobos/phobos ~/.config/blender/${BLENDER_VERSION}/scripts/addons/phobos
```

**方法B：在Blender中安装**
```bash
1. 打开Blender
2. Edit → Preferences (或按 F4)
3. 点击 Add-ons 标签
4. 点击右上角 Install 按钮
5. 选择 ~/Downloads/phobos/__init__.py
6. 点击 Install Add-on
```

### 5. 启用Phobos插件

在Blender中：
1. Edit → Preferences → Add-ons
2. 在搜索框输入 "phobos"
3. 勾选 "Import-Export: Phobos" 前面的复选框 ✅
4. 点击左下角 "Save Preferences" 保存

---

## ✅ 验证安装

### 检查1：查看导入菜单
1. 打开Blender
2. File → Import
3. 应该能看到 "URDF (.urdf)" 选项

### 检查2：运行测试脚本
```bash
blender --background --python ~/Downloads/test_phobos.py
```

应该看到：
```
✅ Phobos模块导入成功
✅ URDF导入功能可用
```

---

## 🎯 使用Phobos导入URDF

### 导入你的Dog2机器人

1. **打开Blender**
```bash
blender
```

2. **删除默认场景**
   - 选中默认的立方体、灯光、相机
   - 按 `X` → Delete

3. **导入URDF**
   - File → Import → URDF (.urdf)
   - 导航到：`~/aperfect/carbot_ws/src/dog2_description/urdf/`
   - 选择 `dog2.urdf`
   - 点击 Import

4. **查看机器人**
   - 使用鼠标中键旋转视图
   - 使用滚轮缩放
   - 你应该能看到完整的四足机器人装配体

---

## 🔧 常见问题

### 问题1：找不到URDF导入选项

**原因：** Phobos插件未启用

**解决：**
```bash
1. Edit → Preferences → Add-ons
2. 搜索 "phobos"
3. 确保复选框已勾选 ✅
4. 保存设置
```

### 问题2：导入URDF时报错 "No module named 'yaml'"

**原因：** 缺少Python依赖

**解决：**
```bash
# 找到Blender的Python路径
blender --background --python-expr "import sys; print(sys.executable)"

# 使用该Python安装依赖（替换下面的路径）
/snap/blender/current/4.0/python/bin/python3.10 -m pip install pyyaml numpy
```

### 问题3：导入URDF后看不到模型

**原因：** STL文件路径问题

**解决：**
```bash
# 确保URDF中的mesh路径正确
# 检查文件是否存在
ls -lh src/dog2_description/meshes/*.STL

# 如果路径是相对路径，可能需要在Blender中设置工作目录
```

### 问题4：Phobos版本不兼容

**原因：** Phobos可能不支持你的Blender版本

**解决：**
```bash
# 尝试使用特定版本的Phobos
cd ~/Downloads/phobos
git checkout v2.0.0  # 或其他稳定版本
```

---

## 🆘 如果还是装不上

### 备选方案1：使用COLLADA格式

```bash
# 安装转换工具
sudo apt-get install ros-humble-collada-urdf

# 转换URDF到COLLADA
cd ~/aperfect/carbot_ws
rosrun collada_urdf urdf_to_collada \
  src/dog2_description/urdf/dog2.urdf \
  dog2.dae

# 在Blender中导入COLLADA
# File → Import → Collada (.dae)
```

### 备选方案2：使用Python脚本批量导入STL

我已经在 `BLENDER_MODIFICATION_WORKFLOW.md` 中提供了详细的脚本。

---

## 📚 参考资源

- Phobos GitHub: https://github.com/dfki-ric/phobos
- Phobos文档: https://github.com/dfki-ric/phobos/wiki
- Blender插件安装: https://docs.blender.org/manual/en/latest/editors/preferences/addons.html

---

## 🎉 安装成功后

你就可以：
1. ✅ 在Blender中打开完整的机器人装配体
2. ✅ 看到所有关节和连接关系
3. ✅ 修改任何部件
4. ✅ 导出回URDF格式
5. ✅ 在ROS2/Gazebo中测试

**准备好了吗？** 运行安装脚本开始吧：
```bash
./scripts/install_phobos_for_blender.sh
```
