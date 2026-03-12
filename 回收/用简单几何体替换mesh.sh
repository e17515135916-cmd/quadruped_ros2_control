#!/bin/bash

# 用简单的几何体（box/cylinder）替换复杂的mesh

set -e

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Mesh → 简单几何体 替换工具"
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
echo "当前文件："
ls -lh "$INPUT_FILE" | awk '{print "  " $9 ": " $5}'
echo ""

# 选择几何体类型
echo "请选择替换的几何体类型："
echo "  1) Box（方形）- 最简单，8个顶点，6个面"
echo "  2) Cylinder（圆柱体）- 可调节精度"
echo ""

read -p "请选择 [1-2]: " geom_type

case $geom_type in
    1)
        GEOM="box"
        echo ""
        echo "Box设置："
        read -p "边界扩展量（米）[默认: 0.0]: " PADDING
        PADDING=${PADDING:-0.0}
        
        OUTPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1_box.STL"
        OUTPUT_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_box_collision.STL"
        
        echo ""
        echo "将创建："
        echo "  类型：Box（方形）"
        echo "  边界扩展：${PADDING}m"
        echo "  顶点数：8"
        echo "  面数：6"
        ;;
        
    2)
        GEOM="cylinder"
        echo ""
        echo "Cylinder设置："
        echo "  轴向："
        echo "    x - 沿X轴（前后方向）"
        echo "    y - 沿Y轴（左右方向）"
        echo "    z - 沿Z轴（上下方向）"
        read -p "  选择轴向 [x/y/z, 默认: z]: " AXIS
        AXIS=${AXIS:-z}
        
        echo ""
        echo "  精度（顶点数）："
        echo "    8  - 极简（八边形）"
        echo "    16 - 简单"
        echo "    32 - 标准"
        echo "    64 - 精细"
        read -p "  选择顶点数 [默认: 16]: " VERTICES
        VERTICES=${VERTICES:-16}
        
        OUTPUT_FILE="$WORKSPACE_DIR/src/dog2_description/meshes/l1_cylinder.STL"
        OUTPUT_COLLISION="$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_cylinder_collision.STL"
        
        echo ""
        echo "将创建："
        echo "  类型：Cylinder（圆柱体）"
        echo "  轴向：${AXIS}"
        echo "  顶点数：${VERTICES}"
        echo "  面数：$((VERTICES * 2))"
        ;;
        
    *)
        echo "✗ 无效选择"
        exit 1
        ;;
esac

echo ""
read -p "确认创建？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "开始创建..."
echo ""

# 备份原文件
BACKUP_FILE="${INPUT_FILE}.backup"
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$INPUT_FILE" "$BACKUP_FILE"
    echo "✓ 已备份原文件"
fi

# 执行替换
if [ "$GEOM" = "box" ]; then
    blender --background --python "$WORKSPACE_DIR/scripts/replace_with_box.py" -- \
        "$INPUT_FILE" "$OUTPUT_FILE" "$PADDING"
else
    blender --background --python "$WORKSPACE_DIR/scripts/replace_with_cylinder.py" -- \
        "$INPUT_FILE" "$OUTPUT_FILE" "$AXIS" "$VERTICES"
fi

# 检查是否成功
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "=========================================="
    echo "✓ 创建成功！"
    echo "=========================================="
    echo ""
    
    # 显示文件大小
    echo "文件大小对比："
    echo "  原始mesh："
    ls -lh "$INPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo "  简化几何体："
    ls -lh "$OUTPUT_FILE" | awk '{print "    " $9 ": " $5}'
    echo ""
    
    # 创建碰撞mesh
    mkdir -p "$WORKSPACE_DIR/src/dog2_description/meshes/collision"
    cp "$OUTPUT_FILE" "$OUTPUT_COLLISION"
    echo "✓ 已创建碰撞mesh"
    echo ""
    
    # 询问操作
    echo "选项："
    echo "  1) 替换原文件（用简单几何体替换l1.STL）"
    echo "  2) 保留两个文件"
    echo "  3) 在Blender中查看对比"
    echo "  4) 仅用作碰撞mesh（不替换视觉mesh）"
    echo ""
    
    read -p "请选择 [1-4]: " action
    
    case $action in
        1)
            echo ""
            echo "替换原文件..."
            mv "$INPUT_FILE" "${INPUT_FILE}.complex"
            mv "$OUTPUT_FILE" "$INPUT_FILE"
            echo "✓ 已替换"
            echo "  原复杂mesh备份：${INPUT_FILE}.complex"
            echo "  原始备份：$BACKUP_FILE"
            
            # 更新碰撞mesh
            cp "$INPUT_FILE" "$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_collision.STL"
            echo "✓ 已更新碰撞mesh"
            ;;
            
        2)
            echo ""
            echo "✓ 保留两个文件"
            echo "  原始：$INPUT_FILE"
            echo "  简化：$OUTPUT_FILE"
            echo "  碰撞：$OUTPUT_COLLISION"
            ;;
            
        3)
            echo ""
            echo "正在启动Blender..."
            blender "$INPUT_FILE" "$OUTPUT_FILE" &
            exit 0
            ;;
            
        4)
            echo ""
            echo "✓ 仅更新碰撞mesh"
            echo "  视觉mesh：$INPUT_FILE (保持不变)"
            echo "  碰撞mesh：$OUTPUT_COLLISION (已更新)"
            
            # 只更新碰撞mesh
            cp "$OUTPUT_FILE" "$WORKSPACE_DIR/src/dog2_description/meshes/collision/l1_collision.STL"
            rm "$OUTPUT_FILE"  # 删除临时文件
            echo "✓ 完成"
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
    echo "  3. 在Gazebo中测试："
    echo "     ros2 launch dog2_description dog2_fortress_with_gui.launch.py"
    echo ""
    
else
    echo ""
    echo "✗ 创建失败"
    exit 1
fi
