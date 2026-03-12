#!/bin/bash
# Dog2 键盘控制快速启动脚本
# 
# 这个脚本会帮助你快速启动 Gazebo 仿真和键盘控制
# 
# 使用方法：
#   ./quick_start_keyboard_control.sh

set -e

echo "=========================================="
echo "Dog2 键盘控制快速启动"
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
    echo "   请先安装 ROS 2 Humble 或检查路径"
    exit 1
fi

# 检查是否已编译
if [ ! -d "install/dog2_champ_config" ]; then
    echo "⚠️  警告：工作空间未编译，正在编译..."
    colcon build --packages-select dog2_champ_config dog2_description champ_base champ_msgs
    echo "✅ 编译完成"
fi

# Source 工作空间环境
echo "📦 加载工作空间环境..."
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "✅ 工作空间环境已加载"
else
    echo "❌ 错误：工作空间未编译"
    echo "   请先运行: colcon build"
    exit 1
fi

echo ""
echo "=========================================="
echo "启动说明"
echo "=========================================="
echo ""
echo "步骤 1: 在当前终端启动 Gazebo + CHAMP 系统"
echo "步骤 2: 等待约 7 秒，直到看到 'System ready' 消息"
echo "步骤 3: 打开新终端，运行键盘控制脚本"
echo ""
echo "按任意键继续启动 Gazebo..."
read -n 1 -s

echo ""
echo "🚀 正在启动 Gazebo Fortress + CHAMP 系统..."
echo ""
echo "⏱️  预计启动时间：7 秒"
echo ""
echo "启动时序："
echo "  Time 0s:   启动 Gazebo Fortress"
echo "  Time 0.5s: 启动 robot_state_publisher"
echo "  Time 1s:   生成 Dog2 机器人"
echo "  Time 3s:   加载 joint_state_broadcaster"
echo "  Time 4s:   加载 joint_trajectory_controller"
echo "  Time 5s:   启动 CHAMP quadruped_controller"
echo "  Time 5s:   启动 state_estimation_node"
echo "  Time 6s:   启动 EKF 节点"
echo "  Time 7s:   ✅ 系统就绪"
echo ""
echo "=========================================="
echo ""
echo "💡 提示：系统启动后，在新终端运行："
echo "   cd $(pwd)"
echo "   source install/setup.bash"
echo "   ./src/dog2_champ_config/scripts/dog2_keyboard_control.py"
echo ""
echo "或者运行："
echo "   ./start_keyboard_control.sh"
echo ""
echo "=========================================="
echo ""

# 启动系统
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
