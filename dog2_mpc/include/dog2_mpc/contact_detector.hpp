#ifndef DOG2_MPC_CONTACT_DETECTOR_HPP
#define DOG2_MPC_CONTACT_DETECTOR_HPP

#include <Eigen/Dense>
#include <array>

namespace dog2_mpc {

/**
 * @brief 足端接触检测器
 * 
 * 检测四条腿是否接触地面
 */
class ContactDetector {
public:
    struct ContactState {
        std::array<bool, 4> in_contact;     // 是否接触
        std::array<double, 4> contact_force; // 接触力
        
        ContactState() {
            in_contact.fill(true);
            contact_force.fill(0.0);
        }
    };
    
    struct Parameters {
        double force_threshold;      // 力阈值 (N)
        double height_threshold;     // 高度阈值 (m)
        double filter_alpha;         // 滤波系数
        
        Parameters()
            : force_threshold(5.0),
              height_threshold(0.05),
              filter_alpha(0.8) {}
    };
    
    ContactDetector(const Parameters& params = Parameters());
    
    /**
     * @brief 基于足端力检测接触
     * @param foot_forces 足端力 (4×3)
     * @return 接触状态
     */
    ContactState detectFromForces(const Eigen::MatrixXd& foot_forces);
    
    /**
     * @brief 基于足端位置检测接触
     * @param foot_positions 足端位置 (4×3)
     * @param ground_height 地面高度
     * @return 接触状态
     */
    ContactState detectFromPositions(
        const Eigen::MatrixXd& foot_positions,
        double ground_height = 0.0);
    
    /**
     * @brief 基于步态相位检测接触
     * @param gait_phases 步态相位 [0, 1]
     * @return 接触状态
     */
    ContactState detectFromGait(const std::array<double, 4>& gait_phases);
    
    /**
     * @brief 获取当前接触状态
     */
    ContactState getContactState() const { return current_state_; }
    
    /**
     * @brief 更新参数
     */
    void updateParameters(const Parameters& params) { params_ = params; }

private:
    /**
     * @brief 滤波接触状态
     */
    void filterContactState(const ContactState& new_state);
    
    Parameters params_;
    ContactState current_state_;
    ContactState filtered_state_;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_CONTACT_DETECTOR_HPP
