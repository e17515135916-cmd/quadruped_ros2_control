#!/bin/bash
# 测试Blender导入脚本

cd ~/aperfect/carbot_ws

echo "=== 测试Blender URDF导入脚本 ==="
echo ""
echo "这个脚本会："
echo "1. 检查所有必需的文件"
echo "2. 验证URDF文件"
echo "3. 启动Blender并导入机器人"
echo ""

# 检查URDF文件
if [ ! -f "src/dog2_description/urdf/dog2.urdf" ]; then
    echo "❌ URDF文件不存在"
    exit 1
fi
echo "✅ URDF文件存在"

# 检查导入脚本
if [ ! -f "scripts/urdf_to_blend_simple.py" ]; then
    echo "❌ 导入脚本不存在"
    exit 1
fi
echo "✅ 导入脚本存在"

# 检查mesh文件
MESH_COUNT=$(find src/dog2_description/meshes -name "*.STL" -type f | wc -l)
echo "✅ 找到 $MESH_COUNT 个STL文件"

# 检查Blender
if ! command -v blender &> /dev/null; then
    echo "❌ Blender未安装"
    echo "请运行: sudo snap install blender --classic"
    exit 1
fi
echo "✅ Blender已安装"

echo ""
echo "所有检查通过！正在启动Blender..."
echo ""
echo "📋 使用说明："
echo "1. 等待Blender打开"
echo "2. 脚本会自动运行并导入所有部件"
echo "3. 查看终端输出了解导入进度"
echo "4. 在Blender中按 Home 键聚焦整个机器人"
echo "5. 使用鼠标中键旋转视图查看装配体"
echo ""

./scripts/open_dog2_in_blender.sh
