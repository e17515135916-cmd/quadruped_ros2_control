#!/bin/bash
# 启动 RViz 髋关节轴向验证
#
# 此脚本用于启动 RViz 并加载修改后的机器人模型，
# 以便手动验证髋关节轴向从 Z 轴改为 X 轴。

echo "========================================================================"
echo "RViz 髋关节轴向验证"
echo "========================================================================"
echo ""
echo "此脚本将启动 RViz 和 joint_state_publisher_gui"
echo "用于验证髋关节 (j11, j21, j31, j41) 的轴向修改"
echo ""
echo "验证步骤："
echo "1. RViz 将自动打开"
echo "2. 添加 'RobotModel' 显示（如果尚未添加）"
echo "3. 使用 joint_state_publisher_gui 的滑块调整髋关节角度"
echo "4. 观察髋关节是否绕 X 轴旋转（前后摆动）"
echo ""
echo "预期行为："
echo "✓ 髋关节应该前后摆动（绕 X 轴）"
echo "✓ 视觉外观应该与修改前一致"
echo ""
echo "之前的行为（用于对比）："
echo "✗ 髋关节左右摆动（绕 Z 轴）"
echo ""
echo "========================================================================"
echo ""
read -p "按 Enter 键启动 RViz，或按 Ctrl+C 取消..."

# 确保环境已设置
source install/setup.bash

# 启动 RViz 验证
echo ""
echo "正在启动 RViz..."
ros2 launch verify_hip_axis_rviz.py

echo ""
echo "RViz 已关闭"
