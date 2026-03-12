#ifndef DOG2_MPC_SRBD_MODEL_HPP
#define DOG2_MPC_SRBD_MODEL_HPP

#include <Eigen/Dense>
#include <vector>

namespace dog2_mpc {

/**
 * @brief 单刚体动力学模型（Single Rigid Body Dynamics）
 * 
 * 用于MPC的简化质心动力学模型
 * 状态: [x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz]^T (12维)
 * 控制: [F1x, F1y, F1z, F2x, F2y, F2z, F3x, F3y, F3z, F4x, F4y, F4z]^T (12维)
 */
class SRBDModel {
public:
    /**
     * @brief 构造函数
     * @param mass 机器人总质量 (kg)
     * @param inertia 惯性张量 (3×3矩阵)
     */
    SRBDModel(double mass, const Eigen::Matrix3d& inertia);
    
    /**
     * @brief 设置重力加速度
     * @param gravity 重力向量 [0, 0, -9.81]
     */
    void setGravity(const Eigen::Vector3d& gravity);
    
    /**
     * @brief 计算连续时间动力学 ẋ = f(x, u)
     * @param state 当前状态 (12维)
     * @param control 控制输入 (12维: 4条腿的接触力)
     * @param foot_positions 足端位置相对质心 (4×3矩阵)
     * @param state_dot 输出：状态导数 (12维)
     */
    void dynamics(const Eigen::VectorXd& state,
                  const Eigen::VectorXd& control,
                  const Eigen::MatrixXd& foot_positions,
                  Eigen::VectorXd& state_dot) const;
    
    /**
     * @brief 离散化动力学（欧拉法）
     * @param state 当前状态
     * @param control 控制输入
     * @param foot_positions 足端位置
     * @param dt 时间步长
     * @param next_state 输出：下一时刻状态
     */
    void discreteDynamics(const Eigen::VectorXd& state,
                         const Eigen::VectorXd& control,
                         const Eigen::MatrixXd& foot_positions,
                         double dt,
                         Eigen::VectorXd& next_state) const;
    
    /**
     * @brief 线性化动力学 x[k+1] = A*x[k] + B*u[k]
     * @param state 线性化点的状态
     * @param control 线性化点的控制
     * @param foot_positions 足端位置
     * @param dt 时间步长
     * @param A 输出：状态转移矩阵 (12×12)
     * @param B 输出：控制输入矩阵 (12×12)
     */
    void linearize(const Eigen::VectorXd& state,
                   const Eigen::VectorXd& control,
                   const Eigen::MatrixXd& foot_positions,
                   double dt,
                   Eigen::MatrixXd& A,
                   Eigen::MatrixXd& B) const;
    
    /**
     * @brief 获取质量
     */
    double getMass() const { return mass_; }
    
    /**
     * @brief 获取惯性张量
     */
    const Eigen::Matrix3d& getInertia() const { return inertia_; }
    
    /**
     * @brief 获取重力
     */
    const Eigen::Vector3d& getGravity() const { return gravity_; }
    
    /**
     * @brief 状态维度
     */
    static constexpr int STATE_DIM = 12;
    
    /**
     * @brief 控制维度
     */
    static constexpr int CONTROL_DIM = 12;
    
    /**
     * @brief 足端数量
     */
    static constexpr int NUM_FEET = 4;

private:
    double mass_;                  ///< 机器人总质量
    Eigen::Matrix3d inertia_;      ///< 惯性张量
    Eigen::Vector3d gravity_;      ///< 重力向量
    
    /**
     * @brief 旋转矩阵（从body到world）
     * @param roll 滚转角
     * @param pitch 俯仰角
     * @param yaw 偏航角
     * @return 旋转矩阵 (3×3)
     */
    Eigen::Matrix3d rotationMatrix(double roll, double pitch, double yaw) const;
    
    /**
     * @brief 角速度到欧拉角速度的转换矩阵
     * @param roll 滚转角
     * @param pitch 俯仰角
     * @return 转换矩阵 (3×3)
     */
    Eigen::Matrix3d angularVelocityToEulerRate(double roll, double pitch) const;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_SRBD_MODEL_HPP
