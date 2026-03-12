#!/bin/bash
# 完整的凸包处理工作流程
# 从生成凸包到更新 URDF 的一站式脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║        凸包处理完整工作流程                                ║${NC}"
echo -e "${BLUE}║        Complete Convex Hull Workflow                       ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 步骤 1: 检查前置条件
# ============================================================================
echo -e "${YELLOW}[步骤 1/5] 检查前置条件${NC}"
echo "-----------------------------------------------------------"

# 检查 Blender
if ! command -v blender &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Blender${NC}"
    echo "请安装: sudo apt install blender"
    exit 1
fi
echo -e "${GREEN}✓${NC} Blender: $(blender --version | head -n 1)"

# 检查 Python 依赖
if ! python3 -c "import numpy" &> /dev/null; then
    echo -e "${YELLOW}⚠️  警告: numpy 未安装，验证步骤将跳过${NC}"
    SKIP_VERIFY=1
else
    if ! python3 -c "from stl import mesh" &> /dev/null; then
        echo -e "${YELLOW}⚠️  警告: numpy-stl 未安装，验证步骤将跳过${NC}"
        SKIP_VERIFY=1
    else
        echo -e "${GREEN}✓${NC} Python 依赖已安装"
        SKIP_VERIFY=0
    fi
fi

# 检查 STL 文件
STL_DIR="src/dog2_description/meshes"
if [ ! -d "$STL_DIR" ]; then
    echo -e "${RED}❌ 错误: meshes 目录不存在${NC}"
    exit 1
fi
STL_COUNT=$(ls -1 "$STL_DIR"/l*.STL 2>/dev/null | wc -l)
echo -e "${GREEN}✓${NC} 找到 $STL_COUNT 个 STL 文件"

echo ""

# ============================================================================
# 步骤 2: 生成凸包
# ============================================================================
echo -e "${YELLOW}[步骤 2/5] 生成凸包文件${NC}"
echo "-----------------------------------------------------------"
echo "这将处理所有 STL 文件（17 个文件：基座 + 所有腿部）"
echo "预计时间: 3-8 分钟"
echo ""

read -p "继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "运行 Blender 批量处理..."
"$SCRIPT_DIR/generate_convex_hulls.sh"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 凸包生成失败${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 步骤 3: 验证凸包质量
# ============================================================================
echo -e "${YELLOW}[步骤 3/5] 验证凸包质量${NC}"
echo "-----------------------------------------------------------"

if [ $SKIP_VERIFY -eq 1 ]; then
    echo -e "${YELLOW}⚠️  跳过验证（缺少 Python 依赖）${NC}"
    echo "如需验证，安装: pip3 install numpy-stl"
else
    python3 "$SCRIPT_DIR/verify_convex_hulls.py"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  验证发现一些警告${NC}"
        read -p "继续更新 URDF? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
    fi
fi

echo ""

# ============================================================================
# 步骤 4: 预览 URDF 修改
# ============================================================================
echo -e "${YELLOW}[步骤 4/5] 预览 URDF 修改${NC}"
echo "-----------------------------------------------------------"

python3 "$SCRIPT_DIR/update_urdf_with_convex_hulls.py" --dry-run

echo ""
read -p "应用这些修改到 URDF? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    echo ""
    echo "凸包文件已生成，但 URDF 未修改"
    echo "你可以稍后手动运行:"
    echo "  python3 scripts/update_urdf_with_convex_hulls.py"
    exit 0
fi

echo ""

# ============================================================================
# 步骤 5: 更新 URDF
# ============================================================================
echo -e "${YELLOW}[步骤 5/5] 更新 URDF 文件${NC}"
echo "-----------------------------------------------------------"

# 自动确认（因为前面已经确认过了）
echo "y" | python3 "$SCRIPT_DIR/update_urdf_with_convex_hulls.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ URDF 更新失败${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 完成总结
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║                  🎉 工作流程完成！                         ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ 凸包文件已生成${NC}"
echo "   位置: src/dog2_description/meshes/collision/"
echo ""
echo -e "${GREEN}✅ URDF 文件已更新${NC}"
echo "   文件: src/dog2_description/urdf/dog2.urdf.xacro"
echo "   备份: backups/dog2.urdf.xacro.backup_*"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}下一步测试:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1️⃣  验证 URDF 语法:"
echo "   cd src/dog2_description"
echo "   xacro urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf"
echo "   check_urdf /tmp/dog2_test.urdf"
echo ""
echo "2️⃣  RViz 可视化检查:"
echo "   ros2 launch dog2_description view_robot.launch.py"
echo "   # 在 RViz 中切换 'Collision Enabled' 查看凸包"
echo ""
echo "3️⃣  Gazebo 稳定性测试:"
echo "   ros2 launch dog2_gazebo spawn_dog2.launch.py"
echo "   # 观察机器人是否平稳落地，无'炸飞'现象"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo "   - 如果 Gazebo 测试失败，可以调整凸包参数重新生成"
echo "   - 备份文件在 backups/ 目录，可以随时回滚"
echo "   - 详细文档: .kiro/specs/gazebo-collision-mesh-fixes/"
echo ""
echo -e "${GREEN}祝你好运！🚀${NC}"
echo ""
