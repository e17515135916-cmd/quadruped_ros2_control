#!/bin/bash
# Dog2 Xacro 文件 RViz2 可视化启动脚本

echo "=========================================="
echo "Dog2 Xacro 文件 RViz2 可视化"
echo "=========================================="
echo ""
echo "正在启动 RViz2 查看 dog2.urdf.xacro..."
echo ""
echo "功能："
echo "  - 直接从 dog2.urdf.xacro 加载机器人模型"
echo "  - 显示关节状态控制 GUI"
echo "  - 可以手动调整关节角度"
echo ""
echo "关节限制："
echo "  - Hip 关节: ±150° (±2.618 rad)"
echo "  - Knee 关节: ±160° (±2.8 rad)"
echo "  - Prismatic 关节: ±0.111 m"
echo ""
echo "=========================================="
echo ""

# 获取脚本所在目录（工作空间根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "工作空间目录: $SCRIPT_DIR"
echo ""

# 检查是否在工作空间根目录
if [ ! -d "src/dog2_description" ]; then
    echo "错误: 找不到 src/dog2_description 目录"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 检查 xacro 文件是否存在
if [ ! -f "src/dog2_description/urdf/dog2.urdf.xacro" ]; then
    echo "错误: 找不到 dog2.urdf.xacro 文件"
    exit 1
fi

# Source ROS 2 环境
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    echo "✓ 已加载 ROS 2 Humble 环境"
elif [ -f "/opt/ros/foxy/setup.bash" ]; then
    source /opt/ros/foxy/setup.bash
    echo "✓ 已加载 ROS 2 Foxy 环境"
else
    echo "❌ 错误: 未找到 ROS 2 环境"
    echo "请先安装 ROS 2 或手动 source"
    exit 1
fi

# 检查并编译工作空间
if [ ! -d "install" ] || [ ! -f "install/setup.bash" ]; then
    echo ""
    echo "⚠️  工作空间未编译，正在编译 dog2_description..."
    echo ""
    colcon build --packages-select dog2_description --symlink-install
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 编译失败！请检查错误信息"
        exit 1
    fi
    echo ""
    echo "✓ 编译完成"
fi

# Source 工作空间
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "✓ 已加载工作空间环境"
else
    echo "❌ 错误: 找不到 install/setup.bash"
    exit 1
fi

# 验证包是否可用
if ! ros2 pkg list | grep -q "dog2_description"; then
    echo ""
    echo "❌ 错误: dog2_description 包未找到"
    echo "尝试重新编译..."
    colcon build --packages-select dog2_description --symlink-install
    source install/setup.bash
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "启动 RViz2..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 启动 launch 文件
ros2 launch dog2_description view_dog2_xacro.launch.py
