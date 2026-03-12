#!/bin/bash
# 立即恢复所有修改到原始状态

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  立即恢复原始状态"
echo "========================================="
echo ""

# 恢复mesh文件
echo "步骤1：恢复mesh文件"
echo "========================================="

meshes_dir="src/dog2_description/meshes"
collision_dir="$meshes_dir/collision"

# 需要恢复的mesh列表
meshes=("l1" "l11" "l2" "l21" "l3" "l31" "l4" "l41")

restored_count=0

for mesh in "${meshes[@]}"; do
    # 恢复视觉mesh
    if [ -f "$meshes_dir/${mesh}.STL.backup" ]; then
        cp "$meshes_dir/${mesh}.STL.backup" "$meshes_dir/${mesh}.STL"
        echo "  ✅ 恢复 ${mesh}.STL"
        ((restored_count++))
    fi
    
    # 恢复碰撞mesh
    if [ -f "$collision_dir/${mesh}_collision.STL.backup" ]; then
        cp "$collision_dir/${mesh}_collision.STL.backup" "$collision_dir/${mesh}_collision.STL"
        echo "  ✅ 恢复 ${mesh}_collision.STL"
        ((restored_count++))
    fi
done

echo "  恢复了 $restored_count 个mesh文件"

# 恢复URDF文件
echo ""
echo "步骤2：恢复URDF文件"
echo "========================================="

urdf_file="src/dog2_description/urdf/dog2.urdf.xacro"

if [ -f "${urdf_file}.backup_axis_change" ]; then
    cp "${urdf_file}.backup_axis_change" "$urdf_file"
    echo "  ✅ 恢复 dog2.urdf.xacro"
else
    echo "  ⚠️  未找到URDF备份文件"
fi

# 重新编译
echo ""
echo "步骤3：重新编译"
echo "========================================="

colcon build --packages-select dog2_description

if [ $? -eq 0 ]; then
    source install/setup.bash
    echo ""
    echo "========================================="
    echo "  ✅ 恢复完成！"
    echo "========================================="
    echo ""
    echo "所有文件已恢复到原始状态"
else
    echo ""
    echo "❌ 编译失败"
fi
