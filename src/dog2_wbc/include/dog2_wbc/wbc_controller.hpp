#ifndef DOG2_WBC_CONTROLLER_HPP
#define DOG2_WBC_CONTROLLER_HPP

#include <Eigen/Dense>
#include <array>

namespace dog2_wbc {

/**
 * @brief 完整的WBC控制器
 * 
 * 功能：
 * 1. 精确的雅可比计算（基于当前关节角度）
 * 2. 考虑滑动副影响
 * 3. 混合构型支持（膝式/肘式）
 * 4. QP优化的力矩分配
 */
class WBCController {
public:
    enum class LegConfiguration {
        ELBOW,  // 肘式（标准）
        KNEE    // 膝式（穿越后）
    };
    
    struct LegState {
        Eigen::Vector3d joint_angles;     // 关节角度 [hip_roll, hip_pitch, knee]
        double sliding_position;          // 滑动副位置
        LegConfiguration config;          // 构型
        bool in_contact;                  // 是否接触地面
    };
    
    struct Parameters {
        // 腿部几何参数
        double l1;  // 大腿长度
        double l2;  // 小腿长度
        double hip_offset_x;  // 髋关节x偏移
        double hip_offset_y;  // 髋关节y偏移
        
        // 力矩限制
        double max_torque;
        double max_sliding_force;
        
        // QP权重
        double w_dynamics;      // 动力学一致性权重
        double w_foot_tracking; // 足端跟踪权重
        double w_regularization; // 正则化权重
        
        Parameters()
            : l1(0.2), l2(0.2),
              hip_offset_x(0.2), hip_offset_y(0.15),
              max_torque(50.0), max_sliding_force(100.0),
              w_dynamics(1000.0), w_foot_tracking(10.0),
              w_regularization(0.01) {}
    };
    
    WBCController(const Parameters& params = Parameters());
    
    /**
     * @brief 计算关节力矩
     * @param foot_forces 期望的足端力 (12维)
     * @param leg_states 四条腿的状态
     * @return 关节力矩 (12维旋转关节 + 4维滑动副)
     */
    Eigen::VectorXd computeTorques(
        const Eigen::VectorXd& foot_forces,
        const std::array<LegState, 4>& leg_states);
    
    /**
     * @brief 计算单条腿的雅可比矩阵
     * @param leg_id 腿编号 (0-3)
     * @param leg_state 腿状态
     * @return 雅可比矩阵 J (3×4): [∂p/∂q1, ∂p/∂q2, ∂p/∂q3, ∂p/∂d]
     */
    Eigen::MatrixXd computeLegJacobian(
        int leg_id,
        const LegState& leg_state);
    
    /**
     * @brief 正运动学：关节角度 → 足端位置
     * @param leg_id 腿编号
     * @param leg_state 腿状态
     * @return 足端位置（机体坐标系）
     */
    Eigen::Vector3d forwardKinematics(
        int leg_id,
        const LegState& leg_state);
    
    /**
     * @brief 更新参数
     */
    void updateParameters(const Parameters& params) { params_ = params; }
    
    /**
     * @brief 获取上次求解的统计信息
     */
    struct SolveStats {
        double solve_time_ms;
        double torque_norm;
        bool success;
    };
    SolveStats getLastSolveStats() const { return last_stats_; }

private:
    /**
     * @brief 计算肘式构型的雅可比
     */
    Eigen::MatrixXd computeElbowJacobian(
        int leg_id,
        const Eigen::Vector3d& joint_angles,
        double sliding_position);
    
    /**
     * @brief 计算膝式构型的雅可比
     */
    Eigen::MatrixXd computeKneeJacobian(
        int leg_id,
        const Eigen::Vector3d& joint_angles,
        double sliding_position);
    
    /**
     * @brief 应用力矩限制
     */
    void applyTorqueLimits(Eigen::VectorXd& torques);
    
    Parameters params_;
    SolveStats last_stats_;
};

} // namespace dog2_wbc

#endif // DOG2_WBC_CONTROLLER_HPP
