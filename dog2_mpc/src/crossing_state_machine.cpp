#include "dog2_mpc/crossing_state_machine.hpp"
#include <iostream>
#include <cmath>

namespace dog2_mpc {

CrossingStateMachine::CrossingStateMachine()
    : current_state_(CrossingState::APPROACH),
      state_start_time_(0.0),
      total_time_(0.0) {
}

void CrossingStateMachine::initialize(const RobotState& initial_state, const WindowObstacle& window) {
    initial_state_ = initial_state;
    window_ = window;
    current_state_ = CrossingState::APPROACH;
    state_start_time_ = 0.0;
    total_time_ = 0.0;
    
    std::cout << "[CrossingStateMachine] 初始化完成" << std::endl;
    std::cout << "  初始位置: x=" << initial_state.position.x() << "m" << std::endl;
    std::cout << "  窗框位置: x=" << window.x_position << "m" << std::endl;
    std::cout << "  距离窗框: " << (window.x_position - initial_state.position.x()) << "m" << std::endl;
}

bool CrossingStateMachine::update(const RobotState& current_state, double dt) {
    total_time_ += dt;
    
    // 检查是否可以转换到下一状态
    if (canTransitionToNext(current_state)) {
        transitionToNextState();
    }
    
    return true;
}

std::string CrossingStateMachine::getStateName(CrossingState state) {
    switch (state) {
        case CrossingState::APPROACH:           return "初始接近";
        case CrossingState::BODY_FORWARD_SHIFT: return "机身前探";
        case CrossingState::FRONT_LEGS_TRANSIT: return "前腿穿越";
        case CrossingState::HYBRID_GAIT_WALKING: return "混合构型行走";
        case CrossingState::RAIL_ALIGNMENT:     return "精确停车定位";
        case CrossingState::REAR_LEGS_TRANSIT:  return "后腿穿越";
        case CrossingState::ALL_KNEE_STATE:     return "全膝式状态";
        case CrossingState::RECOVERY:           return "恢复常态";
        case CrossingState::CONTINUE_FORWARD:   return "继续前进";
        case CrossingState::COMPLETED:          return "越障完成";
        default:                                return "未知状态";
    }
}

CrossingStateMachine::RobotState CrossingStateMachine::getTargetState() const {
    switch (current_state_) {
        case CrossingState::APPROACH:           return computeApproachTarget();
        case CrossingState::BODY_FORWARD_SHIFT: return computeBodyForwardShiftTarget();
        case CrossingState::FRONT_LEGS_TRANSIT: return computeFrontLegsTransitTarget();
        case CrossingState::HYBRID_GAIT_WALKING: return computeHybridGaitWalkingTarget();
        case CrossingState::RAIL_ALIGNMENT:     return computeRailAlignmentTarget();
        case CrossingState::REAR_LEGS_TRANSIT:  return computeRearLegsTransitTarget();
        case CrossingState::ALL_KNEE_STATE:     return computeAllKneeStateTarget();
        case CrossingState::RECOVERY:           return computeRecoveryTarget();
        case CrossingState::CONTINUE_FORWARD:   return computeContinueForwardTarget();
        default:                                return initial_state_;
    }
}

CrossingStateMachine::StageConstraints CrossingStateMachine::getCurrentConstraints() const {
    StageConstraints constraints;
    
    // 滑动副基本限制
    constraints.sliding_min << -0.111, -0.008, -0.008, -0.111;  // [j1, j2, j3, j4]
    constraints.sliding_max <<  0.008,  0.111,  0.111,  0.008;
    constraints.sliding_vel_max << 1.0, 1.0, 1.0, 1.0;  // 1.0 m/s
    
    // 根据当前状态调整约束
    switch (current_state_) {
        case CrossingState::APPROACH:
            // 正常行走，滑动副保持中立
            constraints.sliding_min.setZero();
            constraints.sliding_max.setZero();
            break;
            
        case CrossingState::BODY_FORWARD_SHIFT:
            // 前腿向后滑，后腿向前滑
            // 使用不等式约束而非等式约束，给求解器留出空间
            constraints.sliding_min << -0.111, 0.0, 0.0, -0.111;
            constraints.sliding_max << -0.100, 0.111, 0.111, -0.100;  // 前腿留出11mm余量
            break;
            
        case CrossingState::HYBRID_GAIT_WALKING:
            // 混合构型，需要特殊的工作空间约束
            constraints.min_leg_distance = 0.15;  // 腿间最小距离
            
            // 前腿（膝式）工作空间偏后
            for (int i : {0, 3}) {  // leg1, leg4
                constraints.foot_workspace_min[i] = Eigen::Vector3d(-0.15, -0.15, 0.0);
                constraints.foot_workspace_max[i] = Eigen::Vector3d(-0.05, 0.15, 0.12);
            }
            
            // 后腿（肘式）工作空间偏前
            for (int i : {1, 2}) {  // leg2, leg3
                constraints.foot_workspace_min[i] = Eigen::Vector3d(-0.05, -0.15, 0.0);
                constraints.foot_workspace_max[i] = Eigen::Vector3d(0.15, 0.15, 0.12);
            }
            break;
            
        default:
            // 使用默认约束
            break;
    }
    
    // 质心约束
    constraints.com_min = Eigen::Vector3d(-10.0, -1.0, 0.25);
    constraints.com_max = Eigen::Vector3d(10.0, 1.0, 0.35);
    
    return constraints;
}

bool CrossingStateMachine::canTransitionToNext(const RobotState& current_state) const {
    switch (current_state_) {
        case CrossingState::APPROACH:
            return checkApproachComplete(current_state);
        case CrossingState::BODY_FORWARD_SHIFT:
            return checkBodyForwardShiftComplete(current_state);
        case CrossingState::FRONT_LEGS_TRANSIT:
            return checkFrontLegsTransitComplete(current_state);
        case CrossingState::HYBRID_GAIT_WALKING:
            return checkHybridGaitWalkingComplete(current_state);
        case CrossingState::RAIL_ALIGNMENT:
            return checkRailAlignmentComplete(current_state);
        case CrossingState::REAR_LEGS_TRANSIT:
            return checkRearLegsTransitComplete(current_state);
        case CrossingState::ALL_KNEE_STATE:
            return checkAllKneeStateComplete(current_state);
        case CrossingState::RECOVERY:
            return checkRecoveryComplete(current_state);
        case CrossingState::CONTINUE_FORWARD:
            return true;  // 最后阶段，直接完成
        default:
            return false;
    }
}

void CrossingStateMachine::transitionToNextState() {
    CrossingState next_state;
    
    switch (current_state_) {
        case CrossingState::APPROACH:           next_state = CrossingState::BODY_FORWARD_SHIFT; break;
        case CrossingState::BODY_FORWARD_SHIFT: next_state = CrossingState::FRONT_LEGS_TRANSIT; break;
        case CrossingState::FRONT_LEGS_TRANSIT: next_state = CrossingState::HYBRID_GAIT_WALKING; break;
        case CrossingState::HYBRID_GAIT_WALKING: next_state = CrossingState::RAIL_ALIGNMENT; break;
        case CrossingState::RAIL_ALIGNMENT:     next_state = CrossingState::REAR_LEGS_TRANSIT; break;
        case CrossingState::REAR_LEGS_TRANSIT:  next_state = CrossingState::ALL_KNEE_STATE; break;
        case CrossingState::ALL_KNEE_STATE:     next_state = CrossingState::RECOVERY; break;
        case CrossingState::RECOVERY:           next_state = CrossingState::CONTINUE_FORWARD; break;
        case CrossingState::CONTINUE_FORWARD:   next_state = CrossingState::COMPLETED; break;
        default:                                next_state = CrossingState::COMPLETED; break;
    }
    
    std::cout << "[CrossingStateMachine] 状态转换: " 
              << getStateName(current_state_) << " -> " << getStateName(next_state) << std::endl;
    
    current_state_ = next_state;
    state_start_time_ = total_time_;
}

double CrossingStateMachine::getProgress() const {
    // 简单的线性进度计算
    int total_states = 9;  // 0-8
    int current_index = static_cast<int>(current_state_);
    return static_cast<double>(current_index) / total_states;
}

// 各阶段完成条件检查
bool CrossingStateMachine::checkApproachComplete(const RobotState& state) const {
    // 接近完成条件：距离窗框0.2m，速度接近0
    double distance_to_window = window_.x_position - state.position.x();
    bool position_ok = distance_to_window <= 0.2;
    bool velocity_ok = std::abs(state.velocity.x()) < 0.05;
    
    return position_ok && velocity_ok;
}

bool CrossingStateMachine::checkBodyForwardShiftComplete(const RobotState& state) const {
    // 机身前探完成条件：前腿滑动副完全伸展
    bool front_slides_extended = (state.sliding_positions[0] <= -0.10) && 
                                (state.sliding_positions[3] <= -0.10);
    bool rear_slides_extended = (state.sliding_positions[1] >= 0.10) && 
                               (state.sliding_positions[2] >= 0.10);
    
    return front_slides_extended && rear_slides_extended;
}

bool CrossingStateMachine::checkFrontLegsTransitComplete(const RobotState& state) const {
    // 前腿穿越完成条件：前腿构型为膝式，且足端在窗框后方
    bool front_legs_knee = (state.leg_configs[0] == LegConfiguration::KNEE) &&
                          (state.leg_configs[3] == LegConfiguration::KNEE);
    
    bool front_feet_through = (state.foot_positions[0].x() > window_.x_position) &&
                             (state.foot_positions[3].x() > window_.x_position);
    
    return front_legs_knee && front_feet_through;
}

bool CrossingStateMachine::checkHybridGaitWalkingComplete(const RobotState& state) const {
    // 混合构型行走完成条件：后腿导轨前端穿过窗框
    double rear_rail_front = state.position.x() + state.sliding_positions[1];  // 后腿导轨前端
    bool rear_rails_through = rear_rail_front > window_.x_position;
    
    return rear_rails_through;
}

bool CrossingStateMachine::checkRailAlignmentComplete(const RobotState& state) const {
    // 精确停车完成条件：机身停止，位置精确
    bool velocity_zero = state.velocity.norm() < 0.01;
    bool position_aligned = std::abs(state.position.x() - (window_.x_position + 0.15)) < 0.02;
    
    return velocity_zero && position_aligned;
}

bool CrossingStateMachine::checkRearLegsTransitComplete(const RobotState& state) const {
    // 后腿穿越完成条件：后腿构型为膝式，且足端在窗框后方
    bool rear_legs_knee = (state.leg_configs[1] == LegConfiguration::KNEE) &&
                         (state.leg_configs[2] == LegConfiguration::KNEE);
    
    bool rear_feet_through = (state.foot_positions[1].x() > window_.x_position) &&
                            (state.foot_positions[2].x() > window_.x_position);
    
    return rear_legs_knee && rear_feet_through;
}

bool CrossingStateMachine::checkAllKneeStateComplete(const RobotState& state) const {
    // 全膝式状态完成条件：所有腿都是膝式，机身稳定
    bool all_knee = true;
    for (int i = 0; i < 4; ++i) {
        if (state.leg_configs[i] != LegConfiguration::KNEE) {
            all_knee = false;
            break;
        }
    }
    
    bool stable = state.velocity.norm() < 0.05;
    
    return all_knee && stable;
}

bool CrossingStateMachine::checkRecoveryComplete(const RobotState& state) const {
    // 恢复完成条件：所有腿恢复肘式，滑动副回到中立位置
    bool all_elbow = true;
    for (int i = 0; i < 4; ++i) {
        if (state.leg_configs[i] != LegConfiguration::ELBOW) {
            all_elbow = false;
            break;
        }
    }
    
    bool slides_neutral = state.sliding_positions.norm() < 0.02;
    
    return all_elbow && slides_neutral;
}

// 各阶段目标状态计算
CrossingStateMachine::RobotState CrossingStateMachine::computeApproachTarget() const {
    RobotState target = initial_state_;
    
    // 目标：接近窗框到0.2m距离
    target.position.x() = window_.x_position - 0.2;
    target.velocity.setZero();
    target.sliding_positions.setZero();
    
    // 所有腿保持肘式
    for (int i = 0; i < 4; ++i) {
        target.leg_configs[i] = LegConfiguration::ELBOW;
        target.foot_contacts[i] = true;
    }
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeBodyForwardShiftTarget() const {
    RobotState target = initial_state_;
    
    // 目标：机身前移0.111m
    target.position.x() = window_.x_position - 0.2 + 0.111;
    target.velocity.setZero();
    
    // 滑动副伸展
    target.sliding_positions << -0.111, 0.111, 0.111, -0.111;
    
    // 所有腿保持肘式，接触地面
    for (int i = 0; i < 4; ++i) {
        target.leg_configs[i] = LegConfiguration::ELBOW;
        target.foot_contacts[i] = true;
    }
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeFrontLegsTransitTarget() const {
    RobotState target = computeBodyForwardShiftTarget();
    
    // 前腿切换为膝式
    target.leg_configs[0] = LegConfiguration::KNEE;  // leg1
    target.leg_configs[3] = LegConfiguration::KNEE;  // leg4
    
    // 前腿足端穿过窗框
    target.foot_positions[0].x() = window_.x_position + 0.1;
    target.foot_positions[3].x() = window_.x_position + 0.1;
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeHybridGaitWalkingTarget() const {
    RobotState target = computeFrontLegsTransitTarget();
    
    // 目标：机身继续前移，使后腿导轨前端穿过窗框
    target.position.x() = window_.x_position + 0.15;
    target.velocity.x() = 0.1;  // 慢速前进
    
    // 混合构型：前腿膝式，后腿肘式
    target.leg_configs[0] = LegConfiguration::KNEE;   // leg1
    target.leg_configs[1] = LegConfiguration::ELBOW;  // leg2
    target.leg_configs[2] = LegConfiguration::ELBOW;  // leg3
    target.leg_configs[3] = LegConfiguration::KNEE;   // leg4
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeRailAlignmentTarget() const {
    RobotState target = computeHybridGaitWalkingTarget();
    
    // 目标：精确停车
    target.position.x() = window_.x_position + 0.15;
    target.velocity.setZero();
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeRearLegsTransitTarget() const {
    RobotState target = computeRailAlignmentTarget();
    
    // 后腿切换为膝式
    target.leg_configs[1] = LegConfiguration::KNEE;  // leg2
    target.leg_configs[2] = LegConfiguration::KNEE;  // leg3
    
    // 后腿足端穿过窗框
    target.foot_positions[1].x() = window_.x_position + 0.1;
    target.foot_positions[2].x() = window_.x_position + 0.1;
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeAllKneeStateTarget() const {
    RobotState target = computeRearLegsTransitTarget();
    
    // 所有腿都是膝式
    for (int i = 0; i < 4; ++i) {
        target.leg_configs[i] = LegConfiguration::KNEE;
    }
    
    target.velocity.setZero();
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeRecoveryTarget() const {
    RobotState target = computeAllKneeStateTarget();
    
    // 恢复到肘式
    for (int i = 0; i < 4; ++i) {
        target.leg_configs[i] = LegConfiguration::ELBOW;
    }
    
    // 滑动副回到中立位置
    target.sliding_positions.setZero();
    
    return target;
}

CrossingStateMachine::RobotState CrossingStateMachine::computeContinueForwardTarget() const {
    RobotState target = computeRecoveryTarget();
    
    // 继续前进
    target.position.x() = window_.x_position + 1.0;
    target.velocity.x() = 0.2;
    
    return target;
}

void CrossingStateMachine::forceTransitionTo(CrossingState state) {
    std::cout << "[CrossingStateMachine] 强制转换到状态: " << getStateName(state) << std::endl;
    current_state_ = state;
    state_start_time_ = total_time_;
}

} // namespace dog2_mpc