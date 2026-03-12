#!/bin/bash
# 查看原始 dog2.urdf 文件的 RViz2 可视化

echo "=========================================="
echo "Dog2 原始 URDF 文件 RViz2 可视化"
echo "=========================================="
echo ""
echo "正在启动 RViz2 查看 dog2.urdf..."
echo ""

# 获取脚本所在目录（工作空间根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "工作空间目录: $SCRIPT_DIR"
echo ""

# 检查 URDF 文件是否存在
if [ ! -f "src/dog2_description/urdf/dog2.urdf" ]; then
    echo "错误: 找不到 dog2.urdf 文件"
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
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "启动 RViz2 查看原始 URDF..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 使用现有的 launch 文件（它默认加载 dog2.urdf）
ros2 launch dog2_description view_dog2.launch.py
