#include "dog2_mpc/boundary_constraints.hpp"

namespace dog2_mpc {

BoundaryConstraints::BoundaryConstraints()
    : d_safe_(0.05),
      enable_window_(true) {
    // 默认窗框参数（来自fuel_tank.world）
    window_.x_position = 2.0;
    window_.width = 0.5;
    window_.height = 0.4;
    window_.bottom = 0.2;
    window_.top = 0.6;
}

void BoundaryConstraints::setWindowGeometry(const WindowGeometry& geometry) {
    window_ = geometry;
}

void BoundaryConstraints::setSafetyDistance(double d_safe) {
    d_safe_ = d_safe;
}

void BoundaryConstraints::enableWindowConstraint(bool enable) {
    enable_window_ = enable;
}

void BoundaryConstraints::addWindowConstraints(
    int horizon,
    std::vector<Eigen::Triplet<double>>& A_triplets,
    Eigen::VectorXd& l_ineq,
    Eigen::VectorXd& u_ineq,
    int& constraint_index) const {
    
    if (!enable_window_) {
        return;
    }
    
    // 状态向量：[x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz, d1, d2, d3, d4]
    // 质心位置在索引 0-2
    const int state_dim = 16;
    
    // 对每个时间步添加窗框约束
    for (int k = 0; k < horizon; ++k) {
        int x_idx = k * state_dim + 0;  // x位置
        int y_idx = k * state_dim + 1;  // y位置（未使用，窗框在xz平面）
        int z_idx = k * state_dim + 2;  // z位置
        
        // 约束1：水平位置约束（窗框中心附近）
        // x_window - width/2 - d_safe <= x_CoM <= x_window + width/2 + d_safe
        {
            A_triplets.push_back(Eigen::Triplet<double>(
                constraint_index, x_idx, 1.0));
            
            double x_min = window_.x_position - window_.width / 2.0 - d_safe_;
            double x_max = window_.x_position + window_.width / 2.0 + d_safe_;
            
            l_ineq(constraint_index) = x_min;
            u_ineq(constraint_index) = x_max;
            
            constraint_index++;
        }
        
        // 约束2：高度约束（窗框上下边界）
        // z_bottom + d_safe <= z_CoM <= z_top - d_safe
        {
            A_triplets.push_back(Eigen::Triplet<double>(
                constraint_index, z_idx, 1.0));
            
            double z_min = window_.bottom + d_safe_;
            double z_max = window_.top - d_safe_;
            
            l_ineq(constraint_index) = z_min;
            u_ineq(constraint_index) = z_max;
            
            constraint_index++;
        }
    }
}

bool BoundaryConstraints::isNearWindow(double x_CoM, double threshold) const {
    return std::abs(x_CoM - window_.x_position) < threshold;
}

} // namespace dog2_mpc
