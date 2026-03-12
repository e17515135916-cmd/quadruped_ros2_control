#!/bin/bash
# 在 RViz 中查看碰撞几何体

cd /home/dell/aperfect/carbot_ws
source install/setup.bash

# 杀死之前的进程
killall -9 robot_state_publisher joint_state_publisher_gui rviz2 2>/dev/null
sleep 1

# 启动 RViz 并显示碰撞体
ros2 launch dog2_description view_dog2.launch.py
