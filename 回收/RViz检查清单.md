# RViz2 检查清单 - L1旋转后验证

## ✅ 在RViz2中检查以下内容

### 1. L1部件显示
- [ ] L1部件是否正确显示（没有缺失）
- [ ] Mesh是否完整（没有孔洞或破损）
- [ ] 颜色/材质是否正常

### 2. 旋转效果
- [ ] L1的方向是否符合你的预期
- [ ] 旋转角度是否正确
- [ ] 部件朝向是否合理

### 3. 与其他部件的连接
- [ ] L1与l11（上一级）的连接是否正常
- [ ] L1与l111（下一级）的连接是否正常
- [ ] 关节位置是否正确
- [ ] 没有明显的间隙或重叠

### 4. 整体结构
- [ ] 机器人整体结构是否完整
- [ ] 四条腿的L1部件是否一致
- [ ] TF树是否正常（没有错误）

### 5. 视觉检查
- [ ] 从不同角度查看（前、后、左、右、上、下）
- [ ] 放大查看细节
- [ ] 检查是否有翻转的面（法向量错误）

---

## 🔧 如果发现问题

### 问题1：L1方向不对
**解决方案：**
```bash
# 重新在Blender中调整旋转角度
blender src/dog2_description/meshes/l1_upper.STL \
        src/dog2_description/meshes/l1_lower.STL

# 调整旋转角度后重新合并和导出
```

### 问题2：L1与其他部件连接有间隙
**可能原因：**
- 旋转后位置偏移
- 原点位置改变

**解决方案：**
```bash
# 在Blender中检查原点位置
# Object → Set Origin → Origin to Geometry
```

### 问题3：Mesh有孔洞或不连续
**可能原因：**
- 合并时没有合并重复顶点

**解决方案：**
```bash
# 在Blender中重新打开untitled.stl
blender src/dog2_description/meshes/untitled.stl

# 在编辑模式中：
# Tab → A（全选）→ M → "按距离"
# 重新导出
```

### 问题4：面的法向量翻转（显示为黑色）
**解决方案：**
```bash
# 在Blender中：
# Tab → A（全选）→ Shift+N（重新计算法向量）
# 或者：Mesh → Normals → Recalculate Outside
```

---

## 📊 对比检查

### 原始L1 vs 新L1

| 项目 | 原始L1 | 新L1 | 状态 |
|------|--------|------|------|
| 文件大小 | 78K | 80K | ✓ 相近 |
| 方向 | 原始方向 | 旋转后 | 待确认 |
| 连接 | 正常 | ? | 待确认 |
| 完整性 | 完整 | ? | 待确认 |

---

## 🎯 验证通过标准

当以下所有项都满足时，说明替换成功：

1. ✅ L1部件完整显示，没有缺失
2. ✅ 旋转方向符合设计意图
3. ✅ 与相邻部件（l11、l111）连接正常
4. ✅ 没有明显的mesh错误
5. ✅ 四条腿的L1部件显示一致
6. ✅ TF树没有错误或警告

---

## 📸 建议截图保存

从以下角度截图保存，方便对比：
1. 正面视图
2. 侧面视图
3. 顶视图
4. 放大L1部件的细节视图

---

## 🚀 下一步测试

如果RViz2中显示正常，继续在Gazebo中测试：

```bash
source install/setup.bash
./start_gazebo_with_dog2.sh
```

在Gazebo中检查：
- [ ] 物理仿真是否稳定
- [ ] 碰撞检测是否正常
- [ ] 关节运动是否受影响
- [ ] 机器人能否正常站立

---

## 💡 快速命令

### 重新启动RViz2
```bash
# 关闭当前RViz2
pkill -9 rviz2

# 重新启动
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

### 查看TF树
```bash
ros2 run tf2_tools view_frames
evince frames.pdf
```

### 恢复原始L1（如果需要）
```bash
cp src/dog2_description/meshes/l1.STL.before_rotation src/dog2_description/meshes/l1.STL
colcon build --packages-select dog2_description
source install/setup.bash
```

---

## 📝 记录结果

请在下方记录检查结果：

```
检查时间：____________________

L1显示：□ 正常  □ 有问题
旋转方向：□ 正确  □ 需要调整
连接状态：□ 正常  □ 有间隙
整体结构：□ 完整  □ 有缺失

问题描述：
_________________________________
_________________________________
_________________________________

是否需要调整：□ 是  □ 否
```

---

祝检查顺利！🎉
