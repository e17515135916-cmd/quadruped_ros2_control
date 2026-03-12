#!/bin/bash
# 完整改造关节配置：ZYY → XYY

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  完整改造关节配置：ZYY → XYY"
echo "========================================="
echo ""
echo "这个脚本会："
echo "1. 旋转所有髋关节mesh（l1, l11, l2, l21, l3, l31, l4, l41）"
echo "2. 修改URDF中的joint axis（从Z轴改为X轴）"
echo "3. 重新编译并测试"
echo ""
echo "⚠️  重要："
echo "- 会修改8个mesh文件"
echo "- 会修改URDF文件"
echo "- 所有文件都会自动备份"
echo ""

read -p "确认继续？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

# 检查trimesh
echo ""
echo "步骤0：检查依赖"
echo "========================================="
python3 -c "import trimesh" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ trimesh库未安装"
    read -p "是否现在安装？(y/n): " install_confirm
    
    if [ "$install_confirm" = "y" ]; then
        pip3 install trimesh
        if [ $? -ne 0 ]; then
            echo "❌ 安装失败"
            exit 1
        fi
    else
        echo "已取消"
        exit 0
    fi
fi
echo "✅ trimesh已安装"

# 步骤1：旋转mesh文件
echo ""
echo "步骤1：旋转mesh文件"
echo "========================================="
python3 scripts/rotate_all_hip_meshes.py

if [ $? -ne 0 ]; then
    echo "❌ mesh旋转失败"
    exit 1
fi

# 步骤2：修改URDF
echo ""
echo "步骤2：修改URDF joint axis"
echo "========================================="
python3 scripts/change_joint_axis_to_x.py

if [ $? -ne 0 ]; then
    echo "❌ URDF修改失败"
    exit 1
fi

# 步骤3：编译
echo ""
echo "步骤3：重新编译"
echo "========================================="
colcon build --packages-select dog2_description

if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi

source install/setup.bash

echo ""
echo "========================================="
echo "  ✅ 改造完成！"
echo "========================================="
echo ""
echo "修改总结："
echo "- 旋转了8个mesh文件（l1, l11, l2, l21, l3, l31, l4, l41）"
echo "- 修改了4个joint的axis（j11, j21, j31, j41）"
echo "- 关节配置从ZYY变为XYY"
echo ""
echo "备份文件："
echo "- mesh备份：*.STL.backup"
echo "- URDF备份：dog2.urdf.xacro.backup_axis_change"
echo ""

read -p "是否立即在RViz中查看？(y/n): " view_confirm

if [ "$view_confirm" = "y" ]; then
    echo ""
    echo "正在启动RViz..."
    ros2 launch dog2_description view_dog2.launch.py
else
    echo ""
    echo "手动查看命令："
    echo "  ros2 launch dog2_description view_dog2.launch.py"
fi
