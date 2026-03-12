#!/bin/bash
# 在Blender中打开Dog2机器人模型

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URDF_PATH="$WORKSPACE_DIR/src/dog2_description/urdf/dog2.urdf"
SCRIPT_PATH="$WORKSPACE_DIR/scripts/urdf_to_blend_simple.py"

echo "=== 在Blender中打开Dog2机器人 ==="
echo ""
echo "工作空间: $WORKSPACE_DIR"
echo "URDF文件: $URDF_PATH"
echo "导入脚本: $SCRIPT_PATH"
echo ""

# 检查文件是否存在
if [ ! -f "$URDF_PATH" ]; then
    echo "❌ URDF文件不存在: $URDF_PATH"
    exit 1
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ 导入脚本不存在: $SCRIPT_PATH"
    exit 1
fi

echo "正在启动Blender..."
echo ""
echo "提示："
echo "1. Blender会自动运行导入脚本"
echo "2. 等待几秒钟，所有部件会自动导入"
echo "3. 使用鼠标中键旋转视图"
echo "4. 使用滚轮缩放"
echo "5. 选择任意部件进行修改"
echo ""

# 启动Blender并运行脚本
blender --python "$SCRIPT_PATH" -- "$URDF_PATH"
