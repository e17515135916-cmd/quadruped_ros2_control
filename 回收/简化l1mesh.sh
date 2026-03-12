#!/bin/bash

# 简化L1 mesh，减少面数

set -e

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "L1 Mesh简化工具"
echo "=========================================="
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
echo "当前文件大小："
ls -lh "$INPUT_FILE" | awk '{print "  " $9 ": " $5}'
echo ""

# 询问简化比例
echo "请选择简化程度："
echo "  1) 轻度简化 (保留50%的面)"
echo "  2) 中度简化 (保留25%的面)"
echo "  3) 重度简化 (保留10%的面)"
echo "  4) 极度简化 (保留5%的面)"
echo "  5) 自定义比例"
echo ""

read -p "请选择 [1-5]: " choice

case $choice in
    1)
        RATIO=0.5
        LEVEL="轻度"
        ;;
    2)
        RATIO=0.25
        LEVEL="中度"
        ;;
    3)
        RATIO=0.1
        LEVEL="重度"
        ;;
    4)
        RATIO=0.05
        LEVEL="极度"
        ;;
    5)
        read -p "请输入保留比例 (0.01-1.0): " RATIO
        LEVEL="自定义"
        ;;
    *)
        echo "✗ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "简化设置："
echo "  级别：${LEVEL}简化"
echo "  保留比例：${RATIO} (${RATIO}00%)"
echo ""

# 设置输出文件
OUTPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1_simplified.STL"
OUTPUT_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_simplified_collision.STL"

read -p "确认开始简化？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "开始简化..."
echo ""

# 备份原文件
BACKUP_FILE="${INPUT_FILE}.backup"
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$INPUT_FILE" "$BACKUP_FILE"
    echo "✓ 已备份原文件到：$BACKUP_FILE"
fi

# 运行简化脚本
blender --background --python "$WORKSPACE_DIR/scripts/simplify_mesh.py" -- \
    "$INPUT_FILE" "$OUTPUT_FILE" "$RATIO"

# 检查是否成功
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "=========================================="
    echo "✓ 简化成功！"
    echo "=========================================="
    echo ""
    
    # 显示文件大小对比
    echo "文件大小对比："
    echo "  原始文件："
    ls -lh "$INPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo "  简化后："
    ls -lh "$OUTPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo ""
    
    # 询问是否替换原文件
    echo "选项："
    echo "  1) 替换原文件 (l1.STL → l1_simplified.STL)"
    echo "  2) 保留两个文件"
    echo "  3) 在Blender中查看对比"
    echo ""
    
    read -p "请选择 [1-3]: " action
    
    case $action in
        1)
            echo ""
            echo "替换原文件..."
            mv "$INPUT_FILE" "${INPUT_FILE}.old"
            mv "$OUTPUT_FILE" "$INPUT_FILE"
            echo "✓ 已替换"
            echo "  原文件备份：${INPUT_FILE}.old"
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
            echo "  简化：$OUTPUT_FILE"
            
            # 创建简化版的碰撞mesh
            mkdir -p "$WORKSPACE_DIR/src/dog2_description/meshes/collision"
            cp "$OUTPUT_FILE" "$OUTPUT_COLLISION"
            echo "✓ 已创建简化版碰撞mesh"
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
    echo "  1. 在RViz中查看效果："
    echo "     colcon build --packages-select dog2_description"
    echo "     source install/setup.bash"
    echo "     ros2 launch dog2_description view_dog2.launch.py"
    echo ""
    echo "  2. 如果效果不满意，可以恢复原文件："
    echo "     cp $BACKUP_FILE $INPUT_FILE"
    echo ""
    
else
    echo ""
    echo "✗ 简化失败"
    exit 1
fi
