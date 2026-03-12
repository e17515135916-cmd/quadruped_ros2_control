#!/bin/bash
# 完整的旋转l1流程（包含所有修复）

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  旋转l1部件完整流程"
echo "========================================="
echo ""

# 步骤1：修复编译问题
echo "步骤1：修复编译问题"
echo "-------------------"
if [ -d "backups" ] && [ ! -f "backups/COLCON_IGNORE" ]; then
    touch backups/COLCON_IGNORE
    echo "✅ 已创建 backups/COLCON_IGNORE"
else
    echo "✅ 编译问题已修复"
fi

echo ""
echo "步骤2：旋转l1 mesh文件"
echo "-------------------"
echo ""
echo "这将："
echo "1. 备份原始l1.STL"
echo "2. 在Blender中旋转90度（绕Y轴）"
echo "3. 保存修改后的文件"
echo ""

read -p "确认继续？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

# 检查Blender
if ! command -v blender &> /dev/null; then
    echo "❌ Blender未安装"
    echo "请运行: sudo snap install blender --classic"
    exit 1
fi

# 备份原文件
echo ""
echo "正在备份原文件..."
if [ ! -f "src/dog2_description/meshes/l1.STL.backup" ]; then
    cp src/dog2_description/meshes/l1.STL src/dog2_description/meshes/l1.STL.backup
    echo "✅ 已备份: l1.STL.backup"
fi

if [ -f "src/dog2_description/meshes/collision/l1_collision.STL" ] && [ ! -f "src/dog2_description/meshes/collision/l1_collision.STL.backup" ]; then
    cp src/dog2_description/meshes/collision/l1_collision.STL src/dog2_description/meshes/collision/l1_collision.STL.backup
    echo "✅ 已备份: l1_collision.STL.backup"
fi

# 运行Blender脚本（不需要传递参数，脚本内部已硬编码路径）
echo ""
echo "正在启动Blender旋转mesh..."
blender --background --python scripts/rotate_l1_mesh.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 旋转完成！"
    echo "========================================="
    echo ""
    echo "步骤3：重新编译"
    echo "-------------------"
    
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
    echo ""
    echo "可能的原因："
    echo "1. Blender版本不兼容"
    echo "2. Python脚本路径错误"
    echo ""
    echo "请检查上面的错误信息"
fi

echo ""
echo "如果需要恢复原文件："
echo "  cp src/dog2_description/meshes/l1.STL.backup src/dog2_description/meshes/l1.STL"
echo "  colcon build --packages-select dog2_description"
