#!/bin/bash
# 旋转l1 mesh文件（绕Y轴90度）

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  旋转l1部件（绕Y轴90度）"
echo "========================================="
echo ""
echo "这个脚本会："
echo "1. 自动备份原始l1.STL文件"
echo "2. 在Blender中打开l1.STL"
echo "3. 绕Y轴旋转90度"
echo "4. 保存修改后的文件"
echo "5. 同时处理碰撞mesh"
echo ""
echo "⚠️  重要："
echo "- 只旋转l1这个部件本身"
echo "- 不改变joint位置"
echo "- 不改变其他部件"
echo "- 整条腿的空间位置保持不变"
echo ""

read -p "确认继续？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "正在启动Blender..."
echo ""

# 检查Blender是否安装
if ! command -v blender &> /dev/null; then
    echo "❌ Blender未安装"
    echo "请运行: sudo snap install blender --classic"
    exit 1
fi

# 运行Blender脚本
WORKSPACE_PATH="$(pwd)"
blender --background --python scripts/rotate_l1_mesh.py -- "$WORKSPACE_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 旋转完成！"
    echo "========================================="
    echo ""
    echo "现在需要重新编译并查看："
    echo ""
    read -p "是否立即重新编译并在RViz中查看？(y/n): " view_confirm
    
    if [ "$view_confirm" = "y" ]; then
        echo ""
        echo "正在重新编译..."
        colcon build --packages-select dog2_description
        
        if [ $? -eq 0 ]; then
            source install/setup.bash
            echo ""
            echo "✅ 编译成功！正在启动RViz..."
            echo ""
            ros2 launch dog2_description view_dog2.launch.py
        else
            echo ""
            echo "❌ 编译失败"
        fi
    else
        echo ""
        echo "手动编译命令："
        echo "  colcon build --packages-select dog2_description"
        echo "  source install/setup.bash"
        echo "  ros2 launch dog2_description view_dog2.launch.py"
    fi
else
    echo ""
    echo "❌ 旋转失败"
fi

echo ""
echo "如果需要恢复原文件："
echo "  cp src/dog2_description/meshes/l1.STL.backup src/dog2_description/meshes/l1.STL"
echo "  colcon build --packages-select dog2_description"
