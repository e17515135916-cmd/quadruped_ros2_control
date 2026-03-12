#include <iostream>
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <osqp/osqp.h>

int main() {
    std::cout << "=== Eigen到CSC转换测试 ===" << std::endl;
    
    // 创建一个简单的2x2单位矩阵
    Eigen::MatrixXd P_dense(2, 2);
    P_dense << 1.0, 0.0,
               0.0, 1.0;
    
    Eigen::SparseMatrix<double> P = P_dense.sparseView();
    
    std::cout << "Eigen稀疏矩阵:" << std::endl;
    std::cout << P << std::endl;
    std::cout << "非零元素数: " << P.nonZeros() << std::endl;
    
    // 转换为CSC
    OSQPInt rows = P.rows();
    OSQPInt cols = P.cols();
    OSQPInt nnz = P.nonZeros();
    
    OSQPFloat* x = (OSQPFloat*)malloc(nnz * sizeof(OSQPFloat));
    OSQPInt* i = (OSQPInt*)malloc(nnz * sizeof(OSQPInt));
    OSQPInt* p = (OSQPInt*)malloc((cols + 1) * sizeof(OSQPInt));
    
    OSQPInt idx = 0;
    for (OSQPInt k = 0; k < cols; ++k) {
        p[k] = idx;
        std::cout << "列 " << k << ": p[" << k << "] = " << idx << std::endl;
        for (Eigen::SparseMatrix<double>::InnerIterator it(P, k); it; ++it) {
            x[idx] = it.value();
            i[idx] = it.row();
            std::cout << "  元素 " << idx << ": 行=" << it.row() << ", 值=" << it.value() << std::endl;
            ++idx;
        }
    }
    p[cols] = nnz;
    std::cout << "p[" << cols << "] = " << nnz << std::endl;
    
    std::cout << "\nCSC格式:" << std::endl;
    std::cout << "x = [";
    for (OSQPInt j = 0; j < nnz; ++j) std::cout << x[j] << " ";
    std::cout << "]" << std::endl;
    
    std::cout << "i = [";
    for (OSQPInt j = 0; j < nnz; ++j) std::cout << i[j] << " ";
    std::cout << "]" << std::endl;
    
    std::cout << "p = [";
    for (OSQPInt j = 0; j <= cols; ++j) std::cout << p[j] << " ";
    std::cout << "]" << std::endl;
    
    free(x);
    free(i);
    free(p);
    
    return 0;
}
