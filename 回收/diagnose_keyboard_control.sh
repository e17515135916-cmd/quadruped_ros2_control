#!/bin/bash
# 诊断键盘控制问题

echo "=========================================="
echo "Dog2 键盘控制诊断工具"
echo "=========================================="
echo ""

# 检查 ROS 2 节点
echo "1. 检查运行的节点..."
echo "-------------------------------------------"
ros2 node list 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 无法获取节点列表 - ROS 2 可能未运行"
    exit 1
fi
echo ""

# 检查 /cmd_vel 话题
echo "2. 检查 /cmd_vel 话题..."
echo "-------------------------------------------"
if ros2 topic list 2>/dev/null | grep -q "/cmd_vel"; then
    echo "✅ /cmd_vel 话题存在"
    
    # 检查话题信息
    echo ""
    echo "话题信息:"
    ros2 topic info /cmd_vel
    
    # 检查是否有订阅者
    echo ""
    echo "订阅者数量:"
    ros2 topic info /cmd_vel | grep "Subscription count"
else
    echo "❌ /cmd_vel 话题不存在"
fi
echo ""

# 检查 CHAMP 控制器
echo "3. 检查 CHAMP quadruped_controller..."
echo "-------------------------------------------"
if ros2 node list 2>/dev/null | grep -q "quadruped_controller"; then
    echo "✅ quadruped_controller 正在运行"
    
    # 检查节点信息
    echo ""
    echo "节点信息:"
    ros2 node info /quadruped_controller 2>/dev/null | head -20
else
    echo "❌ quadruped_controller 未运行"
fi
echo ""

# 检查 ros2_control 控制器
echo "4. 检查 ros2_control 控制器..."
echo "-------------------------------------------"
if command -v ros2 &> /dev/null; then
    ros2 control list_controllers 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ 无法获取控制器列表"
    fi
else
    echo "❌ ros2 命令不可用"
fi
echo ""

# 检查关节状态
echo "5. 检查关节状态话题..."
echo "-------------------------------------------"
if ros2 topic list 2>/dev/null | grep -q "/joint_states"; then
    echo "✅ /joint_states 话题存在"
    echo ""
    echo "最近的关节状态（前5行）:"
    timeout 2 ros2 topic echo /joint_states --once 2>/dev/null | head -5
else
    echo "❌ /joint_states 话题不存在"
fi
echo ""

# 检查 Gazebo
echo "6. 检查 Gazebo 进程..."
echo "-------------------------------------------"
if pgrep -f "gz sim" > /dev/null; then
    echo "✅ Gazebo 正在运行"
else
    echo "❌ Gazebo 未运行"
fi
echo ""

# 测试发布速度命令
echo "7. 测试发布速度命令..."
echo "-------------------------------------------"
echo "尝试发布测试命令到 /cmd_vel..."
timeout 1 ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 成功发布测试命令"
else
    echo "❌ 无法发布命令"
fi
echo ""

# 检查关键话题的发布频率
echo "8. 检查话题发布频率..."
echo "-------------------------------------------"
echo "检查 /cmd_vel 发布频率（5秒）..."
timeout 5 ros2 topic hz /cmd_vel 2>/dev/null &
HZ_PID=$!
sleep 5
kill $HZ_PID 2>/dev/null
echo ""

# 总结
echo "=========================================="
echo "诊断总结"
echo "=========================================="
echo ""
echo "请检查以上输出，特别注意："
echo "1. quadruped_controller 是否运行"
echo "2. /cmd_vel 话题是否有订阅者"
echo "3. ros2_control 控制器是否 active"
echo "4. joint_states 是否正常发布"
echo ""
echo "如果发现问题，请查看启动日志获取更多信息"
