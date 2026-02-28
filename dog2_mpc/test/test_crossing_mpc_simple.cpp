/**
 * @file test_crossing_mpc_simple.cpp
 * @brief 简化的MPC越障测试，用于调试OSQP问题
 */

#include "dog2_mpc/mpc_controller.hpp"
#include "test_helpers.hpp"
#include <iostream>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

int main() {
    TestReporter reporter;
    reporter.printHeader("简化MPC越障测试");
    
    // 创建MPC控制器（简化参数）
    double mass = 11.8;
    Eigen::Matrix3d inertia = Eigen::Matrix3d::Identity() * 0.1;
    
    MPCController::Parameters params;
    params.horizon = 5;  // 减小时域
    params.dt = 0.1;     // 增大时间步长
    params.enable_sliding_constraints = false;  // 先禁用滑动副约束
    
    MPCController mpc(mass, inertia, params);
    
    // 设置基础足端位置
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << 0.2,  0.15, 0.0,
                     -0.2,  0.15, 0.0,
                     -0.2, -0.15, 0.0,
                      0.2, -0.15, 0.0;
    mpc.setBaseFootPositions(foot_positions);
    
    // 设置滑动副速度为零
    Eigen::Vector4d sliding_velocity;
    sliding_velocity.setZero();
    mpc.setSlidingVelocity(sliding_velocity);
    
    // 构建简单的16维状态（悬停）
    Eigen::VectorXd x0(16);
    x0 << 0.0, 0.0, 0.3,     // 位置
          0.0, 0.0, 0.0,     // 姿态
          0.0, 0.0, 0.0,     // 线速度
          0.0, 0.0, 0.0,     // 角速度
          0.0, 0.0, 0.0, 0.0; // 滑动副
    
    // 设置简单的参考轨迹（保持悬停）
    std::vector<Eigen::VectorXd> x_ref(params.horizon, x0);
    mpc.setReference(x_ref);
    
    std::cout << "\n测试1：不启用越障模式" << std::endl;
    std::cout << "  horizon=" << params.horizon << std::endl;
    std::cout << "  dt=" << params.dt << std::endl;
    std::cout << "  sliding_constraints=" << params.enable_sliding_constraints << std::endl;
    
    // 求解MPC（不启用越障）
    Eigen::VectorXd u_optimal;
    bool success1 = mpc.solve(x0, u_optimal);
    
    if (success1) {
        reporter.printSuccess("MPC求解成功（无越障）");
        std::cout << "  求解时间: " << mpc.getSolveTime() << " ms" << std::endl;
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
        
        double total_fz = u_optimal(2) + u_optimal(5) + u_optimal(8) + u_optimal(11);
        std::cout << "  总垂直力: " << total_fz << " N" << std::endl;
    } else {
        reporter.printFailure("MPC求解失败（无越障）");
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
        return 1;
    }
    
    // 测试2：启用越障模式
    std::cout << "\n测试2：启用越障模式" << std::endl;
    
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(0.0, 0.0, 0.3);
    robot_state.velocity.setZero();
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();
    robot_state.sliding_velocities.setZero();
    
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_contacts[i] = true;
        robot_state.foot_positions[i] = foot_positions.row(i);
    }
    
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    
    mpc.initializeCrossing(robot_state, window);
    
    // 再次求解
    bool success2 = mpc.solve(x0, u_optimal);
    
    if (success2) {
        reporter.printSuccess("MPC求解成功（有越障）");
        std::cout << "  求解时间: " << mpc.getSolveTime() << " ms" << std::endl;
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
        
        double total_fz = u_optimal(2) + u_optimal(5) + u_optimal(8) + u_optimal(11);
        std::cout << "  总垂直力: " << total_fz << " N" << std::endl;
    } else {
        reporter.printFailure("MPC求解失败（有越障）");
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
        
        // 打印更多调试信息
        std::cout << "\n调试信息：" << std::endl;
        std::cout << "  当前越障状态: " << static_cast<int>(mpc.getCurrentCrossingState()) << std::endl;
        std::cout << "  越障进度: " << mpc.getCrossingProgress() << std::endl;
        
        return 1;
    }
    
    // 测试3：启用滑动副约束
    std::cout << "\n测试3：启用滑动副约束" << std::endl;
    
    params.enable_sliding_constraints = true;
    mpc.updateParameters(params);
    
    bool success3 = mpc.solve(x0, u_optimal);
    
    if (success3) {
        reporter.printSuccess("MPC求解成功（有滑动副约束）");
        std::cout << "  求解时间: " << mpc.getSolveTime() << " ms" << std::endl;
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
    } else {
        reporter.printFailure("MPC求解失败（有滑动副约束）");
        std::cout << "  求解状态: " << mpc.getSolveStatus() << std::endl;
        std::cout << "  这可能是滑动副约束导致的问题" << std::endl;
        return 1;
    }
    
    reporter.printSuccess("所有测试通过！");
    return 0;
}
