#!/usr/bin/env python3
"""
恢复 URDF 文件从备份

此脚本从指定的备份目录恢复 URDF 文件

用法:
    python scripts/restore_urdf_from_backup.py <backup_dir_name>
    
示例:
    python scripts/restore_urdf_from_backup.py urdf_collision_fixes_20260129_142324
"""

import os
import sys
import shutil
from pathlib import Path


def restore_urdf_from_backup(backup_dir_name):
    """
    从备份目录恢复 URDF 文件
    
    Args:
        backup_dir_name: 备份目录名称（不含完整路径）
    
    Returns:
        bool: 恢复是否成功
    """
    workspace_root = Path(__file__).parent.parent
    backup_dir = workspace_root / "backups" / backup_dir_name
    urdf_dir = workspace_root / "src" / "dog2_description" / "urdf"
    
    # 检查备份目录是否存在
    if not backup_dir.exists():
        print(f"❌ 错误: 备份目录不存在: {backup_dir}")
        return False
    
    print(f"从备份恢复 URDF 文件...")
    print(f"备份目录: {backup_dir}")
    print(f"目标目录: {urdf_dir}\n")
    
    # 查找备份文件
    backup_files = list(backup_dir.glob("*.xacro")) + list(backup_dir.glob("*.urdf"))
    
    if not backup_files:
        print(f"❌ 错误: 在备份目录中未找到 URDF 文件")
        return False
    
    # 恢复文件
    restored_count = 0
    for backup_file in backup_files:
        # 确定目标文件名
        if backup_file.suffix == '.xacro':
            target_name = "dog2.urdf.xacro"
        elif backup_file.suffix == '.urdf':
            target_name = "dog2.urdf"
        else:
            continue
        
        target_path = urdf_dir / target_name
        
        # 在覆盖前创建当前文件的临时备份
        if target_path.exists():
            temp_backup = target_path.with_suffix(target_path.suffix + '.pre-restore')
            shutil.copy2(target_path, temp_backup)
            print(f"📋 创建临时备份: {temp_backup.name}")
        
        # 恢复文件
        shutil.copy2(backup_file, target_path)
        print(f"✓ 恢复: {backup_file.name} -> {target_name}")
        restored_count += 1
    
    print(f"\n{'='*60}")
    print(f"恢复完成！已恢复 {restored_count} 个文件")
    print(f"{'='*60}\n")
    
    return True


def list_available_backups():
    """列出所有可用的备份目录"""
    workspace_root = Path(__file__).parent.parent
    backups_dir = workspace_root / "backups"
    
    if not backups_dir.exists():
        print("未找到备份目录")
        return []
    
    backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir()]
    backup_dirs.sort(reverse=True)  # 最新的在前
    
    return backup_dirs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/restore_urdf_from_backup.py <backup_dir_name>")
        print("\n可用的备份目录:")
        
        backups = list_available_backups()
        if backups:
            for i, backup_dir in enumerate(backups, 1):
                print(f"  {i}. {backup_dir.name}")
        else:
            print("  (无可用备份)")
        
        sys.exit(1)
    
    backup_dir_name = sys.argv[1]
    success = restore_urdf_from_backup(backup_dir_name)
    
    sys.exit(0 if success else 1)
