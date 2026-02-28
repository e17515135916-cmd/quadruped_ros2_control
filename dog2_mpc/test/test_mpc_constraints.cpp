#include "dog2_mpc/mpc_controller.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;

/**
 * @brief 专门测试MPC约束构建的正确性
 */
int main() {
    std::cout << "=== MPC约束构建测试 ===" << std::endl;
    
    // 1. 创建简单的MPC控制器
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 3;      // 短时域，便于调试
    mpc_params.dt = 0.1;         // 10Hz
    
    // 简单的权重 - 降低控制权重，提高跟踪权重
    mpc_params.Q = Eigen::MatrixXd::Identity(12, 12);
    mpc_params.Q.diagonal() << 100, 100, 200,  // 位置权重
                              50, 50, 50,       // 姿态权重
                              10, 10, 10,       // 线速度权重
                              5, 5, 5;          // 角速度权重
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;  // 降低控制权重
    
    // 控制限制 - 允许更大的足端力
    mpc_params.u_min = Eigen::VectorXd::Constant(12, -50.0);
    mpc_params.u_max = Eigen::VectorXd::Constant(12, 50.0);
    
    // 禁用复杂约束
    mpc_params.enable_sliding_constraints = false;
    mpc_params.enable_boundary_constraints = false;
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    // 禁用越障功能进行基础测试
    // mpc_controller.initializeCrossing(...);  // 不调用这个
    
    // 2. 设置简单的初始状态
    Eigen::VectorXd x0(12);
    x0.setZero();
    x0(2) = 0.3;  // 高度
    
    // 3. 设置足端位置
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << -0.2, -0.15, -0.3,
                      0.2, -0.15, -0.3,
                      0.2,  0.15, -0.3,
                     -0.2,  0.15, -0.3;
    mpc_controller.setBaseFootPositions(foot_positions);
    
    // 4. 设置简单的参考轨迹（向前移动，保持高度）
    std::vector<Eigen::VectorXd> x_ref(mpc_params.horizon);
    for (int k = 0; k < mpc_params.horizon; ++k) {
        x_ref[k] = Eigen::VectorXd::Zero(12);
        x_ref[k](0) = (k + 1) * 0.05;  // x位置递增，但更小的步长
        x_ref[k](2) = 0.3;             // 保持高度
        x_ref[k](6) = 0.05;            // 期望前进速度，更小的速度
    }
    mpc_controller.setReference(x_ref);
    
    std::cout << "\n=== 参考轨迹 ===" << std::endl;
    for (int k = 0; k < mpc_params.horizon; ++k) {
        std::cout << "步骤" << k << ": x_ref=" << x_ref[k](0) 
                  << ", z_ref=" << x_ref[k](2) 
                  << ", vx_ref=" << x_ref[k](6) << std::endl;
    }
    
    // 5. 求解MPC
    std::cout << "\n=== MPC求解 ===" << std::endl;
    
    // 添加调试信息
    std::cout << "初始状态 x0: [";
    for (int i = 0; i < x0.size(); ++i) {
        std::cout << x0(i);
        if (i < x0.size() - 1) std::cout << ", ";
    }
    std::cout << "]" << std::endl;
    
    std::cout << "足端位置:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "  腿" << (i+1) << ": [" << foot_positions(i, 0) 
                  << ", " << foot_positions(i, 1) 
                  << ", " << foot_positions(i, 2) << "]" << std::endl;
    }
    
    Eigen::VectorXd u_optimal;
    bool success = mpc_controller.solve(x0, u_optimal);
    
    if (success) {
        std::cout << "✅ MPC求解成功！" << std::endl;
        std::cout << "求解时间: " << mpc_controller.getSolveTime() << "ms" << std::endl;
        
        // 6. 分析求解结果
        std::cout << "\n=== 求解结果分析 ===" << std::endl;
        
        // 第一步控制
        std::cout << "第一步控制 u_0:" << std::endl;
        for (int i = 0; i < 4; ++i) {
            Eigen::Vector3d f_i = u_optimal.segment<3>(i * 3);
            std::cout << "  腿" << (i+1) << ": fx=" << std::setw(8) << f_i(0) 
                      << ", fy=" << std::setw(8) << f_i(1) 
                      << ", fz=" << std::setw(8) << f_i(2) << std::endl;
        }
        
        // 总力分析
        Eigen::Vector3d total_force = Eigen::Vector3d::Zero();
        for (int i = 0; i < 4; ++i) {
            total_force += u_optimal.segment<3>(i * 3);
        }
        std::cout << "总力: fx=" << total_force(0) 
                  << ", fy=" << total_force(1) 
                  << ", fz=" << total_force(2) << std::endl;
        
        // 预测轨迹
        auto predicted_states = mpc_controller.getPredictedTrajectory();
        std::cout << "\n预测轨迹:" << std::endl;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            std::cout << "步骤" << k << ": x=" << std::setw(8) << predicted_states[k](0)
                      << ", z=" << std::setw(8) << predicted_states[k](2)
                      << ", vx=" << std::setw(8) << predicted_states[k](6)
                      << " (参考: x=" << x_ref[k](0) << ", vx=" << x_ref[k](6) << ")" << std::endl;
        }
        
        // 7. 验证动力学一致性
        std::cout << "\n=== 动力学验证 ===" << std::endl;
        
        // 使用第一步控制预测下一步状态
        Eigen::VectorXd x1_predicted;
        // 这里需要访问SRBD模型来验证
        // 简化验证：检查x方向的运动
        double mass = 11.8;
        double fx_total = total_force(0);
        double ax_expected = fx_total / mass;
        double vx1_expected = x0(6) + ax_expected * mpc_params.dt;
        double x1_expected = x0(0) + x0(6) * mpc_params.dt + 0.5 * ax_expected * mpc_params.dt * mpc_params.dt;
        
        std::cout << "动力学验证 (x方向):" << std::endl;
        std::cout << "  期望加速度: " << ax_expected << " m/s²" << std::endl;
        std::cout << "  期望速度: " << vx1_expected << " m/s" << std::endl;
        std::cout << "  期望位置: " << x1_expected << " m" << std::endl;
        std::cout << "  MPC预测位置: " << predicted_states[0](0) << " m" << std::endl;
        std::cout << "  MPC预测速度: " << predicted_states[0](6) << " m/s" << std::endl;
        
        // 检查控制方向
        if (fx_total > 0.1) {
            std::cout << "✅ 控制方向正确：正向力，应该向前加速" << std::endl;
        } else if (fx_total < -0.1) {
            std::cout << "❌ 控制方向错误：负向力，会向后加速" << std::endl;
        } else {
            std::cout << "⚠️ 控制力很小，可能是平衡状态" << std::endl;
        }
        
        // 检查重力补偿
        double fz_total = total_force(2);
        double weight = mass * 9.81;
        std::cout << "重力补偿检查:" << std::endl;
        std::cout << "  机器人重量: " << weight << " N" << std::endl;
        std::cout << "  总垂直力: " << fz_total << " N" << std::endl;
        std::cout << "  净垂直力: " << (fz_total - weight) << " N" << std::endl;
        
        if (std::abs(fz_total - weight) < 5.0) {
            std::cout << "✅ 重力补偿合理" << std::endl;
        } else {
            std::cout << "⚠️ 重力补偿可能有问题" << std::endl;
        }
        
    } else {
        std::cout << "❌ MPC求解失败" << std::endl;
        std::cout << "OSQP状态: " << mpc_controller.getSolveStatus() << std::endl;
        return -1;
    }
    
    std::cout << "\n=== 约束构建测试完成 ===" << std::endl;
    
    return 0;
}