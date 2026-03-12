#!/bin/bash
# 激活 joint_trajectory_controller

echo "=========================================="
echo "激活 joint_trajectory_controller"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "正在激活控制器..."
ros2 control set_controller_state joint_trajectory_controller active 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 控制器激活成功"
    echo ""
    echo "验证状态："
    ros2 control list_controllers
    echo ""
    echo "=========================================="
    echo "现在可以测试键盘控制了！"
    echo "=========================================="
    echo ""
    echo "运行: ./start_keyboard_control.sh"
    echo "然后按 W 键向前移动"
else
    echo ""
    echo "❌ 激活失败，请检查错误信息"
    echo ""
    echo "可能的原因："
    echo "1. Gazebo 未运行"
    echo "2. controller_manager 未就绪"
    echo "3. 控制器配置有误"
    echo ""
    echo "请检查 Gazebo 终端的日志输出"
fi
