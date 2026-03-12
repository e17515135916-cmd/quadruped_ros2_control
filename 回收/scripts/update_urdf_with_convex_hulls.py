#!/usr/bin/env python3
"""
自动更新 URDF 文件，使用凸包碰撞网格

使用方法：
    python3 scripts/update_urdf_with_convex_hulls.py [--dry-run]
    
选项：
    --dry-run    只显示将要做的修改，不实际修改文件
"""

import os
import sys
import re
import argparse
from datetime import datetime


# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
URDF_FILE = os.path.join(PROJECT_ROOT, "src/dog2_description/urdf/dog2.urdf.xacro")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups")

# 需要更新的 Link 名称模式
LINK_PATTERNS = [
    r'base_link',    # 基座
    r'l[1-4]',       # l1, l2, l3, l4 (髋关节)
    r'l[1-4]1',      # l11, l21, l31, l41
    r'l[1-4]11',     # l111, l211, l311, l411
    r'l[1-4]111',    # l1111, l2111, l3111, l4111
]


def backup_file(filepath):
    """备份文件"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"dog2.urdf.xacro.backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    print(f"✓ 已备份到: {backup_path}")
    return backup_path


def should_update_link(link_name):
    """检查是否应该更新这个 Link"""
    for pattern in LINK_PATTERNS:
        if re.fullmatch(pattern, link_name):
            return True
    return False


def update_collision_mesh(content, dry_run=False):
    """更新 collision mesh 路径"""
    
    # 正则表达式匹配 collision 标签中的 mesh
    # 匹配模式：<mesh filename="..." scale="..."/>
    pattern = r'(<collision[^>]*>.*?<geometry>.*?<mesh\s+filename="package://dog2_description/meshes/)(l[1-4]1{1,3})(\.STL)"(?:\s+scale="[^"]*")?(\s*/?>.*?</geometry>.*?</collision>)'
    
    modifications = []
    
    def replacer(match):
        full_match = match.group(0)
        prefix = match.group(1)
        link_base = match.group(2)
        extension = match.group(3)
        suffix = match.group(4)
        
        # 检查是否应该更新这个 Link
        if not should_update_link(link_base):
            return full_match
        
        # 构建新的路径（使用 collision 子目录）
        new_path = f'{prefix}collision/{link_base}_collision{extension}"{suffix}'
        
        # 记录修改
        old_filename = f"{link_base}{extension}"
        new_filename = f"collision/{link_base}_collision{extension}"
        modifications.append((old_filename, new_filename))
        
        return new_path
    
    # 执行替换
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    return new_content, modifications


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='更新 URDF 文件使用凸包碰撞网格')
    parser.add_argument('--dry-run', action='store_true', help='只显示修改，不实际修改文件')
    args = parser.parse_args()
    
    print("="*60)
    print("URDF 凸包路径更新工具")
    print("="*60)
    print(f"URDF 文件: {URDF_FILE}")
    print(f"模式: {'预览模式 (不修改文件)' if args.dry_run else '修改模式'}")
    print("="*60)
    
    # 检查文件存在
    if not os.path.exists(URDF_FILE):
        print(f"\n❌ 错误: URDF 文件不存在")
        print(f"   {URDF_FILE}")
        return 1
    
    # 读取文件
    print("\n读取 URDF 文件...")
    with open(URDF_FILE, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 更新内容
    print("分析和更新 collision mesh 路径...")
    new_content, modifications = update_collision_mesh(original_content, args.dry_run)
    
    # 显示修改
    if modifications:
        print(f"\n找到 {len(modifications)} 处需要更新:")
        print("-" * 60)
        for old, new in modifications:
            print(f"  {old}")
            print(f"  → {new}")
            print()
    else:
        print("\n⚠️  未找到需要更新的 collision mesh")
        print("   可能已经更新过，或者文件格式不匹配")
        return 0
    
    # 如果是 dry-run，到此结束
    if args.dry_run:
        print("="*60)
        print("预览完成（未修改文件）")
        print("="*60)
        print("\n要实际应用修改，运行:")
        print("  python3 scripts/update_urdf_with_convex_hulls.py")
        return 0
    
    # 询问确认
    print("="*60)
    response = input("确认应用这些修改? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return 0
    
    # 备份原文件
    print("\n备份原文件...")
    backup_path = backup_file(URDF_FILE)
    
    # 写入新内容
    print("更新 URDF 文件...")
    with open(URDF_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n" + "="*60)
    print("✅ 更新完成！")
    print("="*60)
    print(f"修改数量: {len(modifications)}")
    print(f"备份位置: {backup_path}")
    print("\n下一步:")
    print("  1. 验证 URDF 语法: xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/test.urdf")
    print("  2. RViz 可视化: ros2 launch dog2_description view_robot.launch.py")
    print("  3. Gazebo 测试: ros2 launch dog2_gazebo spawn_dog2.launch.py")
    print("\n如需回滚:")
    print(f"  cp {backup_path} {URDF_FILE}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
