# 凸包自动化处理工具使用说明

## 📦 工具概述

这套工具可以自动将所有腿部 STL 文件转换为优化的凸包碰撞网格，彻底解决 Gazebo 仿真中的"量子爆炸"问题。

## 🛠️ 工具列表

1. **blender_batch_convex_hull.py** - Blender Python 脚本，批量处理 STL 文件
2. **generate_convex_hulls.sh** - Shell 包装脚本，方便运行
3. **verify_convex_hulls.py** - 验证脚本，检查生成的凸包质量

## 📋 前置要求

### 1. 安装 Blender

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install blender

# 验证安装
blender --version
```

### 2. 安装 Python 依赖（用于验证）

```bash
pip3 install numpy-stl
```

## 🚀 使用步骤

### 步骤 1：生成凸包文件

运行自动化脚本：

```bash
cd ~/aperfect/carbot_ws
./scripts/generate_convex_hulls.sh
```

脚本会：
- ✅ 检查 Blender 是否安装
- ✅ 显示待处理的文件列表
- ✅ 询问确认后开始处理
- ✅ 批量处理所有 12 个 STL 文件
- ✅ 生成凸包文件到 `meshes/collision/` 目录

**预计时间**: 2-5 分钟（取决于电脑性能）

### 步骤 2：验证凸包质量

```bash
python3 scripts/verify_convex_hulls.py
```

验证脚本会检查：
- ✅ 面数是否在合理范围（50-500 面）
- ✅ 体积差异是否小于 30%
- ✅ 文件大小是否合理
- ✅ 所有文件是否都已生成

### 步骤 3：检查生成的文件

```bash
ls -lh src/dog2_description/meshes/collision/
```

你应该看到：
```
l11_collision.STL
l111_collision.STL
l1111_collision.STL
l21_collision.STL
l211_collision.STL
l2111_collision.STL
l31_collision.STL
l311_collision.STL
l3111_collision.STL
l41_collision.STL
l411_collision.STL
l4111_collision.STL
```

## ⚙️ 配置参数

如果需要调整凸包质量，编辑 `scripts/blender_batch_convex_hull.py`：

```python
# 凸包处理参数
DECIMATE_RATIO = 0.35      # 保留 35% 的面（可调整：0.2-0.5）
TARGET_FACE_COUNT = 300    # 目标面数
```

- **DECIMATE_RATIO 越小** → 面数越少 → 文件越小 → 精度越低
- **DECIMATE_RATIO 越大** → 面数越多 → 文件越大 → 精度越高

**推荐值**:
- 快速测试: `0.25` (更少面数，更快)
- 平衡: `0.35` (默认)
- 高精度: `0.45` (更多面数，更准确)

## 🔧 故障排除

### 问题 1: "未找到 Blender"

```bash
# 检查 Blender 是否在 PATH 中
which blender

# 如果没有，手动指定路径
/path/to/blender --background --python scripts/blender_batch_convex_hull.py
```

### 问题 2: 某些文件处理失败

检查错误信息，常见原因：
- STL 文件损坏
- 文件路径不正确
- Blender 版本太旧（需要 2.8+）

### 问题 3: 凸包面数太多

调整 `DECIMATE_RATIO` 参数，降低到 `0.25` 或 `0.2`，然后重新运行。

### 问题 4: 凸包体积差异太大

这通常是正常的，因为凸包会"包裹"原始模型。只要差异 < 30% 就可以接受。

## 📊 输出示例

成功运行后，你会看到类似输出：

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

## 🎯 下一步

凸包生成完成后：

1. **更新 URDF 文件** - 修改 collision mesh 路径
2. **RViz 可视化** - 检查凸包是否合理
3. **Gazebo 测试** - 验证稳定性

详细步骤请参考主指南：
`.kiro/specs/gazebo-collision-mesh-fixes/BLENDER_CONVEX_HULL_GUIDE.md`

## 💡 提示

- 第一次运行建议先处理 1-2 个文件测试
- 可以在 Blender GUI 中手动检查生成的凸包
- 如果不满意，调整参数后重新生成
- 保留原始 STL 文件作为备份

## 📞 需要帮助？

如果遇到问题：
1. 检查 Blender 版本（需要 2.8+）
2. 查看脚本输出的错误信息
3. 尝试手动在 Blender 中处理一个文件
4. 调整配置参数后重试
