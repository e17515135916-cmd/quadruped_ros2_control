#!/bin/bash
# 蜘蛛机器人快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}蜘蛛机器人快速启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查ROS 2环境
if [ -z "$ROS_DISTRO" ]; then
    echo -e "${RED}错误: ROS 2环境未设置${NC}"
    echo "请先运行: source /opt/ros/humble/setup.bash"
    exit 1
fi

echo -e "${GREEN}✓ ROS 2环境已设置 ($ROS_DISTRO)${NC}"

# 检查工作空间
if [ ! -f "install/setup.bash" ]; then
    echo -e "${YELLOW}警告: 工作空间未编译${NC}"
    echo "正在编译工作空间..."
    colcon build --packages-select dog2_motion_control
    if [ $? -ne 0 ]; then
        echo -e "${RED}编译失败${NC}"
        exit 1
    fi
fi

# Source工作空间
source install/setup.bash
echo -e "${GREEN}✓ 工作空间已加载${NC}"
echo ""

# 显示菜单
echo "请选择启动模式:"
echo "1) 完整仿真（Gazebo + 控制器）"
echo "2) 仿真 + RViz可视化"
echo "3) 仅控制器（需要已运行的Gazebo）"
echo "4) 快速测试模式（快速步态）"
echo "5) 稳定模式（慢速稳定步态）"
echo "6) 无头模式（无GUI）"
echo ""
read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo -e "${GREEN}启动完整仿真...${NC}"
        ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
        ;;
    2)
        echo -e "${GREEN}启动仿真 + RViz...${NC}"
        ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py
        ;;
    3)
        echo -e "${GREEN}启动控制器...${NC}"
        ros2 launch dog2_motion_control spider_controller.launch.py use_sim_time:=true
        ;;
    4)
        echo -e "${GREEN}启动快速测试模式...${NC}"
        CONFIG_FILE=$(ros2 pkg prefix dog2_motion_control)/share/dog2_motion_control/config/gait_params_fast.yaml
        ros2 launch dog2_motion_control spider_gazebo_rviz.launch.py config_file:=$CONFIG_FILE
        ;;
    5)
        echo -e "${GREEN}启动稳定模式...${NC}"
        CONFIG_FILE=$(ros2 pkg prefix dog2_motion_control)/share/dog2_motion_control/config/gait_params_stable.yaml
        ros2 launch dog2_motion_control spider_gazebo_complete.launch.py config_file:=$CONFIG_FILE
        ;;
    6)
        echo -e "${GREEN}启动无头模式...${NC}"
        ros2 launch dog2_motion_control spider_gazebo_complete.launch.py use_gui:=false
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac
