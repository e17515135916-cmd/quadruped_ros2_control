#ifndef DOG2_MPC_SLIDING_CONSTRAINTS_HPP
#define DOG2_MPC_SLIDING_CONSTRAINTS_HPP

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <vector>

namespace dog2_mpc {

/**
 * @brief 滑动副约束（Dog2创新点）
 * 
 * 实现MPC中的滑动副约束：
 * 1. 位置约束：d_min ≤ d_i ≤ d_max
 * 2. 速度约束：|Δd_i| / Δt ≤ v_max
 * 3. 对称约束：|d1 - d3| ≤ ε, |d2 - d4| ≤ ε
 * 4. 协调约束：Σ d_i ≈ 0
 */
class SlidingConstraints {
public:
    /**
     * @brief 构造函数
     */
    SlidingConstraints();
    
    /**
     * @brief 设置位置限位
     * @param lower 下限 [j1, j2, j3, j4] (m)
     * @param upper 上限 [j1, j2, j3, j4] (m)
     */
    void setPositionLimits(const Eigen::Vector4d& lower,
                          const Eigen::Vector4d& upper);
    
    /**
     * @brief 设置速度限制
     * @param v_max 最大速度 (m/s)
     */
    void setVelocityLimit(double v_max);
    
    /**
     * @brief 设置对称约束容差
     * @param epsilon 对称容差 (m)
     */
    void setSymmetryTolerance(double epsilon);
    
    /**
     * @brief 启用/禁用对称约束
     */
    void enableSymmetryConstraint(bool enable);
    
    /**
     * @brief 启用/禁用协调约束
     */
    void enableCoordinationConstraint(bool enable);
    
    /**
     * @brief 添加位置约束到QP
     * @param horizon MPC预测时域
     * @param A_ineq 不等式约束矩阵（输出，追加）
     * @param l_ineq 不等式约束下界（输出，追加）
     * @param u_ineq 不等式约束上界（输出，追加）
     */
    void addPositionConstraints(int horizon,
                               std::vector<Eigen::Triplet<double>>& A_triplets,
                               Eigen::VectorXd& l_ineq,
                               Eigen::VectorXd& u_ineq,
                               int& constraint_index) const;
    
    /**
     * @brief 添加速度约束到QP
     * @param horizon MPC预测时域
     * @param dt 时间步长
     * @param A_ineq 不等式约束矩阵（输出，追加）
     * @param l_ineq 不等式约束下界（输出，追加）
     * @param u_ineq 不等式约束上界（输出，追加）
     */
    void addVelocityConstraints(int horizon,
                               double dt,
                               std::vector<Eigen::Triplet<double>>& A_triplets,
                               Eigen::VectorXd& l_ineq,
                               Eigen::VectorXd& u_ineq,
                               int& constraint_index) const;
    
    /**
     * @brief 添加对称约束到QP
     * @param horizon MPC预测时域
     * @param A_ineq 不等式约束矩阵（输出，追加）
     * @param l_ineq 不等式约束下界（输出，追加）
     * @param u_ineq 不等式约束上界（输出，追加）
     */
    void addSymmetryConstraints(int horizon,
                                std::vector<Eigen::Triplet<double>>& A_triplets,
                                Eigen::VectorXd& l_ineq,
                                Eigen::VectorXd& u_ineq,
                                int& constraint_index) const;
    
    /**
     * @brief 添加协调约束到QP
     * @param horizon MPC预测时域
     * @param A_ineq 不等式约束矩阵（输出，追加）
     * @param l_ineq 不等式约束下界（输出，追加）
     * @param u_ineq 不等式约束上界（输出，追加）
     */
    void addCoordinationConstraints(int horizon,
                                    std::vector<Eigen::Triplet<double>>& A_triplets,
                                    Eigen::VectorXd& l_ineq,
                                    Eigen::VectorXd& u_ineq,
                                    int& constraint_index) const;
    
    /**
     * @brief 从状态向量中提取滑动副位置
     * @param state_vector 完整状态向量（所有时间步）
     * @param horizon 预测时域
     * @return 滑动副位置 (horizon × 4)
     */
    static Eigen::MatrixXd extractSlidingPositions(
        const Eigen::VectorXd& state_vector,
        int horizon);

private:
    Eigen::Vector4d d_min_;      ///< 位置下限
    Eigen::Vector4d d_max_;      ///< 位置上限
    double v_slide_max_;         ///< 速度限制
    double epsilon_sym_;         ///< 对称容差
    bool enable_symmetry_;       ///< 启用对称约束
    bool enable_coordination_;   ///< 启用协调约束
    
    static constexpr int NUM_SLIDING_JOINTS = 4;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_SLIDING_CONSTRAINTS_HPP
