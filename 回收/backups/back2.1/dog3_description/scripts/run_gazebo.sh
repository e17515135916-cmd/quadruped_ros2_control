#!/bin/bash

# 杀死所有可能的Gazebo进程
echo "关闭所有Gazebo进程..."
pkill -9 -f gazebo
pkill -9 -f gzserver
pkill -9 -f gzclient
sleep 2

# 设置环境变量
echo "设置环境变量..."
export LIBGL_ALWAYS_SOFTWARE=1  # 强制使用软件渲染
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:/usr/share/gazebo-11/models
export GAZEBO_MODEL_PATH=$(ros2 pkg prefix --share dog2_description)/meshes:$GAZEBO_MODEL_PATH

# 获取Xacro文件路径（统一入口）
XACRO_PATH=$(ros2 pkg prefix --share dog2_description)/urdf/dog2.urdf.xacro
echo "Xacro路径: $XACRO_PATH"

# 启动Gazebo服务器
echo "启动Gazebo服务器..."
ros2 run gazebo_ros gzserver --verbose &
SERVER_PID=$!
echo "Gazebo服务器PID: $SERVER_PID"
sleep 5

# 启动机器人状态发布器
echo "启动机器人状态发布器..."
# 生成URDF并移除XML声明
ROBOT_DESC=$(xacro $XACRO_PATH | sed 's/<?xml version="1.0" encoding="utf-8"?>//')
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$ROBOT_DESC" &
RSP_PID=$!
echo "机器人状态发布器PID: $RSP_PID"
sleep 2

# 生成机器人
echo "在Gazebo中生成机器人..."
ros2 run gazebo_ros spawn_entity.py -entity dog2 -topic robot_description -z 0.4
sleep 2

# 启动Gazebo客户端
echo "启动Gazebo客户端..."
ros2 run gazebo_ros gzclient &
CLIENT_PID=$!
echo "Gazebo客户端PID: $CLIENT_PID"

echo "所有进程已启动，按Ctrl+C终止"
wait $CLIENT_PID 