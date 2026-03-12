# 🎉 凸包自动化工具已就绪！

## 📦 已创建的工具

我已经为你创建了一套完整的自动化工具，可以批量处理所有 STL 文件生成凸包：

### 1. 核心处理脚本
- **`scripts/blender_batch_convex_hull.py`** - Blender Python 脚本
  - 自动导入 STL
  - 生成凸包
  - 智能简化网格
  - 清理和优化
  - 导出为 `_collision.STL`

### 2. 便捷包装脚本
- **`scripts/generate_convex_hulls.sh`** - 一键运行工具
  - 检查 Blender 安装
  - 显示待处理文件
  - 批量处理所有文件
  - 彩色输出和进度显示

### 3. 质量验证工具
- **`scripts/verify_convex_hulls.py`** - 验证生成的凸包
  - 检查面数是否合理
  - 对比体积差异
  - 验证文件完整性
  - 生成质量报告

### 4. 测试工具
- **`scripts/test_single_convex_hull.sh`** - 单文件测试
  - 在批量处理前测试流程
  - 快速验证参数设置

### 5. 使用文档
- **`scripts/CONVEX_HULL_AUTOMATION_README.md`** - 详细使用说明
- **`.kiro/specs/gazebo-collision-mesh-fixes/BLENDER_CONVEX_HULL_GUIDE.md`** - 完整指南

## 🚀 快速开始

### 方案 A：一键批量处理（推荐）

```bash
# 1. 运行批量处理
./scripts/generate_convex_hulls.sh

# 2. 验证质量
python3 scripts/verify_convex_hulls.py

# 3. 检查生成的文件
ls -lh src/dog2_description/meshes/collision/
```

### 方案 B：先测试单个文件

```bash
# 1. 测试单个文件（默认 l111.STL）
./scripts/test_single_convex_hull.sh

# 2. 或指定其他文件
./scripts/test_single_convex_hull.sh l211.STL

# 3. 如果满意，运行完整批量处理
./scripts/generate_convex_hulls.sh
```

## 📋 处理的文件列表

脚本会自动处理以下 17 个文件：

```
基座:
  base_link.STL → base_link_collision.STL

第1条腿:
  l1.STL     → l1_collision.STL     (髋关节)
  l11.STL    → l11_collision.STL    (大腿上段)
  l111.STL   → l111_collision.STL   (大腿下段)
  l1111.STL  → l1111_collision.STL  (小腿)

第2条腿:
  l2.STL     → l2_collision.STL
  l21.STL    → l21_collision.STL
  l211.STL   → l211_collision.STL
  l2111.STL  → l2111_collision.STL

第3条腿:
  l3.STL     → l3_collision.STL
  l31.STL    → l31_collision.STL
  l311.STL   → l311_collision.STL
  l3111.STL  → l3111_collision.STL

第4条腿:
  l4.STL     → l4_collision.STL
  l41.STL    → l41_collision.STL
  l411.STL   → l411_collision.STL
  l4111.STL  → l4111_collision.STL
```

## ⚙️ 默认参数

```python
DECIMATE_RATIO = 0.35      # 保留 35% 的面
TARGET_FACE_COUNT = 300    # 目标面数
```

这些参数在 `scripts/blender_batch_convex_hull.py` 中可以调整。

## 🎯 预期结果

成功运行后：

✅ **17 个凸包文件** 生成到 `meshes/collision/` 目录  
✅ **面数优化** 到 100-500 面范围  
✅ **文件大小** 显著减小（通常减少 60-80%）  
✅ **体积差异** 控制在 30% 以内  
✅ **质量验证** 通过所有检查  

## 📊 示例输出

```
============================================================
处理文件: l111.STL
============================================================
  ✓ 场景已清空
  ✓ 已导入: l111.STL
  原始网格: 2456 顶点, 4912 面
  尺寸: 0.045 x 0.035 x 0.180 m
  ✓ 凸包已生成，面数: 856
  ✓ 网格已简化: 856 → 299 面 (65.1% 减少)
  ✓ 网格已清理
  最终网格: 152 顶点, 299 面
  ✓ 已导出: l111_collision.STL (15.2 KB)
✅ 成功处理: l111.STL
```

## 🔧 调整参数

如果需要调整凸包质量，编辑 `scripts/blender_batch_convex_hull.py`：

### 更少面数（更快，精度稍低）
```python
DECIMATE_RATIO = 0.25
TARGET_FACE_COUNT = 200
```

### 更多面数（更准确，文件稍大）
```python
DECIMATE_RATIO = 0.45
TARGET_FACE_COUNT = 400
```

## 📝 下一步：更新 URDF

凸包生成完成后，需要更新 URDF 文件。我可以帮你：

1. **自动更新 URDF** - 创建脚本自动修改 collision mesh 路径
2. **手动更新** - 按照指南手动修改
3. **验证配置** - 在 RViz 和 Gazebo 中测试

你想要哪种方式？

## 🎓 学习资源

- **完整指南**: `.kiro/specs/gazebo-collision-mesh-fixes/BLENDER_CONVEX_HULL_GUIDE.md`
- **使用说明**: `scripts/CONVEX_HULL_AUTOMATION_README.md`
- **Blender 文档**: https://docs.blender.org/manual/en/latest/

## 💡 提示

1. **首次运行建议先测试单个文件**
2. **检查 Blender 版本**（需要 2.8+）
3. **保留原始 STL 文件**作为备份
4. **验证质量**后再更新 URDF
5. **在 RViz 中可视化**检查凸包是否合理

## 🐛 故障排除

### Blender 未找到
```bash
sudo apt install blender
# 或从官网下载: https://www.blender.org/download/
```

### Python 依赖缺失
```bash
pip3 install numpy-stl
```

### 某些文件处理失败
- 检查 STL 文件是否存在
- 查看错误信息
- 尝试手动在 Blender 中打开该文件

## ✅ 准备好了吗？

现在你可以：

1. **运行测试**: `./scripts/test_single_convex_hull.sh`
2. **批量处理**: `./scripts/generate_convex_hulls.sh`
3. **验证质量**: `python3 scripts/verify_convex_hulls.py`

需要我帮你运行吗？或者你想先自己试试看？
