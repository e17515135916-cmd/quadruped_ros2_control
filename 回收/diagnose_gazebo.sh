#!/bin/bash
# 诊断 Gazebo 图形问题

echo "=== Gazebo 诊断 ==="
echo ""

echo "1. 检查 Gazebo 版本："
gazebo --version 2>&1 | head -3
echo ""

echo "2. 检查 DISPLAY："
echo "DISPLAY=$DISPLAY"
echo ""

echo "3. 检查 Gazebo 资源路径："
if [ -f /usr/share/gazebo/setup.sh ]; then
    source /usr/share/gazebo/setup.sh
fi
echo "GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH"
echo "GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH"
echo ""

echo "4. 检查 rtshaderlib："
ls -la /usr/share/gazebo-11/media/rtshaderlib/ | wc -l
echo "着色器文件数量: $(ls /usr/share/gazebo-11/media/rtshaderlib/*.glsl 2>/dev/null | wc -l)"
echo ""

echo "5. 测试 Gazebo 空世界（5秒）："
timeout 5 gazebo --verbose 2>&1 | grep -E "Err|Wrn|Loading" | head -20
echo ""

echo "诊断完成"
