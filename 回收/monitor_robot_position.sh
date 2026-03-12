#!/bin/bash
# 监控机器人位置

echo "监控机器人位置（30秒）..."
echo "如果 Z 坐标快速增加或变成 NaN，说明机器人'飞'了"
echo ""

for i in {1..30}; do
    echo "=== 时间: ${i}s ==="
    gz model -m dog2 -p 2>/dev/null | grep -A 1 "pos" | head -2
    echo ""
    sleep 1
done

echo "监控完成"
