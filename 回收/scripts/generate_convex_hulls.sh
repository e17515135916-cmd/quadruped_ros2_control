#!/bin/bash
# Blender 凸包生成包装脚本
# 自动检测 Blender 并运行批量处理脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Blender 凸包批量生成工具${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 Blender 是否安装
if ! command -v blender &> /dev/null; then
    echo -e "${RED}错误: 未找到 Blender${NC}"
    echo "请先安装 Blender:"
    echo "  sudo apt install blender"
    echo "或从官网下载: https://www.blender.org/download/"
    exit 1
fi

# 显示 Blender 版本
BLENDER_VERSION=$(blender --version | head -n 1)
echo -e "${GREEN}✓${NC} 找到 Blender: $BLENDER_VERSION"

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/blender_batch_convex_hull.py"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}错误: 未找到 Python 脚本${NC}"
    echo "  $PYTHON_SCRIPT"
    exit 1
fi

echo -e "${GREEN}✓${NC} 找到处理脚本"
echo ""

# 询问用户确认
echo -e "${YELLOW}即将处理以下文件:${NC}"
echo "  - base_link.STL (基座)"
echo "  - l1.STL, l11.STL, l111.STL, l1111.STL (第1条腿)"
echo "  - l2.STL, l21.STL, l211.STL, l2111.STL (第2条腿)"
echo "  - l3.STL, l31.STL, l311.STL, l3111.STL (第3条腿)"
echo "  - l4.STL, l41.STL, l411.STL, l4111.STL (第4条腿)"
echo ""
echo -e "${YELLOW}输出目录:${NC} src/dog2_description/meshes/collision/"
echo ""

read -p "继续处理? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo -e "${GREEN}开始处理...${NC}"
echo ""

# 运行 Blender（后台模式）
blender --background --python "$PYTHON_SCRIPT"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 所有文件处理完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "凸包文件已生成到:"
    echo "  src/dog2_description/meshes/collision/"
    echo ""
    echo "下一步:"
    echo "  1. 检查生成的文件: ls -lh src/dog2_description/meshes/collision/"
    echo "  2. 更新 URDF 文件: 修改 collision mesh 路径"
    echo "  3. 测试: ros2 launch dog2_description view_robot.launch.py"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ 处理过程中出现错误${NC}"
    echo -e "${RED}========================================${NC}"
    echo "请检查上面的错误信息"
fi

exit $EXIT_CODE
