#!/bin/bash

# 快速替换新的L1 mesh并测试

set -e

echo "=========================================="
echo "快速替换新L1 Mesh"
echo "=========================================="
echo ""

# 文件路径
NEW_MESH="src/dog2_description/meshes/untitled.stl"
TARGET_MESH="src/dog2_description/meshes/l1.STL"
BACKUP_MESH="src/dog2_description/meshes/l1.STL.backup"
COLLISION_MESH="src/dog2_description/meshes/collision/l1_collision.STL"

# 检查新文件
if [ ! -f "$NEW_MESH" ]; then
    echo "✗ 错误：找不到新mesh文件：$NEW_MESH"
    exit 1
fi

echo "✓ 找到新mesh文件"
ls -lh "$NEW_MESH"
echo ""

# 如果目标文件不存在，从备份恢复
if [ ! -f "$TARGET_MESH" ]; then
    if [ -f "$BACKUP_MESH" ]; then
        echo "从备份恢复原始l1.STL..."
        cp "$BACKUP_MESH" "$TARGET_MESH"
        echo "✓ 已恢复"
    fi
fi

# 备份当前文件（如果还没有备份）
if [ ! -f "${TARGET_MESH}.before_rotation" ]; then
    echo "备份当前l1.STL..."
    cp "$TARGET_MESH" "${TARGET_MESH}.before_rotation"
    echo "✓ 已备份到：${TARGET_MESH}.before_rotation"
fi

echo ""
echo "准备替换："
echo "  新文件：$NEW_MESH"
echo "  目标：$TARGET_MESH"
echo ""

read -p "确认替换？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 替换视觉mesh
echo ""
echo "替换视觉mesh..."
cp "$NEW_MESH" "$TARGET_MESH"
echo "✓ 已替换：$TARGET_MESH"

# 替换碰撞mesh
echo ""
echo "替换碰撞mesh..."
mkdir -p "src/dog2_description/meshes/collision"
cp "$NEW_MESH" "$COLLISION_MESH"
echo "✓ 已替换：$COLLISION_MESH"

# 编译
echo ""
echo "=========================================="
echo "重新编译..."
echo "=========================================="
colcon build --packages-select dog2_description

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 编译成功！"
    echo ""
    echo "=========================================="
    echo "✓ 完成！"
    echo "=========================================="
    echo ""
    echo "现在可以测试："
    echo ""
    echo "1. 在RViz中查看："
    echo "   source install/setup.bash"
    echo "   ros2 launch dog2_description view_dog2.launch.py"
    echo ""
    echo "2. 在Gazebo中测试："
    echo "   source install/setup.bash"
    echo "   ./start_gazebo_with_dog2.sh"
    echo ""
    
    # 询问是否立即启动RViz
    read -p "是否立即在RViz中查看？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "正在启动RViz..."
        source install/setup.bash
        ros2 launch dog2_description view_dog2.launch.py
    fi
else
    echo ""
    echo "✗ 编译失败"
    exit 1
fi
