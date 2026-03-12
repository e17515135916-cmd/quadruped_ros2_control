#!/bin/bash
# 测试 Gazebo 物理仿真（无图形界面）

cd /home/dell/aperfect/carbot_ws
source install/setup.bash

# 启动 gzserver（无图形界面）
ros2 launch dog2_description gazebo_dog2_final.launch.py &

# 等待启动
sleep 10

# 监控机器人位置
echo "监控机器人基座位置（10秒）..."
for i in {1..10}; do
    echo "=== 时间: ${i}s ==="
    ros2 topic echo /model/dog2/pose --once 2>/dev/null || echo "等待 topic..."
    sleep 1
done

echo "测试完成"
