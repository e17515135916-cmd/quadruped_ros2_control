#!/bin/bash

# 杀死所有Gazebo相关进程
pkill -9 -f gazebo
pkill -9 -f gzserver
pkill -9 -f gzclient

# 等待进程完全终止
sleep 2

# 启动Gazebo（不使用GUI，只用服务器）
ros2 run gazebo_ros gzserver --verbose &
SERVER_PID=$!
echo "Started gzserver with PID: $SERVER_PID"

# 等待服务器启动
sleep 5

# 使用简单的字符串作为机器人模型
SIMPLE_URDF='<?xml version="1.0"?><robot name="simple_box"><link name="base_link"><visual><geometry><box size="0.2 0.3 0.1"/></geometry><material name="red"><color rgba="1 0 0 1"/></material></visual><collision><geometry><box size="0.2 0.3 0.1"/></geometry></collision><inertial><mass value="1"/><inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/></inertial></link><gazebo reference="base_link"><material>Gazebo/Red</material></gazebo></robot>'

# 创建临时文件
TEMP_URDF=$(mktemp)
echo "$SIMPLE_URDF" > $TEMP_URDF

# 发布机器人状态
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$SIMPLE_URDF" &
RSP_PID=$!
echo "Started robot_state_publisher with PID: $RSP_PID"

# 等待机器人状态准备好
sleep 2

# 生成机器人实体
ros2 run gazebo_ros spawn_entity.py -entity simple_box -topic robot_description -z 0.5 &
SPAWN_PID=$!
echo "Started spawn_entity with PID: $SPAWN_PID"

# 等待生成过程完成
sleep 5

# 启动Gazebo客户端
ros2 run gazebo_ros gzclient &
CLIENT_PID=$!
echo "Started gzclient with PID: $CLIENT_PID"

echo "Press Ctrl+C to terminate all processes"
wait $CLIENT_PID 