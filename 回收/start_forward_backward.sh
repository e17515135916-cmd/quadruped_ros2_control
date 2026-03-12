#!/bin/bash
# Dog2 前进后退演示启动脚本

echo "🐕 Dog2 前进后退演示"
echo "===================="
echo ""
echo "这个脚本会："
echo "1. 启动 Gazebo Fortress 仿真"
echo "2. 加载 Dog2 机器人"
echo "3. 执行前进和后退运动"
echo ""
echo "请确保你已经编译了工作空间："
echo "  cd ~/aperfect/carbot_ws"
echo "  colcon build"
echo "  source install/setup.bash"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# 设置环境
cd ~/aperfect/carbot_ws
source install/setup.bash

# 启动 Gazebo 和机器人（后台运行）
echo "🚀 启动 Gazebo Fortress..."
ros2 launch dog2_description dog2_fortress_with_control.launch.py &
LAUNCH_PID=$!

# 等待 Gazebo 启动
echo "⏳ 等待 Gazebo 启动 (10秒)..."
sleep 10

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

# 运行前进后退演示
echo "🎬 开始前进后退演示..."
python3 forward_backward_demo.py

# 演示完成后保持 Gazebo 运行
echo ""
echo "✅ 演示完成！"
echo ""
echo "Gazebo 仍在运行，你可以："
echo "  - 查看机器人的位置变化"
echo "  - 再次运行: python3 forward_backward_demo.py"
echo "  - 按 Ctrl+C 退出"
echo ""

# 等待用户中断
wait $LAUNCH_PID
