#!/bin/bash
# 在Blender中打开整个Dog2 URDF装配体

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  在Blender中打开Dog2机器人"
echo "========================================="
echo ""
echo "⚠️  注意："
echo "- Phobos插件有兼容性问题"
echo "- 推荐使用RViz查看完整装配体"
echo "- Blender只适合查看单个mesh文件"
echo ""

read -p "继续尝试在Blender中打开？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    echo ""
    echo "推荐使用RViz查看："
    echo "  ros2 launch dog2_description view_dog2.launch.py"
    exit 0
fi

echo ""
echo "方法1：使用RViz（推荐）"
echo "========================================="
echo "RViz可以正确显示完整的机器人装配体，包括："
echo "- 所有关节连接"
echo "- 正确的坐标变换"
echo "- 交互式关节控制"
echo ""
echo "命令："
echo "  ros2 launch dog2_description view_dog2.launch.py"
echo ""

read -p "是否现在启动RViz？(y/n): " rviz_confirm

if [ "$rviz_confirm" = "y" ]; then
    ros2 launch dog2_description view_dog2.launch.py
    exit 0
fi

echo ""
echo "方法2：在Blender中查看单个部件"
echo "========================================="
echo "可以在Blender中打开单个STL文件："
echo ""
echo "1. 打开Blender"
echo "2. File → Import → STL"
echo "3. 选择mesh文件："
echo "   ~/aperfect/carbot_ws/src/dog2_description/meshes/"
echo ""
echo "可用的mesh文件："
ls -1 ~/aperfect/carbot_ws/src/dog2_description/meshes/*.STL | head -20
echo ""

read -p "是否打开Blender？(y/n): " blender_confirm

if [ "$blender_confirm" = "y" ]; then
    blender &
    echo ""
    echo "Blender已启动"
    echo "请手动导入STL文件："
    echo "  File → Import → STL"
    echo "  路径：~/aperfect/carbot_ws/src/dog2_description/meshes/"
fi
