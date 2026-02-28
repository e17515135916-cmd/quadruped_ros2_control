#include "dog2_mpc/osqp_interface.hpp"
#include <iostream>
#include <Eigen/Dense>

using namespace dog2_mpc;

/**
 * @brief 测试简单的跟踪问题
 * min 0.5 * (x - x_ref)^T * Q * (x - x_ref) + 0.5 * u^T * R * u
 * s.t. x_next = A * x + B * u
 */
int main() {
    std::cout << "=== 简单跟踪问题测试 ===" << std::endl;
    
    // 问题参数
    const int nx = 2;  // 状态维度 [position, velocity]
    const int nu = 1;  // 控制维度 [force]
    const int N = 3;   // 时域长度
    
    // 系统矩阵 (简单的积分器)
    double dt = 0.1;
    Eigen::Matrix2d A;
    A << 1, dt,
         0, 1;
    
    Eigen::Vector2d B;
    B << 0.5 * dt * dt, dt;  // 假设质量为1
    
    // 权重矩阵
    Eigen::Matrix2d Q = Eigen::Matrix2d::Identity() * 100;
    double R = 1.0;
    
    // 初始状态和参考轨迹
    Eigen::Vector2d x0(0, 0);  // 初始位置和速度都为0
    std::vector<Eigen::Vector2d> x_ref(N);
    for (int k = 0; k < N; ++k) {
        x_ref[k] << (k + 1) * 0.1, 0.1;  // 期望位置递增，期望速度0.1
    }
    
    std::cout << "初始状态: x=" << x0(0) << ", v=" << x0(1) << std::endl;
    std::cout << "参考轨迹:" << std::endl;
    for (int k = 0; k < N; ++k) {
        std::cout << "  步骤" << k << ": x_ref=" << x_ref[k](0) << ", v_ref=" << x_ref[k](1) << std::endl;
    }
    
    // 构建QP问题
    // 变量: [x1, u0, x2, u1, x3, u2]
    const int nv = N * (nx + nu);  // 总变量数
    
    // 目标函数 P 矩阵
    Eigen::MatrixXd P = Eigen::MatrixXd::Zero(nv, nv);
    for (int k = 0; k < N; ++k) {
        int x_offset = k * (nx + nu);
        int u_offset = x_offset + nx;
        
        // 状态权重
        P.block(x_offset, x_offset, nx, nx) = Q;
        
        // 控制权重
        P(u_offset, u_offset) = R;
    }
    
    // 线性项 q
    Eigen::VectorXd q = Eigen::VectorXd::Zero(nv);
    for (int k = 0; k < N; ++k) {
        int x_offset = k * (nx + nu);
        q.segment(x_offset, nx) = -Q * x_ref[k];
    }
    
    // 约束矩阵 A_eq 和边界
    // 约束: x_{k+1} = A * x_k + B * u_k (k = 0, 1, ..., N-1)
    // 但是我们的变量是 [x_1, u_0, x_2, u_1, x_3, u_2]
    // 所以约束是: x_1 = A * x_0 + B * u_0, x_2 = A * x_1 + B * u_1, x_3 = A * x_2 + B * u_2
    const int n_constraints = N * nx;
    Eigen::MatrixXd A_eq = Eigen::MatrixXd::Zero(n_constraints, nv);
    Eigen::VectorXd l = Eigen::VectorXd::Zero(n_constraints);
    Eigen::VectorXd u_vec = Eigen::VectorXd::Zero(n_constraints);
    
    for (int k = 0; k < N; ++k) {
        int constraint_offset = k * nx;
        int x_k_offset = k * (nx + nu);      // x_{k+1}的位置
        int u_k_offset = x_k_offset + nx;    // u_k的位置
        
        // 约束: x_{k+1} = A * x_k + B * u_k
        // 重写为: x_{k+1} - B * u_k = A * x_k
        A_eq.block(constraint_offset, x_k_offset, nx, nx) = Eigen::Matrix2d::Identity();
        A_eq.block(constraint_offset, u_k_offset, nx, nu) = -B;
        
        if (k == 0) {
            // 第一个约束: x_1 - B * u_0 = A * x_0
            l.segment(constraint_offset, nx) = A * x0;
            u_vec.segment(constraint_offset, nx) = A * x0;
        } else {
            // 后续约束: x_{k+1} - B * u_k = A * x_k
            // 需要添加 -A * x_k 项
            int prev_x_offset = (k - 1) * (nx + nu);
            A_eq.block(constraint_offset, prev_x_offset, nx, nx) = -A;
            l.segment(constraint_offset, nx).setZero();
            u_vec.segment(constraint_offset, nx).setZero();
        }
    }
    
    std::cout << "\n=== QP问题构建完成 ===" << std::endl;
    std::cout << "变量数: " << nv << std::endl;
    std::cout << "约束数: " << n_constraints << std::endl;
    
    // 转换为稀疏矩阵
    Eigen::SparseMatrix<double> P_sparse = P.sparseView();
    Eigen::SparseMatrix<double> A_sparse = A_eq.sparseView();
    
    // 求解
    OSQPInterface solver;
    solver.setup(P_sparse, q, A_sparse, l, u_vec);
    
    Eigen::VectorXd solution;
    bool success = solver.solve(solution);
    
    if (success) {
        std::cout << "\n=== 求解成功 ===" << std::endl;
        
        // 提取解
        for (int k = 0; k < N; ++k) {
            int x_offset = k * (nx + nu);
            int u_offset = x_offset + nx;
            
            Eigen::Vector2d x_k = solution.segment(x_offset, nx);
            double u_k = solution(u_offset);
            
            std::cout << "步骤" << k << ": x=" << x_k(0) << ", v=" << x_k(1) 
                      << ", u=" << u_k << " (参考: x=" << x_ref[k](0) 
                      << ", v=" << x_ref[k](1) << ")" << std::endl;
        }
        
        // 验证第一步的控制是否合理
        double u0 = solution(nx);
        std::cout << "\n第一步控制: u0=" << u0 << std::endl;
        
        // 预测下一步状态
        Eigen::Vector2d x1_predicted = A * x0 + B * u0;
        std::cout << "预测下一步状态: x=" << x1_predicted(0) << ", v=" << x1_predicted(1) << std::endl;
        std::cout << "期望下一步状态: x=" << x_ref[0](0) << ", v=" << x_ref[0](1) << std::endl;
        
        if (u0 > 0) {
            std::cout << "✅ 控制方向正确（正向力，应该加速前进）" << std::endl;
        } else {
            std::cout << "❌ 控制方向错误（负向力，会向后加速）" << std::endl;
        }
        
    } else {
        std::cout << "❌ 求解失败" << std::endl;
        return -1;
    }
    
    return 0;
}