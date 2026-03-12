#!/bin/bash
# 在Blender中打开完整的Dog2模型

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  在Blender中打开完整Dog2模型"
echo "========================================="
echo ""
echo "这个脚本会："
echo "1. 启动Blender"
echo "2. 自动导入所有STL文件"
echo "3. 应用URDF中的坐标变换"
echo ""
echo "⚠️  注意："
echo "- 坐标变换是简化的，可能不完全准确"
echo "- 推荐使用RViz查看精确的装配体"
echo ""

read -p "继续？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "正在启动Blender并导入模型..."
echo ""

# 启动Blender并执行Python脚本
blender --python scripts/import_urdf_to_blender.py

echo ""
echo "Blender已关闭"
