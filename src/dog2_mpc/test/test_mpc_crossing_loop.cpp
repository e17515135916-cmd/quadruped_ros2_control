#include "dog2_mpc/mpc_controller.hpp"
#include "dog2_mpc/crossing_state_machine.hpp"
#include "dog2_mpc/hybrid_gait_generator.hpp"
#include <iostream>
#include <iomanip>
#include <fstream>

using namespace dog2_mpc;

/**
 * @brief 测试完整的MPC控制循环，包含真实的QP求解
 */
int main() {
    std::cout << "=== Dog2 MPC控制循环测试 ===" << std::endl;
    
    // 1. 创建MPC控制器
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 8;      // 较短时域，提高求解速度
    mpc_params.dt = 0.05;        // 20Hz控制频率
    
    // 设置权重矩阵
    mpc_params.Q = Eigen::MatrixXd::Identity(12, 12);
    mpc_params.Q.diagonal() << 100, 100, 200,  // 位置权重（z方向更重要）
                              50, 50, 50,       // 姿态权重
                              10, 10, 10,       // 线速度权重
                              5, 5, 5;          // 角速度权重
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;  // 控制权重
    
    // 控制限制
    mpc_params.u_min = Eigen::VectorXd::Constant(12, -50.0);  // 最大50N力
    mpc_params.u_max = Eigen::VectorXd::Constant(12, 50.0);
    
    // 启用约束
    mpc_params.enable_sliding_constraints = false;   // 暂时禁用
    mpc_params.enable_boundary_constraints = false;  // 暂时禁用
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    // 2. 初始化机器人状态
    Eigen::VectorXd x0(12);
    x0 << 1.0, 0.0, 0.3,    // 位置 [x, y, z]
          0.0, 0.0, 0.0,    // 姿态 [roll, pitch, yaw]
          0.0, 0.0, 0.0,    // 线速度 [vx, vy, vz]
          0.0, 0.0, 0.0;    // 角速度 [wx, wy, wz]
    
    // 3. 设置足端位置（相对质心）
    Eigen::MatrixXd foot_positions(4, 3);
    foot_positions << -0.2, -0.15, -0.3,  // 腿1 (前左)
                      0.2, -0.15, -0.3,   // 腿2 (后左)
                      0.2,  0.15, -0.3,   // 腿3 (后右)
                     -0.2,  0.15, -0.3;   // 腿4 (前右)
    mpc_controller.setBaseFootPositions(foot_positions);
    
    // 4. 初始化越障功能
    CrossingStateMachine::RobotState initial_state;
    initial_state.position = x0.segment<3>(0);
    initial_state.velocity = x0.segment<3>(6);
    initial_state.orientation = x0.segment<3>(3);
    initial_state.angular_velocity = x0.segment<3>(9);
    initial_state.sliding_positions.setZero();
    initial_state.sliding_velocities.setZero();
    
    for (int i = 0; i < 4; ++i) {
        initial_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
        initial_state.foot_positions[i] = foot_positions.row(i).transpose() + x0.segment<3>(0);
        initial_state.foot_contacts[i] = true;
    }
    
    CrossingStateMachine::WindowObstacle window;
    window.x_position = 2.0;
    window.width = 0.5;
    window.height = 0.4;
    window.bottom_height = 0.2;
    window.top_height = 0.6;
    window.safety_margin = 0.05;
    
    mpc_controller.initializeCrossing(initial_state, window);
    
    // 5. 设置参考轨迹（简单的前进轨迹）
    std::vector<Eigen::VectorXd> x_ref(mpc_params.horizon);
    for (int k = 0; k < mpc_params.horizon; ++k) {
        x_ref[k] = Eigen::VectorXd::Zero(12);
        x_ref[k].segment<3>(0) = x0.segment<3>(0) + Eigen::Vector3d(k * 0.2 * mpc_params.dt, 0, 0);  // 增加前进速度
        x_ref[k](2) = 0.3;  // 保持高度
        x_ref[k](6) = 0.2;  // 期望前进速度 0.2 m/s
    }
    mpc_controller.setReference(x_ref);
    
    std::cout << "\n=== MPC控制器初始化完成 ===" << std::endl;
    std::cout << "时域长度: " << mpc_params.horizon << std::endl;
    std::cout << "控制频率: " << (1.0 / mpc_params.dt) << " Hz" << std::endl;
    std::cout << "初始位置: x=" << x0(0) << "m, z=" << x0(2) << "m" << std::endl;
    
    // 6. 控制循环
    Eigen::VectorXd x_current = x0;
    double total_time = 0.0;
    int step_count = 0;
    const int max_steps = 400;  // 20秒仿真
    
    // 记录数据
    std::vector<double> time_history;
    std::vector<Eigen::VectorXd> state_history;
    std::vector<Eigen::VectorXd> control_history;
    std::vector<double> solve_time_history;
    std::vector<std::string> crossing_state_history;
    
    std::cout << "\n=== 开始MPC控制循环 ===" << std::endl;
    std::cout << std::fixed << std::setprecision(3);
    
    while (step_count < max_steps) {
        // MPC求解
        Eigen::VectorXd u_optimal;
        bool success = mpc_controller.solve(x_current, u_optimal);
        
        if (!success) {
            std::cout << "MPC求解失败，停止仿真" << std::endl;
            break;
        }
        
        // 记录数据
        time_history.push_back(total_time);
        state_history.push_back(x_current);
        control_history.push_back(u_optimal);
        solve_time_history.push_back(mpc_controller.getSolveTime());
        
        // 获取越障状态
        std::string crossing_state = "未启用";
        if (mpc_controller.isCrossingEnabled()) {
            auto state = mpc_controller.getCurrentCrossingState();
            crossing_state = CrossingStateMachine::getStateName(state);
            
            // 显示越障状态转换
            if (step_count % 20 == 0 && step_count > 0) {
                std::cout << "    越障状态: " << crossing_state << std::endl;
                if (state == CrossingStateMachine::CrossingState::HYBRID_GAIT_WALKING) {
                    std::cout << "    🔥 混合构型行走激活！" << std::endl;
                }
            }
        }
        crossing_state_history.push_back(crossing_state);
        
        // 每1秒输出一次状态
        if (step_count % 20 == 0) {
            std::cout << "[" << std::setw(6) << total_time << "s] "
                      << "位置: x=" << std::setw(6) << x_current(0) 
                      << "m, z=" << std::setw(6) << x_current(2) << "m | "
                      << "求解时间: " << std::setw(6) << mpc_controller.getSolveTime() << "ms | "
                      << "状态: " << crossing_state << std::endl;
        }
        
        // 简单的动力学积分（仿真）
        // 这里使用简化的积分，实际应该使用完整的动力学模型
        Eigen::VectorXd x_next = x_current;
        
        // 位置积分
        x_next.segment<3>(0) += x_current.segment<3>(6) * mpc_params.dt;
        
        // 姿态积分（简化）
        x_next.segment<3>(3) += x_current.segment<3>(9) * mpc_params.dt;
        
        // 速度更新（简化的力控制）
        double mass = 11.8;
        Eigen::Vector3d force_sum = Eigen::Vector3d::Zero();
        for (int i = 0; i < 4; ++i) {
            force_sum += u_optimal.segment<3>(i * 3);
        }
        
        // 重力补偿和简单的阻尼
        Eigen::Vector3d gravity(0, 0, -mass * 9.81);
        Eigen::Vector3d net_force = force_sum + gravity;
        
        // 速度更新（考虑阻尼）
        x_next.segment<3>(6) += (net_force / mass) * mpc_params.dt;
        x_next.segment<3>(6) *= 0.95;  // 阻尼
        x_next.segment<3>(9) *= 0.90;  // 角速度阻尼
        
        // 高度和速度限制
        if (x_next(2) < 0.25) {
            x_next(2) = 0.25;
            x_next(8) = std::max(0.0, x_next(8));  // 只允许向上的速度
        }
        if (x_next(2) > 0.5) {
            x_next(2) = 0.5;
            x_next(8) = std::min(0.0, x_next(8));  // 只允许向下的速度
        }
        
        // 前进速度限制
        x_next(6) = std::max(-0.5, std::min(0.5, x_next(6)));  // 限制在±0.5m/s
        
        x_current = x_next;
        total_time += mpc_params.dt;
        step_count++;
        
        // 检查是否到达目标
        if (x_current(0) > 3.0) {
            std::cout << "\n到达目标位置，仿真结束" << std::endl;
            break;
        }
    }
    
    std::cout << "\n=== MPC控制循环完成 ===" << std::endl;
    std::cout << "总步数: " << step_count << std::endl;
    std::cout << "总时间: " << total_time << "s" << std::endl;
    std::cout << "最终位置: x=" << x_current(0) << "m, z=" << x_current(2) << "m" << std::endl;
    
    // 7. 统计分析
    if (!solve_time_history.empty()) {
        double avg_solve_time = 0.0;
        double max_solve_time = 0.0;
        for (double t : solve_time_history) {
            avg_solve_time += t;
            max_solve_time = std::max(max_solve_time, t);
        }
        avg_solve_time /= solve_time_history.size();
        
        std::cout << "\n=== 求解性能统计 ===" << std::endl;
        std::cout << "平均求解时间: " << avg_solve_time << "ms" << std::endl;
        std::cout << "最大求解时间: " << max_solve_time << "ms" << std::endl;
        std::cout << "实时性能: " << (max_solve_time < mpc_params.dt * 1000 ? "✅ 满足实时要求" : "⚠️ 不满足实时要求") << std::endl;
    }
    
    // 8. 保存数据到文件
    std::ofstream data_file("mpc_control_data.csv");
    if (data_file.is_open()) {
        data_file << "time,x,y,z,roll,pitch,yaw,vx,vy,vz,wx,wy,wz,";
        data_file << "fx1,fy1,fz1,fx2,fy2,fz2,fx3,fy3,fz3,fx4,fy4,fz4,";
        data_file << "solve_time,crossing_state\n";
        
        for (size_t i = 0; i < time_history.size(); ++i) {
            data_file << time_history[i];
            
            // 状态
            for (int j = 0; j < 12; ++j) {
                data_file << "," << state_history[i](j);
            }
            
            // 控制
            for (int j = 0; j < 12; ++j) {
                data_file << "," << control_history[i](j);
            }
            
            data_file << "," << solve_time_history[i];
            data_file << "," << crossing_state_history[i];
            data_file << "\n";
        }
        
        data_file.close();
        std::cout << "数据已保存到 mpc_control_data.csv" << std::endl;
    }
    
    std::cout << "\n=== 测试完成 ===" << std::endl;
    
    return 0;
}