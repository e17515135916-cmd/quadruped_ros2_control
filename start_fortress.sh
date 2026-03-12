#!/bin/bash
# 启动Gazebo Fortress仿真

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  启动Gazebo Fortress仿真${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在工作空间根目录
if [ ! -d "src/dog2_motion_control" ]; then
    echo -e "${RED}错误: 请在工作空间根目录运行此脚本${NC}"
    echo "正确位置: ~/aperfect/carbot_ws"
    exit 1
fi

# 重新编译包（确保启动文件是最新的）
echo -e "${BLUE}1. 重新编译dog2_motion_control包...${NC}"
source /opt/ros/humble/setup.bash
colcon build --packages-select dog2_motion_control --symlink-install
echo -e "${GREEN}✓ 编译完成${NC}"
echo ""

# Source环境
echo -e "${BLUE}2. Source ROS 2环境...${NC}"
source install/setup.bash
echo -e "${GREEN}✓ 环境已加载${NC}"
echo ""

# 检查Gazebo Fortress
echo -e "${BLUE}3. 检查Gazebo Fortress...${NC}"
if command -v gz &> /dev/null; then
    gz_version=$(gz sim --version 2>&1 | head -n 1 || echo "Gazebo Fortress")
    echo -e "${GREEN}✓ Gazebo已安装: $gz_version${NC}"
else
    echo -e "${RED}✗ 未找到Gazebo Fortress (gz命令)${NC}"
    echo ""
    echo "安装Gazebo Fortress:"
    echo "  sudo apt install ros-humble-ros-gz"
    exit 1
fi
echo ""

# 启动仿真
echo -e "${BLUE}4. 启动仿真...${NC}"
echo -e "${YELLOW}提示: Gazebo窗口将会打开${NC}"
echo -e "${YELLOW}      机器人将在3秒后spawn到仿真环境中${NC}"
echo -e "${YELLOW}      控制器将在5-8秒后加载${NC}"
echo -e "${YELLOW}      spider_controller将在10秒后启动${NC}"
echo ""

ros2 launch dog2_motion_control spider_with_fortress.launch.py
