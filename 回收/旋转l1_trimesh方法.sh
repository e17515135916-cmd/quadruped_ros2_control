#!/bin/bash
# 使用trimesh库旋转l1（不需要Blender）

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  使用trimesh旋转l1（不需要Blender）"
echo "========================================="
echo ""

# 检查trimesh是否安装
echo "检查trimesh库..."
python3 -c "import trimesh" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ trimesh库未安装"
    echo ""
    read -p "是否现在安装trimesh？(y/n): " install_confirm
    
    if [ "$install_confirm" = "y" ]; then
        echo ""
        echo "正在安装trimesh..."
        pip3 install trimesh
        
        if [ $? -eq 0 ]; then
            echo "✅ trimesh安装成功"
        else
            echo "❌ trimesh安装失败"
            exit 1
        fi
    else
        echo "已取消"
        exit 0
    fi
else
    echo "✅ trimesh已安装"
fi

echo ""
echo "这个方法："
echo "- ✅ 不需要Blender"
echo "- ✅ 使用Python trimesh库"
echo "- ✅ 更快更可靠"
echo ""

read -p "确认继续旋转l1？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "正在旋转l1 mesh..."
python3 scripts/rotate_l1_trimesh.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 旋转完成！"
    echo "========================================="
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
