# Back2.1 备份目录

## 目录说明

这个目录包含 Dog2 机器人的多个配置版本备份。

## 备份内容

### 1. dog3_description
- **说明**: Dog2 的早期版本配置
- **特点**: 包含基础的 URDF 配置和 mesh 文件
- **创建时间**: 2026-01-28

### 2. dog4_description_20260207_194926
- **说明**: Dog2 的 CHAMP 框架兼容版本（完整备份）
- **特点**: 
  - ✅ CHAMP 标准关节命名 (HAA/HFE/KFE)
  - ✅ 正确的关节轴向配置 (1Y + 2X)
  - ✅ 保留滑动副设计
  - ✅ 完整的测试和验证脚本
  - ✅ 详细的文档
- **创建时间**: 2026-02-07 19:49

### 3. dog4_description (符号链接)
- **说明**: 指向 dog4_description_20260207_194926 的符号链接
- **用途**: 方便快速访问最新的 dog4 配置

## 版本对比

| 特性 | dog3 | dog4 (CHAMP) |
|------|------|--------------|
| 关节命名 | j11, j111, j1111 | lf_haa_joint, lf_hfe_joint, lf_kfe_joint |
| HAA 轴向 | X轴 | ✅ Y轴 (CHAMP 标准) |
| 连杆命名 | l11, l111, l1111 | lf_hip_link, lf_upper_leg_link, lf_lower_leg_link |
| CHAMP 兼容 | ❌ | ✅ |
| 滑动副 | ✅ | ✅ |
| 测试脚本 | 部分 | ✅ 完整 |
| 文档 | 基础 | ✅ 详细 |

## 使用建议

### 使用 dog4 (CHAMP 兼容版本)

```bash
# 进入 dog4 目录
cd backups/back2.1/dog4_description

# 查看使用说明
cat README.md

# 测试 RViz2
./quick_test_rviz.sh

# 验证关节配置
python3 verify_champ_axis_config.py
```

### 恢复到工作空间

```bash
# 恢复 dog4 配置
cp -r backups/back2.1/dog4_description/dog2_description src/

# 或恢复 dog3 配置
cp -r backups/back2.1/dog3_description src/

# 编译
colcon build --packages-select dog2_description
source install/setup.bash
```

## 推荐配置

🎯 **推荐使用 dog4_description**

原因：
- ✅ 符合 CHAMP 框架标准
- ✅ 可以与 CHAMP 控制器集成
- ✅ 关节轴向配置正确
- ✅ 包含完整的测试和验证
- ✅ 保留了 Dog2 的独特滑动副设计

## 目录结构

```
back2.1/
├── dog3_description/              # 早期版本
│   ├── urdf/
│   ├── meshes/
│   ├── config/
│   ├── launch/
│   ├── rviz/
│   ├── scripts/
│   └── test/
│
├── dog4_description_20260207_194926/  # CHAMP 兼容版本（完整）
│   ├── dog2_description/          # ROS 2 包
│   │   ├── urdf/
│   │   │   └── dog2.urdf.xacro   # ⭐ CHAMP 兼容 URDF
│   │   ├── meshes/
│   │   └── config/
│   ├── specs/                     # 规范文档
│   ├── quick_test_rviz.sh        # ⭐ 测试脚本
│   ├── verify_champ_axis_config.py  # ⭐ 验证脚本
│   ├── README.md                 # 使用说明
│   ├── BACKUP_INFO.md
│   └── CHAMP_COMPLIANCE_SUMMARY.md
│
├── dog4_description -> dog4_description_20260207_194926/  # 符号链接
│
└── README.md                      # 本文件
```

## 备份历史

- **2026-01-28**: 创建 dog3_description 备份
- **2026-02-07**: 创建 dog4_description CHAMP 兼容配置
  - 修正 HAA 关节轴向为 Y 轴
  - 重命名所有关节和连杆为 CHAMP 标准
  - 添加完整的测试和验证脚本
  - 创建详细的文档

## 快速链接

- **Dog4 使用说明**: `dog4_description/README.md`
- **Dog4 备份信息**: `dog4_description/BACKUP_INFO.md`
- **CHAMP 兼容性总结**: `dog4_description/CHAMP_COMPLIANCE_SUMMARY.md`
- **规范文档**: `dog4_description/specs/champ-compliant-joint-configuration/`

## 注意事项

1. **不要直接修改备份文件** - 如需修改，先复制到工作目录
2. **保持备份完整性** - 不要删除或移动备份中的文件
3. **定期验证备份** - 确保备份文件可以正常使用
4. **记录修改历史** - 如果创建新版本，更新本文档

## 支持

如有问题，请参考：
- Dog4 README: `dog4_description/README.md`
- CHAMP 框架: https://github.com/chvmp/champ
- ROS 2 文档: https://docs.ros.org/en/humble/
