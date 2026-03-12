#!/bin/bash

# 查看L1 mesh的详细信息

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
L1_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1.STL"

echo "=========================================="
echo "L1 Mesh信息查看工具"
echo "=========================================="
echo ""

# 检查文件是否存在
if [ ! -f "$L1_FILE" ]; then
    echo "✗ 错误：找不到L1文件：$L1_FILE"
    exit 1
fi

# 检查Blender是否安装
if ! command -v blender &> /dev/null; then
    echo "✗ 错误：未找到Blender"
    echo "请先安装Blender："
    echo "  sudo snap install blender --classic"
    exit 1
fi

echo "正在分析L1 mesh..."
echo ""

# 运行分析脚本
blender --background --python "$WORKSPACE_DIR/scripts/查看mesh信息.py" -- "$L1_FILE"

echo ""
echo "提示："
echo "  使用这些信息来决定在哪里分离mesh"
echo "  运行 ./分离l1部件.sh 来执行分离"
echo ""
