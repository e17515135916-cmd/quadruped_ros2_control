#!/bin/bash
# 启动 Gazebo 图形界面

cd /home/dell/aperfect/carbot_ws

# 设置 Gazebo 环境变量
if [ -f /usr/share/gazebo/setup.sh ]; then
    source /usr/share/gazebo/setup.sh
fi

export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$GAZEBO_MODEL_PATH

# Source ROS 2 workspace
source install/setup.bash

echo "========================================="
echo "启动 Gazebo 图形界面"
echo "========================================="
echo ""
echo "提示："
echo "1. 如果卡在 logo 界面，请耐心等待 30-60 秒"
echo "2. 碰撞体已简化为 cylinder，加载应该更快"
echo "3. 如果仍然卡住，按 Ctrl+C 停止"
echo ""
echo "启动中..."
echo ""

ros2 launch dog2_description view_dog2_gazebo.launch.py
