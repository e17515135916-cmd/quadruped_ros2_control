#include <iostream>
#include <osqp/osqp.h>

int main() {
    std::cout << "=== 最小OSQP测试 ===" << std::endl;
    
    // 简单的2x2 QP问题
    // min 0.5 * x^T * [1 0; 0 1] * x + [-1; -1]^T * x
    // s.t. x1 + x2 <= 1, x1 >= 0, x2 >= 0
    
    OSQPInt n = 2;  // 变量数
    OSQPInt m = 3;  // 约束数
    
    // P矩阵 (单位矩阵)
    OSQPFloat P_x[] = {1.0, 1.0};
    OSQPInt P_i[] = {0, 1};
    OSQPInt P_p[] = {0, 1, 2};
    OSQPCscMatrix* P = OSQPCscMatrix_new(n, n, 2, P_x, P_i, P_p);
    P->owned = 1;
    
    // q向量
    OSQPFloat q[] = {-1.0, -1.0};
    
    // A矩阵
    OSQPFloat A_x[] = {1.0, 1.0, 1.0, 1.0};
    OSQPInt A_i[] = {0, 1, 0, 1};
    OSQPInt A_p[] = {0, 2, 4};
    OSQPCscMatrix* A = OSQPCscMatrix_new(m, n, 4, A_x, A_i, A_p);
    A->owned = 1;
    
    // 约束边界
    OSQPFloat l[] = {-OSQP_INFTY, 0.0, 0.0};
    OSQPFloat u[] = {1.0, OSQP_INFTY, OSQP_INFTY};
    
    // 设置
    OSQPSettings* settings = (OSQPSettings*)malloc(sizeof(OSQPSettings));
    osqp_set_default_settings(settings);
    settings->verbose = 1;
    
    // 创建求解器
    OSQPSolver* solver = nullptr;
    OSQPInt exitflag = osqp_setup(&solver, P, q, A, l, u, m, n, settings);
    
    if (exitflag != 0) {
        std::cerr << "Setup失败: " << exitflag << std::endl;
        return 1;
    }
    
    std::cout << "Setup成功" << std::endl;
    
    // 求解
    exitflag = osqp_solve(solver);
    
    if (exitflag != 0) {
        std::cerr << "Solve失败: " << exitflag << std::endl;
        return 1;
    }
    
    std::cout << "Solve成功" << std::endl;
    std::cout << "解: x = [" << solver->solution->x[0] << ", " << solver->solution->x[1] << "]" << std::endl;
    std::cout << "状态: " << solver->info->status_val << std::endl;
    
    // 清理
    osqp_cleanup(solver);
    OSQPCscMatrix_free(P);
    OSQPCscMatrix_free(A);
    free(settings);
    
    return 0;
}
