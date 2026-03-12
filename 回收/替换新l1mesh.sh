#!/bin/bash

# 替换新的L1 mesh文件
# 将Blender编辑后的untitled.stl替换为l1.STL

set -e

echo "=========================================="
echo "替换新的L1 Mesh"
echo "=========================================="
echo ""

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$WORKSPACE_DIR"

# 文件路径
NEW_MESH="src/dog2_description/meshes/untitled.stl"
OLD_MESH="src/dog2_description/meshes/l1.STL"
BACKUP_MESH="src/dog2_description/meshes/l1_original_backup.STL"
COLLISION_MESH="src/dog2_description/meshes/collision/l1_collision.STL"

# 检查新文件是否存在
if [ ! -f "$NEW_MESH" ]; then
    echo "✗ 错误：找不到新的mesh文件：$NEW_MESH"
    exit 1
fi

echo "✓ 找到新的mesh文件：$NEW_MESH"

# 显示文件大小
echo ""
echo "文件信息："
ls -lh "$NEW_MESH"
echo ""

# 备份原文件（如果还没有备份）
if [ ! -f "$BACKUP_MESH" ]; then
    echo "备份原始L1文件..."
    cp "$OLD_MESH" "$BACKUP_MESH"
    echo "✓ 已备份到：$BACKUP_MESH"
else
    echo "✓ 原始文件已有备份：$BACKUP_MESH"
fi

echo ""
read -p "确认替换L1 mesh文件？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 替换视觉mesh
echo ""
echo "替换视觉mesh..."
cp "$NEW_MESH" "$OLD_MESH"
echo "✓ 已替换：$OLD_MESH"

# 替换碰撞mesh
echo ""
echo "替换碰撞mesh..."
cp "$NEW_MESH" "$COLLISION_MESH"
echo "✓ 已替换：$COLLISION_MESH"

echo ""
echo "=========================================="
echo "✓ 替换完成！"
echo "=========================================="
echo ""

echo "下一步操作："
echo ""
echo "1. 重新编译："
echo "   colcon build --packages-select dog2_description"
echo "   source install/setup.bash"
echo ""
echo "2. 在RViz中查看："
echo "   ros2 launch dog2_description view_dog2.launch.py"
echo ""
echo "3. 在Gazebo中测试："
echo "   ./start_gazebo_with_dog2.sh"
echo ""

# 询问是否立即编译
read -p "是否立即重新编译？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在编译..."
    colcon build --packages-select dog2_description
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ 编译成功！"
        echo ""
        echo "运行以下命令查看："
        echo "  source install/setup.bash"
        echo "  ros2 launch dog2_description view_dog2.launch.py"
    else
        echo ""
        echo "✗ 编译失败，请检查错误信息"
    fi
fi

echo ""
echo "如果需要恢复原始文件，运行："
echo "  cp $BACKUP_MESH $OLD_MESH"
echo ""
