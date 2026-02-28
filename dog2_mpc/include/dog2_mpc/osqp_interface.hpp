#ifndef DOG2_MPC_OSQP_INTERFACE_HPP
#define DOG2_MPC_OSQP_INTERFACE_HPP

#include <Eigen/Dense>
#include <Eigen/Sparse>

// OSQP C API
extern "C" {
#include <osqp/osqp.h>
}

#include <memory>
#include <vector>

namespace dog2_mpc {

/**
 * @brief OSQP求解器接口类
 * 
 * 封装OSQP库，提供QP问题求解功能
 * 
 * QP问题形式:
 *   min  0.5 * x^T * P * x + q^T * x
 *   s.t. l <= A * x <= u
 */
class OSQPInterface {
public:
    /**
     * @brief 构造函数
     */
    OSQPInterface();
    
    /**
     * @brief 析构函数
     */
    ~OSQPInterface();
    
    /**
     * @brief 设置QP问题
     * 
     * @param P Hessian矩阵 (n x n, 对称正定)
     * @param q 线性项向量 (n x 1)
     * @param A 约束矩阵 (m x n)
     * @param l 约束下界 (m x 1)
     * @param u 约束上界 (m x 1)
     * @return true 设置成功
     * @return false 设置失败
     */
    bool setup(const Eigen::MatrixXd& P,
               const Eigen::VectorXd& q,
               const Eigen::MatrixXd& A,
               const Eigen::VectorXd& l,
               const Eigen::VectorXd& u);
    
    /**
     * @brief 设置QP问题（稀疏矩阵版本）
     * 
     * @param P Hessian矩阵 (稀疏)
     * @param q 线性项向量
     * @param A 约束矩阵 (稀疏)
     * @param l 约束下界
     * @param u 约束上界
     * @return true 设置成功
     * @return false 设置失败
     */
    bool setup(const Eigen::SparseMatrix<double>& P,
               const Eigen::VectorXd& q,
               const Eigen::SparseMatrix<double>& A,
               const Eigen::VectorXd& l,
               const Eigen::VectorXd& u);
    
    /**
     * @brief 求解QP问题
     * 
     * @param solution 输出：最优解 (n x 1)
     * @return true 求解成功
     * @return false 求解失败
     */
    bool solve(Eigen::VectorXd& solution);
    
    // Note: updateBounds() and updateLinearCost() removed - not currently needed
    // Can be added back if warm-start functionality is required in the future
    
    /**
     * @brief 获取求解状态
     * 
     * @return int OSQP状态码
     */
    int getStatus() const;
    
    /**
     * @brief 获取求解时间
     * 
     * @return double 求解时间（毫秒）
     */
    double getSolveTime() const;
    
    /**
     * @brief 获取迭代次数
     * 
     * @return int 迭代次数
     */
    int getIterations() const;
    
    /**
     * @brief 获取目标函数值
     * 
     * @return double 目标函数值
     */
    double getObjectiveValue() const;
    
    // Note: setParameters() removed - parameters are set in setup()
    // Modify setup() if you need to change solver parameters
    
    /**
     * @brief 清理求解器
     */
    void cleanup();
    
    /**
     * @brief 检查求解器是否已初始化
     * 
     * @return true 已初始化
     * @return false 未初始化
     */
    bool isInitialized() const { return initialized_; }

private:
    /**
     * @brief 将Eigen稀疏矩阵转换为OSQP CSC格式
     * 
     * @param eigen_mat Eigen稀疏矩阵
     * @return OSQPCscMatrix* CSC格式矩阵
     */
    OSQPCscMatrix* eigenToCSC(const Eigen::SparseMatrix<double>& eigen_mat);
    
    OSQPSolver* solver_;       ///< OSQP求解器
    OSQPSettings* settings_;   ///< OSQP设置
    
    bool initialized_;         ///< 是否已初始化
    int n_;                    ///< 变量维度
    int m_;                    ///< 约束维度
    
    // 存储CSC矩阵指针，用于内存管理
    OSQPCscMatrix* P_csc_;
    OSQPCscMatrix* A_csc_;
    
    // 存储向量数据
    std::vector<OSQPFloat> q_data_;
    std::vector<OSQPFloat> l_data_;
    std::vector<OSQPFloat> u_data_;
    
    // 求解结果
    int last_status_;
    double last_solve_time_;
    int last_iterations_;
    double last_obj_val_;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_OSQP_INTERFACE_HPP
