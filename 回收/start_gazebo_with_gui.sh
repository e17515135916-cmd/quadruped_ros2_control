#!/bin/bash
# 启动 Gazebo 并显示 GUI，然后测试机器人运动

echo "🐕 Dog2 Gazebo 可视化测试"
echo "========================"
echo ""
echo "这个脚本会："
echo "1. 停止现有的 Gazebo 进程"
echo "2. 启动 Gazebo Fortress 带 GUI"
echo "3. 加载 Dog2 机器人"
echo "4. 测试腿部运动"
echo ""

cd ~/aperfect/carbot_ws
source install/setup.bash

# 停止现有的 Gazebo 进程
echo "🛑 停止现有的 Gazebo 进程..."
pkill -9 -f "gz sim" || true
pkill -9 -f "ign gazebo" || true
pkill -9 -f "gazebo" || true
sleep 2

# 启动 Gazebo 带 GUI
echo "🚀 启动 Gazebo Fortress (带 GUI)..."
ros2 launch dog2_description dog2_fortress_with_control.launch.py &
LAUNCH_PID=$!

echo "⏳ 等待 Gazebo 启动 (15秒)..."
sleep 15

# 检查 Gazebo 是否成功启动
if ! ps -p $LAUNCH_PID > /dev/null; then
    echo "❌ Gazebo 启动失败"
    exit 1
fi

echo "✅ Gazebo 已启动"
echo ""

# 等待控制器准备好
echo "⏳ 等待控制器准备 (5秒)..."
sleep 5

# 运行测试
echo "🎬 开始腿部运动测试..."
echo ""
echo "请观察 Gazebo 窗口中的机器人："
echo "  - 机器人应该会抬起不同的腿"
echo "  - 测试对角步态"
echo ""

python3 test_correct_joints.py

echo ""
echo "✅ 测试完成！"
echo ""
echo "Gazebo 仍在运行。"
echo "按 Ctrl+C 退出"
echo ""

# 等待用户中断
wait $LAUNCH_PID
