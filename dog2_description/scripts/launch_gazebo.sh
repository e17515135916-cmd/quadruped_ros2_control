#!/bin/bash

# 杀死所有Gazebo相关进程
pkill -9 -f gazebo
pkill -9 -f gzserver
pkill -9 -f gzclient

# 等待进程完全终止
sleep 2

# 设置环境变量
export GAZEBO_MODEL_PATH=$(ros2 pkg prefix --share dog2_description)/meshes:$GAZEBO_MODEL_PATH

# Xacro 文件路径（统一入口）
XACRO_PATH=$(ros2 pkg prefix --share dog2_description)/urdf/dog2.urdf.xacro

# 先启动只有gzserver的Gazebo
ros2 run gazebo_ros gzserver --verbose &

# 等待服务器启动
sleep 5

# 启动客户端
ros2 run gazebo_ros gzclient &

# 等待客户端启动
sleep 5

# 启动机器人状态发布器
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(xacro $XACRO_PATH | sed 's/<?xml version="1.0" encoding="utf-8"?>//')" &

# 等待机器人状态准备好
sleep 2

# 生成机器人
ros2 run gazebo_ros spawn_entity.py -entity dog2 -topic robot_description -z 0.4

echo "Gazebo and dog2 model launched." 