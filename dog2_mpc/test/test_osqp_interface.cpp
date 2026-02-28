#include "dog2_mpc/osqp_interface.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "OSQP Interface Test" << std::endl;
    std::cout << "========================================" << std::endl;
    
    // 定义测试问题
    // min  0.5 * x^T * P * x + q^T * x
    // s.t. l <= A * x <= u
    
    Eigen::MatrixXd P(2, 2);
    P << 4.0, 1.0,
         1.0, 2.0;
    
    Eigen::VectorXd q(2);
    q << 1.0, 1.0;
    
    Eigen::MatrixXd A(3, 2);
    A << 1.0, 1.0,
         1.0, 0.0,
         0.0, 1.0;
    
    Eigen::VectorXd l(3);
    l << 1.0, 0.0, 0.0;
    
    Eigen::VectorXd u(3);
    u << 1.0, 0.7, 0.7;
    
    std::cout << "\nProblem definition:" << std::endl;
    std::cout << "P = \n" << P << std::endl;
    std::cout << "q = " << q.transpose() << std::endl;
    std::cout << "A = \n" << A << std::endl;
    std::cout << "l = " << l.transpose() << std::endl;
    std::cout << "u = " << u.transpose() << std::endl;
    
    // 创建OSQP接口
    dog2_mpc::OSQPInterface osqp;
    
    // 设置求解器参数
    osqp.setParameters(4000, 1e-4, 1e-4, true);
    
    // 设置问题
    std::cout << "\nSetting up OSQP solver..." << std::endl;
    if (!osqp.setup(P, q, A, l, u)) {
        std::cerr << "Failed to setup OSQP solver!" << std::endl;
        return 1;
    }
    std::cout << "Setup successful!" << std::endl;
    
    // 求解
    std::cout << "\nSolving..." << std::endl;
    Eigen::VectorXd solution;
    if (!osqp.solve(solution)) {
        std::cerr << "Failed to solve!" << std::endl;
        return 1;
    }
    
    // 输出结果
    std::cout << "\n========================================" << std::endl;
    std::cout << "Results:" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Solution: x = " << solution.transpose() << std::endl;
    std::cout << "Objective value: " << osqp.getObjectiveValue() << std::endl;
    std::cout << "Solve time: " << osqp.getSolveTime() << " ms" << std::endl;
    std::cout << "Iterations: " << osqp.getIterations() << std::endl;
    std::cout << "Status: " << osqp.getStatus() << std::endl;
    
    // 验证解
    std::cout << "\n========================================" << std::endl;
    std::cout << "Verification:" << std::endl;
    std::cout << "========================================" << std::endl;
    
    // 检查约束
    Eigen::VectorXd Ax = A * solution;
    std::cout << "A*x = " << Ax.transpose() << std::endl;
    std::cout << "l   = " << l.transpose() << std::endl;
    std::cout << "u   = " << u.transpose() << std::endl;
    
    bool constraints_satisfied = true;
    for (int i = 0; i < Ax.size(); ++i) {
        if (Ax(i) < l(i) - 1e-6 || Ax(i) > u(i) + 1e-6) {
            constraints_satisfied = false;
            std::cout << "Constraint " << i << " violated!" << std::endl;
        }
    }
    
    if (constraints_satisfied) {
        std::cout << "All constraints satisfied! ✓" << std::endl;
    }
    
    // 预期解
    std::cout << "\nExpected solution: x ≈ [0.3, 0.7]" << std::endl;
    std::cout << "Expected objective: ≈ 1.88" << std::endl;
    
    // 计算误差
    Eigen::VectorXd expected(2);
    expected << 0.3, 0.7;
    double error = (solution - expected).norm();
    std::cout << "Solution error: " << error << std::endl;
    
    if (error < 0.01) {
        std::cout << "\n✓ Test PASSED!" << std::endl;
        return 0;
    } else {
        std::cout << "\n✗ Test FAILED!" << std::endl;
        return 1;
    }
}
