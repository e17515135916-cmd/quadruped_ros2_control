#!/bin/bash
# 修复 Gazebo 图形问题

echo "修复 Gazebo 环境变量..."

# Source Gazebo setup
if [ -f /usr/share/gazebo/setup.sh ]; then
    source /usr/share/gazebo/setup.sh
    echo "✓ Sourced /usr/share/gazebo/setup.sh"
fi

# 设置 Gazebo 资源路径
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$GAZEBO_MODEL_PATH

echo "当前 GAZEBO_RESOURCE_PATH: $GAZEBO_RESOURCE_PATH"
echo "当前 GAZEBO_MODEL_PATH: $GAZEBO_MODEL_PATH"

# 测试 Gazebo
echo ""
echo "测试 Gazebo（将打开空世界）..."
echo "如果成功打开，说明图形驱动正常"
echo "按 Ctrl+C 关闭"

gazebo --verbose
