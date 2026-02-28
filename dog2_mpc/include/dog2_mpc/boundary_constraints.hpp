#ifndef DOG2_MPC_BOUNDARY_CONSTRAINTS_HPP
#define DOG2_MPC_BOUNDARY_CONSTRAINTS_HPP

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <vector>

namespace dog2_mpc {

/**
 * @brief 窗框边界约束（Dog2创新点）
 * 
 * 实现MPC中的窗框边界约束，用于障碍物穿越：
 * 1. 水平边界：x_window - d_safe <= x_CoM <= x_window + d_safe
 * 2. 垂直边界：y_bottom + d_safe <= y_CoM <= y_top - d_safe
 * 3. 高度边界：z_bottom + d_safe <= z_CoM <= z_top - d_safe
 */
class BoundaryConstraints {
public:
    /**
     * @brief 窗框几何参数
     */
    struct WindowGeometry {
        double x_position;    ///< 窗框x位置 (m)
        double width;         ///< 窗框宽度 (m)
        double height;        ///< 窗框高度 (m)
        double bottom;        ///< 窗框底部高度 (m)
        double top;           ///< 窗框顶部高度 (m)
        
        WindowGeometry()
            : x_position(2.0),
              width(0.5),
              height(0.4),
              bottom(0.2),
              top(0.6) {}
    };
    
    /**
     * @brief 构造函数
     */
    BoundaryConstraints();
    
    /**
     * @brief 设置窗框几何参数
     * @param geometry 窗框几何
     */
    void setWindowGeometry(const WindowGeometry& geometry);
    
    /**
     * @brief 设置安全距离
     * @param d_safe 安全距离 (m)
     */
    void setSafetyDistance(double d_safe);
    
    /**
     * @brief 启用/禁用窗框约束
     * @param enable 是否启用
     */
    void enableWindowConstraint(bool enable);
    
    /**
     * @brief 添加窗框约束到QP
     * @param horizon MPC预测时域
     * @param A_triplets 不等式约束矩阵三元组（输出，追加）
     * @param l_ineq 不等式约束下界（输出，追加）
     * @param u_ineq 不等式约束上界（输出，追加）
     * @param constraint_index 约束索引（输入输出）
     */
    void addWindowConstraints(int horizon,
                             std::vector<Eigen::Triplet<double>>& A_triplets,
                             Eigen::VectorXd& l_ineq,
                             Eigen::VectorXd& u_ineq,
                             int& constraint_index) const;
    
    /**
     * @brief 检查质心是否在窗框附近
     * @param x_CoM 质心x位置
     * @param threshold 阈值距离
     * @return 是否在窗框附近
     */
    bool isNearWindow(double x_CoM, double threshold = 1.0) const;
    
    /**
     * @brief 获取窗框几何
     */
    const WindowGeometry& getWindowGeometry() const { return window_; }
    
    /**
     * @brief 获取安全距离
     */
    double getSafetyDistance() const { return d_safe_; }

private:
    WindowGeometry window_;    ///< 窗框几何
    double d_safe_;            ///< 安全距离
    bool enable_window_;       ///< 启用窗框约束
};

} // namespace dog2_mpc

#endif // DOG2_MPC_BOUNDARY_CONSTRAINTS_HPP
