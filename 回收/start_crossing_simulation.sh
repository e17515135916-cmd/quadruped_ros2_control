#!/bin/bash

# Dog2 MPC+WBC 越障仿真启动脚本

echo "=========================================="
echo "  Dog2 MPC+WBC 越障仿真"
echo "=========================================="
echo ""
echo "系统组件："
echo "  ✅ Gazebo 仿真环境"
echo "  ✅ 16维MPC控制器（滑动副约束）"
echo "  ✅ 完整WBC控制器（精确雅可比）"
echo "  ✅ 越障状态机（8阶段）"
echo "  ✅ 混合步态生成器"
echo ""

# 进入工作空间
cd /home/dell/aperfect/carbot_ws

# 设置环境
source install/setup.bash

echo "启动完整仿真系统（越障模式）..."
echo ""
echo "预期行为："
echo "  1. Gazebo窗口打开，Dog2出现在场景中"
echo "  2. MPC节点开始运行（16维状态控制）"
echo "  3. WBC节点开始运行（力矩分配）"
echo "  4. 机器人保持悬停状态"
echo ""
echo "触发越障："
echo "  在新终端运行："
echo "  ros2 topic pub --once /enable_crossing std_msgs/Bool \"data: true\""
echo ""
echo "按Ctrl+C停止仿真"
echo "=========================================="
echo ""

# 启动仿真
ros2 launch dog2_mpc complete_simulation.launch.py mode:=crossing

