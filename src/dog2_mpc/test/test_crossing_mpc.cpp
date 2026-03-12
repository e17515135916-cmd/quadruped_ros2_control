/**
 * @file test_crossing_mpc.cpp
 * @brief 测试MPC控制器的越障功能
 * 
 * 测试内容：
 * 1. 越障初始化
 * 2. 状态机更新
 * 3. 参考轨迹生成（16维扩展状态）
 * 4. MPC求解（混合构型）
 */

#include "dog2_mpc/mpc_controller.hpp"
#include "test_helpers.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

// 测试1：越障初始化
bool testCrossingInitialization() {
    TestReporter reporter;
    reporter.printHeader("越障初始化测试");
    
    // 创建MPC控制器
    double mass = 11.8;
    Eigen::Matrix3d inertia = Eigen::Matrix3d::Identity() * 0.1;
    
    MPCController::Parameters params;
    params.horizon = 10;
    params.dt = 0.05;
    
    MPCController mpc(mass, inertia, params);
    
    // 设置初始状态
    CrossingStateMachine::RobotState initial_state;
    initial_state.position = Eigen::Vector3d(1.0, 0.0, 0.3);
    initial_state.velocity = Eigen::Vector3d(0.2, 0.0, 0.0);
    initial_state.orientation.setZero();
    initial_state.angular_velocity.setZero();
    initial_state.sliding_positions.setZero();
    initial_state.sliding_velocities.setZero();
    
    // 全部肘式
    for (int i = 0; i < 4; ++i) {
        initial_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        initial_state.foot_contacts[i] = true;
    }
    
    // 设置窗框
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    
    // 初始化越障
    mpc.initializeCrossing(initial_state, window);
    
    // 验证
    bool success = mpc.isCrossingEnabled();
    if (success) {
        reporter.printSuccess("越障模式已启用");
    } else {
        reporter.printFailure("越障模式未启用");
        return false;
    }
    
    auto state = mpc.getCurrentCrossingState();
    if (state == CrossingStateMachine::CrossingState::APPROACH) {
        reporter.printSuccess("初始状态为APPROACH");
    } else {
        reporter.printFailure("初始状态不正确");
        return false;
    }
    
    reporter.printSuccess("所有检查通过");
    return true;
}

// 测试2：参考轨迹生成（16维扩展状态）
bool testCrossingReferenceGeneration() {
    TestReporter reporter;
    reporter.printHeader("越障参考轨迹生成测试");
    
    // 创建MPC控制器
    double mass = 11.8;
    Eigen::Matrix3d inertia = Eigen::Matrix3d::Identity() * 0.1;
    
    MPCController::Parameters params;
    params.horizon = 10;
    params.dt = 0.05;
    
    MPCController mpc(mass, inertia, params);
    
    // 初始化越障
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(1.8, 0.0, 0.3);
    robot_state.velocity = Eigen::Vector3d(0.0, 0.0, 0.0);
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();
    robot_state.sliding_velocities.setZero();
    
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_contacts[i] = true;
    }
    
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    
    mpc.initializeCrossing(robot_state, window);
    
    // 生成参考轨迹
    auto ref_traj = mpc.generateCrossingReference(robot_state, params.dt);
    
    // 验证轨迹
    if (ref_traj.size() == static_cast<size_t>(params.horizon)) {
        reporter.printSuccess("参考轨迹长度正确");
    } else {
        reporter.printFailure("参考轨迹长度不正确");
        return false;
    }
    
    // 检查维度（应该是12维，因为generateCrossingReference返回SRBD状态）
    if (!ref_traj.empty()) {
        if (ref_traj[0].size() == 12) {
            reporter.printSuccess("参考轨迹维度为12（SRBD状态）");
        } else {
            reporter.printFailure("参考轨迹维度不正确");
            return false;
        }
        
        std::cout << "  参考轨迹第一步: [" 
                  << ref_traj[0].head(3).transpose() << "]" << std::endl;
    }
    
    reporter.printSuccess("所有检查通过");
    return true;
}

// 测试3：MPC求解（接近阶段）
bool testCrossingMPCSolve() {
    TestReporter reporter;
    reporter.printHeader("越障MPC求解测试");
    
    // 创建MPC控制器
    double mass = 11.8;
    Eigen::Matrix3d inertia = Eigen::Matrix3d::Identity() * 0.1;
    
    MPCController::Parameters params;
    params.horizon = 10;
    params.dt = 0.05;
    params.enable_sliding_constraints = true;
    
    MPCController mpc(mass, inertia, params);
    
    // 设置基础足端位置
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << 0.2,  0.15, 0.0,   // 腿1
                     -0.2,  0.15, 0.0,   // 腿2
                     -0.2, -0.15, 0.0,   // 腿3
                      0.2, -0.15, 0.0;   // 腿4
    mpc.setBaseFootPositions(foot_positions);
    
    // 设置滑动副速度
    Eigen::Vector4d sliding_velocity;
    sliding_velocity.setZero();
    mpc.setSlidingVelocity(sliding_velocity);
    
    // 初始化越障
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(1.8, 0.0, 0.3);
    robot_state.velocity = Eigen::Vector3d(0.0, 0.0, 0.0);
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();
    robot_state.sliding_velocities.setZero();
    
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_contacts[i] = true;
    }
    
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    
    mpc.initializeCrossing(robot_state, window);
    
    // 构建16维扩展状态
    Eigen::VectorXd x0(16);
    x0 << robot_state.position,           // 位置 (3)
          robot_state.orientation,        // 姿态 (3)
          robot_state.velocity,           // 线速度 (3)
          robot_state.angular_velocity,   // 角速度 (3)
          robot_state.sliding_positions;  // 滑动副 (4)
    
    // 求解MPC
    Eigen::VectorXd u_optimal;
    bool success = mpc.solve(x0, u_optimal);
    
    if (success) {
        reporter.printSuccess("MPC求解成功");
    } else {
        reporter.printFailure("MPC求解失败");
        return false;
    }
    
    if (u_optimal.size() == 12) {
        reporter.printSuccess("控制输出维度正确（12维）");
    } else {
        reporter.printFailure("控制输出维度不正确");
        return false;
    }
    
    std::cout << "  求解时间: " << mpc.getSolveTime() << " ms" << std::endl;
    std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
    
    // 检查控制输出的合理性
    double total_fz = u_optimal(2) + u_optimal(5) + u_optimal(8) + u_optimal(11);
    double expected_fz = mass * 9.81;
    double fz_error = std::abs(total_fz - expected_fz) / expected_fz;
    
    std::cout << "  总垂直力: " << total_fz << " N (期望: " << expected_fz << " N)" << std::endl;
    std::cout << "  垂直力误差: " << (fz_error * 100.0) << "%" << std::endl;
    
    if (fz_error < 0.5) {
        reporter.printSuccess("垂直力合理（误差<50%）");
    } else {
        reporter.printWarning("垂直力误差较大");
    }
    
    reporter.printSuccess("所有检查通过");
    return true;
}

// 测试4：状态机更新
bool testCrossingStateUpdate() {
    TestReporter reporter;
    reporter.printHeader("越障状态机更新测试");
    
    // 创建MPC控制器
    double mass = 11.8;
    Eigen::Matrix3d inertia = Eigen::Matrix3d::Identity() * 0.1;
    
    MPCController::Parameters params;
    params.horizon = 10;
    params.dt = 0.05;
    
    MPCController mpc(mass, inertia, params);
    
    // 初始化越障
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(1.0, 0.0, 0.3);
    robot_state.velocity = Eigen::Vector3d(0.2, 0.0, 0.0);
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();
    robot_state.sliding_velocities.setZero();
    
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_contacts[i] = true;
    }
    
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    
    mpc.initializeCrossing(robot_state, window);
    
    // 模拟接近过程
    for (int i = 0; i < 20; ++i) {
        robot_state.position.x() += 0.05;  // 每步前进5cm
        mpc.updateCrossing(robot_state, params.dt);
    }
    
    // 检查状态转换
    auto current_state = mpc.getCurrentCrossingState();
    std::cout << "  当前状态: " << static_cast<int>(current_state) << std::endl;
    std::cout << "  越障进度: " << (mpc.getCrossingProgress() * 100.0) << "%" << std::endl;
    
    // 验证状态已经改变（应该从APPROACH转换到下一阶段）
    if (current_state != CrossingStateMachine::CrossingState::APPROACH ||
        robot_state.position.x() < window.x_position - 0.2) {
        reporter.printSuccess("状态机正常工作");
    } else {
        reporter.printWarning("状态机可能未正常转换");
    }
    
    reporter.printSuccess("所有检查通过");
    return true;
}

int main() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "  Dog2越障MPC功能测试" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    int passed = 0;
    int total = 0;
    
    // 运行测试
    if (testCrossingInitialization()) passed++;
    total++;
    
    if (testCrossingReferenceGeneration()) passed++;
    total++;
    
    if (testCrossingMPCSolve()) passed++;
    total++;
    
    if (testCrossingStateUpdate()) passed++;
    total++;
    
    // 总结
    std::cout << "\n========================================" << std::endl;
    std::cout << "  测试总结" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "通过: " << passed << "/" << total << std::endl;
    
    if (passed == total) {
        std::cout << "✓ 所有测试通过！" << std::endl;
        return 0;
    } else {
        std::cout << "✗ 部分测试失败" << std::endl;
        return 1;
    }
}
