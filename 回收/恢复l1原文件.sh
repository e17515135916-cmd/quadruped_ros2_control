#!/bin/bash
# 恢复l1原文件

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  恢复l1原文件"
echo "========================================="
echo ""

# 检查备份文件
if [ -f "src/dog2_description/meshes/l1.STL.backup" ]; then
    echo "✅ 找到备份文件"
    echo ""
    echo "备份文件信息："
    ls -lh src/dog2_description/meshes/l1.STL.backup
    echo ""
    echo "当前文件信息："
    ls -lh src/dog2_description/meshes/l1.STL
    echo ""
    
    read -p "确认恢复原文件？(y/n): " confirm
    
    if [ "$confirm" = "y" ]; then
        # 恢复视觉mesh
        cp src/dog2_description/meshes/l1.STL.backup src/dog2_description/meshes/l1.STL
        echo "✅ 已恢复 l1.STL"
        
        # 恢复碰撞mesh（如果有备份）
        if [ -f "src/dog2_description/meshes/collision/l1_collision.STL.backup" ]; then
            cp src/dog2_description/meshes/collision/l1_collision.STL.backup src/dog2_description/meshes/collision/l1_collision.STL
            echo "✅ 已恢复 l1_collision.STL"
        fi
        
        echo ""
        echo "========================================="
        echo "  ✅ 恢复完成！"
        echo "========================================="
        echo ""
        echo "下一步："
        echo "  colcon build --packages-select dog2_description"
        echo "  source install/setup.bash"
        echo ""
        
        read -p "是否立即重新编译？(y/n): " build_confirm
        
        if [ "$build_confirm" = "y" ]; then
            echo ""
            echo "正在重新编译..."
            colcon build --packages-select dog2_description
            
            if [ $? -eq 0 ]; then
                source install/setup.bash
                echo ""
                echo "✅ 编译成功！文件已恢复到原始状态"
            else
                echo ""
                echo "❌ 编译失败"
            fi
        fi
    else
        echo "已取消"
    fi
else
    echo "❌ 未找到备份文件"
    echo ""
    echo "备份文件应该在："
    echo "  src/dog2_description/meshes/l1.STL.backup"
    echo ""
    echo "如果你没有备份，文件可能没有被修改"
fi
