#include "dog2_mpc/contact_detector.hpp"
#include <cmath>

namespace dog2_mpc {

ContactDetector::ContactDetector(const Parameters& params)
    : params_(params) {
    current_state_.in_contact.fill(true);
    filtered_state_ = current_state_;
}

ContactDetector::ContactState ContactDetector::detectFromForces(
    const Eigen::MatrixXd& foot_forces) {
    
    ContactState state;
    
    for (int i = 0; i < 4; ++i) {
        // 计算垂直力（z方向）
        double fz = foot_forces(i, 2);
        state.contact_force[i] = fz;
        
        // 如果垂直力大于阈值，认为接触
        state.in_contact[i] = (fz > params_.force_threshold);
    }
    
    filterContactState(state);
    return filtered_state_;
}

ContactDetector::ContactState ContactDetector::detectFromPositions(
    const Eigen::MatrixXd& foot_positions,
    double ground_height) {
    
    ContactState state;
    
    for (int i = 0; i < 4; ++i) {
        // 足端高度
        double foot_height = foot_positions(i, 2);
        
        // 如果足端接近地面，认为接触
        state.in_contact[i] = 
            (std::abs(foot_height - ground_height) < params_.height_threshold);
        
        state.contact_force[i] = state.in_contact[i] ? 20.0 : 0.0;
    }
    
    filterContactState(state);
    return filtered_state_;
}

ContactDetector::ContactState ContactDetector::detectFromGait(
    const std::array<double, 4>& gait_phases) {
    
    ContactState state;
    
    for (int i = 0; i < 4; ++i) {
        // 相位在[0, 0.5]为支撑相，[0.5, 1.0]为摆动相
        state.in_contact[i] = (gait_phases[i] < 0.5);
        state.contact_force[i] = state.in_contact[i] ? 20.0 : 0.0;
    }
    
    filterContactState(state);
    return filtered_state_;
}

void ContactDetector::filterContactState(const ContactState& new_state) {
    // 简单的指数滤波
    for (int i = 0; i < 4; ++i) {
        // 力的滤波
        filtered_state_.contact_force[i] = 
            params_.filter_alpha * filtered_state_.contact_force[i] +
            (1.0 - params_.filter_alpha) * new_state.contact_force[i];
        
        // 接触状态：使用滤波后的力判断
        filtered_state_.in_contact[i] = 
            (filtered_state_.contact_force[i] > params_.force_threshold);
    }
    
    current_state_ = filtered_state_;
}

} // namespace dog2_mpc
