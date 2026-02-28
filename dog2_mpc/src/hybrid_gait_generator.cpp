#include "dog2_mpc/hybrid_gait_generator.hpp"
#include <iostream>
#include <cmath>
#include <algorithm>

namespace dog2_mpc {

HybridGaitGenerator::HybridGaitGenerator()
    : gait_frequency_(1.0),
      forward_speed_(0.1),
      min_leg_distance_(0.15),
      collision_margin_(0.05),
      initialized_(false) {
    
    current_phases_.fill(0.0);
    initializeLegParams();
}

void HybridGaitGenerator::initialize(const CrossingStateMachine::RobotState& robot_state) {
    // 初始化足端位置
    for (int i = 0; i < 4; ++i) {
        last_foot_positions_[i] = robot_state.foot_positions[i];
    }
    
    // 重置相位
    current_phases_.fill(0.0);
    
    initialized_ = true;
    
    std::cout << "[HybridGaitGenerator] 初始化完成" << std::endl;
    std::cout << "  步态频率: " << gait_frequency_ << " Hz" << std::endl;
    std::cout << "  前进速度: " << forward_speed_ << " m/s" << std::endl;
}

void HybridGaitGenerator::initializeLegParams() {
    // 前腿膝式参数（工作空间偏后，步长较短）
    front_knee_params_.step_length = 0.06;      // 减小步长，降低碰撞风险
    front_knee_params_.step_height = 0.08;      // 标准抬腿高度
    front_knee_params_.duty_factor = 0.65;      // 增加支撑相，提高稳定性
    front_knee_params_.workspace_x = Eigen::Vector2d(-0.18, -0.08);  // 更偏后，避免与后腿重叠
    front_knee_params_.workspace_y = Eigen::Vector2d(-0.12, 0.12);   // 稍微收窄
    front_knee_params_.max_velocity = 0.4;
    front_knee_params_.stance_stiffness = 1000.0;
    front_knee_params_.swing_stiffness = 100.0;
    
    // 后腿肘式参数（工作空间偏前，步长较长）
    rear_elbow_params_.step_length = 0.10;      // 保持较长步长，但不过长
    rear_elbow_params_.step_height = 0.10;      // 稍高抬腿，避免干涉
    rear_elbow_params_.duty_factor = 0.65;      // 增加支撑相
    rear_elbow_params_.workspace_x = Eigen::Vector2d(-0.02, 0.18);   // 更偏前，与前腿分离
    rear_elbow_params_.workspace_y = Eigen::Vector2d(-0.12, 0.12);   // 稍微收窄
    rear_elbow_params_.max_velocity = 0.5;
    rear_elbow_params_.stance_stiffness = 1200.0;
    rear_elbow_params_.swing_stiffness = 120.0;
    
    // 正常肘式参数（全肘式时使用）
    normal_elbow_params_.step_length = 0.08;
    normal_elbow_params_.step_height = 0.08;
    normal_elbow_params_.duty_factor = 0.6;
    normal_elbow_params_.workspace_x = Eigen::Vector2d(-0.10, 0.10);
    normal_elbow_params_.workspace_y = Eigen::Vector2d(-0.15, 0.15);
    normal_elbow_params_.max_velocity = 0.5;
    normal_elbow_params_.stance_stiffness = 1000.0;
    normal_elbow_params_.swing_stiffness = 100.0;
    
    // 安全参数优化
    min_leg_distance_ = 0.20;    // 增加最小距离
    collision_margin_ = 0.08;    // 增加安全余量
}

HybridGaitGenerator::GaitState HybridGaitGenerator::generateHybridTrotGait(
    const CrossingStateMachine::RobotState& robot_state,
    const Eigen::Vector3d& desired_velocity,
    double dt) {
    
    if (!initialized_) {
        initialize(robot_state);
    }
    
    GaitState gait_state;
    gait_state.gait_frequency = gait_frequency_;
    gait_state.forward_velocity = desired_velocity.x();
    
    // 更新相位
    updatePhases(dt);
    
    // 计算Trot步态相位偏移
    auto phase_offsets = computeTrotPhaseOffsets();
    
    // 为每条腿生成足端轨迹
    for (int i = 0; i < 4; ++i) {
        double phase = current_phases_[i] + phase_offsets[i];
        if (phase > 1.0) phase -= 1.0;
        
        // 根据腿部构型选择参数
        LegParams params;
        if (i == 0 || i == 3) {  // 前腿（腿1, 腿4）- 膝式
            params = front_knee_params_;
        } else {  // 后腿（腿2, 腿3）- 肘式
            params = rear_elbow_params_;
        }
        
        // 计算目标足端位置
        Eigen::Vector3d start_pos = last_foot_positions_[i];
        Eigen::Vector3d end_pos = start_pos;
        end_pos.x() += params.step_length;  // 前进一步
        
        // 生成足端轨迹
        gait_state.footsteps[i] = computeFootTrajectory(start_pos, end_pos, phase, params);
        gait_state.phases[i] = phase;
    }
    
    // 检查腿间碰撞
    if (!checkLegCollision(gait_state.footsteps)) {
        std::cout << "[HybridGaitGenerator] 警告：检测到腿间碰撞风险" << std::endl;
        // 应用避障约束
        applyLegAvoidanceConstraints(gait_state.footsteps);
    }
    
    // 计算质心轨迹
    gait_state.com_target = computeComTrajectory(robot_state, desired_velocity, dt);
    gait_state.com_velocity_target = desired_velocity;
    
    // 更新上一次足端位置
    for (int i = 0; i < 4; ++i) {
        if (gait_state.footsteps[i].is_contact) {
            last_foot_positions_[i] = gait_state.footsteps[i].position;
        }
    }
    
    return gait_state;
}

HybridGaitGenerator::GaitState HybridGaitGenerator::generateNormalTrotGait(
    const CrossingStateMachine::RobotState& robot_state,
    const Eigen::Vector3d& desired_velocity,
    double dt) {
    
    if (!initialized_) {
        initialize(robot_state);
    }
    
    GaitState gait_state;
    gait_state.gait_frequency = gait_frequency_;
    gait_state.forward_velocity = desired_velocity.x();
    
    // 更新相位
    updatePhases(dt);
    
    // 计算Trot步态相位偏移
    auto phase_offsets = computeTrotPhaseOffsets();
    
    // 为每条腿生成足端轨迹（全部使用正常肘式参数）
    for (int i = 0; i < 4; ++i) {
        double phase = current_phases_[i] + phase_offsets[i];
        if (phase > 1.0) phase -= 1.0;
        
        // 计算目标足端位置
        Eigen::Vector3d start_pos = last_foot_positions_[i];
        Eigen::Vector3d end_pos = start_pos;
        end_pos.x() += normal_elbow_params_.step_length;
        
        // 生成足端轨迹
        gait_state.footsteps[i] = computeFootTrajectory(start_pos, end_pos, phase, normal_elbow_params_);
        gait_state.phases[i] = phase;
    }
    
    // 计算质心轨迹
    gait_state.com_target = computeComTrajectory(robot_state, desired_velocity, dt);
    gait_state.com_velocity_target = desired_velocity;
    
    // 更新上一次足端位置
    for (int i = 0; i < 4; ++i) {
        if (gait_state.footsteps[i].is_contact) {
            last_foot_positions_[i] = gait_state.footsteps[i].position;
        }
    }
    
    return gait_state;
}

bool HybridGaitGenerator::checkLegCollision(const std::array<FootstepPlan, 4>& footsteps) const {
    // 检查前后腿之间的距离
    for (int front_leg : {0, 3}) {  // 前腿
        for (int rear_leg : {1, 2}) {  // 后腿
            double distance = (footsteps[front_leg].position - footsteps[rear_leg].position).norm();
            if (distance < min_leg_distance_) {
                return false;  // 存在碰撞风险
            }
        }
    }
    
    return true;  // 无碰撞
}

HybridGaitGenerator::LegParams HybridGaitGenerator::getLegParams(
    CrossingStateMachine::LegConfiguration leg_config) const {
    
    switch (leg_config) {
        case CrossingStateMachine::LegConfiguration::KNEE:
            return front_knee_params_;  // 膝式使用前腿参数
        case CrossingStateMachine::LegConfiguration::ELBOW:
        default:
            return normal_elbow_params_;  // 肘式使用正常参数
    }
}

void HybridGaitGenerator::setGaitParameters(double frequency, double forward_speed) {
    gait_frequency_ = frequency;
    forward_speed_ = forward_speed;
    
    std::cout << "[HybridGaitGenerator] 更新步态参数: freq=" << frequency 
              << "Hz, speed=" << forward_speed << "m/s" << std::endl;
}

HybridGaitGenerator::FootstepPlan HybridGaitGenerator::computeFootTrajectory(
    const Eigen::Vector3d& start_pos,
    const Eigen::Vector3d& end_pos,
    double phase,
    const LegParams& leg_params) const {
    
    FootstepPlan footstep;
    
    if (phase < leg_params.duty_factor) {
        // 支撑相 (Stance Phase)
        double stance_phase = phase / leg_params.duty_factor;
        
        // 线性插值计算足端位置
        footstep.position = start_pos + stance_phase * (end_pos - start_pos);
        footstep.position.z() = 0.0;  // 接触地面
        
        // 支撑相速度
        footstep.velocity = (end_pos - start_pos) / (leg_params.duty_factor / gait_frequency_);
        footstep.velocity.z() = 0.0;
        
        footstep.is_contact = true;
        footstep.contact_force = leg_params.stance_stiffness;
        
    } else {
        // 摆动相 (Swing Phase)
        double swing_phase = (phase - leg_params.duty_factor) / (1.0 - leg_params.duty_factor);
        
        // 水平位置：线性插值
        footstep.position = start_pos + swing_phase * (end_pos - start_pos);
        
        // 垂直位置：摆线轨迹
        footstep.position.z() = cycloidTrajectory(swing_phase, leg_params.step_height);
        
        // 摆动相速度
        double swing_duration = (1.0 - leg_params.duty_factor) / gait_frequency_;
        footstep.velocity = (end_pos - start_pos) / swing_duration;
        
        // 垂直速度（摆线轨迹的导数）
        double dz_dt = leg_params.step_height * M_PI * sin(M_PI * swing_phase) / swing_duration;
        footstep.velocity.z() = dz_dt;
        
        footstep.is_contact = false;
        footstep.contact_force = 0.0;
    }
    
    footstep.phase = phase;
    
    return footstep;
}

void HybridGaitGenerator::updatePhases(double dt) {
    double phase_increment = gait_frequency_ * dt;
    
    for (int i = 0; i < 4; ++i) {
        current_phases_[i] += phase_increment;
        if (current_phases_[i] > 1.0) {
            current_phases_[i] -= 1.0;
        }
    }
}

std::array<double, 4> HybridGaitGenerator::computeTrotPhaseOffsets() const {
    // Trot步态相位偏移
    // 腿1和腿3同相，腿2和腿4同相，两组相差0.5
    return {0.0, 0.5, 0.0, 0.5};  // [leg1, leg2, leg3, leg4]
}

Eigen::Vector3d HybridGaitGenerator::computeComTrajectory(
    const CrossingStateMachine::RobotState& robot_state,
    const Eigen::Vector3d& desired_velocity,
    double dt) const {
    
    Eigen::Vector3d com_target = robot_state.position;
    
    // 简单的积分控制
    com_target += desired_velocity * dt;
    
    // 保持合理的高度
    com_target.z() = 0.3;  // 标准质心高度
    
    return com_target;
}

bool HybridGaitGenerator::applyLegAvoidanceConstraints(std::array<FootstepPlan, 4>& footsteps) const {
    // 改进的避障策略：更智能的位置调整
    bool adjusted = false;
    const double safety_factor = 1.2;  // 安全系数
    const double min_safe_distance = min_leg_distance_ * safety_factor;
    
    // 多次迭代优化，确保所有腿都满足约束
    for (int iter = 0; iter < 3; ++iter) {
        bool need_adjustment = false;
        
        for (int front_leg : {0, 3}) {  // 前腿
            for (int rear_leg : {1, 2}) {  // 后腿
                Eigen::Vector3d diff = footsteps[front_leg].position - footsteps[rear_leg].position;
                double distance = diff.norm();
                
                if (distance < min_safe_distance) {
                    // 计算调整方向：优先保持前后腿的工作空间特性
                    Eigen::Vector3d direction = diff.normalized();
                    double adjustment = (min_safe_distance - distance) / 2.0;
                    
                    // 前腿向后调整（符合膝式工作空间偏后的特性）
                    Eigen::Vector3d front_adjustment = direction * adjustment;
                    front_adjustment.x() = std::min(front_adjustment.x(), 0.0);  // 只允许向后调整
                    
                    // 后腿向前调整（符合肘式工作空间偏前的特性）
                    Eigen::Vector3d rear_adjustment = -direction * adjustment;
                    rear_adjustment.x() = std::max(rear_adjustment.x(), 0.0);   // 只允许向前调整
                    
                    footsteps[front_leg].position += front_adjustment;
                    footsteps[rear_leg].position += rear_adjustment;
                    
                    // 确保调整后的位置仍在工作空间内
                    clampToWorkspace(footsteps[front_leg], front_leg);
                    clampToWorkspace(footsteps[rear_leg], rear_leg);
                    
                    adjusted = true;
                    need_adjustment = true;
                }
            }
        }
        
        if (!need_adjustment) {
            break;  // 所有约束都满足，退出迭代
        }
    }
    
    return adjusted;
}

void HybridGaitGenerator::clampToWorkspace(FootstepPlan& footstep, int leg_index) const {
    // 根据腿的构型限制工作空间
    LegParams params;
    if (leg_index == 0 || leg_index == 3) {  // 前腿（膝式）
        params = front_knee_params_;
    } else {  // 后腿（肘式）
        params = rear_elbow_params_;
    }
    
    // 限制x方向位置
    footstep.position.x() = std::max(footstep.position.x(), params.workspace_x[0]);
    footstep.position.x() = std::min(footstep.position.x(), params.workspace_x[1]);
    
    // 限制y方向位置
    footstep.position.y() = std::max(footstep.position.y(), params.workspace_y[0]);
    footstep.position.y() = std::min(footstep.position.y(), params.workspace_y[1]);
    
    // 确保足端在地面上（摆动相除外）
    if (footstep.is_contact) {
        footstep.position.z() = 0.0;
    }
}

double HybridGaitGenerator::cycloidTrajectory(double phase, double step_height) const {
    // 摆线轨迹：平滑的抬腿轨迹
    // z(t) = step_height * (1 - cos(π * phase)) / 2
    return step_height * (1.0 - cos(M_PI * phase)) / 2.0;
}

void HybridGaitGenerator::reset() {
    current_phases_.fill(0.0);
    initialized_ = false;
    
    std::cout << "[HybridGaitGenerator] 重置完成" << std::endl;
}

} // namespace dog2_mpc