#!/bin/bash
# 持续监控机器人位置

echo "持续监控机器人位置（30秒）..."
echo "Z 坐标应该在 0.3-0.5 之间（机器人站立）"
echo ""

for i in {1..30}; do
    POS=$(timeout 1 gz topic -e /gazebo/default/pose/info 2>&1 | grep -A 6 "name: \"dog2\"" | grep "position" -A 3 | grep -E "x:|y:|z:" | head -3)
    if [ -n "$POS" ]; then
        echo "[$i秒] $POS"
    else
        echo "[$i秒] 等待数据..."
    fi
    sleep 1
done

echo ""
echo "监控完成"
