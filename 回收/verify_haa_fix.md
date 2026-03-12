# HAA 关节修复验证

## 修复内容

将 Leg 1 和 Leg 2 的 HAA 轴从 `"0 0 1"` 改为 `"0 -1 0"`

## 原理

1. **Prismatic joint** 有 `rpy="1.5708 0 0"` (绕 x 轴旋转 90°)
2. 这导致坐标系旋转：
   - 原来的 Y 轴 → 现在的 Z 轴
   - 原来的 Z 轴 → 现在的 -Y 轴
3. 所以 HAA 使用 `-Y 轴`，旋转后会指向世界坐标系的 `Z 轴`（垂直方向）

## 理论验证

运行 `python3 test_new_axis.py`：
- ✅ HAA 轴指向 Z 轴（垂直方向）
- ✅ HAA 和 HFE 垂直（90°）

## 实际测试

### 方法 1: RViz 手动测试

```bash
./start_champ_rviz_test.sh
```

在 joint_state_publisher_gui 中：
1. 找到 `lf_haa_joint`
2. 移动滑块
3. **预期**：腿部应该左右摆动（外展/内收）

### 方法 2: 自动化测试

```bash
./test_haa_abduction.sh
```

## 可能的问题

### 初始位置错误

如果 Leg 1 和 Leg 2 的初始位置看起来不对，这是因为：
- 改变轴方向后，零位姿态也改变了
- 可能需要调整 HAA 关节的初始位置

### 解决方案

如果初始位置有问题，可以：
1. 在 leg macro 中添加 `hip_initial_position` 参数
2. 或者调整 HAA 关节的 origin xyz

## 下一步

如果这个方案仍然不work，我们需要考虑更彻底的方案：
- 移除 prismatic joint 的 RPY 旋转
- 重新计算所有关节的 origin 和 axis
