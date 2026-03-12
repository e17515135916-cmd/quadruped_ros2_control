#include "dog2_mpc/osqp_interface.hpp"
#include <iostream>
#include <Eigen/Dense>

using namespace dog2_mpc;

int main() {
    std::cout << "=== 简单QP测试 ===" << std::endl;
    
    // 创建一个简单的2D QP问题
    // min 0.5 * x^T * P * x + q^T * x
    // s.t. A * x = b (等式约束)
    
    // 目标函数: min 0.5 * (x1^2 + x2^2) - x1 - 2*x2
    Eigen::MatrixXd P(2, 2);
    P << 1.0, 0.0,
         0.0, 1.0;
    
    Eigen::VectorXd q(2);
    q << -1.0, -2.0;
    
    // 约束: x1 + x2 = 1
    Eigen::MatrixXd A(1, 2);
    A << 1.0, 1.0;
    
    Eigen::VectorXd l(1), u(1);
    l << 1.0;  // 等式约束的下界
    u << 1.0;  // 等式约束的上界
    
    // 求解
    OSQPInterface solver;
    bool setup_success = solver.setup(P, q, A, l, u);
    
    if (!setup_success) {
        std::cout << "❌ OSQP设置失败" << std::endl;
        return -1;
    }
    
    Eigen::VectorXd solution;
    bool solve_success = solver.solve(solution);
    
    if (solve_success) {
        std::cout << "✅ 求解成功！" << std::endl;
        std::cout << "解: x1=" << solution(0) << ", x2=" << solution(1) << std::endl;
        std::cout << "验证约束: x1+x2=" << (solution(0) + solution(1)) << " (应该=1)" << std::endl;
        std::cout << "目标函数值: " << solver.getObjectiveValue() << std::endl;
        
        // 解析解应该是: x1=-0.5, x2=1.5 (拉格朗日乘数法)
        std::cout << "理论解: x1=-0.5, x2=1.5" << std::endl;
    } else {
        std::cout << "❌ 求解失败，状态码: " << solver.getStatus() << std::endl;
    }
    
    return 0;
}