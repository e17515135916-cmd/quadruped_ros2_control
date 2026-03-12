#!/bin/bash

# L1部件分离脚本
# 将L1 mesh从中间分离成上下两部分

set -e

echo "=========================================="
echo "L1部件分离工具"
echo "=========================================="
echo ""

# 获取工作空间路径
WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "工作空间：$WORKSPACE_DIR"

# 检查Blender是否安装
if ! command -v blender &> /dev/null; then
    echo "✗ 错误：未找到Blender"
    echo "请先安装Blender："
    echo "  sudo snap install blender --classic"
    exit 1
fi

echo "✓ Blender已安装"

# 检查输入文件
L1_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1.STL"
if [ ! -f "$L1_FILE" ]; then
    echo "✗ 错误：找不到L1文件：$L1_FILE"
    exit 1
fi

echo "✓ 找到L1文件"
echo ""

# 询问分离高度
echo "请输入分离高度（米）："
echo "  提示：L1部件的高度大约是0.1米"
echo "  建议值：0.05（在中间分离）"
read -p "分离高度 [默认: 0.05]: " SPLIT_HEIGHT
SPLIT_HEIGHT=${SPLIT_HEIGHT:-0.05}

echo ""
echo "分离参数："
echo "  输入文件：$L1_FILE"
echo "  分离高度：${SPLIT_HEIGHT}m"
echo ""

read -p "确认开始分离？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "开始分离..."
echo ""

# 设置文件路径
INPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1.STL"
OUTPUT_UPPER="$WORKSPACE_DIR/src/dog2_description/meshes/l1_upper.STL"
OUTPUT_LOWER="$WORKSPACE_DIR/src/dog2_description/meshes/l1_lower.STL"
OUTPUT_UPPER_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_upper_collision.STL"
OUTPUT_LOWER_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_lower_collision.STL"

# 运行Blender脚本（使用Bisect方法，不需要选择面）
blender --background --python "$WORKSPACE_DIR/scripts/split_mesh_bisect.py" -- \
    "$INPUT_FILE" "$OUTPUT_UPPER" "$OUTPUT_LOWER" "$SPLIT_HEIGHT"

# 复制到碰撞目录
if [ -f "$OUTPUT_UPPER" ]; then
    cp "$OUTPUT_UPPER" "$OUTPUT_UPPER_COLLISION"
    echo "✓ 已创建碰撞mesh：l1_upper_collision.STL"
fi

if [ -f "$OUTPUT_LOWER" ]; then
    cp "$OUTPUT_LOWER" "$OUTPUT_LOWER_COLLISION"
    echo "✓ 已创建碰撞mesh：l1_lower_collision.STL"
fi

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ 分离成功！"
    echo "=========================================="
    echo ""
    echo "生成的文件："
    echo "  视觉mesh："
    ls -lh "$WORKSPACE_DIR/src/dog2_description/meshes/l1_upper.STL" 2>/dev/null || echo "    ✗ l1_upper.STL 未找到"
    ls -lh "$WORKSPACE_DIR/src/dog2_description/meshes/l1_lower.STL" 2>/dev/null || echo "    ✗ l1_lower.STL 未找到"
    echo ""
    echo "  碰撞mesh："
    ls -lh "$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_upper_collision.STL" 2>/dev/null || echo "    ✗ l1_upper_collision.STL 未找到"
    ls -lh "$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_lower_collision.STL" 2>/dev/null || echo "    ✗ l1_lower_collision.STL 未找到"
    echo ""
    
    echo "下一步操作："
    echo ""
    echo "1. 在Blender中查看分离结果："
    echo "   blender src/dog2_description/meshes/l1_upper.STL src/dog2_description/meshes/l1_lower.STL"
    echo ""
    echo "2. 更新URDF文件："
    echo "   gedit src/dog2_description/urdf/dog2.urdf.xacro"
    echo ""
    echo "   需要添加："
    echo "   - l1_upper link定义"
    echo "   - l1_lower link定义"
    echo "   - 连接上下两部分的新关节"
    echo ""
    echo "3. 重新编译："
    echo "   colcon build --packages-select dog2_description"
    echo "   source install/setup.bash"
    echo ""
    echo "4. 在RViz中查看："
    echo "   ros2 launch dog2_description view_dog2.launch.py"
    echo ""
    
    # 询问是否打开Blender查看
    read -p "是否在Blender中查看分离结果？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在启动Blender..."
        blender "$WORKSPACE_DIR/src/dog2_description/meshes/l1_upper.STL" \
                "$WORKSPACE_DIR/src/dog2_description/meshes/l1_lower.STL" &
    fi
    
else
    echo ""
    echo "✗ 分离失败"
    echo "请检查错误信息"
    exit 1
fi
