#!/bin/bash
"""
测试就绪检查脚本

此脚本检查集成测试的前置条件是否满足。
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

print_check() {
    echo -n "检查: $1 ... "
}

print_ok() {
    echo -e "${GREEN}✓${NC}"
}

print_fail() {
    echo -e "${RED}✗${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}"
}

# 检查计数
checks_passed=0
checks_failed=0
checks_warning=0

# 检查ROS 2环境
check_ros_environment() {
    print_check "ROS 2环境"
    if [ -z "$ROS_DISTRO" ]; then
        print_fail
        echo "  错误: ROS 2环境未设置"
        echo "  解决: source /opt/ros/humble/setup.bash"
        ((checks_failed++))
        return 1
    else
        print_ok
        echo "  ROS版本: $ROS_DISTRO"
        ((checks_passed++))
        return 0
    fi
}

# 检查工作空间
check_workspace() {
    print_check "工作空间"
    if [ -f "install/setup.bash" ]; then
        print_ok
        echo "  工作空间已编译"
        ((checks_passed++))
        return 0
    else
        print_fail
        echo "  错误: 工作空间未编译"
        echo "  解决: colcon build"
        ((checks_failed++))
        return 1
    fi
}

# 检查Python依赖
check_python_dependencies() {
    print_check "Python依赖"
    
    missing_deps=()
    
    # 检查rclpy
    if ! python3 -c "import rclpy" 2>/dev/null; then
        missing_deps+=("rclpy")
    fi
    
    # 检查numpy
    if ! python3 -c "import numpy" 2>/dev/null; then
        missing_deps+=("numpy")
    fi
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        print_ok
        echo "  所有依赖已安装"
        ((checks_passed++))
        return 0
    else
        print_fail
        echo "  缺少依赖: ${missing_deps[*]}"
        echo "  解决: pip3 install ${missing_deps[*]}"
        ((checks_failed++))
        return 1
    fi
}

# 检查测试文件
check_test_files() {
    print_check "测试文件"
    
    missing_files=()
    
    if [ ! -f "test/test_gazebo_simulation.py" ]; then
        missing_files+=("test_gazebo_simulation.py")
    fi
    
    if [ ! -f "test/test_rail_locking.py" ]; then
        missing_files+=("test_rail_locking.py")
    fi
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_ok
        echo "  所有测试文件存在"
        ((checks_passed++))
        return 0
    else
        print_fail
        echo "  缺少文件: ${missing_files[*]}"
        ((checks_failed++))
        return 1
    fi
}

# 检查Gazebo
check_gazebo() {
    print_check "Gazebo Fortress"
    
    if command -v gz &> /dev/null; then
        print_ok
        gz_version=$(gz sim --version 2>&1 | head -n 1)
        echo "  版本: $gz_version"
        ((checks_passed++))
        return 0
    else
        print_warning
        echo "  警告: 未找到Gazebo命令"
        echo "  注意: 测试需要Gazebo Fortress"
        ((checks_warning++))
        return 0
    fi
}

# 检查Gazebo是否运行
check_gazebo_running() {
    print_check "Gazebo仿真状态"
    
    if ros2 topic list 2>/dev/null | grep -q "/joint_states"; then
        print_ok
        echo "  Gazebo仿真正在运行"
        ((checks_passed++))
        return 0
    else
        print_warning
        echo "  Gazebo仿真未运行"
        echo "  提示: 测试前需要启动仿真"
        echo "  命令: ros2 launch dog2_motion_control spider_gazebo_complete.launch.py"
        ((checks_warning++))
        return 0
    fi
}

# 检查控制器
check_controllers() {
    print_check "ROS 2控制器"
    
    if ros2 control list_controllers 2>/dev/null | grep -q "joint_trajectory_controller"; then
        print_ok
        echo "  控制器已加载"
        ((checks_passed++))
        return 0
    else
        print_warning
        echo "  控制器未加载"
        echo "  提示: 控制器会在仿真启动后自动加载"
        ((checks_warning++))
        return 0
    fi
}

# 检查启动文件
check_launch_files() {
    print_check "启动文件"
    
    if [ -f "launch/spider_gazebo_complete.launch.py" ]; then
        print_ok
        echo "  启动文件存在"
        ((checks_passed++))
        return 0
    else
        print_fail
        echo "  错误: 启动文件不存在"
        ((checks_failed++))
        return 1
    fi
}

# 主函数
main() {
    print_header "集成测试就绪检查"
    
    # 切换到包目录
    cd "$(dirname "$0")/.."
    
    echo "检查集成测试的前置条件..."
    echo ""
    
    # 运行所有检查
    check_ros_environment
    check_workspace
    check_python_dependencies
    check_test_files
    check_launch_files
    check_gazebo
    check_gazebo_running
    check_controllers
    
    # 打印总结
    print_header "检查总结"
    
    echo "通过: $checks_passed"
    echo "失败: $checks_failed"
    echo "警告: $checks_warning"
    echo ""
    
    if [ $checks_failed -eq 0 ]; then
        if [ $checks_warning -eq 0 ]; then
            echo -e "${GREEN}✓ 所有检查通过！可以运行测试。${NC}"
            echo ""
            echo "运行测试："
            echo "  ./run_integration_tests.sh"
            return 0
        else
            echo -e "${YELLOW}⚠ 基本检查通过，但有警告。${NC}"
            echo ""
            echo "如果Gazebo未运行，请先启动："
            echo "  ros2 launch dog2_motion_control spider_gazebo_complete.launch.py"
            echo ""
            echo "然后运行测试："
            echo "  ./run_integration_tests.sh"
            return 0
        fi
    else
        echo -e "${RED}✗ 有 $checks_failed 项检查失败。${NC}"
        echo ""
        echo "请修复上述问题后再运行测试。"
        return 1
    fi
}

# 运行主函数
main
exit $?
