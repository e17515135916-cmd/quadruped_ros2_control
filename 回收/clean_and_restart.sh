#!/bin/bash
# 彻底清理残留进程并重新启动

echo "=========================================="
echo "清理残留进程"
echo "=========================================="
echo ""

# 1. 停止所有 Gazebo 相关进程
echo "1. 停止 Gazebo 进程..."
pkill -9 -f "gz sim" 2>/dev/null
pkill -9 -f "ign gazebo" 2>/dev/null
pkill -9 -f "ruby.*gz" 2>/dev/null
sleep 1

# 2. 停止所有 ROS 2 节点
echo "2. 停止 ROS 2 节点..."
pkill -9 -f "ros2" 2>/dev/null
pkill -9 -f "controller_manager" 2>/dev/null
pkill -9 -f "quadruped_controller" 2>/dev/null
pkill -9 -f "robot_state_publisher" 2>/dev/null
pkill -9 -f "state_estimation" 2>/dev/null
pkill -9 -f "ekf_node" 2>/dev/null
sleep 1

# 3. 清理共享内存
echo "3. 清理共享内存..."
rm -f /dev/shm/sem.* 2>/dev/null
rm -f /dev/shm/gz-* 2>/dev/null

# 4. 验证清理结果
echo ""
echo "4. 验证清理结果..."
if pgrep -f "gz sim\|ign gazebo\|ros2" > /dev/null; then
    echo "⚠️  警告：仍有进程残留"
    echo "残留进程："
    pgrep -af "gz sim\|ign gazebo\|ros2"
else
    echo "✅ 所有进程已清理"
fi

echo ""
echo "=========================================="
echo "清理完成！"
echo "=========================================="
echo ""
echo "现在可以重新启动 Gazebo："
echo "  ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py"
echo ""
echo "或者运行完整测试："
echo "  ./full_system_test.sh"
