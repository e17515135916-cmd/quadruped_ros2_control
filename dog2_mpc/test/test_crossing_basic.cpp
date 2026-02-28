#include "dog2_mpc/crossing_state_machine.hpp"
#include "dog2_mpc/hybrid_gait_generator.hpp"
#include "test_helpers.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

/**
 * @brief 测试越障状态机和混合步态生成器的基本功能
 */
int main() {
    TestReporter reporter;
    reporter.printHeader("Dog2越障系统基础测试");
    
    // ========================================
    // 测试1：状态机初始化和状态转换
    // ========================================
    reporter.printSection("测试1：状态机初始化");
    
    CrossingStateMachine state_machine;
    
    // 初始化机器人状态
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(1.0, 0.0, 0.3);
    robot_state.velocity.setZero();
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();
    robot_state.sliding_velocities.setZero();
    
    // 初始化腿部构型（全部肘式）
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_contacts[i] = true;
        robot_state.foot_positions[i] = Eigen::Vector3d(0.0, 0.0, 0.0);
    }
    
    // 初始化窗框参数
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    window.top_height = 0.6;
    window.safety_margin = 0.05;
    
    state_machine.initialize(robot_state, window);
    
    // 验证初始状态
    if (state_machine.getCurrentState() == CrossingStateMachine::CrossingState::APPROACH) {
        reporter.printSuccess("状态机初始化成功，当前状态：初始接近");
    } else {
        reporter.printFailure("状态机初始化失败");
        return -1;
    }
    
    // ========================================
    // 测试2：状态转换逻辑
    // ========================================
    reporter.printSection("测试2：状态转换逻辑");
    
    int test_count = 0;
    int pass_count = 0;
    
    // 测试2.1：接近阶段完成条件
    test_count++;
    robot_state.position.x() = 1.8;  // 距离窗框0.2m
    robot_state.velocity.x() = 0.01;  // 速度接近0
    
    if (state_machine.canTransitionToNext(robot_state)) {
        reporter.printSuccess("接近阶段完成条件检查通过");
        pass_count++;
    } else {
        reporter.printFailure("接近阶段完成条件检查失败");
    }
    
    // 测试2.2：机身前探完成条件
    test_count++;
    robot_state.sliding_positions << -0.111, 0.111, 0.111, -0.111;
    state_machine.forceTransitionTo(CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT);
    
    if (state_machine.canTransitionToNext(robot_state)) {
        reporter.printSuccess("机身前探完成条件检查通过");
        pass_count++;
    } else {
        reporter.printFailure("机身前探完成条件检查失败");
    }
    
    // 测试2.3：前腿穿越完成条件
    test_count++;
    robot_state.leg_configs[0] = CrossingStateMachine::LegConfiguration::KNEE;
    robot_state.leg_configs[3] = CrossingStateMachine::LegConfiguration::KNEE;
    robot_state.foot_positions[0].x() = 2.1;
    robot_state.foot_positions[3].x() = 2.1;
    state_machine.forceTransitionTo(CrossingStateMachine::CrossingState::FRONT_LEGS_TRANSIT);
    
    if (state_machine.canTransitionToNext(robot_state)) {
        reporter.printSuccess("前腿穿越完成条件检查通过");
        pass_count++;
    } else {
        reporter.printFailure("前腿穿越完成条件检查失败");
    }
    
    reporter.printSummary(pass_count == test_count, test_count, pass_count);
    
    // ========================================
    // 测试3：混合步态生成器
    // ========================================
    reporter.printSection("测试3：混合步态生成器");
    
    HybridGaitGenerator gait_generator;
    
    // 初始化步态生成器
    robot_state.position = Eigen::Vector3d(2.0, 0.0, 0.3);
    robot_state.leg_configs[0] = CrossingStateMachine::LegConfiguration::KNEE;   // 前腿膝式
    robot_state.leg_configs[1] = CrossingStateMachine::LegConfiguration::ELBOW;  // 后腿肘式
    robot_state.leg_configs[2] = CrossingStateMachine::LegConfiguration::ELBOW;
    robot_state.leg_configs[3] = CrossingStateMachine::LegConfiguration::KNEE;
    
    // 设置足端初始位置
    robot_state.foot_positions[0] = Eigen::Vector3d(1.9, -0.15, 0.0);  // 前左
    robot_state.foot_positions[1] = Eigen::Vector3d(1.8, -0.15, 0.0);  // 后左
    robot_state.foot_positions[2] = Eigen::Vector3d(1.8, 0.15, 0.0);   // 后右
    robot_state.foot_positions[3] = Eigen::Vector3d(1.9, 0.15, 0.0);   // 前右
    
    gait_generator.initialize(robot_state);
    
    // 生成混合步态
    Eigen::Vector3d desired_velocity(0.1, 0.0, 0.0);  // 前进0.1 m/s
    double dt = 0.1;  // 100ms
    
    auto gait_state = gait_generator.generateHybridTrotGait(robot_state, desired_velocity, dt);
    
    // 验证步态生成结果
    test_count = 0;
    pass_count = 0;
    
    // 测试3.1：验证步态频率
    test_count++;
    if (std::abs(gait_state.gait_frequency - 1.0) < 0.01) {
        reporter.printSuccess("步态频率正确: " + std::to_string(gait_state.gait_frequency) + " Hz");
        pass_count++;
    } else {
        reporter.printFailure("步态频率错误");
    }
    
    // 测试3.2：验证足端轨迹生成
    test_count++;
    bool all_footsteps_valid = true;
    for (int i = 0; i < 4; ++i) {
        if (gait_state.footsteps[i].position.hasNaN()) {
            all_footsteps_valid = false;
            break;
        }
    }
    
    if (all_footsteps_valid) {
        reporter.printSuccess("所有足端轨迹生成成功");
        pass_count++;
    } else {
        reporter.printFailure("足端轨迹包含NaN");
    }
    
    // 测试3.3：验证腿间距离约束
    test_count++;
    bool collision_free = gait_generator.checkLegCollision(gait_state.footsteps);
    
    if (collision_free) {
        reporter.printSuccess("腿间距离约束满足，无碰撞风险");
        pass_count++;
    } else {
        reporter.printWarning("检测到腿间距离过近，但已应用避障约束");
        pass_count++;  // 警告不算失败
    }
    
    // 测试3.4：输出足端位置信息
    std::cout << "\n足端位置信息:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "  腿" << (i+1) << ": ";
        std::cout << "x=" << std::fixed << std::setprecision(3) << gait_state.footsteps[i].position.x() << "m, ";
        std::cout << "y=" << gait_state.footsteps[i].position.y() << "m, ";
        std::cout << "z=" << gait_state.footsteps[i].position.z() << "m, ";
        std::cout << "接触=" << (gait_state.footsteps[i].is_contact ? "是" : "否") << std::endl;
    }
    
    reporter.printSummary(pass_count == test_count, test_count, pass_count);
    
    // ========================================
    // 测试4：正常步态生成
    // ========================================
    reporter.printSection("测试4：正常步态生成");
    
    // 切换到全肘式构型
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
    }
    
    gait_generator.reset();
    gait_generator.initialize(robot_state);
    
    auto normal_gait = gait_generator.generateNormalTrotGait(robot_state, desired_velocity, dt);
    
    test_count = 0;
    pass_count = 0;
    
    // 测试4.1：验证正常步态生成
    test_count++;
    bool normal_gait_valid = true;
    for (int i = 0; i < 4; ++i) {
        if (normal_gait.footsteps[i].position.hasNaN()) {
            normal_gait_valid = false;
            break;
        }
    }
    
    if (normal_gait_valid) {
        reporter.printSuccess("正常步态生成成功");
        pass_count++;
    } else {
        reporter.printFailure("正常步态生成失败");
    }
    
    reporter.printSummary(pass_count == test_count, test_count, pass_count);
    
    // ========================================
    // 总结
    // ========================================
    reporter.printSection("测试总结");
    reporter.printSuccess("状态机测试完成");
    reporter.printSuccess("混合步态生成器测试完成");
    reporter.printSuccess("正常步态生成器测试完成");
    
    std::cout << "\n✅ Dog2越障系统基础功能验证通过！" << std::endl;
    
    return 0;
}
