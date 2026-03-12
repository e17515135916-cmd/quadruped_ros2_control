#include "dog2_mpc/srbd_model.hpp"
#include <cmath>

namespace dog2_mpc {

SRBDModel::SRBDModel(double mass, const Eigen::Matrix3d& inertia)
    : mass_(mass), inertia_(inertia), gravity_(0.0, 0.0, -9.81) {
}

void SRBDModel::setGravity(const Eigen::Vector3d& gravity) {
    gravity_ = gravity;
}

Eigen::Matrix3d SRBDModel::rotationMatrix(double roll, double pitch, double yaw) const {
    // ZYX欧拉角旋转矩阵
    double cr = std::cos(roll);
    double sr = std::sin(roll);
    double cp = std::cos(pitch);
    double sp = std::sin(pitch);
    double cy = std::cos(yaw);
    double sy = std::sin(yaw);
    
    Eigen::Matrix3d R;
    R << cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr,
         sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr,
         -sp,   cp*sr,            cp*cr;
    
    return R;
}

Eigen::Matrix3d SRBDModel::angularVelocityToEulerRate(double roll, double pitch) const {
    double cr = std::cos(roll);
    double sr = std::sin(roll);
    double cp = std::cos(pitch);
    double sp = std::sin(pitch);
    double tp = std::tan(pitch);
    
    Eigen::Matrix3d E;
    E << 1.0, sr*tp, cr*tp,
         0.0, cr,    -sr,
         0.0, sr/cp, cr/cp;
    
    return E;
}

void SRBDModel::dynamics(const Eigen::VectorXd& state,
                        const Eigen::VectorXd& control,
                        const Eigen::MatrixXd& foot_positions,
                        Eigen::VectorXd& state_dot) const {
    // 状态: [x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz]
    // 控制: [F1x, F1y, F1z, F2x, F2y, F2z, F3x, F3y, F3z, F4x, F4y, F4z]
    
    state_dot.resize(STATE_DIM);
    
    // 提取状态
    Eigen::Vector3d position = state.segment<3>(0);
    Eigen::Vector3d euler = state.segment<3>(3);
    Eigen::Vector3d velocity = state.segment<3>(6);
    Eigen::Vector3d angular_velocity = state.segment<3>(9);
    
    double roll = euler(0);
    double pitch = euler(1);
    double yaw = euler(2);
    
    // 旋转矩阵
    Eigen::Matrix3d R = rotationMatrix(roll, pitch, yaw);
    
    // 位置导数 = 速度
    state_dot.segment<3>(0) = velocity;
    
    // 欧拉角导数 = E * 角速度
    Eigen::Matrix3d E = angularVelocityToEulerRate(roll, pitch);
    state_dot.segment<3>(3) = E * angular_velocity;
    
    // 线性加速度：m*a = Σ F_i + m*g
    Eigen::Vector3d total_force = Eigen::Vector3d::Zero();
    for (int i = 0; i < NUM_FEET; ++i) {
        total_force += control.segment<3>(i * 3);
    }
    
    Eigen::Vector3d linear_acceleration = total_force / mass_ + gravity_;
    state_dot.segment<3>(6) = linear_acceleration;
    
    // 角加速度：I*ω̇ + ω×(I*ω) = Σ (r_i × F_i)
    Eigen::Vector3d total_torque = Eigen::Vector3d::Zero();
    for (int i = 0; i < NUM_FEET; ++i) {
        Eigen::Vector3d r_i = foot_positions.row(i).transpose();  // 足端相对质心
        Eigen::Vector3d F_i = control.segment<3>(i * 3);
        total_torque += r_i.cross(F_i);
    }
    
    // I*ω̇ = τ - ω×(I*ω)
    Eigen::Vector3d I_omega = inertia_ * angular_velocity;
    Eigen::Vector3d gyroscopic = angular_velocity.cross(I_omega);
    Eigen::Vector3d angular_acceleration = inertia_.inverse() * (total_torque - gyroscopic);
    
    state_dot.segment<3>(9) = angular_acceleration;
}

void SRBDModel::discreteDynamics(const Eigen::VectorXd& state,
                                const Eigen::VectorXd& control,
                                const Eigen::MatrixXd& foot_positions,
                                double dt,
                                Eigen::VectorXd& next_state) const {
    // 简单的欧拉法离散化
    Eigen::VectorXd state_dot;
    dynamics(state, control, foot_positions, state_dot);
    
    next_state = state + dt * state_dot;
}

void SRBDModel::linearize(const Eigen::VectorXd& state,
                         const Eigen::VectorXd& control,
                         const Eigen::MatrixXd& foot_positions,
                         double dt,
                         Eigen::MatrixXd& A,
                         Eigen::MatrixXd& B) const {
    // 数值微分计算雅可比矩阵
    const double epsilon = 1e-6;
    
    A.resize(STATE_DIM, STATE_DIM);
    B.resize(STATE_DIM, CONTROL_DIM);
    
    Eigen::VectorXd state_dot_nominal;
    dynamics(state, control, foot_positions, state_dot_nominal);
    
    // 计算 A = ∂f/∂x
    for (int i = 0; i < STATE_DIM; ++i) {
        Eigen::VectorXd state_perturbed = state;
        state_perturbed(i) += epsilon;
        
        Eigen::VectorXd state_dot_perturbed;
        dynamics(state_perturbed, control, foot_positions, state_dot_perturbed);
        
        A.col(i) = (state_dot_perturbed - state_dot_nominal) / epsilon;
    }
    
    // 计算 B = ∂f/∂u
    for (int i = 0; i < CONTROL_DIM; ++i) {
        Eigen::VectorXd control_perturbed = control;
        control_perturbed(i) += epsilon;
        
        Eigen::VectorXd state_dot_perturbed;
        dynamics(state, control_perturbed, foot_positions, state_dot_perturbed);
        
        B.col(i) = (state_dot_perturbed - state_dot_nominal) / epsilon;
    }
    
    // 离散化：x[k+1] = x[k] + dt*f(x[k], u[k])
    // A_d = I + dt*A, B_d = dt*B
    A = Eigen::MatrixXd::Identity(STATE_DIM, STATE_DIM) + dt * A;
    B = dt * B;
}

} // namespace dog2_mpc
