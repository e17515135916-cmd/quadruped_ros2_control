#!/bin/bash
# 启动键盘控制脚本
# 
# 在 Gazebo 系统启动后，在新终端运行此脚本
# 
# 使用方法：
#   ./start_keyboard_control.sh

set -e

echo "=========================================="
echo "Dog2 键盘控制"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "src/dog2_champ_config/scripts/dog2_keyboard_control.py" ]; then
    echo "❌ 错误：请在工作空间根目录运行此脚本"
    exit 1
fi

# Source ROS 2 环境
echo "📦 加载 ROS 2 环境..."
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    echo "✅ ROS 2 Humble 环境已加载"
else
    echo "❌ 错误：未找到 ROS 2 Humble"
    exit 1
fi

# Source 工作空间环境
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "✅ 工作空间环境已加载"
else
    echo "❌ 错误：工作空间未编译"
    echo "   请先运行: colcon build"
    exit 1
fi

# 检查 /cmd_vel 话题是否存在
echo "🔍 检查系统状态..."
if ! ros2 topic list 2>/dev/null | grep -q "/cmd_vel"; then
    echo "⚠️  警告：未检测到 /cmd_vel 话题"
    echo "   请确保 Gazebo + CHAMP 系统已启动"
    echo ""
    echo "   在另一个终端运行："
    echo "   ./quick_start_keyboard_control.sh"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "键盘控制说明"
echo "=========================================="
echo ""
echo "移动控制："
echo "  W/w - 向前移动"
echo "  S/s - 向后移动"
echo "  A/a - 向左平移"
echo "  D/d - 向右平移"
echo "  Q/q - 左转"
echo "  E/e - 右转"
echo ""
echo "功能键："
echo "  空格 - 停止所有运动"
echo "  X/x - 退出程序"
echo ""
echo "=========================================="
echo ""
echo "🎮 启动键盘控制..."
echo ""

# 启动键盘控制
python3 src/dog2_champ_config/scripts/dog2_keyboard_control.py
