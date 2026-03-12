#!/bin/bash
# 验证任务13的所有文件是否已创建

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "任务13文件验证脚本"
echo "========================================="
echo ""

ERRORS=0

# 检查启动文件
echo "检查启动文件..."
FILES=(
    "launch/spider_controller.launch.py"
    "launch/spider_gazebo_complete.launch.py"
    "launch/spider_gazebo_rviz.launch.py"
)

for file in "${FILES[@]}"; do
    if [ -f "src/dog2_motion_control/$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "检查配置文件..."
FILES=(
    "config/gait_params.yaml"
    "config/gait_params_fast.yaml"
    "config/gait_params_stable.yaml"
    "config/spider_robot.rviz"
    "config/spider_robot_simple.rviz"
)

for file in "${FILES[@]}"; do
    if [ -f "src/dog2_motion_control/$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "检查文档..."
FILES=(
    "LAUNCH_FILES_GUIDE.md"
    "TASK_13_LAUNCH_CONFIG_COMPLETION.md"
    "QUICK_START.md"
)

for file in "${FILES[@]}"; do
    if [ -f "src/dog2_motion_control/$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "检查脚本..."
FILES=(
    "scripts/quick_start.sh"
    "scripts/verify_task13.sh"
)

for file in "${FILES[@]}"; do
    if [ -f "src/dog2_motion_control/$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
        # 检查是否可执行
        if [ -x "src/dog2_motion_control/$file" ]; then
            echo -e "  ${GREEN}✓${NC} 可执行"
        else
            echo -e "  ${RED}✗${NC} 不可执行"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有文件验证通过！${NC}"
    echo "任务13已完成。"
else
    echo -e "${RED}✗ 发现 $ERRORS 个错误${NC}"
    exit 1
fi
echo "========================================="
