#include "src/dog2_mpc/include/dog2_mpc/osqp_interface.hpp"
#include <iostream>

int main() {
    std::cout << "=== OSQP接口调试测试 ===" << std::endl;
    
    // 简单的2x2问题
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
    
    std::cout << "1. 调用setup..." << std::endl;
    bool setup_ok = solver.setup(P, q, A, l, u);
    std::cout << "   setup返回: " << (setup_ok ? "true" : "false") << std::endl;
    std::cout << "   isInitialized: " << (solver.isInitialized() ? "true" : "false") << std::endl;
    
    if (!setup_ok) {
        std::cerr << "Setup失败！" << std::endl;
        return 1;
    }
    
    std::cout << "\n2. 调用solve..." << std::endl;
    Eigen::VectorXd solution;
    bool solve_ok = solver.solve(solution);
    std::cout << "   solve返回: " << (solve_ok ? "true" : "false") << std::endl;
    std::cout << "   状态码: " << solver.getStatus() << std::endl;
    std::cout << "   迭代次数: " << solver.getIterations() << std::endl;
    
    if (solve_ok) {
        std::cout << "\n3. 解:" << std::endl;
        std::cout << "   x = [" << solution(0) << ", " << solution(1) << "]" << std::endl;
        std::cout << "   obj = " << solver.getObjectiveValue() << std::endl;
    }
    
    return solve_ok ? 0 : 1;
}
