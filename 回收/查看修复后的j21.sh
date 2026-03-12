#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  查看修复后的J21位置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/dell/aperfect/carbot_ws

echo "✓ J21位置已修复"
echo ""
echo "修改内容:"
echo "  Leg 2添加了 hip_xyz=\"0.016 0.0199 0.055\""
echo ""
echo "原理:"
echo "  - Leg 1 (左前): hip_xyz=\"-0.016 0.0199 0.055\""
echo "  - Leg 2 (右前): hip_xyz=\"0.016 0.0199 0.055\" (X取反)"
echo "  - 这样两条前腿就对称了"
echo ""

echo "正在启动RViz..."
killall -9 robot_state_publisher joint_state_publisher rviz2 2>/dev/null
sleep 1

source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py &

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ RViz已启动"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请在RViz中检查:"
echo "  1. Leg 2的j21位置是否正确"
echo "  2. 两条前腿是否对称"
echo "  3. 所有关节是否在正确位置"
echo ""
