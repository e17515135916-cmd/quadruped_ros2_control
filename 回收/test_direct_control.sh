#!/bin/bash
# 测试直接控制机器人（跳过 CHAMP）

echo "=========================================="
echo "测试直接控制机器人"
echo "=========================================="
echo ""

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "这个测试会跳过 CHAMP，直接使用 ros2_control 控制机器人"
echo ""

echo "步骤 1: 检查 joint_trajectory_controller 是否激活..."
CONTROLLER_STATUS=$(ros2 control list_controllers 2>/dev/null | grep joint_trajectory_controller | awk '{print $NF}')

if [ "$CONTROLLER_STATUS" != "active" ]; then
    echo "❌ joint_trajectory_controller 未激活"
    echo "   当前状态: $CONTROLLER_STATUS"
    echo ""
    echo "请确保 Gazebo 正在运行："
    echo "  ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py"
    exit 1
fi

echo "✅ joint_trajectory_controller 已激活"
echo ""

echo "步骤 2: 发送测试命令到左前腿髋关节..."
echo "命令: 将 lf_hfe_joint 移动到 0.5 弧度（约 28.6 度）"
echo ""

ros2 topic pub /joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{
    joint_names: ['lf_hfe_joint'],
    points: [{
      positions: [0.5],
      time_from_start: {sec: 2, nanosec: 0}
    }]
  }" --once

echo ""
echo "=========================================="
echo "测试命令已发送！"
echo "=========================================="
echo ""
echo "请观察 Gazebo 中的机器人："
echo "  - 左前腿（左边前面的腿）应该向前移动"
echo "  - 移动应该在 2 秒内完成"
echo ""
echo "如果看到腿移动了："
echo "  ✅ ros2_control 工作正常！"
echo "  → 可以跳过 CHAMP，直接实现简单的运动控制"
echo ""
echo "如果腿没有移动："
echo "  ❌ ros2_control 可能有问题"
echo "  → 需要进一步诊断"
echo ""
echo "想测试所有腿吗？运行:"
echo "  ./test_all_legs.sh"
echo ""
