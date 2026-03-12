#include "dog2_mpc/extended_srbd_model.hpp"
#include <iostream>

using namespace dog2_mpc;

int main() {
    std::cout << "=== 简单16维测试 ===" << std::endl;
    
    // 测试扩展SRBD模型
    ExtendedSRBDModel model(7.94, Eigen::Matrix3d::Identity() * 0.1);
    
    // 16维状态
    Eigen::VectorXd state(16);
    state.setZero();
    state(2) = 0.3;  // z = 0.3m
    
    // 控制输入
    Eigen::VectorXd control(12);
    control.setZero();
    for (int i = 0; i < 4; ++i) {
        control(i * 3 + 2) = 7.94 * 9.81 / 4.0;  // 重力补偿
    }
    
    // 基础足端位置
    Eigen::MatrixXd base_foot_positions(4, 3);
    base_foot_positions << -0.2, -0.15, -0.3,
                           0.2, -0.15, -0.3,
                           0.2,  0.15, -0.3,
                          -0.2,  0.15, -0.3;
    
    // 滑动副速度
    Eigen::Vector4d sliding_velocity = Eigen::Vector4d::Zero();
    
    // 计算动力学
    Eigen::VectorXd state_dot;
    model.dynamics(state, control, base_foot_positions, sliding_velocity, state_dot);
    
    std::cout << "16维状态: " << state.transpose() << std::endl;
    std::cout << "16维状态导数: " << state_dot.transpose() << std::endl;
    
    // 检查z加速度是否接近0（重力补偿）
    if (std::abs(state_dot(8)) < 0.1) {
        std::cout << "✅ 16维扩展SRBD模型工作正常" << std::endl;
    } else {
        std::cout << "❌ 16维扩展SRBD模型有问题" << std::endl;
    }
    
    return 0;
}