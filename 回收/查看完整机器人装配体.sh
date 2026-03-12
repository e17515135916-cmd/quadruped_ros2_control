#!/bin/bash
# 查看Dog2完整机器人装配体

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  查看Dog2完整机器人装配体"
echo "========================================="
echo ""
echo "选择查看方式："
echo ""
echo "1. RViz - 查看完整装配体（推荐）"
echo "   ✅ 显示所有部件和关节"
echo "   ✅ 可以控制关节角度"
echo "   ✅ 显示坐标系"
echo ""
echo "2. Blender - 查看所有mesh（仅视觉）"
echo "   ⚠️  只显示mesh，不显示关节关系"
echo "   ⚠️  位置可能不准确"
echo ""
echo "3. FreeCAD - 编辑单个mesh文件"
echo "   ✅ 精确编辑mesh几何形状"
echo "   ❌ 不能导入URDF"
echo ""

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "正在启动RViz查看完整机器人..."
        echo ""
        echo "💡 RViz中的操作："
        echo "  - 鼠标左键：旋转视图"
        echo "  - 鼠标中键：平移视图"
        echo "  - 鼠标滚轮：缩放"
        echo "  - 左侧面板：可以控制关节角度"
        echo ""
        source install/setup.bash
        ros2 launch dog2_description view_dog2.launch.py
        ;;
    2)
        echo ""
        echo "正在启动Blender导入所有mesh..."
        echo ""
        echo "⚠️  注意："
        echo "  - Blender只显示mesh的视觉效果"
        echo "  - 不显示关节连接关系"
        echo "  - 位置是近似的，不是精确的"
        echo ""
        ./在blender中打开完整模型.sh
        ;;
    3)
        echo ""
        echo "正在启动FreeCAD编辑单个mesh..."
        echo ""
        echo "💡 提示："
        echo "  - FreeCAD不能导入URDF"
        echo "  - 只能编辑单个STL文件"
        echo "  - 适合精确修改mesh几何形状"
        echo ""
        ./启动FreeCAD编辑mesh.sh
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
