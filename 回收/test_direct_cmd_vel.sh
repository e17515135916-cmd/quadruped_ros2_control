#!/bin/bash
# 直接测试 /cmd_vel 话题

echo "=========================================="
echo "直接测试速度命令"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "检查 /cmd_vel 话题..."
if ! ros2 topic list 2>/dev/null | grep -q "/cmd_vel"; then
    echo "❌ /cmd_vel 话题不存在"
    echo "   CHAMP 控制器可能没有启动"
    exit 1
fi

echo "✅ /cmd_vel 话题存在"
echo ""

echo "发送测试命令（向前 0.1 m/s，持续 1 秒）..."
timeout 1 ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" 2>/dev/null

echo ""
echo "命令已发送"
echo "请观察 Gazebo 中的机器人是否移动"
echo ""
echo "如果机器人移动了："
echo "  ✅ 说明系统工作正常，可能是键盘控制脚本的问题"
echo ""
echo "如果机器人没有移动："
echo "  ❌ 说明 CHAMP 控制器或 ros2_control 有问题"
echo "     请检查启动日志中的错误"
