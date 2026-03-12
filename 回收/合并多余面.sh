#!/bin/bash

# 合并共面的三角形，将过度细分的平面恢复成简单的面

set -e

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "合并共面三角形工具"
echo "=========================================="
echo ""
echo "这个工具会："
echo "  ✓ 将共面的小三角形合并成大面"
echo "  ✓ 移除冗余的顶点和边"
echo "  ✓ 保持原始形状不变"
echo "  ✓ 大幅减少面数"
echo ""

# 检查Blender
if ! command -v blender &> /dev/null; then
    echo "✗ 错误：未找到Blender"
    echo "请先安装：sudo snap install blender --classic"
    exit 1
fi

# 检查输入文件
INPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1.STL"
if [ ! -f "$INPUT_FILE" ]; then
    echo "✗ 错误：找不到L1文件：$INPUT_FILE"
    exit 1
fi

echo "✓ 找到L1文件"
echo ""

# 显示当前文件信息
echo "当前文件："
ls -lh "$INPUT_FILE" | awk '{print "  " $9 ": " $5}'
echo ""

# 询问角度阈值
echo "角度阈值设置："
echo "  角度阈值决定了多大的角度差异内的面会被认为是共面的"
echo ""
echo "  1) 严格 (1度) - 只合并几乎完全平行的面"
echo "  2) 标准 (5度) - 推荐，平衡效果和准确性"
echo "  3) 宽松 (10度) - 合并更多面，可能改变细节"
echo "  4) 自定义"
echo ""

read -p "请选择 [1-4, 默认: 2]: " choice
choice=${choice:-2}

case $choice in
    1)
        ANGLE=1
        LEVEL="严格"
        ;;
    2)
        ANGLE=5
        LEVEL="标准"
        ;;
    3)
        ANGLE=10
        LEVEL="宽松"
        ;;
    4)
        read -p "请输入角度阈值（度）: " ANGLE
        LEVEL="自定义"
        ;;
    *)
        echo "✗ 无效选择，使用默认值5度"
        ANGLE=5
        LEVEL="标准"
        ;;
esac

OUTPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1_merged.STL"
OUTPUT_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_merged_collision.STL"

echo ""
echo "设置："
echo "  级别：${LEVEL}"
echo "  角度阈值：${ANGLE}度"
echo ""

read -p "确认开始合并？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "开始合并..."
echo ""

# 备份原文件
BACKUP_FILE="${INPUT_FILE}.backup"
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$INPUT_FILE" "$BACKUP_FILE"
    echo "✓ 已备份原文件到：$BACKUP_FILE"
fi

# 运行合并脚本
blender --background --python "$WORKSPACE_DIR/scripts/merge_coplanar_faces.py" -- \
    "$INPUT_FILE" "$OUTPUT_FILE" "$ANGLE"

# 检查是否成功
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "=========================================="
    echo "✓ 合并成功！"
    echo "=========================================="
    echo ""
    
    # 显示文件大小对比
    echo "文件大小对比："
    echo "  原始文件："
    ls -lh "$INPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo "  合并后："
    ls -lh "$OUTPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo ""
    
    # 询问操作
    echo "选项："
    echo "  1) 替换原文件（用合并后的替换l1.STL）"
    echo "  2) 保留两个文件"
    echo "  3) 在Blender中查看对比"
    echo ""
    
    read -p "请选择 [1-3]: " action
    
    case $action in
        1)
            echo ""
            echo "替换原文件..."
            mv "$INPUT_FILE" "${INPUT_FILE}.细分版"
            mv "$OUTPUT_FILE" "$INPUT_FILE"
            echo "✓ 已替换"
            echo "  原细分版备份：${INPUT_FILE}.细分版"
            echo "  原始备份：$BACKUP_FILE"
            
            # 同时更新碰撞mesh
            mkdir -p "$WORKSPACE_DIR/src/dog2_description/meshes/collision"
            cp "$INPUT_FILE" "$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_collision.STL"
            echo "✓ 已更新碰撞mesh"
            ;;
        2)
            echo ""
            echo "✓ 保留两个文件"
            echo "  原始：$INPUT_FILE"
            echo "  合并后：$OUTPUT_FILE"
            
            # 创建合并版的碰撞mesh
            mkdir -p "$WORKSPACE_DIR/src/dog2_description/meshes/collision"
            cp "$OUTPUT_FILE" "$OUTPUT_COLLISION"
            echo "✓ 已创建合并版碰撞mesh"
            ;;
        3)
            echo ""
            echo "正在启动Blender..."
            blender "$INPUT_FILE" "$OUTPUT_FILE" &
            exit 0
            ;;
    esac
    
    echo ""
    echo "下一步："
    echo "  1. 重新编译："
    echo "     colcon build --packages-select dog2_description"
    echo "     source install/setup.bash"
    echo ""
    echo "  2. 在RViz中查看："
    echo "     ros2 launch dog2_description view_dog2.launch.py"
    echo ""
    echo "  3. 如果效果不满意："
    echo "     - 面数减少不够：增大角度阈值（比如10度）"
    echo "     - 形状变化太大：减小角度阈值（比如1度）"
    echo "     - 恢复原文件：cp $BACKUP_FILE $INPUT_FILE"
    echo ""
    
else
    echo ""
    echo "✗ 合并失败"
    exit 1
fi
