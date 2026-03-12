#!/bin/bash
# 在Ubuntu上安装CAD软件

echo "========================================="
echo "  Ubuntu CAD软件安装"
echo "========================================="
echo ""
echo "推荐的CAD软件："
echo ""
echo "1. FreeCAD - 功能强大的参数化3D CAD"
echo "   - 完全免费开源"
echo "   - 支持STL导入/导出"
echo "   - 参数化建模"
echo "   - 装配体功能"
echo ""
echo "2. Blender - 3D建模和动画（已安装）"
echo "   - 适合mesh编辑"
echo "   - 不适合精确CAD设计"
echo ""
echo "3. OpenSCAD - 程序化CAD"
echo "   - 用代码定义模型"
echo "   - 适合参数化设计"
echo ""

read -p "选择要安装的软件 (1=FreeCAD, 2=OpenSCAD, 3=两个都装): " choice

case $choice in
    1)
        echo ""
        echo "正在安装FreeCAD..."
        sudo apt update
        sudo apt install -y freecad
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ FreeCAD安装成功！"
            echo ""
            echo "启动命令："
            echo "  freecad"
            echo ""
            echo "或者从应用菜单中找到 'FreeCAD'"
            echo ""
            read -p "是否现在启动FreeCAD？(y/n): " start
            if [ "$start" = "y" ]; then
                freecad &
            fi
        else
            echo "❌ 安装失败"
        fi
        ;;
    2)
        echo ""
        echo "正在安装OpenSCAD..."
        sudo apt update
        sudo apt install -y openscad
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ OpenSCAD安装成功！"
            echo ""
            echo "启动命令："
            echo "  openscad"
            echo ""
            read -p "是否现在启动OpenSCAD？(y/n): " start
            if [ "$start" = "y" ]; then
                openscad &
            fi
        else
            echo "❌ 安装失败"
        fi
        ;;
    3)
        echo ""
        echo "正在安装FreeCAD和OpenSCAD..."
        sudo apt update
        sudo apt install -y freecad openscad
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 安装成功！"
            echo ""
            echo "启动命令："
            echo "  freecad"
            echo "  openscad"
            echo ""
            read -p "是否现在启动FreeCAD？(y/n): " start
            if [ "$start" = "y" ]; then
                freecad &
            fi
        else
            echo "❌ 安装失败"
        fi
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  使用指南"
echo "========================================="
echo ""
echo "STL文件位置："
echo "  ~/aperfect/carbot_ws/src/dog2_description/meshes/"
echo ""
echo "在FreeCAD中："
echo "1. File → Import → 选择STL文件"
echo "2. 编辑mesh或重新建模"
echo "3. File → Export → 导出为STL"
echo ""
echo "在OpenSCAD中："
echo "1. 使用代码导入STL："
echo "   import(\"path/to/file.stl\");"
echo "2. 编写代码修改模型"
echo "3. Design → Render → Export → STL"
echo ""
echo "⚠️  注意："
echo "- 修改后记得备份原文件"
echo "- 导出时使用相同的文件名"
echo "- 重新编译URDF：colcon build --packages-select dog2_description"
