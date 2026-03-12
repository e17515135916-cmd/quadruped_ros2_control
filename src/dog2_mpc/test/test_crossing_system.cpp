#include "dog2_mpc/crossing_state_machine.hpp"
#include "dog2_mpc/hybrid_gait_generator.hpp"
#include "dog2_mpc/mpc_controller.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;

/**
 * @brief 测试Dog2越障系统的完整流程
 */
int main() {
    std::cout << "=== Dog2越障系统测试 ===" << std::endl;
    
    // 1. 初始化机器人状态
    CrossingStateMachine::RobotState robot_state;
    robot_state.position = Eigen::Vector3d(1.0, 0.0, 0.3);  // 距离窗框1m
    robot_state.velocity = Eigen::Vector3d(0.2, 0.0, 0.0);  // 0.2m/s前进
    robot_state.orientation.setZero();
    robot_state.angular_velocity.setZero();
    robot_state.sliding_positions.setZero();  // 滑动副中立位置
    robot_state.sliding_velocities.setZero();
    
    // 初始化腿部构型（全部肘式）
    for (int i = 0; i < 4; ++i) {
        robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        robot_state.foot_positions[i] = Eigen::Vector3d(1.0 + (i % 2) * 0.4 - 0.2, 
                                                       (i / 2) * 0.3 - 0.15, 0.0);
        robot_state.foot_contacts[i] = true;
    }
    
    // 2. 初始化窗框障碍物
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    window.top_height = 0.6;
    window.safety_margin = 0.05;
    
    // 3. 创建越障状态机
    CrossingStateMachine state_machine;
    state_machine.initialize(robot_state, window);
    
    // 4. 创建混合步态生成器
    HybridGaitGenerator gait_generator;
    gait_generator.initialize(robot_state);
    
    // 5. 创建MPC控制器
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 10;
    mpc_params.dt = 0.02;
    
    // 设置权重矩阵
    mpc_params.Q = Eigen::MatrixXd::Identity(12, 12);
    mpc_params.Q.diagonal() << 100, 100, 100,  // 位置权重
                              50, 50, 50,       // 姿态权重
                              10, 10, 10,       // 线速度权重
                              1, 1, 1;          // 角速度权重
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.1;  // 控制权重
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    std::cout << "\n=== 系统初始化完成 ===" << std::endl;
    std::cout << "机器人初始位置: x=" << robot_state.position.x() << "m" << std::endl;
    std::cout << "窗框位置: x=" << window.x_position << "m" << std::endl;
    std::cout << "距离窗框: " << (window.x_position - robot_state.position.x()) << "m" << std::endl;
    
    // 6. 仿真越障过程
    double dt = 0.02;  // 50Hz控制频率
    double total_time = 0.0;
    int step_count = 0;
    
    std::cout << "\n=== 开始越障仿真 ===" << std::endl;
    std::cout << std::fixed << std::setprecision(3);
    
    while (!state_machine.isCompleted() && total_time < 30.0) {
        // 更新状态机
        state_machine.update(robot_state, dt);
        
        // 获取当前状态和目标
        auto current_state = state_machine.getCurrentState();
        auto target_state = state_machine.getTargetState();
        auto constraints = state_machine.getCurrentConstraints();
        
        // 根据当前阶段生成步态
        Eigen::Vector3d desired_velocity(0.1, 0.0, 0.0);  // 默认速度
        
        // 根据状态调整速度
        if (current_state == CrossingStateMachine::CrossingState::APPROACH) {
            // 接近阶段：当接近窗框时减速
            double distance_to_window = window.x_position - robot_state.position.x();
            if (distance_to_window <= 0.3) {
                desired_velocity.x() = 0.02;  // 减速到很慢
            }
            if (distance_to_window <= 0.2) {
                desired_velocity.x() = 0.0;   // 停止
            }
        } else if (current_state == CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT) {
            desired_velocity.x() = 0.0;  // 机身前探时停止
        } else if (current_state == CrossingStateMachine::CrossingState::RAIL_ALIGNMENT) {
            desired_velocity.x() = 0.0;  // 精确停车时停止
        }
        
        HybridGaitGenerator::GaitState gait_state;
        if (current_state == CrossingStateMachine::CrossingState::HYBRID_GAIT_WALKING) {
            // 混合构型步态
            gait_state = gait_generator.generateHybridTrotGait(robot_state, desired_velocity, dt);
            std::cout << "[" << std::setw(6) << total_time << "s] 🔥 混合构型行走中..." << std::endl;
        } else {
            // 正常步态
            gait_state = gait_generator.generateNormalTrotGait(robot_state, desired_velocity, dt);
        }
        
        // 每0.5秒输出一次状态
        if (step_count % 25 == 0) {
            std::cout << "[" << std::setw(6) << total_time << "s] " 
                      << CrossingStateMachine::getStateName(current_state)
                      << " | 位置: x=" << robot_state.position.x() 
                      << "m | 进度: " << std::setw(5) << (state_machine.getProgress() * 100) << "%" << std::endl;
            
            // 显示腿部构型
            if (current_state == CrossingStateMachine::CrossingState::HYBRID_GAIT_WALKING ||
                current_state == CrossingStateMachine::CrossingState::FRONT_LEGS_TRANSIT ||
                current_state == CrossingStateMachine::CrossingState::REAR_LEGS_TRANSIT) {
                std::cout << "    腿部构型: ";
                for (int i = 0; i < 4; ++i) {
                    std::cout << "腿" << (i+1) << "=";
                    if (robot_state.leg_configs[i] == CrossingStateMachine::LegConfiguration::KNEE) {
                        std::cout << "膝式 ";
                    } else {
                        std::cout << "肘式 ";
                    }
                }
                std::cout << std::endl;
            }
        }
        
        // 简单的状态更新（仿真）
        robot_state.position += gait_state.com_velocity_target * dt;
        robot_state.velocity = gait_state.com_velocity_target;
        
        // 模拟滑动副运动
        if (current_state == CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT) {
            // 机身前探：滑动副伸展
            robot_state.sliding_positions << -0.111, 0.111, 0.111, -0.111;
        } else if (current_state == CrossingStateMachine::CrossingState::RECOVERY) {
            // 恢复：滑动副收缩
            robot_state.sliding_positions.setZero();
        }
        
        // 更新足端位置
        for (int i = 0; i < 4; ++i) {
            robot_state.foot_positions[i] = gait_state.footsteps[i].position;
            robot_state.foot_contacts[i] = gait_state.footsteps[i].is_contact;
        }
        
        // 模拟构型切换（简化）
        if (current_state == CrossingStateMachine::CrossingState::FRONT_LEGS_TRANSIT) {
            // 前腿切换为膝式
            robot_state.leg_configs[0] = CrossingStateMachine::LegConfiguration::KNEE;
            robot_state.leg_configs[3] = CrossingStateMachine::LegConfiguration::KNEE;
        } else if (current_state == CrossingStateMachine::CrossingState::REAR_LEGS_TRANSIT) {
            // 后腿切换为膝式
            robot_state.leg_configs[1] = CrossingStateMachine::LegConfiguration::KNEE;
            robot_state.leg_configs[2] = CrossingStateMachine::LegConfiguration::KNEE;
        } else if (current_state == CrossingStateMachine::CrossingState::RECOVERY) {
            // 恢复为肘式
            for (int i = 0; i < 4; ++i) {
                robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
            }
        }
        
        total_time += dt;
        step_count++;
    }
    
    std::cout << "\n=== 越障仿真完成 ===" << std::endl;
    if (state_machine.isCompleted()) {
        std::cout << "✅ 越障成功！" << std::endl;
        std::cout << "总耗时: " << total_time << "s" << std::endl;
        std::cout << "最终位置: x=" << robot_state.position.x() << "m" << std::endl;
        std::cout << "穿越距离: " << (robot_state.position.x() - 1.0) << "m" << std::endl;
    } else {
        std::cout << "⚠️ 越障超时或失败" << std::endl;
    }
    
    // 7. 测试混合构型步态生成器的特殊功能
    std::cout << "\n=== 测试混合构型步态生成器 ===" << std::endl;
    
    // 设置混合构型
    robot_state.leg_configs[0] = CrossingStateMachine::LegConfiguration::KNEE;   // 前腿膝式
    robot_state.leg_configs[1] = CrossingStateMachine::LegConfiguration::ELBOW;  // 后腿肘式
    robot_state.leg_configs[2] = CrossingStateMachine::LegConfiguration::ELBOW;  // 后腿肘式
    robot_state.leg_configs[3] = CrossingStateMachine::LegConfiguration::KNEE;   // 前腿膝式
    
    // 生成混合构型步态
    Eigen::Vector3d test_velocity(0.1, 0.0, 0.0);
    auto hybrid_gait = gait_generator.generateHybridTrotGait(robot_state, test_velocity, dt);
    
    std::cout << "混合构型步态参数:" << std::endl;
    std::cout << "  前腿膝式参数: " << std::endl;
    auto front_params = gait_generator.getLegParams(CrossingStateMachine::LegConfiguration::KNEE);
    std::cout << "    步长: " << front_params.step_length << "m" << std::endl;
    std::cout << "    工作空间: x∈[" << front_params.workspace_x[0] << ", " << front_params.workspace_x[1] << "]" << std::endl;
    
    std::cout << "  后腿肘式参数: " << std::endl;
    auto rear_params = gait_generator.getLegParams(CrossingStateMachine::LegConfiguration::ELBOW);
    std::cout << "    步长: " << rear_params.step_length << "m" << std::endl;
    std::cout << "    工作空间: x∈[" << rear_params.workspace_x[0] << ", " << rear_params.workspace_x[1] << "]" << std::endl;
    
    // 检查腿间碰撞
    bool collision_free = gait_generator.checkLegCollision(hybrid_gait.footsteps);
    std::cout << "腿间碰撞检查: " << (collision_free ? "✅ 无碰撞" : "⚠️ 存在碰撞风险") << std::endl;
    
    std::cout << "\n=== 所有测试完成 ===" << std::endl;
    
    return 0;
}