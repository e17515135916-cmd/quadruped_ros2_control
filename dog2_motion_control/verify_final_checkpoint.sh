#!/bin/bash
# 最终检查点验证脚本
# 任务15: 验证系统完整性

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  蜘蛛机器人基础运动算法 - 最终检查点"
echo "=========================================="
echo ""

# 检查计数
total_checks=0
passed_checks=0
failed_checks=0

check_item() {
    local name=$1
    local result=$2
    total_checks=$((total_checks + 1))
    
    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $name"
        passed_checks=$((passed_checks + 1))
    elif [ "$result" = "fail" ]; then
        echo -e "${RED}✗${NC} $name"
        failed_checks=$((failed_checks + 1))
    else
        echo -e "${YELLOW}⚠${NC} $name"
    fi
}

echo "1. 核心模块检查"
echo "-------------------"

# 检查Python模块
if python3 -c "from dog2_motion_control.kinematics_solver import KinematicsSolver" 2>/dev/null; then
    check_item "运动学求解器模块" "pass"
else
    check_item "运动学求解器模块" "fail"
fi

if python3 -c "from dog2_motion_control.gait_generator import GaitGenerator" 2>/dev/null; then
    check_item "步态生成器模块" "pass"
else
    check_item "步态生成器模块" "fail"
fi

if python3 -c "from dog2_motion_control.trajectory_planner import TrajectoryPlanner" 2>/dev/null; then
    check_item "轨迹规划器模块" "pass"
else
    check_item "轨迹规划器模块" "fail"
fi

if python3 -c "from dog2_motion_control.joint_controller import JointController" 2>/dev/null; then
    check_item "关节控制器模块" "pass"
else
    check_item "关节控制器模块" "fail"
fi

if python3 -c "from dog2_motion_control.spider_robot_controller import SpiderRobotController" 2>/dev/null; then
    check_item "主控制器模块" "pass"
else
    check_item "主控制器模块" "fail"
fi

if python3 -c "from dog2_motion_control.config_loader import ConfigLoader" 2>/dev/null; then
    check_item "配置加载器模块" "pass"
else
    check_item "配置加载器模块" "fail"
fi

echo ""
echo "2. 配置文件检查"
echo "-------------------"

if [ -f "config/gait_params.yaml" ]; then
    check_item "步态参数配置文件" "pass"
else
    check_item "步态参数配置文件" "fail"
fi

if [ -f "config/spider_robot.rviz" ]; then
    check_item "RViz配置文件" "pass"
else
    check_item "RViz配置文件" "fail"
fi

echo ""
echo "3. 启动文件检查"
echo "-------------------"

if [ -f "launch/spider_gazebo_complete.launch.py" ]; then
    check_item "Gazebo完整启动文件" "pass"
else
    check_item "Gazebo完整启动文件" "fail"
fi

echo ""
echo "4. 单元测试检查"
echo "-------------------"

# 运行核心测试
echo "运行核心单元测试..."
if python3 -m pytest test/test_kinematics.py -q --tb=no 2>&1 | grep -q "passed"; then
    check_item "运动学测试" "pass"
else
    check_item "运动学测试" "fail"
fi

if python3 -m pytest test/test_gait_generator.py -q --tb=no 2>&1 | grep -q "passed"; then
    check_item "步态生成器测试" "pass"
else
    check_item "步态生成器测试" "fail"
fi

if python3 -m pytest test/test_config_loader.py -q --tb=no 2>&1 | grep -q "passed"; then
    check_item "配置加载器测试" "pass"
else
    check_item "配置加载器测试" "fail"
fi

if python3 -m pytest test/test_system_integration.py -q --tb=no 2>&1 | grep -q "passed"; then
    check_item "系统集成测试" "pass"
else
    check_item "系统集成测试" "fail"
fi

echo ""
echo "5. 文档检查"
echo "-------------------"

if [ -f "FINAL_CHECKPOINT_REPORT.md" ]; then
    check_item "最终检查点报告" "pass"
else
    check_item "最终检查点报告" "fail"
fi

if [ -f "README.md" ]; then
    check_item "README文档" "pass"
else
    check_item "README文档" "fail"
fi

echo ""
echo "=========================================="
echo "  检查总结"
echo "=========================================="
echo ""
echo -e "总检查项: $total_checks"
echo -e "${GREEN}通过: $passed_checks${NC}"
echo -e "${RED}失败: $failed_checks${NC}"
echo ""

# 计算通过率
pass_rate=$((passed_checks * 100 / total_checks))

if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！系统就绪。${NC}"
    echo ""
    echo "下一步："
    echo "1. 启动Gazebo仿真环境："
    echo "   ros2 launch dog2_motion_control spider_gazebo_complete.launch.py"
    echo ""
    echo "2. 在另一个终端运行集成测试："
    echo "   cd test && bash run_integration_tests.sh"
    echo ""
    exit 0
else
    echo -e "${RED}✗ 有 $failed_checks 项检查失败。${NC}"
    echo ""
    echo "请检查失败项并修复。"
    exit 1
fi
