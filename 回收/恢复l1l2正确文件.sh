#!/bin/bash

# 恢复L1和L2的正确mesh文件
# 从backups/back2.1恢复原始正确版本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  恢复L1和L2正确Mesh文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

MESH_DIR="src/dog2_description/meshes"
BACKUP_SOURCE="backups/back2.1/dog3_description/meshes"

# 检查备份文件是否存在
if [ ! -f "$BACKUP_SOURCE/l1.STL" ] || [ ! -f "$BACKUP_SOURCE/l2.STL" ]; then
    echo "❌ 错误：备份文件不存在！"
    echo "   备份目录：$BACKUP_SOURCE"
    exit 1
fi

echo "📋 当前文件状态："
echo ""
echo "l1.STL:"
echo "  当前: $(md5sum $MESH_DIR/l1.STL | cut -d' ' -f1)"
echo "  备份: $(md5sum $BACKUP_SOURCE/l1.STL | cut -d' ' -f1)"
echo ""
echo "l2.STL:"
echo "  当前: $(md5sum $MESH_DIR/l2.STL | cut -d' ' -f1)"
echo "  备份: $(md5sum $BACKUP_SOURCE/l2.STL | cut -d' ' -f1)"
echo ""

# 检查文件是否已经是正确的
l1_current=$(md5sum $MESH_DIR/l1.STL | cut -d' ' -f1)
l1_backup=$(md5sum $BACKUP_SOURCE/l1.STL | cut -d' ' -f1)
l2_current=$(md5sum $MESH_DIR/l2.STL | cut -d' ' -f1)
l2_backup=$(md5sum $BACKUP_SOURCE/l2.STL | cut -d' ' -f1)

if [ "$l1_current" = "$l1_backup" ] && [ "$l2_current" = "$l2_backup" ]; then
    echo "✅ 文件已经是正确版本，无需恢复！"
    exit 0
fi

echo "⚠️  文件不匹配，需要恢复"
echo ""
read -p "是否继续恢复？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消恢复操作"
    exit 0
fi

echo ""
echo "🔄 正在恢复mesh文件..."

# 创建当前文件的备份（以防万一）
CURRENT_BACKUP_DIR="backups/mesh_before_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CURRENT_BACKUP_DIR"
cp "$MESH_DIR/l1.STL" "$CURRENT_BACKUP_DIR/" 2>/dev/null
cp "$MESH_DIR/l2.STL" "$CURRENT_BACKUP_DIR/" 2>/dev/null
echo "✓ 当前文件已备份到：$CURRENT_BACKUP_DIR"

# 恢复文件
cp "$BACKUP_SOURCE/l1.STL" "$MESH_DIR/l1.STL"
cp "$BACKUP_SOURCE/l2.STL" "$MESH_DIR/l2.STL"

echo "✓ l1.STL 已恢复"
echo "✓ l2.STL 已恢复"
echo ""

# 验证恢复结果
echo "🔍 验证恢复结果..."
l1_current=$(md5sum $MESH_DIR/l1.STL | cut -d' ' -f1)
l1_backup=$(md5sum $BACKUP_SOURCE/l1.STL | cut -d' ' -f1)
l2_current=$(md5sum $MESH_DIR/l2.STL | cut -d' ' -f1)
l2_backup=$(md5sum $BACKUP_SOURCE/l2.STL | cut -d' ' -f1)

if [ "$l1_current" = "$l1_backup" ] && [ "$l2_current" = "$l2_backup" ]; then
    echo "✓ 验证成功：文件已正确恢复"
else
    echo "❌ 验证失败：文件MD5不匹配"
    exit 1
fi

echo ""
echo "🔨 正在重新编译工作空间..."
colcon build --packages-select dog2_description --symlink-install

if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ L1和L2 Mesh文件恢复完成！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 下一步："
    echo "   1. 运行: source install/setup.bash"
    echo "   2. 验证: ./view_xacro_in_rviz.sh"
    echo ""
    echo "📊 恢复的文件："
    echo "   - l1.STL: 髋关节部件（从back2.1备份恢复）"
    echo "   - l2.STL: 大腿部件（从back2.1备份恢复）"
    echo ""
else
    echo "❌ 编译失败，请检查错误信息"
    exit 1
fi
