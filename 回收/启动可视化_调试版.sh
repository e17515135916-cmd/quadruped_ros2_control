#!/bin/bash

echo "========================================="
echo "Dog2 可视化系统 - 调试版"
echo "========================================="
echo ""

source install/setup.bash

# 清理之前的进程
echo "清理之前的进程..."
pkill -9 -f "ros2|rviz|state_simulator|mpc_node|wbc_node" 2>/dev/null
sleep 2

echo "正在启动系统组件..."
echo ""

# 1. 启动 robot_state_publisher
echo "[1/8] 启动 robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat src/dog2_description/urdf/dog2.urdf)" \
    > /tmp/dog2_robot_state_publisher.log 2>&1 &
sleep 1

# 2. 启动 TF 发布器: world -> odom
echo "[2/8] 启动 TF: world -> odom..."
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world odom \
    > /tmp/dog2_tf_world_odom.log 2>&1 &
sleep 0.5

# 3. 启动 joint_state_publisher
echo "[3/8] 启动 joint_state_publisher..."
ros2 run joint_state_publisher joint_state_publisher \
    > /tmp/dog2_joint_state_publisher.log 2>&1 &
sleep 0.5

# 4. 启动状态模拟器
echo "[4/8] 启动 state_simulator..."
ros2 run dog2_mpc state_simulator \
    > /tmp/dog2_state_simulator.log 2>&1 &
sleep 1

# 5. 启动 MPC 节点
echo "[5/8] 启动 MPC 控制器..."
ros2 run dog2_mpc mpc_node_complete --ros-args -p mode:=walking \
    > /tmp/dog2_mpc.log 2>&1 &
sleep 1

# 6. 启动 WBC 节点
echo "[6/8] 启动 WBC 控制器..."
ros2 run dog2_wbc wbc_node_complete \
    > /tmp/dog2_wbc.log 2>&1 &
sleep 1

# 7. 启动可视化节点
echo "[7/8] 启动可视化节点..."
python3 -m dog2_visualization.visualization_node \
    > /tmp/dog2_visualization.log 2>&1 &
sleep 1

# 8. 启动 RViz2
echo "[8/8] 启动 RViz2..."
ros2 run rviz2 rviz2 -d src/dog2_visualization/config/rviz/dog2_walking.rviz \
    > /tmp/dog2_rviz2.log 2>&1 &
sleep 2

echo ""
echo "========================================="
echo "✓ 所有节点已启动！"
echo "========================================="
echo ""
echo "日志文件位置："
echo "  /tmp/dog2_*.log"
echo ""
echo "检查系统状态："
echo "  ros2 node list"
echo "  ros2 topic list"
echo ""
echo "发送速度命令（在新终端中）："
echo "  source install/setup.bash"
echo "  ros2 topic pub /cmd_vel geometry_msgs/Twist \"{linear: {x: 0.1}}\""
echo ""
echo "查看机器人位置："
echo "  ros2 topic echo /dog2/odom | grep -A 3 'position:'"
echo ""
echo "查看日志："
echo "  tail -f /tmp/dog2_state_simulator.log"
echo "  tail -f /tmp/dog2_mpc.log"
echo ""
echo "停止系统："
echo "  pkill -9 -f 'ros2|rviz|state_simulator|mpc_node|wbc_node'"
echo ""
echo "========================================="

# 等待5秒后自动发送测试命令
echo "5秒后将自动发送测试速度命令..."
sleep 5

echo ""
echo "发送测试命令: vx=0.1 m/s"
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.1}}" &
CMD_PID=$!

echo ""
echo "等待3秒，然后检查位置..."
sleep 3

echo ""
echo "当前机器人位置："
ros2 topic echo /dog2/odom --once | grep -A 5 "position:"

echo ""
echo "========================================="
echo "如果位置的 x 值在增加，说明系统工作正常！"
echo "如果 RViz2 中看不到机器人移动，请检查："
echo "  1. RViz2 的 Fixed Frame 是否设置为 'odom' 或 'world'"
echo "  2. RobotModel 显示是否已启用"
echo "  3. TF 显示是否已启用"
echo "========================================="
echo ""

# 保持脚本运行
wait
