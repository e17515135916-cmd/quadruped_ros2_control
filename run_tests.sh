#!/bin/bash
# 快速测试脚本 - 从工作空间根目录运行

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  蜘蛛机器人 - 快速测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在工作空间根目录
if [ ! -d "src/dog2_motion_control" ]; then
    echo -e "${YELLOW}错误: 请在工作空间根目录运行此脚本${NC}"
    echo "正确位置: ~/aperfect/carbot_ws"
    echo ""
    echo "使用方法:"
    echo "  cd ~/aperfect/carbot_ws"
    echo "  bash run_tests.sh"
    exit 1
fi

# Source环境
echo -e "${BLUE}1. Source ROS 2环境...${NC}"
source /opt/ros/humble/setup.bash
source install/setup.bash
echo -e "${GREEN}✓ 环境已加载${NC}"
echo ""

# 运行单元测试
echo -e "${BLUE}2. 运行单元测试...${NC}"
cd src/dog2_motion_control
python3 -m pytest test/ -v --tb=short -q
echo ""

# 运行验证脚本
echo -e "${BLUE}3. 运行系统验证...${NC}"
bash verify_final_checkpoint.sh
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "下一步："
echo "1. 启动Gazebo仿真："
echo "   ros2 launch dog2_motion_control spider_gazebo_complete.launch.py"
echo ""
echo "2. 发送速度命令："
echo "   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \\"
echo "     \"{linear: {x: 0.05, y: 0.0, z: 0.0}}\" --once"
echo ""
