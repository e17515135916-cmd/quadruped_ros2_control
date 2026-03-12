#!/bin/bash
# 启动 Gazebo 并加载 DOG2 机器人

cd /home/dell/aperfect/carbot_ws

# Source Gazebo setup
if [ -f /usr/share/gazebo/setup.sh ]; then
    source /usr/share/gazebo/setup.sh
fi

# 设置 Gazebo 资源路径
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$GAZEBO_MODEL_PATH

# Source ROS 2 workspace
source install/setup.bash

echo "启动 Gazebo 并加载 DOG2 机器人..."
echo "GAZEBO_RESOURCE_PATH: $GAZEBO_RESOURCE_PATH"
echo ""

# 启动 Gazebo
ros2 launch dog2_description view_dog2_gazebo.launch.py
