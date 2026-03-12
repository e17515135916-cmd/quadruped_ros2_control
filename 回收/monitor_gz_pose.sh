#!/bin/bash
# 监控 Gazebo 中机器人的 pose

echo "监控机器人 pose（20秒）..."
echo ""

for i in {1..20}; do
    echo "=== 时间: ${i}s ==="
    gz topic -e /gazebo/default/pose/info -d 0.1 2>&1 | grep -A 10 "name: \"dog2\"" | grep -E "name:|position" | head -5
    echo ""
    sleep 1
done

echo "监控完成"
