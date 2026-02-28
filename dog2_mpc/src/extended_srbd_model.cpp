#include "dog2_mpc/extended_srbd_model.hpp"
#include <iostream>

namespace dog2_mpc {

ExtendedSRBDModel::ExtendedSRBDModel(double mass, const Eigen::Matrix3d& inertia)
    : srbd_model_(mass, inertia) {
    sliding_velocity_.setZero();
}

void ExtendedSRBDModel::setGravity(const Eigen::Vector3d& gravity) {
    srbd_model_.setGravity(gravity);
}

void ExtendedSRBDModel::setSlidingVelocity(const Eigen::Vector4d& sliding_velocity) {
    sliding_velocity_ = sliding_velocity;
}

Eigen::MatrixXd ExtendedSRBDModel::computeFootPositions(
    const Eigen::Vector4d& sliding_positions,
    const Eigen::MatrixXd& base_foot_positions) const {
    
    if (base_foot_positions.rows() != NUM_FEET || base_foot_positions.cols() != 3) {
        std::cerr << "Error: base_foot_positions must be 4×3 matrix" << std::endl;
        return base_foot_positions;
    }
    
    Eigen::MatrixXd foot_positions = base_foot_positions;
    
    // Dog2滑动副影响足端的x坐标（纵向滑动）
    for (int i = 0; i < NUM_FEET; ++i) {
        Eigen::Vector3d offset = slidingOffset(i, sliding_positions(i));
        foot_positions.row(i) += offset.transpose();
    }
    
    return foot_positions;
}

void ExtendedSRBDModel::dynamics(const Eigen::VectorXd& state,
                                const Eigen::VectorXd& control,
                                const Eigen::MatrixXd& base_foot_positions,
                                const Eigen::Vector4d& sliding_velocity,
                                Eigen::VectorXd& state_dot) const {
    
    if (state.size() != EXTENDED_STATE_DIM) {
        std::cerr << "Error: Extended state must be " << EXTENDED_STATE_DIM << "-dimensional" << std::endl;
        return;
    }
    
    state_dot.resize(EXTENDED_STATE_DIM);
    
    // 提取SRBD状态和滑动副位置
    Eigen::VectorXd srbd_state = extractSRBDState(state);
    Eigen::Vector4d sliding_positions = extractSlidingPositions(state);
    
    // 计算实际足端位置（考虑滑动副）
    Eigen::MatrixXd foot_positions = computeFootPositions(sliding_positions, base_foot_positions);
    
    // 计算SRBD动力学
    Eigen::VectorXd srbd_state_dot;
    srbd_model_.dynamics(srbd_state, control, foot_positions, srbd_state_dot);
    
    // 扩展状态导数
    state_dot.segment<SRBD_STATE_DIM>(0) = srbd_state_dot;
    state_dot.segment<SLIDING_STATE_DIM>(SRBD_STATE_DIM) = sliding_velocity;
}

void ExtendedSRBDModel::discreteDynamics(const Eigen::VectorXd& state,
                                        const Eigen::VectorXd& control,
                                        const Eigen::MatrixXd& base_foot_positions,
                                        const Eigen::Vector4d& sliding_velocity,
                                        double dt,
                                        Eigen::VectorXd& next_state) const {
    
    // 简单的欧拉法离散化
    Eigen::VectorXd state_dot;
    dynamics(state, control, base_foot_positions, sliding_velocity, state_dot);
    
    next_state = state + dt * state_dot;
}

void ExtendedSRBDModel::linearize(const Eigen::VectorXd& state,
                                 const Eigen::VectorXd& control,
                                 const Eigen::MatrixXd& base_foot_positions,
                                 const Eigen::Vector4d& sliding_velocity,
                                 double dt,
                                 Eigen::MatrixXd& A,
                                 Eigen::MatrixXd& B,
                                 Eigen::MatrixXd& C) const {
    
    // 数值微分计算雅可比矩阵
    const double epsilon = 1e-6;
    
    A.resize(EXTENDED_STATE_DIM, EXTENDED_STATE_DIM);
    B.resize(EXTENDED_STATE_DIM, CONTROL_DIM);
    C.resize(EXTENDED_STATE_DIM, SLIDING_STATE_DIM);
    
    Eigen::VectorXd state_dot_nominal;
    dynamics(state, control, base_foot_positions, sliding_velocity, state_dot_nominal);
    
    // 计算 A = ∂f/∂x
    for (int i = 0; i < EXTENDED_STATE_DIM; ++i) {
        Eigen::VectorXd state_perturbed = state;
        state_perturbed(i) += epsilon;
        
        Eigen::VectorXd state_dot_perturbed;
        dynamics(state_perturbed, control, base_foot_positions, sliding_velocity, state_dot_perturbed);
        
        A.col(i) = (state_dot_perturbed - state_dot_nominal) / epsilon;
    }
    
    // 计算 B = ∂f/∂u
    for (int i = 0; i < CONTROL_DIM; ++i) {
        Eigen::VectorXd control_perturbed = control;
        control_perturbed(i) += epsilon;
        
        Eigen::VectorXd state_dot_perturbed;
        dynamics(state, control_perturbed, base_foot_positions, sliding_velocity, state_dot_perturbed);
        
        B.col(i) = (state_dot_perturbed - state_dot_nominal) / epsilon;
    }
    
    // 计算 C = ∂f/∂v (滑动副速度的影响)
    for (int i = 0; i < SLIDING_STATE_DIM; ++i) {
        Eigen::Vector4d sliding_velocity_perturbed = sliding_velocity;
        sliding_velocity_perturbed(i) += epsilon;
        
        Eigen::VectorXd state_dot_perturbed;
        dynamics(state, control, base_foot_positions, sliding_velocity_perturbed, state_dot_perturbed);
        
        C.col(i) = (state_dot_perturbed - state_dot_nominal) / epsilon;
    }
    
    // 离散化：x[k+1] = x[k] + dt*f(x[k], u[k], v[k])
    // A_d = I + dt*A, B_d = dt*B, C_d = dt*C
    A = Eigen::MatrixXd::Identity(EXTENDED_STATE_DIM, EXTENDED_STATE_DIM) + dt * A;
    B = dt * B;
    C = dt * C;
}

Eigen::VectorXd ExtendedSRBDModel::extractSRBDState(const Eigen::VectorXd& extended_state) {
    if (extended_state.size() != EXTENDED_STATE_DIM) {
        std::cerr << "Error: Extended state size mismatch" << std::endl;
        return Eigen::VectorXd::Zero(SRBD_STATE_DIM);
    }
    
    return extended_state.segment<SRBD_STATE_DIM>(0);
}

Eigen::Vector4d ExtendedSRBDModel::extractSlidingPositions(const Eigen::VectorXd& extended_state) {
    if (extended_state.size() != EXTENDED_STATE_DIM) {
        std::cerr << "Error: Extended state size mismatch" << std::endl;
        return Eigen::Vector4d::Zero();
    }
    
    return extended_state.segment<SLIDING_STATE_DIM>(SRBD_STATE_DIM);
}

Eigen::VectorXd ExtendedSRBDModel::buildExtendedState(
    const Eigen::VectorXd& srbd_state,
    const Eigen::Vector4d& sliding_positions) {
    
    if (srbd_state.size() != SRBD_STATE_DIM) {
        std::cerr << "Error: SRBD state size mismatch" << std::endl;
        return Eigen::VectorXd::Zero(EXTENDED_STATE_DIM);
    }
    
    Eigen::VectorXd extended_state(EXTENDED_STATE_DIM);
    extended_state.segment<SRBD_STATE_DIM>(0) = srbd_state;
    extended_state.segment<SLIDING_STATE_DIM>(SRBD_STATE_DIM) = sliding_positions;
    
    return extended_state;
}

Eigen::Vector3d ExtendedSRBDModel::slidingOffset(int leg_index, double sliding_position) const {
    // Dog2滑动副是纵向的，影响足端的x坐标
    // 滑动副正值表示向前伸展，负值表示向后收缩
    
    Eigen::Vector3d offset = Eigen::Vector3d::Zero();
    
    switch (leg_index) {
        case 0:  // 腿1 (前左)
        case 3:  // 腿4 (前右)
            // 前腿：正向滑动使足端向前移动
            offset(0) = sliding_position;
            break;
            
        case 1:  // 腿2 (后左)  
        case 2:  // 腿3 (后右)
            // 后腿：正向滑动使足端向前移动
            offset(0) = sliding_position;
            break;
            
        default:
            std::cerr << "Error: Invalid leg index " << leg_index << std::endl;
            break;
    }
    
    return offset;
}

} // namespace dog2_mpc