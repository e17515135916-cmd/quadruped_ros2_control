#!/bin/bash
# 快速调整j41关节位置

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  快速调整j41关节（第四条腿）"
echo "========================================="
echo ""
echo "当前配置："
echo "  hip_joint_xyz: 0.0116 0.0199 0.055"
echo ""
echo "从图片看，需要微调对齐"
echo ""
echo "请选择调整方向："
echo ""
echo "1. X方向 +0.001 (向前微调)"
echo "2. X方向 -0.001 (向后微调)"
echo "3. Y方向 +0.001 (向上微调)"
echo "4. Y方向 -0.001 (向下微调)"
echo "5. Z方向 +0.001 (向右微调)"
echo "6. Z方向 -0.001 (向左微调)"
echo "7. 自定义输入"
echo "8. 查看当前值"
echo "9. 恢复原始值"
echo ""

read -p "请选择 (1-9): " choice

urdf_file="src/dog2_description/urdf/dog2.urdf.xacro"

# 备份
if [ ! -f "${urdf_file}.backup_j41_original" ]; then
    cp "$urdf_file" "${urdf_file}.backup_j41_original"
    echo "✅ 已创建原始备份"
fi

case $choice in
    1)
        new_x=0.0126
        new_y=0.0199
        new_z=0.055
        echo "调整：X +0.001"
        ;;
    2)
        new_x=0.0106
        new_y=0.0199
        new_z=0.055
        echo "调整：X -0.001"
        ;;
    3)
        new_x=0.0116
        new_y=0.0209
        new_z=0.055
        echo "调整：Y +0.001"
        ;;
    4)
        new_x=0.0116
        new_y=0.0189
        new_z=0.055
        echo "调整：Y -0.001"
        ;;
    5)
        new_x=0.0116
        new_y=0.0199
        new_z=0.056
        echo "调整：Z +0.001"
        ;;
    6)
        new_x=0.0116
        new_y=0.0199
        new_z=0.054
        echo "调整：Z -0.001"
        ;;
    7)
        read -p "输入X值: " new_x
        read -p "输入Y值: " new_y
        read -p "输入Z值: " new_z
        echo "自定义：X=$new_x Y=$new_y Z=$new_z"
        ;;
    8)
        echo ""
        echo "当前配置："
        grep -A 5 "Leg 4: Rear Right" "$urdf_file" | grep "hip_joint_xyz"
        exit 0
        ;;
    9)
        if [ -f "${urdf_file}.backup_j41_original" ]; then
            cp "${urdf_file}.backup_j41_original" "$urdf_file"
            echo "✅ 已恢复原始值"
            colcon build --packages-select dog2_description
            echo ""
            echo "重新编译完成，可以在RViz中查看"
        else
            echo "❌ 未找到原始备份"
        fi
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "新配置："
echo "  hip_joint_xyz: $new_x $new_y $new_z"
echo ""

# 使用sed修改URDF
# 查找Leg 4的hip_joint_xyz并替换
sed -i.bak "/Leg 4: Rear Right/,/leg_num=\"4\"/s/hip_joint_xyz=\"[^\"]*\"/hip_joint_xyz=\"$new_x $new_y $new_z\"/" "$urdf_file"

if [ $? -eq 0 ]; then
    echo "✅ URDF已修改"
    echo ""
    echo "正在重新编译..."
    colcon build --packages-select dog2_description
    
    if [ $? -eq 0 ]; then
        source install/setup.bash
        echo ""
        echo "========================================="
        echo "  ✅ 修改完成！"
        echo "========================================="
        echo ""
        read -p "是否在RViz中查看？(y/n): " view
        
        if [ "$view" = "y" ]; then
            ros2 launch dog2_description view_dog2.launch.py
        else
            echo ""
            echo "手动查看命令："
            echo "  ros2 launch dog2_description view_dog2.launch.py"
            echo ""
            echo "如果需要继续调整，再次运行："
            echo "  ./快速调整j41.sh"
        fi
    else
        echo "❌ 编译失败"
    fi
else
    echo "❌ 修改失败"
fi
