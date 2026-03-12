# 备份日志 - Gazebo 碰撞网格修复

## 最新备份

- **备份目录**: `backups/urdf_collision_fixes_20260129_142324`
- **时间戳**: 2026-01-29 14:23:24
- **状态**: ✓ 已完成

## 备份文件

1. `dog2.urdf.xacro` → `dog2.urdf.backup_20260129_142324.xacro`
2. `dog2.urdf` → `dog2.backup_20260129_142324.urdf`

## 恢复方法

### 方法 1: 使用恢复脚本（推荐）

```bash
python3 scripts/restore_urdf_from_backup.py urdf_collision_fixes_20260129_142324
```

### 方法 2: 手动复制

```bash
cp backups/urdf_collision_fixes_20260129_142324/dog2.urdf.backup_20260129_142324.xacro src/dog2_description/urdf/dog2.urdf.xacro
cp backups/urdf_collision_fixes_20260129_142324/dog2.backup_20260129_142324.urdf src/dog2_description/urdf/dog2.urdf
```

## 验证备份完整性

```bash
# 检查备份文件是否存在
ls -lh backups/urdf_collision_fixes_20260129_142324/

# 查看备份 README
cat backups/urdf_collision_fixes_20260129_142324/README.md
```

## 备份内容说明

此备份在应用碰撞网格修复之前创建，包含：
- 原始的 Xacro 文件（使用 STL mesh 作为碰撞几何体）
- 原始的编译后 URDF 文件

## 后续修改

备份创建后将应用以下修改：
1. 用碰撞原语（cylinder/box）替换 STL mesh 碰撞几何体
2. 截断小腿碰撞体以防止与足端重叠
3. 配置相邻 Link 的碰撞过滤
4. 调整接触参数以提高稳定性

## 相关需求

- **Requirements 10.1**: 在修改 URDF 前创建带时间戳的备份文件
