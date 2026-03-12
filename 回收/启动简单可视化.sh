#!/bin/bash

echo "========================================="
echo "Dog2 简单可视化系统 (无 Gazebo)"
echo "========================================="
echo ""
echo "正在启动："
echo "  ✓ 状态模拟器"
echo "  ✓ MPC 控制器"
echo "  ✓ WBC 控制器"
echo "  ✓ 可视化节点"
echo "  ✓ RViz2"
echo ""
echo "========================================="

source install/setup.bash

# 启动 robot_state_publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat src/dog2_description/urdf/dog2.urdf)" &
sleep 1

# 启动 TF 发布器
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world odom &
sleep 0.5

# 启动 joint_state_publisher
ros2 run joint_state_publisher joint_state_publisher &
sleep 0.5

# 启动状态模拟器
ros2 run dog2_mpc state_simulator &
sleep 1

# 启动 MPC 节点
ros2 run dog2_mpc mpc_node_complete --ros-args -p mode:=walking &
sleep 1

# 启动 WBC 节点
ros2 run dog2_wbc wbc_node_complete &
sleep 1

# 启动可视化节点
python3 -m dog2_visualization.visualization_node &
sleep 1

# 启动 RViz2
ros2 run rviz2 rviz2 -d src/dog2_visualization/config/rviz/dog2_walking.rviz &

echo ""
echo "所有节点已启动！"
echo ""
echo "发送速度命令："
echo "  ros2 topic pub /cmd_vel geometry_msgs/Twist \"{linear: {x: 0.1}}\""
echo ""

wait
