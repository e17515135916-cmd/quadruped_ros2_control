#!/bin/bash
# 重新编译并测试

echo "=========================================="
echo "重新编译工作空间"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash

# 重新编译相关包
echo "正在编译 dog2_champ_config 和 dog2_description..."
colcon build --packages-select dog2_champ_config dog2_description --symlink-install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 编译成功！"
    echo ""
    echo "=========================================="
    echo "现在可以重新启动系统"
    echo "=========================================="
    echo ""
    echo "终端 1："
    echo "  ./quick_start_keyboard_control.sh"
    echo ""
    echo "终端 2（等待 7 秒）："
    echo "  ./start_keyboard_control.sh"
else
    echo ""
    echo "❌ 编译失败，请检查错误信息"
    exit 1
fi
