#!/bin/bash
# 测试物理仿真（无图形界面）

cd /home/dell/aperfect/carbot_ws

# Source Gazebo setup
if [ -f /usr/share/gazebo/setup.sh ]; then
    source /usr/share/gazebo/setup.sh
fi

export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$GAZEBO_MODEL_PATH

source install/setup.bash

echo "启动 Gazebo 物理引擎（无图形界面）..."
echo "这将只启动 gzserver，不启动 gzclient"
echo ""

# 在后台启动 gzserver
gzserver /usr/share/gazebo-11/worlds/empty.world &
GZSERVER_PID=$!

sleep 3

# 启动 robot_state_publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(xacro src/dog2_description/urdf/dog2.urdf.xacro)" &
RSP_PID=$!

sleep 2

# Spawn 机器人
echo "生成机器人..."
ros2 run gazebo_ros spawn_entity.py -entity dog2 -topic robot_description -z 0.5

sleep 3

echo ""
echo "=== 监控机器人位置（20秒）==="
echo "如果 Z 坐标快速增加或变成 NaN，说明机器人'飞'了"
echo ""

for i in {1..20}; do
    echo "--- 时间: ${i}s ---"
    # 尝试获取模型状态
    gz model -m dog2 -p 2>/dev/null | grep -E "pos|orientation" || echo "等待数据..."
    sleep 1
done

echo ""
echo "测试完成。按 Ctrl+C 停止所有进程"
wait
