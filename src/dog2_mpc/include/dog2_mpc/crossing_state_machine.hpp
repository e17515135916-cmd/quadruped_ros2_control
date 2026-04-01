#ifndef DOG2_MPC_CROSSING_STATE_MACHINE_HPP
#define DOG2_MPC_CROSSING_STATE_MACHINE_HPP

#include <Eigen/Dense>
#include <array>
#include <string>
#include <memory>

namespace dog2_mpc {

/**
 * @brief Dog2窗框越障状态机
 * 
 * 实现9阶段越障过程：
 * 0. 初始接近 (Approach)
 * 1. 机身前探 (Body Forward Shift)  
 * 2. 前腿穿越 (Front Legs Transit)
 * 3. 混合构型行走 (Hybrid Gait Walking) ⭐核心创新⭐
 * 4. 精确停车定位 (Rail Alignment Positioning)
 * 5. 后腿穿越 (Rear Legs Transit)
 * 6. 全膝式状态 (All-Knee State)
 * 7. 恢复常态 (Recovery)
 * 8. 继续前进 (Continue Forward)
 */
class CrossingStateMachine {
public:
    /**
     * @brief 越障状态枚举
     */
    enum class CrossingState {
        APPROACH = 0,           ///< 初始接近
        BODY_FORWARD_SHIFT,     ///< 机身前探
        FRONT_LEGS_TRANSIT,     ///< 前腿穿越
        HYBRID_GAIT_WALKING,    ///< 混合构型行走 ⭐
        RAIL_ALIGNMENT,         ///< 精确停车定位
        REAR_LEGS_TRANSIT,      ///< 后腿穿越
        ALL_KNEE_STATE,         ///< 全膝式状态
        RECOVERY,               ///< 恢复常态
        CONTINUE_FORWARD,       ///< 继续前进
        COMPLETED               ///< 越障完成
    };

    /**
     * @brief 腿部构型枚举
     */
    enum class LegConfiguration {
        ELBOW,  ///< 肘式：关节向后/外突出，工作空间偏前
        KNEE    ///< 膝式：关节向前/内收束，工作空间偏后
    };

    /**
     * @brief 机器人状态
     */
    struct RobotState {
        Eigen::Vector3d position;           ///< 质心位置 [x, y, z]
        Eigen::Vector3d velocity;           ///< 质心速度 [vx, vy, vz]
        Eigen::Vector3d orientation;        ///< 姿态角 [roll, pitch, yaw]
        Eigen::Vector3d angular_velocity;   ///< 角速度 [wx, wy, wz]
        
        // 滑动副状态 (4个腿的滑动副位移)
        Eigen::Vector4d sliding_positions;  ///< [d1, d2, d3, d4]
        Eigen::Vector4d sliding_velocities; ///< [v1, v2, v3, v4]
        
        // 腿部构型
        std::array<LegConfiguration, 4> leg_configs; ///< [leg1, leg2, leg3, leg4]
        
        // 足端位置 (世界坐标系)
        std::array<Eigen::Vector3d, 4> foot_positions;
        
        // 接触状态
        std::array<bool, 4> foot_contacts; ///< [leg1, leg2, leg3, leg4]
    };

    /**
     * @brief 窗框障碍物参数
     */
    struct WindowObstacle {
        double x_position = 2.0;    ///< 窗框x位置 (m)
        double width = 0.5;         ///< 宽度 (m)
        double height = 0.4;        ///< 高度 (m)
        double bottom_height = 0.2; ///< 底部高度 (m)
        double top_height = 0.6;    ///< 顶部高度 (m)
        double safety_margin = 0.05; ///< 安全距离 (m)
    };

    /**
     * @brief 构造函数
     */
    CrossingStateMachine();

    /**
     * @brief 析构函数
     */
    ~CrossingStateMachine() = default;

    /**
     * @brief 初始化状态机
     * 
     * @param initial_state 初始机器人状态
     * @param window 窗框参数
     */
    void initialize(const RobotState& initial_state, const WindowObstacle& window);

    /**
     * @brief 更新状态机
     * 
     * @param current_state 当前机器人状态
     * @param dt 时间步长 (s)
     * @return true 状态更新成功
     * @return false 状态更新失败
     */
    bool update(const RobotState& current_state, double dt);

    /**
     * @brief 获取当前状态
     * 
     * @return CrossingState 当前越障状态
     */
    CrossingState getCurrentState() const { return current_state_; }

    /**
     * @brief 获取状态名称
     * 
     * @param state 状态枚举
     * @return std::string 状态名称
     */
    static std::string getStateName(CrossingState state);

    /**
     * @brief 获取当前阶段的目标状态
     * 
     * @return RobotState 目标状态
     */
    RobotState getTargetState() const;

    /**
     * @brief 获取当前阶段的约束
     * 
     * @return 约束参数结构体
     */
    struct StageConstraints {
        // 滑动副约束
        Eigen::Vector4d sliding_min;  ///< 滑动副最小位置
        Eigen::Vector4d sliding_max;  ///< 滑动副最大位置
        Eigen::Vector4d sliding_vel_max; ///< 滑动副最大速度
        
        // 姿态约束
        double max_pitch_angle = 0.087; ///< 最大pitch角 (5度)
        double max_roll_angle = 0.087;  ///< 最大roll角 (5度)
        
        // 质心约束
        Eigen::Vector3d com_min;  ///< 质心最小位置
        Eigen::Vector3d com_max;  ///< 质心最大位置
        
        // 足端约束
        std::array<Eigen::Vector3d, 4> foot_workspace_min; ///< 足端工作空间最小值
        std::array<Eigen::Vector3d, 4> foot_workspace_max; ///< 足端工作空间最大值
        
        // 腿间避障约束
        double min_leg_distance = 0.15; ///< 腿间最小距离 (m)
    };

    StageConstraints getCurrentConstraints() const;

    /**
     * @brief 检查是否可以进入下一状态
     * 
     * @param current_state 当前机器人状态
     * @return true 可以进入下一状态
     * @return false 不能进入下一状态
     */
    bool canTransitionToNext(const RobotState& current_state) const;

    /**
     * @brief 强制转换到指定状态（调试用）
     * 
     * @param state 目标状态
     */
    void forceTransitionTo(CrossingState state);

    /**
     * @brief 获取越障进度 (0.0 ~ 1.0)
     * 
     * @return double 进度百分比
     */
    double getProgress() const;

    /**
     * @brief 获取当前窗框障碍物参数
     */
    WindowObstacle getWindowObstacle() const { return window_; }

    /**
     * @brief 设置 rail tracking guard 阈值（单位：m）
     */
    void setRailTrackingErrorThreshold(double threshold) {
        rail_tracking_error_threshold_ = threshold;
    }

    /**
     * @brief 设置支撑多边形 guard 阈值（单位：m）
     */
    void setSupportPolygonMarginThreshold(double threshold) {
        support_polygon_margin_threshold_ = threshold;
    }

    /**
     * @brief 设置 stage transition 稳定保持时长（单位：s）
     */
    void setTransitionStableTime(double t) {
        transition_stable_time_ = t;
    }

    /**
     * @brief 是否完成越障
     * 
     * @return true 越障完成
     * @return false 越障未完成
     */
    bool isCompleted() const { return current_state_ == CrossingState::COMPLETED; }

private:
    CrossingState current_state_;   ///< 当前状态
    double state_start_time_;       ///< 当前状态开始时间
    double total_time_;             ///< 总时间
    
    RobotState initial_state_;      ///< 初始状态
    WindowObstacle window_;         ///< 窗框参数

    /**
     * @brief 稳定保持时间（稳定 transition graph 的关键：guards 需要连续满足才允许切换）
     */
    double transition_stable_time_ = 0.15;     ///< s
    double transition_stable_elapsed_ = 0.0;   ///< s

    /**
     * @brief rail 跟踪 guard 阈值（2mm）
     */
    double rail_tracking_error_threshold_ = 0.005;  ///< m

    /**
     * @brief support polygon guard 阈值（1.5cm）
     * 以 x 方向 1D 支撑区间近似计算 margin
     */
    double support_polygon_margin_threshold_ = 0.015;  ///< m

    /**
     * @brief 计算 rail 跟踪误差（最大逐腿偏差）
     */
    double computeRailTrackingError(const RobotState& state) const;

    /**
     * @brief 计算 support polygon margin（x 方向 1D 近似）
     */
    double computeSupportPolygonMargin(const RobotState& state) const;
    
    /**
     * @brief 状态转换逻辑
     */
    void transitionToNextState();
    
    /**
     * @brief 检查各阶段的完成条件
     */
    bool checkApproachComplete(const RobotState& state) const;
    bool checkBodyForwardShiftComplete(const RobotState& state) const;
    bool checkFrontLegsTransitComplete(const RobotState& state) const;
    bool checkHybridGaitWalkingComplete(const RobotState& state) const;
    bool checkRailAlignmentComplete(const RobotState& state) const;
    bool checkRearLegsTransitComplete(const RobotState& state) const;
    bool checkAllKneeStateComplete(const RobotState& state) const;
    bool checkRecoveryComplete(const RobotState& state) const;
    
    /**
     * @brief 计算各阶段的目标状态
     */
    RobotState computeApproachTarget() const;
    RobotState computeBodyForwardShiftTarget() const;
    RobotState computeFrontLegsTransitTarget() const;
    RobotState computeHybridGaitWalkingTarget() const;
    RobotState computeRailAlignmentTarget() const;
    RobotState computeRearLegsTransitTarget() const;
    RobotState computeAllKneeStateTarget() const;
    RobotState computeRecoveryTarget() const;
    RobotState computeContinueForwardTarget() const;
};

} // namespace dog2_mpc

#endif // DOG2_MPC_CROSSING_STATE_MACHINE_HPP