#!/bin/bash
# 快速测试旋转l1

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  快速测试旋转l1"
echo "========================================="
echo ""

# 检查文件
echo "检查文件..."
if [ ! -f "src/dog2_description/meshes/l1.STL" ]; then
    echo "❌ l1.STL不存在"
    exit 1
fi
echo "✅ l1.STL存在"

# 备份
echo ""
echo "备份原文件..."
if [ ! -f "src/dog2_description/meshes/l1.STL.backup" ]; then
    cp src/dog2_description/meshes/l1.STL src/dog2_description/meshes/l1.STL.backup
    echo "✅ 已备份"
else
    echo "✅ 备份已存在"
fi

# 运行Blender
echo ""
echo "运行Blender脚本..."
echo "（这可能需要几秒钟）"
echo ""

blender --background --python scripts/rotate_l1_mesh.py

echo ""
echo "========================================="
echo "完成！"
echo "========================================="
echo ""
echo "检查结果："
ls -lh src/dog2_description/meshes/l1.STL*
echo ""
echo "如果成功，文件修改时间应该是刚才"
echo ""
echo "下一步："
echo "  colcon build --packages-select dog2_description"
echo "  source install/setup.bash"
echo "  ros2 launch dog2_description view_dog2.launch.py"
