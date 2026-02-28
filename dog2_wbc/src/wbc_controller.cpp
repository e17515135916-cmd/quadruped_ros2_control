#include "dog2_wbc/wbc_controller.hpp"
#include <cmath>
#include <chrono>

namespace dog2_wbc {

WBCController::WBCController(const Parameters& params)
    : params_(params) {
    last_stats_.success = false;
    last_stats_.solve_time_ms = 0.0;
    last_stats_.torque_norm = 0.0;
}

Eigen::VectorXd WBCController::computeTorques(
    const Eigen::VectorXd& foot_forces,
    const std::array<LegState, 4>& leg_states) {
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // 输出：12个旋转关节力矩 + 4个滑动副力
    Eigen::VectorXd torques = Eigen::VectorXd::Zero(16);
    
    // 对每条腿计算力矩：τ = J^T * f
    for (int leg = 0; leg < 4; ++leg) {
        // 提取该腿的足端力
        Eigen::Vector3d f_leg = foot_forces.segment<3>(leg * 3);
        
        // 如果不接触，跳过
        if (!leg_states[leg].in_contact) {
            continue;
        }
        
        // 计算雅可比矩阵
        Eigen::MatrixXd J = computeLegJacobian(leg, leg_states[leg]);
        
        // 计算力矩：τ = J^T * f
        // J是3×4矩阵，J^T是4×3
        // τ = [τ_hip_roll, τ_hip_pitch, τ_knee, f_sliding]^T
        Eigen::Vector4d leg_torques = J.transpose() * f_leg;
        
        // 分配到输出向量
        // 旋转关节力矩
        torques.segment<3>(leg * 3) = leg_torques.segment<3>(0);
        
        // 滑动副力
        torques(12 + leg) = leg_torques(3);
    }
    
    // 应用力矩限制
    applyTorqueLimits(torques);
    
    // 统计
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        end_time - start_time);
    
    last_stats_.solve_time_ms = duration.count() / 1000.0;
    last_stats_.torque_norm = torques.norm();
    last_stats_.success = true;
    
    return torques;
}

Eigen::MatrixXd WBCController::computeLegJacobian(
    int leg_id,
    const LegState& leg_state) {
    
    // 根据构型选择不同的雅可比计算
    if (leg_state.config == LegConfiguration::ELBOW) {
        return computeElbowJacobian(
            leg_id,
            leg_state.joint_angles,
            leg_state.sliding_position);
    } else {
        return computeKneeJacobian(
            leg_id,
            leg_state.joint_angles,
            leg_state.sliding_position);
    }
}

Eigen::MatrixXd WBCController::computeElbowJacobian(
    int leg_id,
    const Eigen::Vector3d& q,
    double d) {
    
    // 肘式构型的雅可比矩阵
    // q = [q_hip_roll, q_hip_pitch, q_knee]
    // d = 滑动副位置
    
    double l1 = params_.l1;
    double l2 = params_.l2;
    
    double q1 = q(0);  // hip_roll
    double q2 = q(1);  // hip_pitch
    double q3 = q(2);  // knee
    
    // 肘式：膝关节向后突出
    // 足端位置（简化）：
    // x = d + l1*cos(q2) + l2*cos(q2+q3)
    // y = hip_offset_y + l1*sin(q1)*sin(q2) + l2*sin(q1)*sin(q2+q3)
    // z = -l1*cos(q1)*sin(q2) - l2*cos(q1)*sin(q2+q3)
    
    Eigen::MatrixXd J = Eigen::MatrixXd::Zero(3, 4);
    
    double s1 = std::sin(q1);
    double c1 = std::cos(q1);
    double s2 = std::sin(q2);
    double c2 = std::cos(q2);
    double s23 = std::sin(q2 + q3);
    double c23 = std::cos(q2 + q3);
    
    // ∂p/∂q1 (hip_roll)
    J(0, 0) = 0.0;
    J(1, 0) = l1 * c1 * s2 + l2 * c1 * s23;
    J(2, 0) = l1 * s1 * s2 + l2 * s1 * s23;
    
    // ∂p/∂q2 (hip_pitch)
    J(0, 1) = -l1 * s2 - l2 * s23;
    J(1, 1) = l1 * s1 * c2 + l2 * s1 * c23;
    J(2, 1) = -l1 * c1 * c2 - l2 * c1 * c23;
    
    // ∂p/∂q3 (knee)
    J(0, 2) = -l2 * s23;
    J(1, 2) = l2 * s1 * c23;
    J(2, 2) = -l2 * c1 * c23;
    
    // ∂p/∂d (sliding)
    J(0, 3) = 1.0;
    J(1, 3) = 0.0;
    J(2, 3) = 0.0;
    
    return J;
}

Eigen::MatrixXd WBCController::computeKneeJacobian(
    int leg_id,
    const Eigen::Vector3d& q,
    double d) {
    
    // 膝式构型的雅可比矩阵
    // 膝关节向前收束
    
    double l1 = params_.l1;
    double l2 = params_.l2;
    
    double q1 = q(0);  // hip_roll
    double q2 = q(1);  // hip_pitch
    double q3 = q(2);  // knee
    
    // 膝式：膝关节向前收束
    // 足端位置（简化）：
    // x = d + l1*cos(q2) - l2*cos(q2-q3)  // 注意符号变化
    // y = hip_offset_y + l1*sin(q1)*sin(q2) - l2*sin(q1)*sin(q2-q3)
    // z = -l1*cos(q1)*sin(q2) + l2*cos(q1)*sin(q2-q3)
    
    Eigen::MatrixXd J = Eigen::MatrixXd::Zero(3, 4);
    
    double s1 = std::sin(q1);
    double c1 = std::cos(q1);
    double s2 = std::sin(q2);
    double c2 = std::cos(q2);
    double s2_3 = std::sin(q2 - q3);  // 注意符号
    double c2_3 = std::cos(q2 - q3);
    
    // ∂p/∂q1 (hip_roll)
    J(0, 0) = 0.0;
    J(1, 0) = l1 * c1 * s2 - l2 * c1 * s2_3;
    J(2, 0) = l1 * s1 * s2 - l2 * s1 * s2_3;
    
    // ∂p/∂q2 (hip_pitch)
    J(0, 1) = -l1 * s2 + l2 * s2_3;
    J(1, 1) = l1 * s1 * c2 - l2 * s1 * c2_3;
    J(2, 1) = -l1 * c1 * c2 + l2 * c1 * c2_3;
    
    // ∂p/∂q3 (knee)
    J(0, 2) = l2 * s2_3;  // 符号变化
    J(1, 2) = -l2 * s1 * c2_3;
    J(2, 2) = l2 * c1 * c2_3;
    
    // ∂p/∂d (sliding)
    J(0, 3) = 1.0;
    J(1, 3) = 0.0;
    J(2, 3) = 0.0;
    
    return J;
}

Eigen::Vector3d WBCController::forwardKinematics(
    int leg_id,
    const LegState& leg_state) {
    
    double l1 = params_.l1;
    double l2 = params_.l2;
    
    double q1 = leg_state.joint_angles(0);
    double q2 = leg_state.joint_angles(1);
    double q3 = leg_state.joint_angles(2);
    double d = leg_state.sliding_position;
    
    Eigen::Vector3d foot_pos;
    
    if (leg_state.config == LegConfiguration::ELBOW) {
        // 肘式
        foot_pos(0) = d + l1 * std::cos(q2) + l2 * std::cos(q2 + q3);
        foot_pos(1) = params_.hip_offset_y + 
                     l1 * std::sin(q1) * std::sin(q2) + 
                     l2 * std::sin(q1) * std::sin(q2 + q3);
        foot_pos(2) = -l1 * std::cos(q1) * std::sin(q2) - 
                      l2 * std::cos(q1) * std::sin(q2 + q3);
    } else {
        // 膝式
        foot_pos(0) = d + l1 * std::cos(q2) - l2 * std::cos(q2 - q3);
        foot_pos(1) = params_.hip_offset_y + 
                     l1 * std::sin(q1) * std::sin(q2) - 
                     l2 * std::sin(q1) * std::sin(q2 - q3);
        foot_pos(2) = -l1 * std::cos(q1) * std::sin(q2) + 
                      l2 * std::cos(q1) * std::sin(q2 - q3);
    }
    
    // 考虑腿的位置（前腿/后腿，左/右）
    double sign_x = (leg_id == 0 || leg_id == 3) ? -1.0 : 1.0;  // 前腿负，后腿正
    double sign_y = (leg_id == 0 || leg_id == 1) ? -1.0 : 1.0;  // 左腿负，右腿正
    
    foot_pos(0) = sign_x * params_.hip_offset_x + foot_pos(0);
    foot_pos(1) = sign_y * foot_pos(1);
    
    return foot_pos;
}

void WBCController::applyTorqueLimits(Eigen::VectorXd& torques) {
    // 旋转关节力矩限制
    for (int i = 0; i < 12; ++i) {
        if (torques(i) > params_.max_torque) {
            torques(i) = params_.max_torque;
        } else if (torques(i) < -params_.max_torque) {
            torques(i) = -params_.max_torque;
        }
    }
    
    // 滑动副力限制
    for (int i = 12; i < 16; ++i) {
        if (torques(i) > params_.max_sliding_force) {
            torques(i) = params_.max_sliding_force;
        } else if (torques(i) < -params_.max_sliding_force) {
            torques(i) = -params_.max_sliding_force;
        }
    }
}

} // namespace dog2_wbc
