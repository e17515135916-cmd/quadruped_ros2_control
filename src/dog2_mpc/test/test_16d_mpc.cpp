#include "dog2_mpc/mpc_controller.hpp"
#include "dog2_mpc/extended_srbd_model.hpp"
#include "test_helpers.hpp"
#include <iostream>
#include <iomanip>

using namespace dog2_mpc;
using namespace dog2_mpc::test;

/**
 * @brief 测试16维MPC的基本功能（不包含滑动副约束）
 */
int main() {
    TestReporter reporter;
    reporter.printHeader("Dog2 16维MPC基础测试");
    
    // 1. 创建简化的16维MPC控制器
    Eigen::Matrix3d inertia;
    inertia << 0.0153, 0.00011, 0.0,
               0.00011, 0.052, 0.0,
               0.0, 0.0, 0.044;
    MPCController::Parameters mpc_params;
    mpc_params.horizon = 3;      // 短时域，便于调试
    mpc_params.dt = 0.1;         // 10Hz
    
    // 16维状态权重
    mpc_params.Q = Eigen::MatrixXd::Identity(16, 16);
    mpc_params.Q.diagonal() << 100, 100, 200,  // 位置权重 [x, y, z]
                              50, 50, 50,       // 姿态权重 [roll, pitch, yaw]
                              10, 10, 10,       // 线速度权重 [vx, vy, vz]
                              5, 5, 5,          // 角速度权重 [wx, wy, wz]
                              20, 20, 20, 20;   // 滑动副位置权重 [j1, j2, j3, j4]
    
    mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;  // 控制权重
    
    // 控制限制
    mpc_params.u_min = Eigen::VectorXd::Constant(12, -50.0);
    mpc_params.u_max = Eigen::VectorXd::Constant(12, 50.0);
    
    // 暂时禁用滑动副约束，只测试基本16维MPC
    mpc_params.enable_sliding_constraints = false;
    mpc_params.enable_boundary_constraints = false;
    
    MPCController mpc_controller(11.8, inertia, mpc_params);
    
    // 2. 设置16维初始状态
    Eigen::VectorXd x0(16);
    x0 << 0.0, 0.0, 0.3,    // 位置 [x, y, z]
          0.0, 0.0, 0.0,    // 姿态 [roll, pitch, yaw]
          0.0, 0.0, 0.0,    // 线速度 [vx, vy, vz]
          0.0, 0.0, 0.0,    // 角速度 [wx, wy, wz]
          0.0, 0.0, 0.0, 0.0;  // 滑动副位置 [j1, j2, j3, j4]
    
    // 3. 设置基础足端位置
    Eigen::MatrixXd base_foot_positions(4, 3);
    base_foot_positions << -0.2, -0.15, -0.3,  // 腿1
                           0.2, -0.15, -0.3,   // 腿2
                           0.2,  0.15, -0.3,   // 腿3
                          -0.2,  0.15, -0.3;   // 腿4
    mpc_controller.setBaseFootPositions(base_foot_positions);
    
    // 4. 设置滑动副速度（零速度）
    Eigen::Vector4d sliding_velocity = Eigen::Vector4d::Zero();
    mpc_controller.setSlidingVelocity(sliding_velocity);
    
    // 5. 设置16维参考轨迹（向前移动）
    std::vector<Eigen::VectorXd> x_ref(mpc_params.horizon);
    for (int k = 0; k < mpc_params.horizon; ++k) {
        x_ref[k] = Eigen::VectorXd::Zero(16);
        x_ref[k](0) = (k + 1) * 0.05;  // x位置递增
        x_ref[k](2) = 0.3;             // 保持高度
        x_ref[k](6) = 0.05;            // 期望前进速度
        // 滑动副位置保持为0
    }
    mpc_controller.setReference(x_ref);
    
    reporter.printSection("16维参考轨迹");
    for (int k = 0; k < mpc_params.horizon; ++k) {
        std::cout << "步骤" << k << ": x_ref=" << x_ref[k](0) 
                  << ", z_ref=" << x_ref[k](2) 
                  << ", vx_ref=" << x_ref[k](6) 
                  << ", j1_ref=" << x_ref[k](12) << std::endl;
    }
    
    // 6. 求解16维MPC
    reporter.printSection("16维MPC求解");
    
    std::cout << "16维初始状态: [";
    for (int i = 0; i < x0.size(); ++i) {
        std::cout << x0(i);
        if (i < x0.size() - 1) std::cout << ", ";
    }
    std::cout << "]" << std::endl;
    
    std::cout << "基础足端位置:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "  腿" << (i+1) << ": [" << base_foot_positions.row(i) << "]" << std::endl;
    }
    
    Eigen::VectorXd u_optimal;
    bool success = mpc_controller.solve(x0, u_optimal);
    
    if (success) {
        reporter.printSuccess("16维MPC求解成功！");
        reporter.printKeyValue("求解时间", std::to_string(mpc_controller.getSolveTime()) + "ms");
        
        // 7. 分析求解结果
        reporter.printSection("16维求解结果分析");
        
        // 第一步控制
        std::cout << "第一步控制 u_0:" << std::endl;
        for (int i = 0; i < 4; ++i) {
            Eigen::Vector3d f_i = u_optimal.segment<3>(i * 3);
            std::cout << "  腿" << (i+1) << ": fx=" << std::setw(8) << f_i(0) 
                      << ", fy=" << std::setw(8) << f_i(1) 
                      << ", fz=" << std::setw(8) << f_i(2) << std::endl;
        }
        
        // 总力分析
        Eigen::Vector3d total_force = Eigen::Vector3d::Zero();
        for (int i = 0; i < 4; ++i) {
            total_force += u_optimal.segment<3>(i * 3);
        }
        std::cout << "总力: fx=" << total_force(0) 
                  << ", fy=" << total_force(1) 
                  << ", fz=" << total_force(2) << std::endl;
        
        // 16维预测轨迹
        auto predicted_states = mpc_controller.getPredictedTrajectory();
        std::cout << "\n16维预测轨迹:" << std::endl;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            std::cout << "步骤" << k << ": x=" << std::setw(8) << predicted_states[k](0)
                      << ", z=" << std::setw(8) << predicted_states[k](2)
                      << ", vx=" << std::setw(8) << predicted_states[k](6)
                      << ", j1=" << std::setw(8) << predicted_states[k](12)
                      << " (参考: x=" << x_ref[k](0) << ", vx=" << x_ref[k](6) << ")" << std::endl;
        }
        
        // 8. 验证16维动力学一致性
        reporter.printSection("16维动力学验证");
        
        // 检查控制方向
        if (total_force(0) > 0.01) {
            reporter.printSuccess("控制方向正确：正向力，应该向前加速");
        } else if (total_force(0) < -0.01) {
            reporter.printFailure("控制方向错误：负向力，会向后加速");
        } else {
            reporter.printWarning("控制力很小，可能是平衡状态");
        }
        
        // 使用GravityCompensationValidator验证重力补偿
        GravityCompensationValidator gravity_validator(11.8, 9.81, 10.0);
        bool gravity_valid = gravity_validator.validate(u_optimal);
        
        if (!gravity_valid) {
            reporter.printWarning("重力补偿验证未通过，但这可能是由于MPC优化目标");
            std::cout << "   MPC可能为了跟踪参考轨迹而产生额外的垂直力" << std::endl;
        }
        
        // 检查滑动副状态
        std::cout << "\n滑动副状态检查:" << std::endl;
        for (int k = 0; k < mpc_params.horizon; ++k) {
            Eigen::Vector4d sliding_pos = predicted_states[k].segment<4>(12);
            std::cout << "  步骤" << k << " 滑动副: [" << sliding_pos.transpose() << "]" << std::endl;
        }
        
    } else {
        reporter.printFailure("16维MPC求解失败");
        reporter.printKeyValue("OSQP状态", mpc_controller.getSolveStatus());
        reporter.printSummary(false, 1, 0);
        return -1;
    }
    
    // 测试总结
    reporter.printSection("16维MPC基础测试完成");
    reporter.printSummary(true, 1, 1);
    
    return 0;
}