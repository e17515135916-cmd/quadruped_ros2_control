#ifndef DOG2_MPC_TRAJECTORY_GENERATOR_HPP
#define DOG2_MPC_TRAJECTORY_GENERATOR_HPP

#include "dog2_mpc/crossing_state_machine.hpp"
#include "dog2_mpc/hybrid_gait_generator.hpp"
#include <Eigen/Dense>
#include <vector>

namespace dog2_mpc {

/**
 * @brief 参考轨迹生成器
 * 
 * 根据不同模式生成16维MPC参考轨迹：
 * 1. 静态悬停
 * 2. 动态行走
 * 3. 窗框越障
 */
class TrajectoryGenerator {
public:
    enum class Mode {
        HOVER,      // 悬停
        WALKING,    // 行走
        CROSSING    // 越障
    };
    
    struct Parameters {
        double default_height;          // 默认高度 (m)
        double walking_speed;           // 行走速度 (m/s)
        double crossing_speed;          // 越障速度 (m/s)
        double trajectory_smoothness;   // 轨迹平滑系数
        
        Parameters()
            : default_height(0.3),
              walking_speed(0.2),
              crossing_speed(0.1),
              trajectory_smoothness(0.8) {}
    };
    
    TrajectoryGenerator(const Parameters& params = Parameters());
    
    /**
     * @brief 生成悬停轨迹
     * @param current_state 当前16维状态
     * @param horizon 预测时域
     * @param dt 时间步长
     * @return 参考轨迹序列
     */
    std::vector<Eigen::VectorXd> generateHoverTrajectory(
        const Eigen::VectorXd& current_state,
        int horizon,
        double dt);
    
    /**
     * @brief 生成行走轨迹
     * @param current_state 当前16维状态
     * @param velocity_cmd 速度命令 [vx, vy, vyaw]
     * @param gait_state 步态状态
     * @param horizon 预测时域
     * @param dt 时间步长
     * @return 参考轨迹序列
     */
    std::vector<Eigen::VectorXd> generateWalkingTrajectory(
        const Eigen::VectorXd& current_state,
        const Eigen::Vector3d& velocity_cmd,
        const HybridGaitGenerator::GaitState& gait_state,
        int horizon,
        double dt);
    
    /**
     * @brief 生成越障轨迹
     * @param current_state 当前16维状态
     * @param crossing_state 越障状态
     * @param window 窗框参数
     * @param horizon 预测时域
     * @param dt 时间步长
     * @return 参考轨迹序列
     */
    std::vector<Eigen::VectorXd> generateCrossingTrajectory(
        const Eigen::VectorXd& current_state,
        const CrossingStateMachine::CrossingState& crossing_state,
        const CrossingStateMachine::WindowObstacle& window,
        int horizon,
        double dt);
    
    /**
     * @brief 设置当前模式
     */
    void setMode(Mode mode) { current_mode_ = mode; }
    
    /**
     * @brief 获取当前模式
     */
    Mode getMode() const { return current_mode_; }
    
    /**
     * @brief 更新参数
     */
    void updateParameters(const Parameters& params) { params_ = params; }

private:
    /**
     * @brief 平滑轨迹
     */
    std::vector<Eigen::VectorXd> smoothTrajectory(
        const std::vector<Eigen::VectorXd>& trajectory,
        double smoothness);
    
    /**
     * @brief 插值两个状态
     */
    Eigen::VectorXd interpolateState(
        const Eigen::VectorXd& state1,
        const Eigen::VectorXd& state2,
        double alpha);
    
    /**
     * @brief 根据越障阶段规划滑动副位置
     */
    Eigen::Vector4d planSlidingPositions(
        const CrossingStateMachine::CrossingState& state,
        double progress);
    
    Parameters params_;
    Mode current_mode_;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_TRAJECTORY_GENERATOR_HPP
