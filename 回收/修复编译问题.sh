#!/bin/bash
# 修复colcon编译重复包的问题

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  修复colcon编译重复包问题"
echo "========================================="
echo ""
echo "问题：backups文件夹中有重复的dog2_description包"
echo "解决：在backups文件夹中创建COLCON_IGNORE文件"
echo ""

# 在backups文件夹创建COLCON_IGNORE
if [ -d "backups" ]; then
    touch backups/COLCON_IGNORE
    echo "✅ 已创建 backups/COLCON_IGNORE"
    echo "   colcon现在会忽略backups文件夹"
else
    echo "⚠️  backups文件夹不存在"
fi

echo ""
echo "现在可以正常编译了："
echo "  colcon build --packages-select dog2_description"
echo ""

read -p "是否立即编译？(y/n): " confirm

if [ "$confirm" = "y" ]; then
    echo ""
    echo "正在编译..."
    colcon build --packages-select dog2_description
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 编译成功！"
        source install/setup.bash
    else
        echo ""
        echo "❌ 编译失败"
    fi
fi
