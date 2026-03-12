#!/bin/bash
# 修复的 RViz 启动脚本

source install/setup.bash

echo "编译 URDF..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2.urdf

echo "✓ URDF 编译成功"
echo "  Link 数量: $(grep -c '<link name=' /tmp/dog2.urdf)"
echo "  Joint 数量: $(grep -c '<joint name=' /tmp/dog2.urdf)"
echo ""

# 使用 launch 文件启动（避免命令行参数过长）
echo "启动 RViz..."
ros2 launch launch_champ_rviz_test.py

