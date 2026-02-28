#include "dog2_mpc/osqp_interface.hpp"
#include <iostream>
#include <iomanip>
#include <cmath>

// 测试用例1：简单的2D QP问题
bool test_simple_2d_qp() {
    std::cout << "\n=== 测试1: 简单2D QP问题 ===" << std::endl;
    std::cout << "问题: min 0.5*(x1^2 + x2^2) - x1 - x2" << std::endl;
    std::cout << "约束: x1 + x2 <= 1, x1 >= 0, x2 >= 0" << std::endl;
    std::cout << "理论最优解: x1=0.5, x2=0.5, obj=-0.75" << std::endl;
    
    Eigen::MatrixXd P(2, 2);
    P << 1.0, 0.0,
         0.0, 1.0;
    
    Eigen::VectorXd q(2);
    q << -1.0, -1.0;
    
    Eigen::MatrixXd A(3, 2);
    A << 1.0, 1.0,
         1.0, 0.0,
         0.0, 1.0;
    
    Eigen::VectorXd l(3);
    l << -1e20, 0.0, 0.0;
    
    Eigen::VectorXd u(3);
    u << 1.0, 1e20, 1e20;
    
    dog2_mpc::OSQPInterface solver;
    
    if (!solver.setup(P, q, A, l, u)) {
        std::cerr << "✗ 设置失败" << std::endl;
        return false;
    }
    
    Eigen::VectorXd solution;
    if (!solver.solve(solution)) {
        std::cerr << "✗ 求解失败 (状态码: " << solver.getStatus() << ")" << std::endl;
        return false;
    }
    
    std::cout << "求解结果:" << std::endl;
    std::cout << "  x = [" << solution(0) << ", " << solution(1) << "]" << std::endl;
    std::cout << "  目标函数值: " << solver.getObjectiveValue() << std::endl;
    std::cout << "  迭代次数: " << solver.getIterations() << std::endl;
    std::cout << "  求解时间: " << solver.getSolveTime() << " ms" << std::endl;
    
    double tol = 1e-2;
    bool x1_ok = std::abs(solution(0) - 0.5) < tol;
    bool x2_ok = std::abs(solution(1) - 0.5) < tol;
    bool obj_ok = std::abs(solver.getObjectiveValue() - (-0.75)) < tol;
    
    if (x1_ok && x2_ok && obj_ok) {
        std::cout << "✓ 测试通过！" << std::endl;
        return true;
    } else {
        std::cout << "✗ 解不正确" << std::endl;
        return false;
    }
}

// 测试用例2：带等式约束的QP问题
bool test_equality_constraint_qp() {
    std::cout << "\n=== 测试2: 带等式约束的QP问题 ===" << std::endl;
    std::cout << "问题: min 0.5*(x1^2 + x2^2 + x3^2)" << std::endl;
    std::cout << "约束: x1 + x2 + x3 = 1, x1,x2,x3 >= 0" << std::endl;
    std::cout << "理论最优解: x1=x2=x3=1/3, obj=1/6≈0.1667" << std::endl;
    
    Eigen::MatrixXd P(3, 3);
    P << 1.0, 0.0, 0.0,
         0.0, 1.0, 0.0,
         0.0, 0.0, 1.0;
    
    Eigen::VectorXd q(3);
    q << 0.0, 0.0, 0.0;
    
    Eigen::MatrixXd A(4, 3);
    A << 1.0, 1.0, 1.0,
         1.0, 0.0, 0.0,
         0.0, 1.0, 0.0,
         0.0, 0.0, 1.0;
    
    Eigen::VectorXd l(4);
    l << 1.0, 0.0, 0.0, 0.0;
    
    Eigen::VectorXd u(4);
    u << 1.0, 1e20, 1e20, 1e20;
    
    dog2_mpc::OSQPInterface solver;
    
    if (!solver.setup(P, q, A, l, u)) {
        std::cerr << "✗ 设置失败" << std::endl;
        return false;
    }
    
    Eigen::VectorXd solution;
    if (!solver.solve(solution)) {
        std::cerr << "✗ 求解失败 (状态码: " << solver.getStatus() << ")" << std::endl;
        return false;
    }
    
    std::cout << "求解结果:" << std::endl;
    std::cout << "  x = [" << solution(0) << ", " << solution(1) << ", " << solution(2) << "]" << std::endl;
    std::cout << "  目标函数值: " << solver.getObjectiveValue() << std::endl;
    std::cout << "  迭代次数: " << solver.getIterations() << std::endl;
    
    double tol = 1e-2;
    double expected_val = 1.0/3.0;
    bool x1_ok = std::abs(solution(0) - expected_val) < tol;
    bool x2_ok = std::abs(solution(1) - expected_val) < tol;
    bool x3_ok = std::abs(solution(2) - expected_val) < tol;
    bool obj_ok = std::abs(solver.getObjectiveValue() - 1.0/6.0) < tol;
    
    if (x1_ok && x2_ok && x3_ok && obj_ok) {
        std::cout << "✓ 测试通过！" << std::endl;
        return true;
    } else {
        std::cout << "✗ 解不正确" << std::endl;
        return false;
    }
}

// 测试用例3：稀疏矩阵接口
bool test_sparse_matrix_qp() {
    std::cout << "\n=== 测试3: 稀疏矩阵接口 ===" << std::endl;
    
    Eigen::SparseMatrix<double> P(2, 2);
    P.insert(0, 0) = 1.0;
    P.insert(1, 1) = 1.0;
    P.makeCompressed();
    
    Eigen::VectorXd q(2);
    q << -1.0, -1.0;
    
    Eigen::SparseMatrix<double> A(3, 2);
    A.insert(0, 0) = 1.0;
    A.insert(0, 1) = 1.0;
    A.insert(1, 0) = 1.0;
    A.insert(2, 1) = 1.0;
    A.makeCompressed();
    
    Eigen::VectorXd l(3);
    l << -1e20, 0.0, 0.0;
    
    Eigen::VectorXd u(3);
    u << 1.0, 1e20, 1e20;
    
    dog2_mpc::OSQPInterface solver;
    
    if (!solver.setup(P, q, A, l, u)) {
        std::cerr << "✗ 设置失败" << std::endl;
        return false;
    }
    
    Eigen::VectorXd solution;
    if (!solver.solve(solution)) {
        std::cerr << "✗ 求解失败 (状态码: " << solver.getStatus() << ")" << std::endl;
        return false;
    }
    
    std::cout << "求解结果:" << std::endl;
    std::cout << "  x = [" << solution(0) << ", " << solution(1) << "]" << std::endl;
    std::cout << "  目标函数值: " << solver.getObjectiveValue() << std::endl;
    
    double tol = 1e-2;
    bool x1_ok = std::abs(solution(0) - 0.5) < tol;
    bool x2_ok = std::abs(solution(1) - 0.5) < tol;
    
    if (x1_ok && x2_ok) {
        std::cout << "✓ 测试通过！" << std::endl;
        return true;
    } else {
        std::cout << "✗ 解不正确" << std::endl;
        return false;
    }
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "  OSQP接口完整功能测试" << std::endl;
    std::cout << "========================================" << std::endl;
    
    int passed = 0;
    int total = 3;
    
    if (test_simple_2d_qp()) passed++;
    if (test_equality_constraint_qp()) passed++;
    if (test_sparse_matrix_qp()) passed++;
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "测试总结: " << passed << "/" << total << " 通过" << std::endl;
    std::cout << "========================================" << std::endl;
    
    if (passed == total) {
        std::cout << "✓ 所有测试通过！OSQP接口工作正常。" << std::endl;
        return 0;
    } else {
        std::cout << "✗ 部分测试失败。" << std::endl;
        return 1;
    }
}
