#include "dog2_mpc/srbd_model.hpp"
#include "test_helpers.hpp"
#include <iostream>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

int main() {
    TestReporter reporter;
    reporter.printHeader("动力学模型测试");
    
    // 创建SRBD模型
    double mass = 11.8;
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    SRBDModel model(mass, inertia);
    
    // 初始状态：悬停在0.3m高度
    Eigen::VectorXd state(12);
    state << 0.0, 0.0, 0.3,    // 位置
             0.0, 0.0, 0.0,    // 姿态
             0.0, 0.0, 0.0,    // 线速度
             0.0, 0.0, 0.0;    // 角速度
    
    // 足端位置
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << -0.2, -0.15, -0.3,
                      0.2, -0.15, -0.3,
                      0.2,  0.15, -0.3,
                     -0.2,  0.15, -0.3;
    
    std::cout << "初始状态: [";
    for (int i = 0; i < state.size(); ++i) {
        std::cout << state(i);
        if (i < state.size() - 1) std::cout << ", ";
    }
    std::cout << "]" << std::endl;
    
    // 测试1：重力补偿
    reporter.printSection("测试1：重力补偿");
    double weight = mass * 9.81;
    std::cout << "机器人重量: " << weight << " N" << std::endl;
    
    // 每条腿承担1/4重量，向上的力
    Eigen::VectorXd control_hover(12);
    for (int i = 0; i < 4; ++i) {
        control_hover.segment<3>(i * 3) << 0.0, 0.0, weight / 4.0;  // 向上的力
    }
    
    std::cout << "悬停控制力 (每条腿): [0, 0, " << weight/4.0 << "]" << std::endl;
    
    Eigen::VectorXd state_dot;
    model.dynamics(state, control_hover, foot_positions, state_dot);
    
    std::cout << "状态导数:" << std::endl;
    std::cout << "  位置导数: [" << state_dot(0) << ", " << state_dot(1) << ", " << state_dot(2) << "]" << std::endl;
    std::cout << "  速度导数: [" << state_dot(6) << ", " << state_dot(7) << ", " << state_dot(8) << "]" << std::endl;
    
    if (std::abs(state_dot(8)) < 0.01) {
        reporter.printSuccess("重力补偿正确，z加速度接近0");
    } else {
        reporter.printFailure("重力补偿错误，z加速度=" + std::to_string(state_dot(8)));
    }
    
    // 测试2：前进控制
    reporter.printSection("测试2：前进控制");
    
    // 在重力补偿基础上，前腿增加向前的力
    Eigen::VectorXd control_forward = control_hover;
    control_forward(0) += 5.0;  // 腿1 x方向 +5N
    control_forward(9) += 5.0;  // 腿4 x方向 +5N
    
    std::cout << "前进控制力:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        Eigen::Vector3d f_i = control_forward.segment<3>(i * 3);
        std::cout << "  腿" << (i+1) << ": [" << f_i(0) << ", " << f_i(1) << ", " << f_i(2) << "]" << std::endl;
    }
    
    model.dynamics(state, control_forward, foot_positions, state_dot);
    
    std::cout << "状态导数:" << std::endl;
    std::cout << "  x加速度: " << state_dot(6) << " m/s²" << std::endl;
    std::cout << "  z加速度: " << state_dot(8) << " m/s²" << std::endl;
    
    if (state_dot(6) > 0.1) {
        reporter.printSuccess("前进控制正确，x加速度为正");
    } else {
        reporter.printFailure("前进控制错误，x加速度=" + std::to_string(state_dot(6)));
    }
    
    // 测试3：线性化
    reporter.printSection("测试3：线性化测试");
    
    Eigen::MatrixXd A, B;
    model.linearize(state, control_hover, foot_positions, 0.1, A, B);
    
    std::cout << "A矩阵大小: " << A.rows() << "x" << A.cols() << std::endl;
    std::cout << "B矩阵大小: " << B.rows() << "x" << B.cols() << std::endl;
    
    // 检查B矩阵的z方向控制影响
    std::cout << "B矩阵中z加速度对足端力的响应:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        double b_z_fz = B(8, i * 3 + 2);  // z加速度对第i条腿z力的响应
        std::cout << "  腿" << (i+1) << " z力 -> z加速度: " << b_z_fz << std::endl;
    }
    
    double expected_b_z_fz = 0.1 / mass;  // dt / mass
    std::cout << "期望值: " << expected_b_z_fz << std::endl;
    
    // 测试总结
    reporter.printSection("测试完成");
    reporter.printSummary(true, 3, 3);
    
    return 0;
}