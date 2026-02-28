#include "dog2_mpc/extended_srbd_model.hpp"
#include "dog2_mpc/sliding_constraints.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;

/**
 * @brief 测试滑动副约束的核心功能
 */
int main() {
    std::cout << "=== Dog2 滑动副约束测试 ===" << std::endl;
    
    // 1. 测试扩展SRBD模型
    std::cout << "\n=== 测试1：扩展SRBD模型 ===" << std::endl;
    
    double mass = 11.8;
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    ExtendedSRBDModel extended_model(mass, inertia);
    
    // 初始状态：16维 [SRBD(12) + 滑动副(4)]
    Eigen::VectorXd extended_state(16);
    extended_state << 0.0, 0.0, 0.3,    // 位置
                      0.0, 0.0, 0.0,    // 姿态
                      0.0, 0.0, 0.0,    // 线速度
                      0.0, 0.0, 0.0,    // 角速度
                      0.0, 0.0, 0.0, 0.0;  // 滑动副位置 [j1, j2, j3, j4]
    
    std::cout << "扩展状态维度: " << extended_state.size() << std::endl;
    
    // 提取SRBD状态和滑动副位置
    Eigen::VectorXd srbd_state = ExtendedSRBDModel::extractSRBDState(extended_state);
    Eigen::Vector4d sliding_positions = ExtendedSRBDModel::extractSlidingPositions(extended_state);
    
    std::cout << "SRBD状态维度: " << srbd_state.size() << std::endl;
    std::cout << "滑动副位置: [" << sliding_positions.transpose() << "]" << std::endl;
    
    // 基础足端位置
    Eigen::MatrixXd base_foot_positions(4, 3);
    base_foot_positions << -0.2, -0.15, -0.3,  // 腿1
                           0.2, -0.15, -0.3,   // 腿2
                           0.2,  0.15, -0.3,   // 腿3
                          -0.2,  0.15, -0.3;   // 腿4
    
    // 计算实际足端位置（考虑滑动副）
    Eigen::MatrixXd actual_foot_positions = extended_model.computeFootPositions(
        sliding_positions, base_foot_positions);
    
    std::cout << "基础足端位置:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "  腿" << (i+1) << ": [" << base_foot_positions.row(i) << "]" << std::endl;
    }
    
    std::cout << "实际足端位置（滑动副=0）:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "  腿" << (i+1) << ": [" << actual_foot_positions.row(i) << "]" << std::endl;
    }
    
    // 2. 测试滑动副影响
    std::cout << "\n=== 测试2：滑动副影响 ===" << std::endl;
    
    // 设置滑动副位置：前腿向前伸展0.05m，后腿向后收缩0.03m
    Eigen::Vector4d test_sliding_positions;
    test_sliding_positions << 0.05, -0.03, -0.03, 0.05;  // j1, j2, j3, j4
    
    Eigen::MatrixXd test_foot_positions = extended_model.computeFootPositions(
        test_sliding_positions, base_foot_positions);
    
    std::cout << "滑动副位置: [" << test_sliding_positions.transpose() << "]" << std::endl;
    std::cout << "影响后的足端位置:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        Eigen::Vector3d offset = test_foot_positions.row(i) - base_foot_positions.row(i);
        std::cout << "  腿" << (i+1) << ": [" << test_foot_positions.row(i) 
                  << "] (偏移: [" << offset.transpose() << "])" << std::endl;
    }
    
    // 3. 测试扩展动力学
    std::cout << "\n=== 测试3：扩展动力学 ===" << std::endl;
    
    // 控制输入：重力补偿
    Eigen::VectorXd control(12);
    double weight_per_leg = mass * 9.81 / 4.0;
    for (int i = 0; i < 4; ++i) {
        control.segment<3>(i * 3) << 0.0, 0.0, weight_per_leg;
    }
    
    // 滑动副速度：前腿向前，后腿向后
    Eigen::Vector4d sliding_velocity;
    sliding_velocity << 0.1, -0.1, -0.1, 0.1;  // m/s
    
    Eigen::VectorXd state_dot;
    extended_model.dynamics(extended_state, control, base_foot_positions, 
                           sliding_velocity, state_dot);
    
    std::cout << "控制输入 (每条腿): [0, 0, " << weight_per_leg << "]" << std::endl;
    std::cout << "滑动副速度: [" << sliding_velocity.transpose() << "]" << std::endl;
    std::cout << "状态导数:" << std::endl;
    std::cout << "  位置导数: [" << state_dot.segment<3>(0).transpose() << "]" << std::endl;
    std::cout << "  速度导数: [" << state_dot.segment<3>(6).transpose() << "]" << std::endl;
    std::cout << "  滑动副导数: [" << state_dot.segment<4>(12).transpose() << "]" << std::endl;
    
    // 验证滑动副导数是否等于滑动副速度
    Eigen::Vector4d sliding_dot = state_dot.segment<4>(12);
    if ((sliding_dot - sliding_velocity).norm() < 1e-6) {
        std::cout << "✅ 滑动副动力学正确：j̇ = v_sliding" << std::endl;
    } else {
        std::cout << "❌ 滑动副动力学错误" << std::endl;
    }
    
    // 4. 测试线性化
    std::cout << "\n=== 测试4：扩展线性化 ===" << std::endl;
    
    Eigen::MatrixXd A, B, C;
    extended_model.linearize(extended_state, control, base_foot_positions,
                            sliding_velocity, 0.1, A, B, C);
    
    std::cout << "A矩阵大小: " << A.rows() << "×" << A.cols() << std::endl;
    std::cout << "B矩阵大小: " << B.rows() << "×" << B.cols() << std::endl;
    std::cout << "C矩阵大小: " << C.rows() << "×" << C.cols() << std::endl;
    
    // 检查C矩阵的滑动副部分（应该是单位矩阵*dt）
    Eigen::Matrix4d C_sliding = C.block<4, 4>(12, 0);
    Eigen::Matrix4d expected_C = Eigen::Matrix4d::Identity() * 0.1;
    
    std::cout << "C矩阵滑动副部分:" << std::endl;
    std::cout << C_sliding << std::endl;
    std::cout << "期望值:" << std::endl;
    std::cout << expected_C << std::endl;
    
    if ((C_sliding - expected_C).norm() < 1e-6) {
        std::cout << "✅ 滑动副线性化正确" << std::endl;
    } else {
        std::cout << "❌ 滑动副线性化错误" << std::endl;
    }
    
    // 5. 测试滑动副约束
    std::cout << "\n=== 测试5：滑动副约束 ===" << std::endl;
    
    SlidingConstraints sliding_constraints;
    
    // 设置约束参数
    Eigen::Vector4d d_min, d_max;
    d_min << -0.111, -0.008, -0.008, -0.111;  // j1, j2, j3, j4 下限
    d_max << 0.008, 0.111, 0.111, 0.008;     // j1, j2, j3, j4 上限
    
    sliding_constraints.setPositionLimits(d_min, d_max);
    sliding_constraints.setVelocityLimit(1.0);  // 1 m/s
    sliding_constraints.setSymmetryTolerance(0.02);  // 2cm
    
    std::cout << "位置限位:" << std::endl;
    std::cout << "  下限: [" << d_min.transpose() << "]" << std::endl;
    std::cout << "  上限: [" << d_max.transpose() << "]" << std::endl;
    std::cout << "速度限制: 1.0 m/s" << std::endl;
    std::cout << "对称容差: 0.02 m" << std::endl;
    
    // 测试约束添加
    int horizon = 3;
    std::vector<Eigen::Triplet<double>> A_triplets;
    Eigen::VectorXd l_ineq(1000), u_ineq(1000);  // 预分配足够空间
    int constraint_index = 0;
    
    // 添加位置约束
    sliding_constraints.addPositionConstraints(horizon, A_triplets, l_ineq, u_ineq, constraint_index);
    int pos_constraints = constraint_index;
    
    // 添加速度约束
    sliding_constraints.addVelocityConstraints(horizon, 0.1, A_triplets, l_ineq, u_ineq, constraint_index);
    int vel_constraints = constraint_index - pos_constraints;
    
    // 添加对称约束
    sliding_constraints.addSymmetryConstraints(horizon, A_triplets, l_ineq, u_ineq, constraint_index);
    int sym_constraints = constraint_index - pos_constraints - vel_constraints;
    
    std::cout << "约束统计:" << std::endl;
    std::cout << "  位置约束: " << pos_constraints << " 个" << std::endl;
    std::cout << "  速度约束: " << vel_constraints << " 个" << std::endl;
    std::cout << "  对称约束: " << sym_constraints << " 个" << std::endl;
    std::cout << "  总约束: " << constraint_index << " 个" << std::endl;
    std::cout << "  非零元素: " << A_triplets.size() << " 个" << std::endl;
    
    // 验证约束数量
    int expected_pos = horizon * 4;  // 每个时间步4个滑动副
    int expected_vel = (horizon - 1) * 4;  // 相邻时间步的速度约束
    int expected_sym = horizon * 2;  // 每个时间步2个对称约束
    
    if (pos_constraints == expected_pos && vel_constraints == expected_vel && sym_constraints == expected_sym) {
        std::cout << "✅ 约束数量正确" << std::endl;
    } else {
        std::cout << "❌ 约束数量错误" << std::endl;
        std::cout << "  期望位置约束: " << expected_pos << ", 实际: " << pos_constraints << std::endl;
        std::cout << "  期望速度约束: " << expected_vel << ", 实际: " << vel_constraints << std::endl;
        std::cout << "  期望对称约束: " << expected_sym << ", 实际: " << sym_constraints << std::endl;
    }
    
    std::cout << "\n=== 滑动副约束测试完成 ===" << std::endl;
    
    return 0;
}