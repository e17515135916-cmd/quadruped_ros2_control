#!/bin/bash
# 启动FreeCAD编辑Dog2机器人mesh文件

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  FreeCAD - 编辑Dog2机器人Mesh文件"
echo "========================================="
echo ""
echo "STL文件位置："
echo "  ~/aperfect/carbot_ws/src/dog2_description/meshes/"
echo ""
echo "髋关节相关文件（已旋转90度）："
echo "  l1.STL, l11.STL - 左前腿"
echo "  l2.STL, l21.STL - 右前腿"
echo "  l3.STL, l31.STL - 左后腿"
echo "  l4.STL, l41.STL - 右后腿"
echo ""
echo "========================================="
echo ""

# 检查FreeCAD是否安装
if ! command -v freecad &> /dev/null; then
    echo "❌ FreeCAD未安装"
    echo ""
    read -p "是否现在安装？(y/n): " install
    if [ "$install" = "y" ]; then
        sudo apt update
        sudo apt install -y freecad
    else
        exit 1
    fi
fi

echo "选择操作："
echo ""
echo "1. 启动FreeCAD（空白项目）"
echo "2. 打开特定mesh文件"
echo "3. 查看使用指南"
echo "4. 查看mesh文件列表"
echo ""

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "正在启动FreeCAD..."
        echo ""
        echo "💡 提示："
        echo "  - File → Import 导入STL文件"
        echo "  - 文件位置：src/dog2_description/meshes/"
        echo ""
        freecad &
        ;;
    2)
        echo ""
        echo "可用的mesh文件："
        echo ""
        ls -1 src/dog2_description/meshes/*.STL | grep -v backup | nl
        echo ""
        read -p "输入文件编号: " num
        
        file=$(ls -1 src/dog2_description/meshes/*.STL | grep -v backup | sed -n "${num}p")
        
        if [ -n "$file" ]; then
            echo ""
            echo "正在打开: $file"
            echo ""
            echo "💡 提示："
            echo "  - 修改后：File → Export → STL"
            echo "  - 导出到原位置会覆盖原文件"
            echo "  - 修改后需要重新编译：colcon build --packages-select dog2_description"
            echo ""
            freecad "$file" &
        else
            echo "❌ 无效的文件编号"
        fi
        ;;
    3)
        echo ""
        if [ -f "FreeCAD使用指南.md" ]; then
            cat FreeCAD使用指南.md | less
        else
            echo "使用指南文件不存在"
        fi
        ;;
    4)
        echo ""
        echo "========================================="
        echo "  Mesh文件列表"
        echo "========================================="
        echo ""
        echo "视觉mesh文件："
        ls -lh src/dog2_description/meshes/*.STL | grep -v backup | grep -v collision
        echo ""
        echo "碰撞mesh文件："
        ls -lh src/dog2_description/meshes/collision/*.STL | grep -v backup
        echo ""
        echo "备份文件："
        ls -lh src/dog2_description/meshes/*.backup 2>/dev/null || echo "  无备份文件"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  修改后的工作流程"
echo "========================================="
echo ""
echo "1. 在FreeCAD中修改STL文件"
echo "2. File → Export → 保存为STL"
echo "3. 重新编译："
echo "   colcon build --packages-select dog2_description"
echo "   source install/setup.bash"
echo "4. 在RViz中查看："
echo "   ros2 launch dog2_description view_dog2.launch.py"
echo ""
