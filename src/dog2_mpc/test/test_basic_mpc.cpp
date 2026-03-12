#include "dog2_mpc/mpc_controller.hpp"
#include "test_helpers.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

/**
 * @brief 测试基本的MPC功能，不包含越障
 */
int main() {
    TestReporter reporter;
    reporter.printHeader("Dog2 基本MPC测试");
    
    // 1. 创建MPC控制器（不启用越障功能）
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 6;      // 短时域
    mpc_params.dt = 0.1;         // 10Hz控制频率
    
    // 设置权重矩阵 (16×16 for extended state)
    mpc_params.Q = Eigen::MatrixXd::Identity(16, 16);
    mpc_params.Q.diagonal() << 100, 100, 200,  // 位置权重
                              50, 50, 50,       // 姿态权重
                              10, 10, 10,       // 线速度权重
                              5, 5, 5,          // 角速度权重
                              20, 20, 20, 20;   // 滑动副权重
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.1;  // 控制权重
    
    // 控制限制
    mpc_params.u_min = Eigen::VectorXd::Constant(12, -30.0);
    mpc_params.u_max = Eigen::VectorXd::Constant(12, 30.0);
    
    // 禁用复杂约束
    mpc_params.enable_sliding_constraints = false;
    mpc_params.enable_boundary_constraints = false;
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    // 2. 初始化机器人状态 (16维扩展状态)
    Eigen::VectorXd x0(16);
    x0 << 0.0, 0.0, 0.3,    // 位置 [x, y, z]
          0.0, 0.0, 0.0,    // 姿态 [roll, pitch, yaw]
          0.0, 0.0, 0.0,    // 线速度 [vx, vy, vz]
          0.0, 0.0, 0.0,    // 角速度 [wx, wy, wz]
          0.0, 0.0, 0.0, 0.0;  // 滑动副位置 [j1, j2, j3, j4]
    
    // 3. 设置足端位置（相对质心）
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << -0.2, -0.15, -0.3,  // 腿1 (前左)
                      0.2, -0.15, -0.3,   // 腿2 (后左)
                      0.2,  0.15, -0.3,   // 腿3 (后右)
                     -0.2,  0.15, -0.3;   // 腿4 (前右)
    mpc_controller.setBaseFootPositions(foot_positions);
    
    // 4. 设置参考轨迹（前进1m，16维扩展状态）
    std::vector<Eigen::VectorXd> x_ref(mpc_params.horizon);
    for (int k = 0; k < mpc_params.horizon; ++k) {
        x_ref[k] = Eigen::VectorXd::Zero(16);
        x_ref[k](0) = (k + 1) * 0.2;  // 每步前进0.2m
        x_ref[k](2) = 0.3;            // 保持高度
        x_ref[k](6) = 0.2;            // 期望前进速度
        // 滑动副位置保持为0 (x_ref[k](12-15) = 0)
        
        // 调试输出
        if (k == 0) {
            std::cout << "参考轨迹第" << k << "步: x=" << x_ref[k](0) 
                      << ", z=" << x_ref[k](2) << ", vx=" << x_ref[k](6) << std::endl;
        }
    }
    mpc_controller.setReference(x_ref);
    
    reporter.printSection("MPC控制器初始化完成");
    reporter.printKeyValue("时域长度", mpc_params.horizon);
    reporter.printKeyValue("控制频率", std::to_string(1.0 / mpc_params.dt) + " Hz");
    reporter.printKeyValue("目标", "前进到x=1.2m");
    
    // 5. 控制循环
    Eigen::VectorXd x_current = x0;
    double total_time = 0.0;
    int step_count = 0;
    const int max_steps = 100;  // 10秒仿真
    
    reporter.printSection("开始MPC控制循环");
    std::cout << std::fixed << std::setprecision(3);
    
    while (step_count < max_steps) {
        // MPC求解
        Eigen::VectorXd u_optimal;
        bool success = mpc_controller.solve(x_current, u_optimal);
        
        if (!success) {
            reporter.printFailure("MPC求解失败，停止仿真");
            return -1;
        }
        
        // 每1秒输出一次状态
        if (step_count % 10 == 0) {
            std::cout << "[" << std::setw(5) << total_time << "s] "
                      << "位置: x=" << std::setw(6) << x_current(0) 
                      << "m, z=" << std::setw(6) << x_current(2) << "m | "
                      << "速度: vx=" << std::setw(6) << x_current(6) << "m/s | "
                      << "求解: " << std::setw(5) << mpc_controller.getSolveTime() << "ms" << std::endl;
        }
        
        // 简单的动力学积分 (保持16维状态)
        Eigen::VectorXd x_next = x_current;
        
        // 位置积分
        x_next.segment<3>(0) += x_current.segment<3>(6) * mpc_params.dt;
        
        // 姿态积分
        x_next.segment<3>(3) += x_current.segment<3>(9) * mpc_params.dt;
        
        // 速度更新
        double mass = 11.8;
        Eigen::Vector3d force_sum = Eigen::Vector3d::Zero();
        for (int i = 0; i < 4; ++i) {
            force_sum += u_optimal.segment<3>(i * 3);
        }
        
        // 重力和阻尼
        Eigen::Vector3d gravity(0, 0, -mass * 9.81);
        x_next.segment<3>(6) += (force_sum + gravity) / mass * mpc_params.dt;
        x_next.segment<3>(6) *= 0.95;  // 阻尼
        x_next.segment<3>(9) *= 0.90;  // 角速度阻尼
        
        // 滑动副状态更新 (保持为0，因为速度为0)
        // x_next.segment<4>(12) 保持不变
        
        // 高度限制
        if (x_next(2) < 0.25) {
            x_next(2) = 0.25;
            x_next(8) = std::max(0.0, x_next(8));
        }
        if (x_next(2) > 0.4) {
            x_next(2) = 0.4;
            x_next(8) = std::min(0.0, x_next(8));
        }
        
        x_current = x_next;
        total_time += mpc_params.dt;
        step_count++;
        
        // 检查是否到达目标
        if (x_current(0) > 1.0) {
            reporter.printSuccess("到达目标位置！");
            break;
        }
    }
    
    reporter.printSection("基本MPC测试完成");
    reporter.printKeyValue("总步数", step_count);
    reporter.printKeyValue("总时间", std::to_string(total_time) + "s");
    std::cout << "  最终位置: x=" << x_current(0) << "m, z=" << x_current(2) << "m" << std::endl;
    std::cout << "  最终速度: vx=" << x_current(6) << "m/s" << std::endl;
    
    // 性能统计
    reporter.printSection("性能统计");
    reporter.printKeyValue("平均求解时间", std::to_string(mpc_controller.getSolveTime()) + "ms");
    
    bool realtime_ok = mpc_controller.getSolveTime() < mpc_params.dt * 1000;
    if (realtime_ok) {
        reporter.printSuccess("实时性能满足要求");
    } else {
        reporter.printWarning("实时性能不满足要求");
    }
    
    // 测试总结
    bool all_passed = (step_count > 0) && (x_current(0) > 1.0) && realtime_ok;
    reporter.printSummary(all_passed, 3, all_passed ? 3 : 2);
    
    return all_passed ? 0 : -1;
}