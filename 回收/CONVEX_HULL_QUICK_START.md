# 🚀 凸包处理快速开始

## 一键运行（推荐）

```bash
./scripts/complete_convex_hull_workflow.sh
```

这个脚本会自动完成所有步骤：
1. ✅ 检查前置条件
2. ✅ 生成 12 个凸包文件
3. ✅ 验证凸包质量
4. ✅ 预览 URDF 修改
5. ✅ 更新 URDF 文件

**预计时间**: 3-6 分钟

---

## 分步运行

### 步骤 1: 测试单个文件（可选）
```bash
./scripts/test_single_convex_hull.sh
```

### 步骤 2: 批量生成凸包
```bash
./scripts/generate_convex_hulls.sh
```

### 步骤 3: 验证质量
```bash
python3 scripts/verify_convex_hulls.py
```

### 步骤 4: 预览 URDF 修改
```bash
python3 scripts/update_urdf_with_convex_hulls.py --dry-run
```

### 步骤 5: 应用 URDF 修改
```bash
python3 scripts/update_urdf_with_convex_hulls.py
```

---

## 测试验证

### 1. 检查生成的文件
```bash
ls -lh src/dog2_description/meshes/collision/
```

应该看到 17 个 `*_collision.STL` 文件

### 2. 验证 URDF 语法
```bash
cd src/dog2_description
xacro urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf
check_urdf /tmp/dog2_test.urdf
```

### 3. RViz 可视化
```bash
ros2 launch dog2_description view_robot.launch.py
```

在 RViz 中切换 "Collision Enabled" 查看凸包

### 4. Gazebo 测试
```bash
ros2 launch dog2_gazebo spawn_dog2.launch.py
```

观察：
- ✅ 机器人平稳落地
- ✅ 无"炸飞"现象
- ✅ 无碰撞警告

---

## 前置要求

### 必需
```bash
sudo apt install blender
```

### 可选（用于验证）
```bash
pip3 install numpy-stl
```

---

## 调整参数

编辑 `scripts/blender_batch_convex_hull.py`:

```python
# 更少面数（更快）
DECIMATE_RATIO = 0.25
TARGET_FACE_COUNT = 200

# 更多面数（更准确）
DECIMATE_RATIO = 0.45
TARGET_FACE_COUNT = 400
```

---

## 回滚

如果需要恢复原始 URDF：

```bash
# 查看备份文件
ls -lt backups/

# 恢复最新备份
cp backups/dog2.urdf.xacro.backup_YYYYMMDD_HHMMSS \
   src/dog2_description/urdf/dog2.urdf.xacro
```

---

## 故障排除

### Blender 未找到
```bash
sudo apt install blender
```

### Python 依赖缺失
```bash
pip3 install numpy-stl
```

### 某些文件处理失败
- 检查 STL 文件是否存在
- 查看错误信息
- 尝试单独处理该文件

---

## 文档

- **完整指南**: `.kiro/specs/gazebo-collision-mesh-fixes/BLENDER_CONVEX_HULL_GUIDE.md`
- **自动化说明**: `scripts/CONVEX_HULL_AUTOMATION_README.md`
- **工具总结**: `.kiro/specs/gazebo-collision-mesh-fixes/AUTOMATION_COMPLETE.md`

---

## 需要帮助？

1. 查看详细文档
2. 检查脚本输出的错误信息
3. 尝试 `--dry-run` 模式预览修改
4. 使用测试脚本验证单个文件

---

**准备好了吗？运行这个命令开始：**

```bash
./scripts/complete_convex_hull_workflow.sh
```

🎉 祝你成功！
