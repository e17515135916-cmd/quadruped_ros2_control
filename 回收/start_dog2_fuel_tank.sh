#!/bin/bash
#
# Dog2 油箱环境启动脚本
#
# 在飞机油箱仿真环境中启动 Dog2 机器人，用于穿越测试。
#
# 用法：
#   ./start_dog2_fuel_tank.sh
#
# 环境说明：
#   - 底部有规律交错的桁条网格
#   - 竖直方向有穿越孔面板
#   - 机器人在桁条区域前方生成
#

echo "=================================================="
echo "  Dog2 油箱环境启动脚本"
echo "=================================================="
echo ""
echo "环境特点："
echo "  - 油箱底板桁条网格 (间距: 0.15m, 高度: 0.03m)"
echo "  - 穿越孔面板 (孔尺寸: 0.25m x 0.20m)"
echo "  - 机器人起始位置: 桁条区域前方"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source ROS2 环境
source /opt/ros/humble/setup.bash
source "$SCRIPT_DIR/install/setup.bash"

echo "启动 Gazebo 油箱环境..."
echo ""
echo "控制命令："
echo "  python3 dog2_gazebo_obstacle_crossing.py  # 跨越障碍控制"
echo ""
echo "按 Ctrl+C 退出"
echo "--------------------------------------------------"

# 启动油箱环境
ros2 launch dog2_champ_config dog2_fuel_tank.launch.py
