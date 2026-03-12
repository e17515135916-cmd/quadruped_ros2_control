#!/bin/bash
"""
集成测试运行脚本

此脚本用于运行任务14的集成测试：
- 14.3 Gazebo仿真测试
- 14.4 导轨锁定验证

使用方法：
1. 在一个终端启动Gazebo仿真：
   ros2 launch dog2_motion_control spider_gazebo_complete.launch.py

2. 在另一个终端运行此脚本：
   ./run_integration_tests.sh
"""

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印标题
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# 检查ROS 2环境
check_ros_environment() {
    print_info "检查ROS 2环境..."
    
    if [ -z "$ROS_DISTRO" ]; then
        print_error "ROS 2环境未设置"
        print_info "请先source ROS 2环境："
        print_info "  source /opt/ros/humble/setup.bash"
        print_info "  source install/setup.bash"
        exit 1
    fi
    
    print_success "ROS 2环境已设置: $ROS_DISTRO"
}

# 检查Gazebo是否运行
check_gazebo_running() {
    print_info "检查Gazebo仿真是否运行..."
    
    # 检查/joint_states话题是否存在
    if ros2 topic list | grep -q "/joint_states"; then
        print_success "Gazebo仿真正在运行"
        return 0
    else
        print_warning "未检测到Gazebo仿真"
        print_info "请在另一个终端启动仿真："
        print_info "  ros2 launch dog2_motion_control spider_gazebo_complete.launch.py"
        echo ""
        read -p "按Enter继续（如果已启动仿真），或Ctrl+C取消..." dummy
        return 0
    fi
}

# 运行Gazebo仿真测试
run_gazebo_tests() {
    print_header "任务 14.3: Gazebo仿真测试"
    
    print_info "运行Gazebo仿真集成测试..."
    python3 test_gazebo_simulation.py
    
    if [ $? -eq 0 ]; then
        print_success "Gazebo仿真测试通过"
        return 0
    else
        print_error "Gazebo仿真测试失败"
        return 1
    fi
}

# 运行导轨锁定测试
run_rail_locking_tests() {
    print_header "任务 14.4: 导轨锁定验证"
    
    print_info "运行导轨锁定验证测试..."
    python3 test_rail_locking.py
    
    if [ $? -eq 0 ]; then
        print_success "导轨锁定测试通过"
        return 0
    else
        print_error "导轨锁定测试失败"
        return 1
    fi
}

# 主函数
main() {
    print_header "任务14: 集成测试和验证"
    
    # 检查环境
    check_ros_environment
    check_gazebo_running
    
    # 切换到测试目录
    cd "$(dirname "$0")"
    
    # 运行测试
    gazebo_result=0
    rail_result=0
    
    run_gazebo_tests || gazebo_result=$?
    echo ""
    
    run_rail_locking_tests || rail_result=$?
    echo ""
    
    # 打印总结
    print_header "测试总结"
    
    if [ $gazebo_result -eq 0 ]; then
        print_success "✓ 任务 14.3: Gazebo仿真测试 - 通过"
    else
        print_error "✗ 任务 14.3: Gazebo仿真测试 - 失败"
    fi
    
    if [ $rail_result -eq 0 ]; then
        print_success "✓ 任务 14.4: 导轨锁定验证 - 通过"
    else
        print_error "✗ 任务 14.4: 导轨锁定验证 - 失败"
    fi
    
    echo ""
    
    if [ $gazebo_result -eq 0 ] && [ $rail_result -eq 0 ]; then
        print_success "所有集成测试通过！"
        return 0
    else
        print_error "部分测试失败"
        return 1
    fi
}

# 运行主函数
main
exit $?
