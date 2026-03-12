#!/bin/bash

# Dog2 URDF/Xacro 恢复脚本
# 用于恢复到2026-01-27修复后的正确版本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dog2 URDF/Xacro 恢复脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BACKUP_DIR="backups/urdf_correct_versions"
BACKUP_DATE="20260127_124509"

# 检查备份文件是否存在
if [ ! -f "$BACKUP_DIR/dog2.urdf.xacro.correct_$BACKUP_DATE" ]; then
    echo "❌ 错误：备份文件不存在！"
    echo "   请确保备份目录存在：$BACKUP_DIR"
    exit 1
fi

echo "📋 将恢复以下文件："
echo "   - dog2.urdf.xacro (Xacro源文件)"
echo "   - dog2.urdf (URDF参考文件)"
echo ""

read -p "是否继续？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消恢复操作"
    exit 0
fi

echo ""
echo "🔄 正在恢复文件..."

# 创建当前文件的备份（以防万一）
CURRENT_BACKUP_DIR="backups/before_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CURRENT_BACKUP_DIR"
cp src/dog2_description/urdf/dog2.urdf.xacro "$CURRENT_BACKUP_DIR/" 2>/dev/null
cp src/dog2_description/urdf/dog2.urdf "$CURRENT_BACKUP_DIR/" 2>/dev/null
echo "✓ 当前文件已备份到：$CURRENT_BACKUP_DIR"

# 恢复文件
cp "$BACKUP_DIR/dog2.urdf.xacro.correct_$BACKUP_DATE" src/dog2_description/urdf/dog2.urdf.xacro
cp "$BACKUP_DIR/dog2.urdf.correct_$BACKUP_DATE" src/dog2_description/urdf/dog2.urdf

echo "✓ Xacro文件已恢复"
echo "✓ URDF文件已恢复"
echo ""

echo "🔨 正在重新编译工作空间..."
colcon build --packages-select dog2_description --symlink-install

if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ 恢复完成！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 下一步："
    echo "   1. 运行: source install/setup.bash"
    echo "   2. 验证: ./view_xacro_in_rviz.sh"
    echo ""
else
    echo "❌ 编译失败，请检查错误信息"
    exit 1
fi
