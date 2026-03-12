#!/bin/bash
# 检查系统状态

echo "=========================================="
echo "系统状态检查"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 检查 ROS 2 节点"
echo "-------------------------------------------"
ros2 node list 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 无法获取节点列表"
    echo "   可能原因：ROS 2 系统未运行或环境未 source"
    exit 1
fi
echo ""

echo "2. 检查关键节点"
echo "-------------------------------------------"
NODES=$(ros2 node list 2>/dev/null)

if echo "$NODES" | grep -q "quadruped_controller"; then
    echo "✅ quadruped_controller 正在运行"
else
    echo "❌ quadruped_controller 未运行"
fi

if echo "$NODES" | grep -q "robot_state_publisher"; then
    echo "✅ robot_state_publisher 正在运行"
else
    echo "❌ robot_state_publisher 未运行"
fi

if echo "$NODES" | grep -q "controller_manager"; then
    echo "✅ controller_manager 正在运行"
else
    echo "❌ controller_manager 未运行"
fi
echo ""

echo "3. 检查话题"
echo "-------------------------------------------"
TOPICS=$(ros2 topic list 2>/dev/null)

if echo "$TOPICS" | grep -q "/cmd_vel"; then
    echo "✅ /cmd_vel 话题存在"
    echo ""
    echo "   话题信息："
    ros2 topic info /cmd_vel 2>/dev/null
else
    echo "❌ /cmd_vel 话题不存在"
fi
echo ""

if echo "$TOPICS" | grep -q "/joint_states"; then
    echo "✅ /joint_states 话题存在"
else
    echo "❌ /joint_states 话题不存在"
fi
echo ""

echo "4. 检查控制器状态"
echo "-------------------------------------------"
ros2 control list_controllers 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 无法获取控制器列表"
fi
echo ""

echo "5. 检查 Gazebo 进程"
echo "-------------------------------------------"
if pgrep -f "gz sim" > /dev/null; then
    echo "✅ Gazebo 正在运行"
    echo "   进程 ID: $(pgrep -f 'gz sim')"
else
    echo "❌ Gazebo 未运行"
fi
echo ""

echo "=========================================="
echo "诊断建议"
echo "=========================================="
echo ""

# 根据检查结果给出建议
if ! echo "$NODES" | grep -q "quadruped_controller"; then
    echo "⚠️  CHAMP 控制器未运行"
    echo "   请检查启动日志中的错误信息"
    echo "   可能需要修复配置文件后重新启动"
fi

if ! echo "$TOPICS" | grep -q "/cmd_vel"; then
    echo "⚠️  /cmd_vel 话题不存在"
    echo "   这意味着 CHAMP 控制器没有正常启动"
    echo "   键盘控制无法工作"
fi

if ! pgrep -f "gz sim" > /dev/null; then
    echo "⚠️  Gazebo 未运行"
    echo "   请先启动 Gazebo 系统"
fi
