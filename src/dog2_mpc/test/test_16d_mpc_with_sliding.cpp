#include "dog2_mpc/mpc_controller.hpp"
#include "dog2_mpc/extended_srbd_model.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;

/**
 * @brief 测试完整的16维MPC + 滑动副约束
 */
int main() {
    std::cout << "=== Dog2 16维MPC + 滑动副约束完整测试 ===" << std::endl;
    
    // 1. 创建16维MPC控制器（启用滑动副约束）
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 5;      // 中等时域
    mpc_params.dt = 0.1;         // 10Hz
    
    // 16维状态权重
    mpc_params.Q = Eigen::MatrixXd::Identity(16, 16);
    mpc_params.Q.diagonal() << 100, 100, 200,  // 位置权重 [x, y, z]
                              50, 50, 50,       // 姿态权重 [roll, pitch, yaw]
                              10, 10, 10,       // 线速度权重 [vx, vy, vz]
                              5, 5, 5,          // 角速度权重 [wx, wy, wz]
                              50, 50, 50, 50;   // 滑动副位置权重 [j1, j2, j3, j4]
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;  // 控制权重
    
    // 控制限制
    mpc_params.u_min = Eigen::VectorXd::Constant(12, -50.0);
    mpc_params.u_max = Eigen::VectorXd::Constant(12, 50.0);
    
    // 启用滑动副约束
    mpc_params.enable_sliding_constraints = true;
    mpc_params.enable_boundary_constraints = false;
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    // 2. 设置16维初始状态（滑动副位置满足协调约束：Σd≈0）
    Eigen::VectorXd x0(16);
    x0 << 0.0, 0.0, 0.3,    // 位置 [x, y, z]
          0.0, 0.0, 0.0,    // 姿态 [roll, pitch, yaw]
          0.0, 0.0, 0.0,    // 线速度 [vx, vy, vz]
          0.0, 0.0, 0.0,    // 角速度 [wx, wy, wz]
          0.0, 0.0, 0.0, 0.0;  // 滑动副位置 [j1, j2, j3, j4] - 初始为0（满足协调约束）
    
    // 3. 设置基础足端位置
    Eigen::MatrixXd base_foot_positions(4, 3);
    base_foot_positions << -0.2, -0.15, -0.3,  // 腿1
                           0.2, -0.15, -0.3,   // 腿2
                           0.2,  0.15, -0.3,   // 腿3
                          -0.2,  0.15, -0.3;   // 腿4
    mpc_controller.setBaseFootPositions(base_foot_positions);
    
    // 4. 设置滑动副速度（零速度，保持静止）
    Eigen::Vector4d sliding_velocity = Eigen::Vector4d::Zero();
    mpc_controller.setSlidingVelocity(sliding_velocity);
    
    // 5. 设置16维参考轨迹（向前移动，滑动副保持为0）
    std::vector<Eigen::VectorXd> x_ref(mpc_params.horizon);
    for (int k = 0; k < mpc_params.horizon; ++k) {
        x_ref[k] = Eigen::VectorXd::Zero(16);
        x_ref[k](0) = (k + 1) * 0.05;  // x位置递增
        x_ref[k](2) = 0.3;             // 保持高度
        x_ref[k](6) = 0.05;            // 期望前进速度
        // 滑动副位置保持为0（满足协调约束）
        x_ref[k](12) = 0.0;  // j1
        x_ref[k](13) = 0.0;  // j2
        x_ref[k](14) = 0.0;  // j3
        x_ref[k](15) = 0.0;  // j4
    }
    mpc_controller.setReference(x_ref);
    
    std::cout << "\n=== 16维参考轨迹（包含滑动副） ===" << std::endl;
    for (int k = 0; k < mpc_params.horizon; ++k) {
        std::cout << "步骤" << k << ": x_ref=" << x_ref[k](0) 
                  << ", z_ref=" << x_ref[k](2) 
                  << ", vx_ref=" << x_ref[k](6) 
                  << ", j1_ref=" << x_ref[k](12) << std::endl;
    }
    
    // 6. 求解16维MPC + 滑动副约束
    std::cout << "\n=== 16维MPC + 滑动副约束求解 ===" << std::endl;
    
    std::cout << "16维初始状态: [";
    for (int i = 0; i < 12; ++i) {
        std::cout << x0(i) << ", ";
    }
    std::cout << "滑动副: " << x0(12) << ", " << x0(13) << ", " 
              << x0(14) << ", " << x0(15) << "]" << std::endl;
    
    Eigen::VectorXd u_optimal;
    bool success = mpc_controller.solve(x0, u_optimal);
    
    if (success) {
        std::cout << "✅ 16维MPC + 滑动副约束求解成功！" << std::endl;
        std::cout << "求解时间: " << mpc_controller.getSolveTime() << "ms" << std::endl;
        
        // 7. 分析求解结果
        std::cout << "\n=== 求解结果分析 ===" << std::endl;
        
        // 第一步控制
        std::cout << "第一步控制 u_0:" << std::endl;
        for (int i = 0; i < 4; ++i) {
            Eigen::Vector3d f_i = u_optimal.segment<3>(i * 3);
            std::cout << "  腿" << (i+1) << ": fx=" << std::setw(8) << f_i(0) 
                      << ", fy=" << std::setw(8) << f_i(1) 
                      << ", fz=" << std::setw(8) << f_i(2) << std::endl;
        }
        
        // 16维预测轨迹（包含滑动副）
        auto predicted_states = mpc_controller.getPredictedTrajectory();
        std::cout << "\n16维预测轨迹（包含滑动副）:" << std::endl;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            std::cout << "步骤" << k << ": x=" << std::setw(8) << predicted_states[k](0)
                      << ", z=" << std::setw(8) << predicted_states[k](2)
                      << ", vx=" << std::setw(8) << predicted_states[k](6)
                      << ", 滑动副=[" << predicted_states[k](12) << ", " 
                      << predicted_states[k](13) << ", " 
                      << predicted_states[k](14) << ", " 
                      << predicted_states[k](15) << "]" << std::endl;
        }
        
        // 8. 验证滑动副约束
        std::cout << "\n=== 滑动副约束验证 ===" << std::endl;
        
        // 检查位置限位
        Eigen::Vector4d d_min(-0.111, -0.008, -0.008, -0.111);
        Eigen::Vector4d d_max(0.008, 0.111, 0.111, 0.008);
        
        bool position_ok = true;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            Eigen::Vector4d d = predicted_states[k].segment<4>(12);
            for (int i = 0; i < 4; ++i) {
                if (d(i) < d_min(i) - 1e-6 || d(i) > d_max(i) + 1e-6) {
                    std::cout << "❌ 步骤" << k << " 滑动副" << (i+1) 
                              << " 超出限位: " << d(i) 
                              << " (限位: [" << d_min(i) << ", " << d_max(i) << "])" << std::endl;
                    position_ok = false;
                }
            }
        }
        if (position_ok) {
            std::cout << "✅ 所有滑动副位置满足限位约束" << std::endl;
        }
        
        // 检查速度限制
        double v_max = 1.0;
        bool velocity_ok = true;
        for (int k = 0; k < mpc_params.horizon - 1; ++k) {
            Eigen::Vector4d d_k = predicted_states[k].segment<4>(12);
            Eigen::Vector4d d_k1 = predicted_states[k+1].segment<4>(12);
            Eigen::Vector4d v = (d_k1 - d_k) / mpc_params.dt;
            
            for (int i = 0; i < 4; ++i) {
                if (std::abs(v(i)) > v_max + 1e-6) {
                    std::cout << "❌ 步骤" << k << "→" << (k+1) << " 滑动副" << (i+1) 
                              << " 速度超限: " << v(i) << " m/s (限制: " << v_max << " m/s)" << std::endl;
                    velocity_ok = false;
                }
            }
        }
        if (velocity_ok) {
            std::cout << "✅ 所有滑动副速度满足限制" << std::endl;
        }
        
        // 检查对称约束
        double epsilon_sym = 0.02;
        bool symmetry_ok = true;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            Eigen::Vector4d d = predicted_states[k].segment<4>(12);
            double diff_13 = std::abs(d(0) - d(2));
            double diff_24 = std::abs(d(1) - d(3));
            
            if (diff_13 > epsilon_sym + 1e-6) {
                std::cout << "❌ 步骤" << k << " 对称约束违反: |d1-d3|=" << diff_13 
                          << " > " << epsilon_sym << std::endl;
                symmetry_ok = false;
            }
            if (diff_24 > epsilon_sym + 1e-6) {
                std::cout << "❌ 步骤" << k << " 对称约束违反: |d2-d4|=" << diff_24 
                          << " > " << epsilon_sym << std::endl;
                symmetry_ok = false;
            }
        }
        if (symmetry_ok) {
            std::cout << "✅ 所有滑动副满足对称约束" << std::endl;
        }
        
        // 检查协调约束
        double coord_tolerance = 0.05;
        bool coordination_ok = true;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            Eigen::Vector4d d = predicted_states[k].segment<4>(12);
            double sum = d.sum();
            
            if (std::abs(sum) > coord_tolerance + 1e-6) {
                std::cout << "❌ 步骤" << k << " 协调约束违反: Σd=" << sum 
                          << " (容差: " << coord_tolerance << ")" << std::endl;
                coordination_ok = false;
            }
        }
        if (coordination_ok) {
            std::cout << "✅ 所有滑动副满足协调约束" << std::endl;
        }
        
        // 总结
        std::cout << "\n=== 约束验证总结 ===" << std::endl;
        if (position_ok && velocity_ok && symmetry_ok && coordination_ok) {
            std::cout << "🎉 所有滑动副约束都满足！16维MPC + 滑动副约束系统工作正常！" << std::endl;
        } else {
            std::cout << "⚠️ 部分约束未满足，需要调整参数或检查实现" << std::endl;
        }
        
    } else {
        std::cout << "❌ 16维MPC + 滑动副约束求解失败" << std::endl;
        std::cout << "OSQP状态: " << mpc_controller.getSolveStatus() << std::endl;
        return -1;
    }
    
    std::cout << "\n=== 16维MPC + 滑动副约束完整测试完成 ===" << std::endl;
    
    return 0;
}
