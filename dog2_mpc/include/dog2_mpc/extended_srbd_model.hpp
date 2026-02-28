#ifndef DOG2_MPC_EXTENDED_SRBD_MODEL_HPP
#define DOG2_MPC_EXTENDED_SRBD_MODEL_HPP

#include "dog2_mpc/srbd_model.hpp"
#include <Eigen/Dense>
#include <vector>

namespace dog2_mpc {

/**
 * @brief 扩展单刚体动力学模型（包含滑动副）
 * 
 * 扩展SRBD模型以包含Dog2的滑动副机构
 * 状态: [x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz, j1, j2, j3, j4]^T (16维)
 * 控制: [F1x, F1y, F1z, F2x, F2y, F2z, F3x, F3y, F3z, F4x, F4y, F4z]^T (12维)
 * 
 * 滑动副状态：
 * - j1, j4: 前腿滑动副位置 (m)
 * - j2, j3: 后腿滑动副位置 (m)
 */
class ExtendedSRBDModel {
public:
    /**
     * @brief 构造函数
     * @param mass 机器人总质量 (kg)
     * @param inertia 惯性张量 (3×3矩阵)
     */
    ExtendedSRBDModel(double mass, const Eigen::Matrix3d& inertia);
    
    /**
     * @brief 设置重力加速度
     * @param gravity 重力向量 [0, 0, -9.81]
     */
    void setGravity(const Eigen::Vector3d& gravity);
    
    /**
     * @brief 设置滑动副参数
     * @param sliding_velocity 滑动副速度 [v1, v2, v3, v4] (m/s)
     */
    void setSlidingVelocity(const Eigen::Vector4d& sliding_velocity);
    
    /**
     * @brief 计算足端位置（考虑滑动副）
     * @param sliding_positions 滑动副位置 [j1, j2, j3, j4]
     * @param base_foot_positions 基础足端位置（滑动副为0时）
     * @return 实际足端位置 (4×3矩阵)
     */
    Eigen::MatrixXd computeFootPositions(
        const Eigen::Vector4d& sliding_positions,
        const Eigen::MatrixXd& base_foot_positions) const;
    
    /**
     * @brief 计算扩展动力学 ẋ = f(x, u)
     * @param state 当前状态 (16维)
     * @param control 控制输入 (12维: 4条腿的接触力)
     * @param base_foot_positions 基础足端位置 (4×3矩阵)
     * @param sliding_velocity 滑动副速度 (4维)
     * @param state_dot 输出：状态导数 (16维)
     */
    void dynamics(const Eigen::VectorXd& state,
                  const Eigen::VectorXd& control,
                  const Eigen::MatrixXd& base_foot_positions,
                  const Eigen::Vector4d& sliding_velocity,
                  Eigen::VectorXd& state_dot) const;
    
    /**
     * @brief 离散化动力学（欧拉法）
     * @param state 当前状态 (16维)
     * @param control 控制输入 (12维)
     * @param base_foot_positions 基础足端位置
     * @param sliding_velocity 滑动副速度
     * @param dt 时间步长
     * @param next_state 输出：下一时刻状态 (16维)
     */
    void discreteDynamics(const Eigen::VectorXd& state,
                         const Eigen::VectorXd& control,
                         const Eigen::MatrixXd& base_foot_positions,
                         const Eigen::Vector4d& sliding_velocity,
                         double dt,
                         Eigen::VectorXd& next_state) const;
    
    /**
     * @brief 线性化扩展动力学 x[k+1] = A*x[k] + B*u[k] + C*v[k]
     * @param state 线性化点的状态 (16维)
     * @param control 线性化点的控制 (12维)
     * @param base_foot_positions 基础足端位置
     * @param sliding_velocity 滑动副速度
     * @param dt 时间步长
     * @param A 输出：状态转移矩阵 (16×16)
     * @param B 输出：控制输入矩阵 (16×12)
     * @param C 输出：滑动副速度矩阵 (16×4)
     */
    void linearize(const Eigen::VectorXd& state,
                   const Eigen::VectorXd& control,
                   const Eigen::MatrixXd& base_foot_positions,
                   const Eigen::Vector4d& sliding_velocity,
                   double dt,
                   Eigen::MatrixXd& A,
                   Eigen::MatrixXd& B,
                   Eigen::MatrixXd& C) const;
    
    /**
     * @brief 从扩展状态提取SRBD状态
     * @param extended_state 扩展状态 (16维)
     * @return SRBD状态 (12维)
     */
    static Eigen::VectorXd extractSRBDState(const Eigen::VectorXd& extended_state);
    
    /**
     * @brief 从扩展状态提取滑动副位置
     * @param extended_state 扩展状态 (16维)
     * @return 滑动副位置 [j1, j2, j3, j4]
     */
    static Eigen::Vector4d extractSlidingPositions(const Eigen::VectorXd& extended_state);
    
    /**
     * @brief 构建扩展状态
     * @param srbd_state SRBD状态 (12维)
     * @param sliding_positions 滑动副位置 (4维)
     * @return 扩展状态 (16维)
     */
    static Eigen::VectorXd buildExtendedState(
        const Eigen::VectorXd& srbd_state,
        const Eigen::Vector4d& sliding_positions);
    
    /**
     * @brief 获取质量
     */
    double getMass() const { return srbd_model_.getMass(); }
    
    /**
     * @brief 获取惯性张量
     */
    const Eigen::Matrix3d& getInertia() const { return srbd_model_.getInertia(); }
    
    /**
     * @brief 获取重力
     */
    const Eigen::Vector3d& getGravity() const { return srbd_model_.getGravity(); }
    
    /**
     * @brief 扩展状态维度
     */
    static constexpr int EXTENDED_STATE_DIM = 16;
    
    /**
     * @brief SRBD状态维度
     */
    static constexpr int SRBD_STATE_DIM = 12;
    
    /**
     * @brief 滑动副状态维度
     */
    static constexpr int SLIDING_STATE_DIM = 4;
    
    /**
     * @brief 控制维度
     */
    static constexpr int CONTROL_DIM = 12;
    
    /**
     * @brief 足端数量
     */
    static constexpr int NUM_FEET = 4;

private:
    SRBDModel srbd_model_;         ///< 基础SRBD模型
    Eigen::Vector4d sliding_velocity_;  ///< 当前滑动副速度
    
    /**
     * @brief 滑动副对足端位置的影响
     * Dog2的滑动副是纵向的，影响足端的x坐标
     * @param leg_index 腿索引 (0-3)
     * @param sliding_position 该腿的滑动副位置
     * @return 足端位置偏移 (3维向量)
     */
    Eigen::Vector3d slidingOffset(int leg_index, double sliding_position) const;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_EXTENDED_SRBD_MODEL_HPP