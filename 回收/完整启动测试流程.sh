#!/bin/bash
# 完整启动测试流程

echo "=========================================="
echo "完整启动测试流程"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "步骤 1: 清理残留进程..."
pkill -9 -f "gz sim" 2>/dev/null
pkill -9 -f "gzserver" 2>/dev/null
pkill -9 -f "gzclient" 2>/dev/null
pkill -9 -f "quadruped_controller" 2>/dev/null
pkill -9 -f "ros2" 2>/dev/null
sleep 2
echo "✅ 清理完成"

echo ""
echo "步骤 2: 检查编译状态..."
if [ -d "install/dog2_champ_config" ]; then
    echo "✅ dog2_champ_config 已安装"
else
    echo "❌ dog2_champ_config 未安装，正在编译..."
    colcon build --packages-select dog2_champ_config --symlink-install
fi

echo ""
echo "步骤 3: 重新加载环境..."
source install/setup.bash
echo "✅ 环境已加载"

echo ""
echo "=========================================="
echo "准备启动 Gazebo"
echo "=========================================="
echo ""
echo "请在另一个终端运行以下命令："
echo ""
echo "  cd ~/aperfect/carbot_ws"
echo "  source /opt/ros/humble/setup.bash"
echo "  source install/setup.bash"
echo "  ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py"
echo ""
echo "启动后，请仔细观察终端输出，特别注意："
echo "  1. 是否有红色错误信息"
echo "  2. 约 5 秒后是否看到 'quadruped_controller' 启动"
echo "  3. 是否有 'terminate called' 或其他崩溃信息"
echo ""
echo "等待 10 秒后，回到这个终端按回车继续..."
read -p "按回车继续..."

echo ""
echo "=========================================="
echo "验证系统状态"
echo "=========================================="
echo ""

echo "检查 1: Gazebo 是否运行？"
if pgrep -f "gz sim" > /dev/null; then
    echo "✅ Gazebo 正在运行"
else
    echo "❌ Gazebo 未运行"
    exit 1
fi

echo ""
echo "检查 2: quadruped_controller 是否运行？"
if ros2 node list 2>/dev/null | grep -q quadruped_controller; then
    echo "✅ quadruped_controller 正在运行"
else
    echo "❌ quadruped_controller 未运行"
    echo ""
    echo "请检查 Gazebo 终端的输出，查找包含以下关键词的错误："
    echo "  - 'quadruped'"
    echo "  - 'champ'"
    echo "  - 'terminate'"
    echo "  - 'error'"
    exit 1
fi

echo ""
echo "检查 3: /cmd_vel 话题是否存在？"
if ros2 topic list 2>/dev/null | grep -q "^/cmd_vel$"; then
    echo "✅ /cmd_vel 话题存在"
else
    echo "❌ /cmd_vel 话题不存在"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 系统启动成功！"
echo "=========================================="
echo ""
echo "现在运行诊断脚本："
echo "  ./check_champ_connections.sh"
echo ""
