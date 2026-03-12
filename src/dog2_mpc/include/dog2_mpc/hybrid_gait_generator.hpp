#ifndef DOG2_MPC_HYBRID_GAIT_GENERATOR_HPP
#define DOG2_MPC_HYBRID_GAIT_GENERATOR_HPP

#include "dog2_mpc/crossing_state_machine.hpp"
#include <Eigen/Dense>
#include <vector>
#include <array>

namespace dog2_mpc {

/**
 * @brief 混合构型步态生成器
 * 
 * Dog2的核心创新：在"前腿膝式+后腿肘式"极度不对称的混合构型下
 * 进行动态行走的能力。这是Dog2相比传统四足机器人的杀手锏。
 * 
 * 技术挑战：
 * 1. 前后腿工作空间完全不同
 * 2. 腿间距离约束（防止碰撞）
 * 3. 不对称步态参数
 * 4. 动态稳定性控制
 */
class HybridGaitGenerator {
public:
    /**
     * @brief 足端轨迹点
     */
    struct FootstepPlan {
        Eigen::Vector3d position;    ///< 足端位置 [x, y, z]
        Eigen::Vector3d velocity;    ///< 足端速度 [vx, vy, vz]
        double contact_force;        ///< 接触力 (N)
        bool is_contact;             ///< 是否接触地面
        double phase;                ///< 步态相位 [0, 1]
    };

    /**
     * @brief 腿部参数（针对不同构型）
     */
    struct LegParams {
        double step_length;          ///< 步长 (m)
        double step_height;          ///< 抬腿高度 (m)
        double duty_factor;          ///< 支撑相占比 [0, 1]
        Eigen::Vector2d workspace_x; ///< x方向工作空间 [min, max] (相对机身)
        Eigen::Vector2d workspace_y; ///< y方向工作空间 [min, max] (相对机身)
        double max_velocity;         ///< 最大足端速度 (m/s)
        double stance_stiffness;     ///< 支撑相刚度 (N/m)
        double swing_stiffness;      ///< 摆动相刚度 (N/m)
    };

    /**
     * @brief 步态状态
     */
    struct GaitState {
        std::array<FootstepPlan, 4> footsteps;  ///< 四条腿的足端计划
        std::array<double, 4> phases;           ///< 各腿的步态相位
        double gait_frequency;                  ///< 步态频率 (Hz)
        double forward_velocity;                ///< 前进速度 (m/s)
        Eigen::Vector3d com_target;             ///< 质心目标位置
        Eigen::Vector3d com_velocity_target;    ///< 质心目标速度
    };

    /**
     * @brief 构造函数
     */
    HybridGaitGenerator();

    /**
     * @brief 析构函数
     */
    ~HybridGaitGenerator() = default;

    /**
     * @brief 初始化步态生成器
     * 
     * @param robot_state 当前机器人状态
     */
    void initialize(const CrossingStateMachine::RobotState& robot_state);

    /**
     * @brief 生成混合构型Trot步态
     * 
     * 核心算法：在前腿膝式+后腿肘式的混合构型下生成稳定的对角线步态
     * 
     * @param robot_state 当前机器人状态
     * @param desired_velocity 期望速度 [vx, vy, vyaw]
     * @param dt 时间步长 (s)
     * @return GaitState 生成的步态状态
     */
    GaitState generateHybridTrotGait(const CrossingStateMachine::RobotState& robot_state,
                                    const Eigen::Vector3d& desired_velocity,
                                    double dt);

    /**
     * @brief 生成正常Trot步态（全肘式）
     * 
     * @param robot_state 当前机器人状态
     * @param desired_velocity 期望速度
     * @param dt 时间步长
     * @return GaitState 生成的步态状态
     */
    GaitState generateNormalTrotGait(const CrossingStateMachine::RobotState& robot_state,
                                    const Eigen::Vector3d& desired_velocity,
                                    double dt);

    /**
     * @brief 检查腿间碰撞
     * 
     * 在混合构型下，前后腿的工作空间可能重叠，需要检查碰撞
     * 
     * @param footsteps 足端计划
     * @return true 无碰撞
     * @return false 存在碰撞风险
     */
    bool checkLegCollision(const std::array<FootstepPlan, 4>& footsteps) const;

    /**
     * @brief 获取腿部参数
     * 
     * @param leg_config 腿部构型
     * @return LegParams 对应的腿部参数
     */
    LegParams getLegParams(CrossingStateMachine::LegConfiguration leg_config) const;

    /**
     * @brief 设置步态参数
     * 
     * @param frequency 步态频率 (Hz)
     * @param forward_speed 前进速度 (m/s)
     */
    void setGaitParameters(double frequency, double forward_speed);

    /**
     * @brief 计算足端轨迹
     * 
     * 使用摆线轨迹生成足端路径
     * 
     * @param start_pos 起始位置
     * @param end_pos 结束位置
     * @param phase 当前相位 [0, 1]
     * @param leg_params 腿部参数
     * @return FootstepPlan 足端轨迹点
     */
    FootstepPlan computeFootTrajectory(const Eigen::Vector3d& start_pos,
                                      const Eigen::Vector3d& end_pos,
                                      double phase,
                                      const LegParams& leg_params) const;

    /**
     * @brief 更新步态相位
     * 
     * @param dt 时间步长
     */
    void updatePhases(double dt);

    /**
     * @brief 获取当前步态相位
     * 
     * @return std::array<double, 4> 四条腿的相位
     */
    std::array<double, 4> getCurrentPhases() const { return current_phases_; }

    /**
     * @brief 重置步态生成器
     */
    void reset();

private:
    // 步态参数
    double gait_frequency_;      ///< 步态频率 (Hz)
    double forward_speed_;       ///< 前进速度 (m/s)
    std::array<double, 4> current_phases_; ///< 当前相位 [leg1, leg2, leg3, leg4]
    
    // 腿部参数配置
    LegParams front_knee_params_;  ///< 前腿膝式参数
    LegParams rear_elbow_params_;  ///< 后腿肘式参数
    LegParams normal_elbow_params_; ///< 正常肘式参数
    
    // 安全参数
    double min_leg_distance_;    ///< 腿间最小距离 (m)
    double collision_margin_;    ///< 碰撞安全余量 (m)
    
    // 内部状态
    bool initialized_;
    std::array<Eigen::Vector3d, 4> last_foot_positions_; ///< 上一次的足端位置
    
    /**
     * @brief 初始化腿部参数
     */
    void initializeLegParams();
    
    /**
     * @brief 计算Trot步态的相位偏移
     * 
     * Trot步态：对角线步态
     * - 腿1和腿3同相
     * - 腿2和腿4同相
     * - 两组相位差0.5
     */
    std::array<double, 4> computeTrotPhaseOffsets() const;
    
    /**
     * @brief 计算质心轨迹
     * 
     * @param robot_state 当前状态
     * @param desired_velocity 期望速度
     * @param dt 时间步长
     * @return Eigen::Vector3d 质心目标位置
     */
    Eigen::Vector3d computeComTrajectory(const CrossingStateMachine::RobotState& robot_state,
                                        const Eigen::Vector3d& desired_velocity,
                                        double dt) const;
    
    /**
     * @brief 应用腿间避障约束
     * 
     * @param footsteps 输入输出：足端计划
     * @return true 约束应用成功
     * @return false 约束应用失败
     */
    bool applyLegAvoidanceConstraints(std::array<FootstepPlan, 4>& footsteps) const;
    
    /**
     * @brief 将足端位置限制在工作空间内
     * 
     * @param footstep 输入输出：足端计划
     * @param leg_index 腿的索引 (0-3)
     */
    void clampToWorkspace(FootstepPlan& footstep, int leg_index) const;
    
    /**
     * @brief 计算摆线轨迹
     * 
     * @param phase 相位 [0, 1]
     * @param step_height 抬腿高度
     * @return double 垂直位移
     */
    double cycloidTrajectory(double phase, double step_height) const;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_HYBRID_GAIT_GENERATOR_HPP