#!/bin/bash
# URDF文件清理脚本
# 安全删除不需要的备份、测试和临时文件

set -e

WORKSPACE_DIR="/home/dell/aperfect/carbot_ws"
URDF_DIR="${WORKSPACE_DIR}/src/dog2_description/urdf"
BACKUP_DIR="${WORKSPACE_DIR}/backups/urdf_cleanup_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "URDF 文件清理脚本"
echo "=========================================="
echo ""
echo "工作目录: ${WORKSPACE_DIR}"
echo "URDF目录: ${URDF_DIR}"
echo "备份目录: ${BACKUP_DIR}"
echo ""

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

echo "📋 分析文件..."
echo ""

# 统计文件
TOTAL_BACKUP=0
TOTAL_TEST=0
TOTAL_SIZE=0

# 1. 备份文件（移动到备份目录而不是删除）
echo "🔄 移动备份文件到备份目录..."
for file in "${URDF_DIR}"/*.backup* "${URDF_DIR}"/*.xacro.backup* "${URDF_DIR}"/*.xacro.broken "${URDF_DIR}"/*.xacro.incomplete* "${URDF_DIR}"/*.xacro.before_macro "${URDF_DIR}"/*.xacro.new "${URDF_DIR}"/*.old_backup; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  → $filename"
        mv "$file" "${BACKUP_DIR}/"
        TOTAL_BACKUP=$((TOTAL_BACKUP + 1))
        TOTAL_SIZE=$((TOTAL_SIZE + $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)))
    fi
done

# 2. 删除测试/临时文件
echo ""
echo "🗑️  删除测试和临时文件..."
TEST_FILES=(
    "dog2_test.urdf"
    "dog2_debug.urdf"
    "dog2_generated.urdf"
    "dog2_generated_from_xacro.urdf"
    "dog2_from_xacro.urdf"
    "dog2_from_xacro_corrected.urdf"
    "dog2_from_xacro_fixed.urdf"
    "dog2_modified.urdf"
    "simple.urdf"
)

for file in "${TEST_FILES[@]}"; do
    filepath="${URDF_DIR}/${file}"
    if [ -f "$filepath" ]; then
        filename=$(basename "$filepath")
        echo "  ✗ $filename"
        rm -f "$filepath"
        TOTAL_TEST=$((TOTAL_TEST + 1))
    fi
done

# 3. 删除根目录的测试文件
echo ""
echo "🗑️  删除根目录测试文件..."
ROOT_TEST_FILES=(
    "generated_test.urdf"
    "generated_test_new.urdf"
    "generated_test_final.urdf"
)

for file in "${ROOT_TEST_FILES[@]}"; do
    filepath="${WORKSPACE_DIR}/${file}"
    if [ -f "$filepath" ]; then
        filename=$(basename "$filepath")
        echo "  ✗ $filename"
        rm -f "$filepath"
        TOTAL_TEST=$((TOTAL_TEST + 1))
    fi
done

echo ""
echo "=========================================="
echo "✅ 清理完成！"
echo "=========================================="
echo ""
echo "📊 统计:"
echo "  - 备份文件移动: ${TOTAL_BACKUP} 个"
echo "  - 测试文件删除: ${TOTAL_TEST} 个"
echo "  - 备份位置: ${BACKUP_DIR}"
echo ""
echo "📁 保留的核心文件:"
echo "  ✓ dog2.urdf.xacro (主源文件)"
echo "  ✓ dog2.urdf (生成文件)"
echo "  ✓ dog2_visual.urdf (可视化专用)"
echo ""
echo "⚠️  专用文件（请确认是否需要）:"
echo "  ? dog2_gazebo.urdf"
echo "  ? dog2_champ.urdf"
echo "  ? dog2_optimized_for_crossing.urdf"
echo "  ? dog2_fixed_prismatic.urdf"
echo "  ? links.xacro"
echo ""
echo "💡 提示: 如果确认不需要专用文件，可以手动删除"
echo ""




