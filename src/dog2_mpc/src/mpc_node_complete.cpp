#include "dog2_mpc/mpc_controller.hpp"
#include "dog2_mpc/trajectory_generator.hpp"
#include "dog2_mpc/contact_detector.hpp"
#include "dog2_mpc/hybrid_gait_generator.hpp"
#include "dog2_mpc/crossing_state_machine.hpp"
#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <algorithm>
#include <array>
#include <cmath>
#include <sstream>

#include "dog2_dynamics/dog2_model.hpp"
#include <stdexcept>

namespace dog2_mpc {

/**
 * @brief 完整的16维MPC节点
 * 
 * 功能：
 * 1. 行走控制（Trot步态）
 * 2. 窗框越障
 * 3. 滑动副协调控制
 * 4. 足端接触检测
 * 5. 参考轨迹生成
 */
class MPCNodeComplete : public rclcpp::Node {
public:
    MPCNodeComplete() : Node("mpc_node_complete") {
        initializeParameters();
        initializeControllers();
        initializePublishersSubscribers();
        
        RCLCPP_INFO(this->get_logger(), "Complete 16D MPC Node initialized");
        RCLCPP_INFO(this->get_logger(), "  Mass: %.2f kg", mass_);
        RCLCPP_INFO(this->get_logger(), "  Horizon: %d", horizon_);
        RCLCPP_INFO(this->get_logger(), "  Control frequency: %.1f Hz", control_freq_);
        RCLCPP_INFO(this->get_logger(), "  Mode: %s", getModeString().c_str());
        RCLCPP_INFO(this->get_logger(), "  Stance (L x W): %.3f x %.3f m",
                    stance_length_, stance_width_);
        RCLCPP_INFO(this->get_logger(), "  Nominal body height: %.3f m", nominal_body_height_);
        RCLCPP_INFO(this->get_logger(), "  CoM offset: [%.3f, %.3f, %.3f] m",
                    com_offset_.x(), com_offset_.y(), com_offset_.z());
    }

private:
    struct LevelAttitudeError {
        double roll_like = 0.0;
        double pitch_like = 0.0;
        double tilt = 0.0;
        double body_up_z = 1.0;
        bool valid = false;
        bool inverted = false;
    };

    static double clampDouble(double v, double lo, double hi) {
        return std::max(lo, std::min(hi, v));
    }

    Eigen::Vector4d rail_position_lower_;
    Eigen::Vector4d rail_position_upper_;

    void loadRailLimitsFromRobotDescription() {
        const std::string robot_description =
            this->get_parameter("robot_description").as_string();

        if (robot_description.empty()) {
            throw std::runtime_error(
                "mpc_node_complete requires robot_description parameter to load rail limits from URDF");
        }

        const auto dog2_model = dog2_dynamics::Dog2Model::fromUrdfXml(robot_description);
        rail_position_lower_ = dog2_model.slidingJointLowerLimits();
        rail_position_upper_ = dog2_model.slidingJointUpperLimits();

        RCLCPP_INFO(this->get_logger(),
                    "Loaded rail limits from URDF: lower=[%.3f %.3f %.3f %.3f], upper=[%.3f %.3f %.3f %.3f]",
                    rail_position_lower_(0), rail_position_lower_(1),
                    rail_position_lower_(2), rail_position_lower_(3),
                    rail_position_upper_(0), rail_position_upper_(1),
                    rail_position_upper_(2), rail_position_upper_(3));
    }

    void initializeParameters() {
        // 声明参数
        this->declare_parameter<std::string>("robot_description", "");
        this->declare_parameter("mass", 11.8);
        this->declare_parameter("horizon", 10);
        this->declare_parameter("dt", 0.05);
        this->declare_parameter("control_frequency", 20.0);
        this->declare_parameter("enable_sliding_constraints", true);
        this->declare_parameter("mode", "hover");  // hover, walking, crossing
        this->declare_parameter("slack_linear_weight", 5e3);
        this->declare_parameter("rail_tracking_error_threshold", 0.020);
        this->declare_parameter("support_polygon_margin_threshold", 0.015);
        this->declare_parameter("crossing_transition_stable_time", 0.15);
        this->declare_parameter("default_stance_length", 0.40);
        this->declare_parameter("default_stance_width", 0.30);
        this->declare_parameter("nominal_body_height", 0.28);
        this->declare_parameter("com_offset_x", 0.0);
        this->declare_parameter("com_offset_y", 0.0);
        this->declare_parameter("com_offset_z", 0.0);
        this->declare_parameter("crossing_window_x_position", 1.55);
        this->declare_parameter("crossing_window_width", 0.48);
        this->declare_parameter("crossing_window_height", 0.62);
        this->declare_parameter("crossing_window_bottom_height", 0.0);
        this->declare_parameter("crossing_window_top_height", 0.62);
        this->declare_parameter("crossing_window_safety_margin", 0.04);
        this->declare_parameter("crossing_activation_distance", 0.25);
        this->declare_parameter("crossing_approach_speed", 0.05);
        this->declare_parameter("vertical_support_enabled", true);
        this->declare_parameter("vertical_support_target_height", 0.0);
        this->declare_parameter("vertical_support_kp", 700.0);
        this->declare_parameter("vertical_support_kd", 90.0);
        this->declare_parameter("vertical_support_min_total_force_multiplier", 1.20);
        this->declare_parameter("vertical_support_max_leg_force", 100.0);
        this->declare_parameter("vertical_support_height_error_limit", 0.25);
        this->declare_parameter("hover_force_sanitize_enabled", true);
        this->declare_parameter("hover_force_max_leg_fz", 55.0);
        this->declare_parameter("hover_force_min_leg_fz", 18.0);
        this->declare_parameter("attitude_support_enabled", true);
        this->declare_parameter("attitude_support_roll_target", 0.0);
        this->declare_parameter("attitude_support_pitch_target", 0.0);
        this->declare_parameter("attitude_support_roll_kp", 90.0);
        this->declare_parameter("attitude_support_roll_kd", 12.0);
        this->declare_parameter("attitude_support_pitch_kp", 140.0);
        this->declare_parameter("attitude_support_pitch_kd", 18.0);
        this->declare_parameter("attitude_support_max_leg_delta", 24.0);
        this->declare_parameter("crossing_forward_assist_enabled", false);
        this->declare_parameter("crossing_forward_assist_force_per_leg", 14.0);
        this->declare_parameter("crossing_forward_assist_pre_approach_enabled", false);
        this->declare_parameter("crossing_force_full_support", true);
        this->declare_parameter("crossing_freeze_rail_targets", false);
        this->declare_parameter("bfs_rail_ramp_enabled", true);
        this->declare_parameter("bfs_rail_ramp_rate", 0.015);
        this->declare_parameter("bfs_rail_ramp_slow_scale", 0.25);
        this->declare_parameter("bfs_attitude_gate_roll", 0.30);
        this->declare_parameter("bfs_attitude_gate_pitch", 0.25);
        this->declare_parameter("bfs_attitude_gate_tilt", 0.40);
        this->declare_parameter("bfs_attitude_gate_up_z", 0.85);
        this->declare_parameter("bfs_attitude_gate_angular_rate", 1.20);
        this->declare_parameter("bfs_min_body_z_for_ramp", 0.080);
        this->declare_parameter("bfs_hard_fail_body_z", 0.055);
        
        
        // 获取参数
        mass_ = this->get_parameter("mass").as_double();
        horizon_ = this->get_parameter("horizon").as_int();
        dt_ = this->get_parameter("dt").as_double();
        control_freq_ = this->get_parameter("control_frequency").as_double();
        stance_length_ = this->get_parameter("default_stance_length").as_double();
        stance_width_ = this->get_parameter("default_stance_width").as_double();
        nominal_body_height_ = this->get_parameter("nominal_body_height").as_double();
        com_offset_ << this->get_parameter("com_offset_x").as_double(),
                       this->get_parameter("com_offset_y").as_double(),
                       this->get_parameter("com_offset_z").as_double();
        crossing_window_.x_position =
            this->get_parameter("crossing_window_x_position").as_double();
        crossing_window_.width =
            this->get_parameter("crossing_window_width").as_double();
        crossing_window_.height =
            this->get_parameter("crossing_window_height").as_double();
        crossing_window_.bottom_height =
            this->get_parameter("crossing_window_bottom_height").as_double();
        crossing_window_.top_height =
            this->get_parameter("crossing_window_top_height").as_double();
        crossing_window_.safety_margin =
            this->get_parameter("crossing_window_safety_margin").as_double();
        crossing_activation_distance_ =
            this->get_parameter("crossing_activation_distance").as_double();
        crossing_approach_speed_ =
            this->get_parameter("crossing_approach_speed").as_double();
        refreshVerticalSupportParameters();
        
        std::string mode_str = this->get_parameter("mode").as_string();
        if (mode_str == "walking") {
            current_mode_ = TrajectoryGenerator::Mode::WALKING;
        } else if (mode_str == "crossing") {
            current_mode_ = TrajectoryGenerator::Mode::CROSSING;
        } else {
            current_mode_ = TrajectoryGenerator::Mode::HOVER;
        }
    }
    
    void initializeControllers() {
        loadRailLimitsFromRobotDescription();

        // 惯性张量
        Eigen::Matrix3d inertia;
        inertia << 0.0153, 0.00011, 0.0,
                   0.00011, 0.052, 0.0,
                   0.0, 0.0, 0.044;
        
        // MPC参数
        MPCController::Parameters mpc_params;
        mpc_params.horizon = horizon_;
        mpc_params.dt = dt_;
        mpc_params.enable_sliding_constraints = 
            this->get_parameter("enable_sliding_constraints").as_bool();
        
        // 16维状态权重
        mpc_params.Q = Eigen::MatrixXd::Identity(16, 16);
        mpc_params.Q.diagonal() << 100, 100, 200,  // 位置
                                  50, 50, 50,       // 姿态
                                  10, 10, 10,       // 线速度
                                  5, 5, 5,          // 角速度
                                  50, 50, 50, 50;   // 滑动副
        
        mpc_params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;
        mpc_params.u_min = Eigen::VectorXd::Constant(12, -100.0);
        mpc_params.u_max = Eigen::VectorXd::Constant(12, 100.0);
        
        // 创建控制器
        mpc_controller_ = std::make_unique<MPCController>(mass_, inertia, mpc_params);
        mpc_controller_->setSlidingPositionLimits(rail_position_lower_, rail_position_upper_);

        // rail soft bound exact penalty 一次项权重（支持动态调参）
        mpc_controller_->setSlackLinearWeight(
            this->get_parameter("slack_linear_weight").as_double());
        mpc_controller_->setFreezeCrossingRailTargets(
            this->get_parameter("crossing_freeze_rail_targets").as_bool());

        // 设置越障状态机 guard 参数（可通过 ROS2 参数服务器调节）
        const double rail_tracking_error_threshold =
            this->get_parameter("rail_tracking_error_threshold").as_double();
        const double support_polygon_margin_threshold =
            this->get_parameter("support_polygon_margin_threshold").as_double();
        const double crossing_transition_stable_time =
            this->get_parameter("crossing_transition_stable_time").as_double();
        mpc_controller_->setCrossingGuardParams(
            rail_tracking_error_threshold,
            support_polygon_margin_threshold,
            crossing_transition_stable_time);

        TrajectoryGenerator::Parameters trajectory_params;
        trajectory_params.default_height = nominal_body_height_;
        trajectory_generator_ = std::make_unique<TrajectoryGenerator>(trajectory_params);
        contact_detector_ = std::make_unique<ContactDetector>();
        gait_generator_ = std::make_unique<HybridGaitGenerator>();
        
        // 设置基础足端位置（蜘蛛式站姿参数化）
        const double half_length = 0.5 * stance_length_;
        const double half_width = 0.5 * stance_width_;
        base_foot_positions_ = Eigen::MatrixXd::Zero(4, 3);
        base_foot_positions_ << -half_length, -half_width, -nominal_body_height_,
                                 half_length, -half_width, -nominal_body_height_,
                                 half_length,  half_width, -nominal_body_height_,
                                -half_length,  half_width, -nominal_body_height_;
        base_foot_positions_.rowwise() += com_offset_.transpose();
        mpc_controller_->setBaseFootPositions(base_foot_positions_);

        RCLCPP_INFO(this->get_logger(),
                    "Base feet x (lf,lh,rh,rf) relative to body: [%.3f, %.3f, %.3f, %.3f]",
                    base_foot_positions_(0, 0),
                    base_foot_positions_(1, 0),
                    base_foot_positions_(2, 0),
                    base_foot_positions_(3, 0));
        
        // 初始化滑动副速度
        Eigen::Vector4d sliding_velocity = Eigen::Vector4d::Zero();
        mpc_controller_->setSlidingVelocity(sliding_velocity);
        
        // 设置轨迹生成器模式
        trajectory_generator_->setMode(current_mode_);
    }
    
    void initializePublishersSubscribers() {
        // 订阅
        odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/dog2/odom", 10,
            std::bind(&MPCNodeComplete::odomCallback, this, std::placeholders::_1));
        
        joint_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10,
            std::bind(&MPCNodeComplete::jointCallback, this, std::placeholders::_1));
        
        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&MPCNodeComplete::cmdVelCallback, this, std::placeholders::_1));
        
        enable_crossing_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "/enable_crossing", 10,
            std::bind(&MPCNodeComplete::enableCrossingCallback, this, std::placeholders::_1));
        
        // 发布
        foot_force_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/dog2/mpc/foot_forces", 10);
        crossing_state_pub_ = this->create_publisher<std_msgs::msg::String>(
            "/dog2/mpc/crossing_state", 10);
        
        // 控制定时器
        auto timer_period = std::chrono::duration<double>(1.0 / control_freq_);
        timer_ = this->create_wall_timer(
            timer_period,
            std::bind(&MPCNodeComplete::controlLoop, this));
    }
    
    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        // 提取SRBD状态
        Eigen::VectorXd srbd_state(12);
        
        srbd_state(0) = msg->pose.pose.position.x;
        srbd_state(1) = msg->pose.pose.position.y;
        srbd_state(2) = msg->pose.pose.position.z;
        
        // 四元数转欧拉角
        double qx = msg->pose.pose.orientation.x;
        double qy = msg->pose.pose.orientation.y;
        double qz = msg->pose.pose.orientation.z;
        double qw = msg->pose.pose.orientation.w;

        Eigen::Quaterniond q_wb(qw, qx, qy, qz);
        if (std::isfinite(q_wb.w()) &&
            std::isfinite(q_wb.x()) &&
            std::isfinite(q_wb.y()) &&
            std::isfinite(q_wb.z()) &&
            q_wb.norm() > 1e-6) {
            current_body_q_wb_ = q_wb.normalized();
            current_body_q_valid_ = true;
            const LevelAttitudeError level_err =
                computeLevelAttitudeErrorFromQuat(current_body_q_wb_);
            if (level_err.valid) {
                last_level_roll_like_ = level_err.roll_like;
                last_level_pitch_like_ = level_err.pitch_like;
                last_level_tilt_ = level_err.tilt;
                last_body_up_z_ = level_err.body_up_z;
            }
        }
        
        double sinr_cosp = 2.0 * (qw * qx + qy * qz);
        double cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy);
        srbd_state(3) = std::atan2(sinr_cosp, cosr_cosp);
        
        double sinp = 2.0 * (qw * qy - qz * qx);
        srbd_state(4) = std::abs(sinp) >= 1 ? 
            std::copysign(M_PI / 2, sinp) : std::asin(sinp);
        
        double siny_cosp = 2.0 * (qw * qz + qx * qy);
        double cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz);
        srbd_state(5) = std::atan2(siny_cosp, cosy_cosp);
        
        srbd_state(6) = msg->twist.twist.linear.x;
        srbd_state(7) = msg->twist.twist.linear.y;
        srbd_state(8) = msg->twist.twist.linear.z;
        srbd_state(9) = msg->twist.twist.angular.x;
        srbd_state(10) = msg->twist.twist.angular.y;
        srbd_state(11) = msg->twist.twist.angular.z;
        
        current_srbd_state_ = srbd_state;
        odom_received_ = true;
    }
    
    void jointCallback(const sensor_msgs::msg::JointState::SharedPtr msg) {
        Eigen::Vector4d sliding_positions = Eigen::Vector4d::Zero();
        Eigen::Vector4d sliding_velocities = current_sliding_velocities_;
        
        for (size_t i = 0; i < msg->name.size(); ++i) {
            double vel = 0.0;
            if (i < msg->velocity.size()) {
                vel = msg->velocity[i];
            }

            if (msg->name[i] == "j1" || msg->name[i] == "lf_rail_joint") {
                sliding_positions(0) = msg->position[i];
                sliding_velocities(0) = vel;
            } else if (msg->name[i] == "j2" || msg->name[i] == "lh_rail_joint") {
                sliding_positions(1) = msg->position[i];
                sliding_velocities(1) = vel;
            } else if (msg->name[i] == "j3" || msg->name[i] == "rh_rail_joint") {
                sliding_positions(2) = msg->position[i];
                sliding_velocities(2) = vel;
            } else if (msg->name[i] == "j4" || msg->name[i] == "rf_rail_joint") {
                sliding_positions(3) = msg->position[i];
                sliding_velocities(3) = vel;
            } else if (msg->name[i].find("hip_roll") != std::string::npos ||
                       msg->name[i].find("_haa_joint") != std::string::npos ||
                       msg->name[i].find("_coxa_joint") != std::string::npos) {
                int leg = getLegIdFromName(msg->name[i]);
                if (leg >= 0) current_joint_angles_[leg](0) = msg->position[i];
            } else if (msg->name[i].find("hip_pitch") != std::string::npos ||
                       msg->name[i].find("_hfe_joint") != std::string::npos ||
                       msg->name[i].find("_femur_joint") != std::string::npos) {
                int leg = getLegIdFromName(msg->name[i]);
                if (leg >= 0) current_joint_angles_[leg](1) = msg->position[i];
            } else if (msg->name[i].find("knee") != std::string::npos ||
                       msg->name[i].find("_kfe_joint") != std::string::npos ||
                       msg->name[i].find("_tibia_joint") != std::string::npos) {
                int leg = getLegIdFromName(msg->name[i]);
                if (leg >= 0) {
                    current_joint_angles_[leg](2) = msg->position[i];
                    leg_joint_received_[leg] = true;
                }
            }
        }
        
        current_sliding_positions_ = sliding_positions;
        current_sliding_velocities_ =
            sanitizeSlidingVelocities(sliding_positions, sliding_velocities);
        mpc_controller_->setSlidingVelocity(current_sliding_velocities_);
        measured_leg_configs_valid_ =
            leg_joint_received_[0] &&
            leg_joint_received_[1] &&
            leg_joint_received_[2] &&
            leg_joint_received_[3];
        joint_received_ = true;
    }

    std::array<CrossingStateMachine::LegConfiguration, 4> estimateMeasuredLegConfigurations() const {
        std::array<CrossingStateMachine::LegConfiguration, 4> configs;
        for (int i = 0; i < 4; ++i) {
            if (leg_joint_received_[i]) {
                configs[i] = (current_joint_angles_[i](2) < 0.0)
                    ? CrossingStateMachine::LegConfiguration::ELBOW
                    : CrossingStateMachine::LegConfiguration::KNEE;
            } else {
                configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
            }
        }
        return configs;
    }

    Eigen::Vector4d sanitizeSlidingVelocities(const Eigen::Vector4d& positions,
                                              const Eigen::Vector4d& velocities) const {
        // The simplified SRBD MPC treats rail velocity as a known exogenous input.
        // In WALKING/PRE_APPROACH, measured rail velocities are often controller
        // transient/noise and can make the hard physical rail bounds infeasible.
        // Real rail motion is only required after the crossing controller is initialized.
        const bool initialized_crossing =
            current_mode_ == TrajectoryGenerator::Mode::CROSSING &&
            mpc_controller_ &&
            mpc_controller_->isCrossingEnabled();

        if (!initialized_crossing) {
            return Eigen::Vector4d::Zero();
        }

        Eigen::Vector4d sanitized = velocities;
        const Eigen::Vector4d& rail_min = rail_position_lower_;
        const Eigen::Vector4d& rail_max = rail_position_upper_;
        constexpr double kLimitMargin = 0.002;
        constexpr double kMaxPredictionVelocity = 0.25;

        for (int i = 0; i < 4; ++i) {
            sanitized(i) = std::max(
                -kMaxPredictionVelocity,
                std::min(sanitized(i), kMaxPredictionVelocity));
            if (positions(i) <= rail_min(i) + kLimitMargin && sanitized(i) < 0.0) {
                sanitized(i) = 0.0;
            }
            if (positions(i) >= rail_max(i) - kLimitMargin && sanitized(i) > 0.0) {
                sanitized(i) = 0.0;
            }
        }

        return sanitized;
    }
    
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        velocity_cmd_(0) = msg->linear.x;
        velocity_cmd_(1) = msg->linear.y;
        velocity_cmd_(2) = msg->angular.z;
        
        // 如果收到速度命令，切换到行走模式
        if (velocity_cmd_.norm() > 0.01 && 
            current_mode_ == TrajectoryGenerator::Mode::HOVER) {
            current_mode_ = TrajectoryGenerator::Mode::WALKING;
            trajectory_generator_->setMode(current_mode_);
            RCLCPP_INFO(this->get_logger(), "Switched to WALKING mode");
        }
    }

    bool hasCrossingState() const {
        return odom_received_ && joint_received_ && current_srbd_state_.size() >= 12;
    }

    void enableCrossingMode() {
        current_mode_ = TrajectoryGenerator::Mode::CROSSING;
        trajectory_generator_->setMode(current_mode_);
        crossing_enabled_ = true;
        publishCrossingState();

        RCLCPP_INFO(this->get_logger(),
                    "Crossing mode ENABLED: window_x=%.3f width=%.3f top=%.3f safety=%.3f activation_distance=%.3f",
                    crossing_window_.x_position,
                    crossing_window_.width,
                    crossing_window_.top_height,
                    crossing_window_.safety_margin,
                    crossing_activation_distance_);
    }
    
    void enableCrossingCallback(const std_msgs::msg::Bool::SharedPtr msg) {
        if (!msg->data || current_mode_ == TrajectoryGenerator::Mode::CROSSING) {
            return;
        }

        if (!hasCrossingState()) {
            pending_crossing_request_ = true;
            RCLCPP_WARN(this->get_logger(),
                        "Crossing request received before state was ready; deferring mode switch");
            return;
        }

        pending_crossing_request_ = false;
        enableCrossingMode();
    }
    
    void controlLoop() {
        if (!odom_received_ || !joint_received_) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                               "Waiting for state...");
            return;
        }

        if (pending_crossing_request_ &&
            current_mode_ != TrajectoryGenerator::Mode::CROSSING) {
            enableCrossingMode();
            pending_crossing_request_ = false;
        }

        // 动态读取 exact penalty 一次项权重
        mpc_controller_->setSlackLinearWeight(
            this->get_parameter("slack_linear_weight").as_double());
        refreshVerticalSupportParameters();
        
        // 构建16维扩展状态
        Eigen::VectorXd extended_state(16);
        extended_state.segment<12>(0) = current_srbd_state_;
        extended_state.segment<4>(12) = current_sliding_positions_;
        
        // 生成参考轨迹
        std::vector<Eigen::VectorXd> x_ref;
        
        bool crossing_pre_approach = false;
        switch (current_mode_) {
            case TrajectoryGenerator::Mode::HOVER:
                x_ref = trajectory_generator_->generateHoverTrajectory(
                    extended_state, horizon_, dt_);
                break;
                
            case TrajectoryGenerator::Mode::WALKING: {
                advanceGaitPhase();
                
                HybridGaitGenerator::GaitState gait_state;
                // GaitState不需要phase成员，直接传递
                
                x_ref = trajectory_generator_->generateWalkingTrajectory(
                    extended_state, velocity_cmd_, gait_state, horizon_, dt_);
                break;
            }
                
            case TrajectoryGenerator::Mode::CROSSING: {
                if (!mpc_controller_->isCrossingEnabled()) {
                    const double activation_x =
                        crossing_window_.x_position - crossing_activation_distance_;
                    if (current_srbd_state_(0) < activation_x) {
                        advanceGaitPhase();
                        HybridGaitGenerator::GaitState gait_state;
                        Eigen::Vector3d approach_velocity(
                            crossing_approach_speed_, 0.0, 0.0);
                        x_ref = trajectory_generator_->generateWalkingTrajectory(
                            extended_state, approach_velocity, gait_state, horizon_, dt_);
                        crossing_pre_approach = true;
                        break;
                    }

                    mpc_controller_->initializeCrossing(buildCrossingRobotState(), crossing_window_);
                    RCLCPP_INFO(this->get_logger(),
                                "Initialized controller crossing at x=%.3f (window_x=%.3f)",
                                current_srbd_state_(0),
                                crossing_window_.x_position);
                }

                // Crossing 主参考由 MPCController 内部状态机维护，这里仅保持中性轨迹。
                x_ref = trajectory_generator_->generateHoverTrajectory(
                    extended_state, horizon_, dt_);
                break;
            }
        }
        
        // 设置MPC参考轨迹
        mpc_controller_->setReference(x_ref);
        updateBfsRailGate();

        const bool use_gait_contact_mask =
            (current_mode_ == TrajectoryGenerator::Mode::WALKING || crossing_pre_approach);
        ContactDetector::ContactState contact_state =
            computeCommandContactState(crossing_pre_approach);
        
        // 注入真实腿部构型（让状态机使用真实测量值而非 stage 期望值）
        {
            auto measured_configs = estimateMeasuredLegConfigurations();
            mpc_controller_->setMeasuredLegConfigurations(measured_configs, measured_leg_configs_valid_);
        }
        {
            auto mc = estimateMeasuredLegConfigurations();
            RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 2000,
                       "Leg configs: valid=%d lf=%s lh=%s rh=%s rf=%s tibia=[%.3f,%.3f,%.3f,%.3f]",
                       measured_leg_configs_valid_ ? 1 : 0,
                       (mc[0] == CrossingStateMachine::LegConfiguration::ELBOW ? "E" : "K"),
                       (mc[1] == CrossingStateMachine::LegConfiguration::ELBOW ? "E" : "K"),
                       (mc[2] == CrossingStateMachine::LegConfiguration::ELBOW ? "E" : "K"),
                       (mc[3] == CrossingStateMachine::LegConfiguration::ELBOW ? "E" : "K"),
                       current_joint_angles_[0](2),
                       current_joint_angles_[1](2),
                       current_joint_angles_[2](2),
                       current_joint_angles_[3](2));
        }

        // 求解MPC
        Eigen::VectorXd u_optimal;
        bool success = mpc_controller_->solve(extended_state, u_optimal);
        
        if (!success) {
            RCLCPP_ERROR_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                                "MPC solve failed, publishing vertical support fallback");
            u_optimal = Eigen::VectorXd::Zero(12);
            applyVerticalSupport(u_optimal, contact_state, use_gait_contact_mask,
                                 crossing_pre_approach);
            applyAttitudeSupport(u_optimal, contact_state, use_gait_contact_mask,
                                 crossing_pre_approach);
            applyCrossingForwardAssist(u_optimal, contact_state, use_gait_contact_mask,
                                       crossing_pre_approach);
            applyHoverForceSanitizer(u_optimal);
            publishCrossingState();
            publishFootForces(u_optimal);
            return;
        }

        publishCrossingState();
        
        if (use_gait_contact_mask) {
            zeroSwingLegForces(u_optimal, contact_state);
        }
        applyVerticalSupport(u_optimal, contact_state, use_gait_contact_mask,
                             crossing_pre_approach);
        applyAttitudeSupport(u_optimal, contact_state, use_gait_contact_mask,
                             crossing_pre_approach);
        applyCrossingForwardAssist(u_optimal, contact_state, use_gait_contact_mask,
                                   crossing_pre_approach);
        applyHoverForceSanitizer(u_optimal);
        
        // 发布足端力
        publishFootForces(u_optimal);
        
        // 统计
        if (++control_count_ % 20 == 0) {
            const std::string crossing_stage =
                (current_mode_ == TrajectoryGenerator::Mode::CROSSING && mpc_controller_->isCrossingEnabled())
                    ? crossingStateKey(mpc_controller_->getCurrentCrossingState())
                    : "NONE";
            const double total_fz =
                u_optimal(2) + u_optimal(5) + u_optimal(8) + u_optimal(11);
            RCLCPP_INFO(this->get_logger(),
                       "MPC: t=%.2fms, h=%.3fm, vz=%.3fm/s, fz=%.1fN, mode=%s, stage=%s, full_support=%d, freeze_rails=%d, bfs_freeze=%d, rails=[%.3f,%.3f,%.3f,%.3f], contacts=[%d,%d,%d,%d]",
                       mpc_controller_->getSolveTime(),
                       current_srbd_state_(2),
                       current_srbd_state_(8),
                       total_fz,
                       getModeString().c_str(),
                       crossing_stage.c_str(),
                       crossing_force_full_support_ ? 1 : 0,
                       crossing_freeze_rail_targets_ ? 1 : 0,
                       last_bfs_rail_freeze_ ? 1 : 0,
                       current_sliding_positions_(0),
                       current_sliding_positions_(1),
                       current_sliding_positions_(2),
                       current_sliding_positions_(3),
                       contact_state.in_contact[0],
                       contact_state.in_contact[1],
                       contact_state.in_contact[2],
                       contact_state.in_contact[3]);
            RCLCPP_INFO(this->get_logger(),
                       "MPC attitude: euler=[%.3f,%.3f] level=[%.3f,%.3f] tilt=%.3f up_z=%.3f wx=%.3f wy=%.3f att_dz=[%.1f,%.1f,%.1f,%.1f] err=[%.3f,%.3f]",
                       current_srbd_state_(3),
                       current_srbd_state_(4),
                       last_level_roll_like_,
                       last_level_pitch_like_,
                       last_level_tilt_,
                       last_body_up_z_,
                       current_srbd_state_(9),
                       current_srbd_state_(10),
                       last_attitude_support_delta_(0),
                       last_attitude_support_delta_(1),
                       last_attitude_support_delta_(2),
                       last_attitude_support_delta_(3),
                       last_roll_error_,
                       last_pitch_error_);
            logFootForceBreakdown(u_optimal, contact_state, use_gait_contact_mask);
        }
    }

    void refreshVerticalSupportParameters() {
        vertical_support_enabled_ =
            this->get_parameter("vertical_support_enabled").as_bool();
        vertical_support_target_height_ =
            this->get_parameter("vertical_support_target_height").as_double();
        vertical_support_kp_ =
            this->get_parameter("vertical_support_kp").as_double();
        vertical_support_kd_ =
            this->get_parameter("vertical_support_kd").as_double();
        vertical_support_min_total_force_multiplier_ =
            std::max(1.0, this->get_parameter("vertical_support_min_total_force_multiplier").as_double());
        vertical_support_max_leg_force_ =
            std::max(0.0, this->get_parameter("vertical_support_max_leg_force").as_double());
        vertical_support_height_error_limit_ =
            std::max(0.0, this->get_parameter("vertical_support_height_error_limit").as_double());
        hover_force_sanitize_enabled_ =
            this->get_parameter("hover_force_sanitize_enabled").as_bool();
        hover_force_max_leg_fz_ =
            std::max(0.0, this->get_parameter("hover_force_max_leg_fz").as_double());
        hover_force_min_leg_fz_ =
            clampDouble(
                this->get_parameter("hover_force_min_leg_fz").as_double(),
                0.0,
                hover_force_max_leg_fz_);
        attitude_support_enabled_ =
            this->get_parameter("attitude_support_enabled").as_bool();
        attitude_support_roll_target_ =
            this->get_parameter("attitude_support_roll_target").as_double();
        attitude_support_pitch_target_ =
            this->get_parameter("attitude_support_pitch_target").as_double();
        attitude_support_roll_kp_ =
            std::max(0.0, this->get_parameter("attitude_support_roll_kp").as_double());
        attitude_support_roll_kd_ =
            std::max(0.0, this->get_parameter("attitude_support_roll_kd").as_double());
        attitude_support_pitch_kp_ =
            std::max(0.0, this->get_parameter("attitude_support_pitch_kp").as_double());
        attitude_support_pitch_kd_ =
            std::max(0.0, this->get_parameter("attitude_support_pitch_kd").as_double());
        attitude_support_max_leg_delta_ =
            std::max(0.0, this->get_parameter("attitude_support_max_leg_delta").as_double());
        crossing_forward_assist_enabled_ =
            this->get_parameter("crossing_forward_assist_enabled").as_bool();
        crossing_forward_assist_force_per_leg_ =
            std::max(0.0, this->get_parameter("crossing_forward_assist_force_per_leg").as_double());
        crossing_forward_assist_pre_approach_enabled_ =
            this->get_parameter("crossing_forward_assist_pre_approach_enabled").as_bool();
        crossing_force_full_support_ =
            this->get_parameter("crossing_force_full_support").as_bool();
        crossing_freeze_rail_targets_ =
            this->get_parameter("crossing_freeze_rail_targets").as_bool();
        bfs_rail_ramp_enabled_ =
            this->get_parameter("bfs_rail_ramp_enabled").as_bool();
        bfs_rail_ramp_rate_ =
            std::max(0.0, this->get_parameter("bfs_rail_ramp_rate").as_double());
        bfs_rail_ramp_slow_scale_ =
            clampDouble(this->get_parameter("bfs_rail_ramp_slow_scale").as_double(), 0.0, 1.0);
        bfs_attitude_gate_roll_ =
            std::max(0.0, this->get_parameter("bfs_attitude_gate_roll").as_double());
        bfs_attitude_gate_pitch_ =
            std::max(0.0, this->get_parameter("bfs_attitude_gate_pitch").as_double());
        bfs_attitude_gate_tilt_ =
            std::max(0.0, this->get_parameter("bfs_attitude_gate_tilt").as_double());
        bfs_attitude_gate_up_z_ =
            clampDouble(this->get_parameter("bfs_attitude_gate_up_z").as_double(), -1.0, 1.0);
        bfs_attitude_gate_angular_rate_ =
            std::max(0.0, this->get_parameter("bfs_attitude_gate_angular_rate").as_double());
        bfs_min_body_z_for_ramp_ =
            std::max(0.0, this->get_parameter("bfs_min_body_z_for_ramp").as_double());
        bfs_hard_fail_body_z_ =
            std::max(0.0, this->get_parameter("bfs_hard_fail_body_z").as_double());
        if (mpc_controller_) {
            mpc_controller_->setFreezeCrossingRailTargets(crossing_freeze_rail_targets_);
            mpc_controller_->setCrossingBfsRailGate(
                bfs_rail_ramp_enabled_,
                last_bfs_rail_freeze_,
                last_bfs_rail_ramp_scale_,
                bfs_rail_ramp_rate_);
        }
    }

    LevelAttitudeError computeLevelAttitudeErrorFromQuat(
        const Eigen::Quaterniond& q_wb) const {
        LevelAttitudeError out;
        if (q_wb.norm() < 1e-6) {
            return out;
        }

        const Eigen::Quaterniond q = q_wb.normalized();
        const Eigen::Matrix3d R_wb = q.toRotationMatrix();
        const Eigen::Vector3d body_z_w = R_wb.col(2);
        const double up_z = clampDouble(body_z_w.z(), -1.0, 1.0);
        const double lateral_norm =
            std::sqrt(body_z_w.x() * body_z_w.x() +
                      body_z_w.y() * body_z_w.y());

        out.body_up_z = up_z;
        out.tilt = std::atan2(lateral_norm, up_z);
        const double denom = std::max(0.15, std::abs(up_z));
        out.roll_like = std::atan2(-body_z_w.y(), denom);
        out.pitch_like = std::atan2(body_z_w.x(), denom);
        out.inverted = up_z < 0.2;
        out.valid = true;
        return out;
    }

    void updateBfsRailGate() {
        if (!mpc_controller_) {
            return;
        }

        const LevelAttitudeError level_err =
            current_body_q_valid_
                ? computeLevelAttitudeErrorFromQuat(current_body_q_wb_)
                : LevelAttitudeError{};
        if (level_err.valid) {
            last_level_roll_like_ = level_err.roll_like;
            last_level_pitch_like_ = level_err.pitch_like;
            last_level_tilt_ = level_err.tilt;
            last_body_up_z_ = level_err.body_up_z;
            mpc_controller_->setLevelAttitudeState(
                true,
                level_err.roll_like,
                level_err.pitch_like,
                level_err.tilt,
                level_err.body_up_z);
        } else {
            mpc_controller_->setLevelAttitudeState(false, 0.0, 0.0, 0.0, 1.0);
        }

        bool freeze = false;
        double ramp_scale = 1.0;

        if (!bfs_rail_ramp_enabled_ ||
            current_mode_ != TrajectoryGenerator::Mode::CROSSING ||
            !mpc_controller_->isCrossingEnabled()) {
            last_bfs_rail_freeze_ = false;
            last_bfs_rail_ramp_scale_ = 1.0;
            mpc_controller_->setCrossingBfsRailGate(
                bfs_rail_ramp_enabled_, false, 1.0, bfs_rail_ramp_rate_);
            return;
        }

        const auto stage = mpc_controller_->getCurrentCrossingState();
        if (stage != CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT) {
            last_bfs_rail_freeze_ = false;
            last_bfs_rail_ramp_scale_ = 1.0;
            mpc_controller_->setCrossingBfsRailGate(
                bfs_rail_ramp_enabled_, false, 1.0, bfs_rail_ramp_rate_);
            return;
        }

        const double wx = current_srbd_state_.size() > 10 ? current_srbd_state_(9) : 0.0;
        const double wy = current_srbd_state_.size() > 10 ? current_srbd_state_(10) : 0.0;
        const double body_z = current_srbd_state_.size() > 2 ? current_srbd_state_(2) : 0.0;

        if (!level_err.valid || bfs_rail_ramp_rate_ <= 0.0) {
            freeze = true;
            ramp_scale = 0.0;
        } else {
            const bool attitude_bad =
                std::abs(level_err.roll_like) > bfs_attitude_gate_roll_ ||
                std::abs(level_err.pitch_like) > bfs_attitude_gate_pitch_ ||
                level_err.tilt > bfs_attitude_gate_tilt_ ||
                level_err.body_up_z < bfs_attitude_gate_up_z_ ||
                std::abs(wx) > bfs_attitude_gate_angular_rate_ ||
                std::abs(wy) > bfs_attitude_gate_angular_rate_ ||
                level_err.inverted;
            const bool height_bad = body_z < bfs_min_body_z_for_ramp_;
            freeze = attitude_bad || height_bad;
            ramp_scale = freeze ? 0.0 : 1.0;
            if (!freeze && level_err.tilt > 0.25) {
                ramp_scale = bfs_rail_ramp_slow_scale_;
            }
        }

        if (body_z < bfs_hard_fail_body_z_) {
            freeze = true;
            ramp_scale = 0.0;
        }

        last_bfs_rail_freeze_ = freeze;
        last_bfs_rail_ramp_scale_ = ramp_scale;
        mpc_controller_->setCrossingBfsRailGate(
            bfs_rail_ramp_enabled_, freeze, ramp_scale, bfs_rail_ramp_rate_);

        RCLCPP_INFO_THROTTLE(
            this->get_logger(),
            *this->get_clock(),
            500,
            "[BFS rail_gate] freeze=%d ramp_scale=%.2f roll_like=%.3f pitch_like=%.3f tilt=%.3f up_z=%.3f z=%.3f wx=%.3f wy=%.3f",
            freeze ? 1 : 0,
            ramp_scale,
            level_err.roll_like,
            level_err.pitch_like,
            level_err.tilt,
            level_err.body_up_z,
            body_z,
            wx,
            wy);
    }

    bool isCrossingSupportStabilizationActive(bool crossing_pre_approach) const {
        if (current_mode_ != TrajectoryGenerator::Mode::CROSSING) {
            return false;
        }

        if (crossing_pre_approach) {
            return true;
        }

        if (!mpc_controller_ || !mpc_controller_->isCrossingEnabled()) {
            return false;
        }

        const auto stage = mpc_controller_->getCurrentCrossingState();
        return stage == CrossingStateMachine::CrossingState::APPROACH ||
               stage == CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT;
    }

    ContactDetector::ContactState computeCommandContactState(bool crossing_pre_approach) {
        ContactDetector::ContactState contact_state;
        if (current_mode_ == TrajectoryGenerator::Mode::WALKING || crossing_pre_approach) {
            std::array<double, 4> gait_phases;
            for (int i = 0; i < 4; ++i) {
                gait_phases[i] = gait_phase_ + (i % 2) * 0.5;
                if (gait_phases[i] >= 1.0) gait_phases[i] -= 1.0;
            }
            contact_state = contact_detector_->detectFromGait(gait_phases);
        }

        if (crossing_force_full_support_ &&
            isCrossingSupportStabilizationActive(crossing_pre_approach)) {
            contact_state.in_contact.fill(true);
        }

        return contact_state;
    }

    void logFootForceBreakdown(const Eigen::VectorXd& foot_forces,
                               const ContactDetector::ContactState& contact_state,
                               bool use_contact_mask) const {
        if (foot_forces.size() < 12) {
            return;
        }

        static constexpr const char* kLegNames[4] = {"lf", "lh", "rh", "rf"};
        std::ostringstream stream;
        stream << "MPC leg_forces:";
        for (int leg = 0; leg < 4; ++leg) {
            const Eigen::Vector3d f_leg = foot_forces.segment<3>(leg * 3);
            const bool support = !use_contact_mask || contact_state.in_contact[leg];
            stream << " " << kLegNames[leg]
                   << "[s=" << (support ? 1 : 0)
                   << " fx=" << f_leg.x()
                   << " fy=" << f_leg.y()
                   << " fz=" << f_leg.z()
                   << " n=" << f_leg.norm() << "]";
        }
        RCLCPP_INFO(this->get_logger(), "%s", stream.str().c_str());
    }

    void zeroSwingLegForces(Eigen::VectorXd& foot_forces,
                            const ContactDetector::ContactState& contact_state) const {
        if (foot_forces.size() < 12) {
            return;
        }

        for (int i = 0; i < 4; ++i) {
            if (!contact_state.in_contact[i]) {
                foot_forces.segment<3>(i * 3).setZero();
            }
        }
    }

    void applyVerticalSupport(Eigen::VectorXd& foot_forces,
                              const ContactDetector::ContactState& contact_state,
                              bool use_contact_mask,
                              bool crossing_pre_approach) const {
        if (!vertical_support_enabled_ ||
            foot_forces.size() < 12 ||
            current_srbd_state_.size() < 12) {
            return;
        }

        std::array<bool, 4> support_legs{};
        int support_count = 0;
        for (int i = 0; i < 4; ++i) {
            support_legs[i] = !use_contact_mask || contact_state.in_contact[i];
            if (support_legs[i]) {
                ++support_count;
            }
        }

        if (support_count < 2) {
            support_legs.fill(true);
            support_count = 4;
        }

        const double target_height =
            vertical_support_target_height_ > 0.0
                ? vertical_support_target_height_
                : nominal_body_height_;
        const double raw_height_error = target_height - current_srbd_state_(2);
        const double height_error = std::max(
            -vertical_support_height_error_limit_,
            std::min(raw_height_error, vertical_support_height_error_limit_));
        const double downward_velocity = -std::min(0.0, current_srbd_state_(8));
        const double gravity_force = mass_ * 9.81;
        const double support_force =
            gravity_force +
            vertical_support_kp_ * std::max(0.0, height_error) +
            vertical_support_kd_ * downward_velocity;
        const double min_total_force =
            gravity_force * vertical_support_min_total_force_multiplier_;
        const double target_total_force =
            std::max(min_total_force, support_force);
        const double stabilization_headroom =
            (attitude_support_enabled_ &&
             isCrossingSupportStabilizationActive(crossing_pre_approach))
                ? std::min(attitude_support_max_leg_delta_,
                           vertical_support_max_leg_force_)
                : 0.0;
        const double vertical_force_ceiling =
            std::max(0.0, vertical_support_max_leg_force_ - stabilization_headroom);
        const double per_leg_force =
            std::min(vertical_force_ceiling,
                     target_total_force / static_cast<double>(support_count));

        for (int i = 0; i < 4; ++i) {
            if (!support_legs[i]) {
                continue;
            }

            const int z_index = i * 3 + 2;
            foot_forces(z_index) = std::max(foot_forces(z_index), per_leg_force);
        }
    }

    void applyHoverForceSanitizer(Eigen::VectorXd& foot_forces) const {
        if (!hover_force_sanitize_enabled_ ||
            current_mode_ != TrajectoryGenerator::Mode::HOVER ||
            foot_forces.size() < 12) {
            return;
        }

        for (int leg = 0; leg < 4; ++leg) {
            const int base = leg * 3;
            foot_forces(base + 0) = 0.0;
            foot_forces(base + 1) = 0.0;
            foot_forces(base + 2) = clampDouble(
                foot_forces(base + 2),
                hover_force_min_leg_fz_,
                hover_force_max_leg_fz_);
        }
    }

    void applyAttitudeSupport(Eigen::VectorXd& foot_forces,
                              const ContactDetector::ContactState& contact_state,
                              bool use_contact_mask,
                              bool crossing_pre_approach) {
        last_attitude_support_delta_.setZero();
        last_roll_error_ = 0.0;
        last_pitch_error_ = 0.0;

        if (!attitude_support_enabled_ ||
            foot_forces.size() < 12 ||
            current_srbd_state_.size() < 12 ||
            !isCrossingSupportStabilizationActive(crossing_pre_approach)) {
            return;
        }

        std::array<bool, 4> support_legs{};
        for (int i = 0; i < 4; ++i) {
            support_legs[i] = !use_contact_mask || contact_state.in_contact[i];
        }

        if (!current_body_q_valid_) {
            return;
        }

        const LevelAttitudeError level_err =
            computeLevelAttitudeErrorFromQuat(current_body_q_wb_);
        if (!level_err.valid) {
            return;
        }

        last_level_roll_like_ = level_err.roll_like;
        last_level_pitch_like_ = level_err.pitch_like;
        last_level_tilt_ = level_err.tilt;
        last_body_up_z_ = level_err.body_up_z;
        if (level_err.inverted) {
            RCLCPP_WARN_THROTTLE(
                this->get_logger(),
                *this->get_clock(),
                1000,
                "Attitude support skipped: body appears inverted/up_z=%.3f tilt=%.3f",
                level_err.body_up_z,
                level_err.tilt);
            return;
        }

        const double roll_rate = current_srbd_state_(9);
        const double pitch_rate = current_srbd_state_(10);

        last_roll_error_ = attitude_support_roll_target_ - level_err.roll_like;
        last_pitch_error_ = attitude_support_pitch_target_ - level_err.pitch_like;

        double tau_roll =
            attitude_support_roll_kp_ * last_roll_error_ -
            attitude_support_roll_kd_ * roll_rate;
        double tau_pitch =
            attitude_support_pitch_kp_ * last_pitch_error_ -
            attitude_support_pitch_kd_ * pitch_rate;
        tau_roll = clampDouble(tau_roll, -40.0, 40.0);
        tau_pitch = clampDouble(tau_pitch, -45.0, 45.0);

        Eigen::MatrixXd foot_rel = base_foot_positions_;

        double denom_y = 1e-6;
        double denom_x = 1e-6;
        int support_count = 0;
        for (int i = 0; i < 4; ++i) {
            if (!support_legs[i]) {
                continue;
            }
            denom_y += foot_rel(i, 1) * foot_rel(i, 1);
            denom_x += foot_rel(i, 0) * foot_rel(i, 0);
            ++support_count;
        }
        if (support_count < 2) {
            return;
        }

        std::array<double, 4> dfz{};
        double mean_dfz = 0.0;
        for (int leg = 0; leg < 4; ++leg) {
            if (!support_legs[leg]) {
                continue;
            }
            const double x = foot_rel(leg, 0);
            const double y = foot_rel(leg, 1);
            double d = tau_roll * y / denom_y - tau_pitch * x / denom_x;
            d = clampDouble(
                d,
                -attitude_support_max_leg_delta_,
                attitude_support_max_leg_delta_);
            dfz[leg] = d;
            mean_dfz += d;
        }
        mean_dfz /= static_cast<double>(support_count);

        for (int leg = 0; leg < 4; ++leg) {
            if (!support_legs[leg]) {
                continue;
            }
            const double delta = clampDouble(
                dfz[leg] - mean_dfz,
                -attitude_support_max_leg_delta_,
                attitude_support_max_leg_delta_);
            const int z_index = leg * 3 + 2;
            const double updated_force = std::max(
                0.0,
                std::min(vertical_support_max_leg_force_,
                         foot_forces(z_index) + delta));
            last_attitude_support_delta_(leg) += updated_force - foot_forces(z_index);
            foot_forces(z_index) = updated_force;
        }

        RCLCPP_DEBUG_THROTTLE(
            this->get_logger(),
            *this->get_clock(),
            500,
            "[attitude_support] roll_like=%.3f pitch_like=%.3f tilt=%.3f up_z=%.3f tau=[%.2f,%.2f] dfz=[%.1f,%.1f,%.1f,%.1f]",
            level_err.roll_like,
            level_err.pitch_like,
            level_err.tilt,
            level_err.body_up_z,
            tau_roll,
            tau_pitch,
            last_attitude_support_delta_(0),
            last_attitude_support_delta_(1),
            last_attitude_support_delta_(2),
            last_attitude_support_delta_(3));
    }

    void applyCrossingForwardAssist(Eigen::VectorXd& foot_forces,
                                    const ContactDetector::ContactState& contact_state,
                                    bool use_contact_mask,
                                    bool crossing_pre_approach) {
        if (!crossing_forward_assist_enabled_ || foot_forces.size() < 12) {
            return;
        }

        if (crossing_pre_approach && !crossing_forward_assist_pre_approach_enabled_) {
            return;
        }

        bool active = false;
        if (current_mode_ == TrajectoryGenerator::Mode::CROSSING) {
            active = crossing_pre_approach;
            if (!active && mpc_controller_ && mpc_controller_->isCrossingEnabled()) {
                const auto stage = mpc_controller_->getCurrentCrossingState();
                active = stage == CrossingStateMachine::CrossingState::APPROACH ||
                         stage == CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT;
            }
        }

        if (!active) {
            return;
        }

        const LevelAttitudeError level_err =
            current_body_q_valid_
                ? computeLevelAttitudeErrorFromQuat(current_body_q_wb_)
                : LevelAttitudeError{};
        if (!level_err.valid ||
            std::abs(level_err.roll_like) > 0.30 ||
            std::abs(level_err.pitch_like) > 0.25 ||
            level_err.tilt > 0.40 ||
            level_err.body_up_z < 0.85 ||
            level_err.inverted) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                                 "Crossing forward assist gated by level attitude: valid=%d roll=%.3f pitch=%.3f tilt=%.3f up_z=%.3f",
                                 level_err.valid ? 1 : 0,
                                 level_err.roll_like,
                                 level_err.pitch_like,
                                 level_err.tilt,
                                 level_err.body_up_z);
            return;
        }

        std::array<bool, 4> support_legs{};
        int support_count = 0;
        for (int i = 0; i < 4; ++i) {
            support_legs[i] = !use_contact_mask || contact_state.in_contact[i];
            if (support_legs[i]) {
                ++support_count;
            }
        }
        if (support_count < 2) {
            support_legs.fill(true);
        }

        for (int i = 0; i < 4; ++i) {
            if (!support_legs[i]) {
                continue;
            }
            const int x_index = i * 3;
            foot_forces(x_index) = std::max(foot_forces(x_index),
                                            crossing_forward_assist_force_per_leg_);
        }
    }

    void publishFootForces(const Eigen::VectorXd& foot_forces) {
        auto force_msg = std_msgs::msg::Float64MultiArray();
        force_msg.data.resize(12, 0.0);
        const int count = std::min<int>(12, foot_forces.size());
        for (int i = 0; i < count; ++i) {
            force_msg.data[i] = foot_forces(i);
        }
        foot_force_pub_->publish(force_msg);
    }

    void advanceGaitPhase() {
        gait_phase_ += dt_ / gait_period_;
        if (gait_phase_ >= 1.0) {
            gait_phase_ -= 1.0;
        }
    }

    CrossingStateMachine::RobotState buildCrossingRobotState() const {
        CrossingStateMachine::RobotState robot_state;
        robot_state.position = current_srbd_state_.segment<3>(0);
        robot_state.velocity = current_srbd_state_.segment<3>(6);
        robot_state.orientation = current_srbd_state_.segment<3>(3);
        robot_state.angular_velocity = current_srbd_state_.segment<3>(9);
        robot_state.sliding_positions = current_sliding_positions_;
        robot_state.sliding_velocities = current_sliding_velocities_;

        for (int i = 0; i < 4; ++i) {
            if (joint_received_) {
                // Infer ELBOW vs KNEE config from true joint state (knee angle)
                // Negative knee angle corresponds to ELBOW configuration
                bool is_elbow = current_joint_angles_[i](2) < 0.0;
                robot_state.leg_configs[i] = is_elbow ? 
                    CrossingStateMachine::LegConfiguration::ELBOW : 
                    CrossingStateMachine::LegConfiguration::KNEE;
                    
                robot_state.foot_contacts[i] = true;
                
                // Keep expectation-based foot positions for MPC SRBD stability
                robot_state.foot_positions[i] = robot_state.position;
                if (base_foot_positions_.rows() == 4 && base_foot_positions_.cols() == 3) {
                    robot_state.foot_positions[i] += base_foot_positions_.row(i).transpose();
                    robot_state.foot_positions[i].x() += robot_state.sliding_positions(i);
                }
            } else {
                robot_state.leg_configs[i] = CrossingStateMachine::LegConfiguration::ELBOW;
                robot_state.foot_contacts[i] = true;
                robot_state.foot_positions[i] = robot_state.position;
                if (base_foot_positions_.rows() == 4 && base_foot_positions_.cols() == 3) {
                    robot_state.foot_positions[i] += base_foot_positions_.row(i).transpose();
                    robot_state.foot_positions[i].x() += robot_state.sliding_positions(i);
                }
            }
        }

        return robot_state;
    }

    std::string crossingStateKey(CrossingStateMachine::CrossingState state) const {
        switch (state) {
            case CrossingStateMachine::CrossingState::APPROACH:
                return "APPROACH";
            case CrossingStateMachine::CrossingState::BODY_FORWARD_SHIFT:
                return "BODY_FORWARD_SHIFT";
            case CrossingStateMachine::CrossingState::FRONT_LEGS_TRANSIT:
                return "FRONT_LEGS_TRANSIT";
            case CrossingStateMachine::CrossingState::HYBRID_GAIT_WALKING:
                return "HYBRID_GAIT_WALKING";
            case CrossingStateMachine::CrossingState::RAIL_ALIGNMENT:
                return "RAIL_ALIGNMENT";
            case CrossingStateMachine::CrossingState::REAR_LEGS_TRANSIT:
                return "REAR_LEGS_TRANSIT";
            case CrossingStateMachine::CrossingState::ALL_KNEE_STATE:
                return "ALL_KNEE_STATE";
            case CrossingStateMachine::CrossingState::RECOVERY:
                return "RECOVERY";
            case CrossingStateMachine::CrossingState::CONTINUE_FORWARD:
                return "CONTINUE_FORWARD";
            case CrossingStateMachine::CrossingState::COMPLETED:
                return "COMPLETED";
            default:
                return "UNKNOWN";
        }
    }

    void publishCrossingState() {
        if (!crossing_state_pub_) {
            return;
        }

        std_msgs::msg::String msg;
        if (current_mode_ == TrajectoryGenerator::Mode::CROSSING &&
            mpc_controller_->isCrossingEnabled()) {
            msg.data = "CROSSING:" + crossingStateKey(mpc_controller_->getCurrentCrossingState());
        } else if (current_mode_ == TrajectoryGenerator::Mode::CROSSING) {
            msg.data = "CROSSING:PRE_APPROACH";
        } else {
            msg.data = getModeString();
        }
        crossing_state_pub_->publish(msg);
    }
    
    std::string getModeString() const {
        switch (current_mode_) {
            case TrajectoryGenerator::Mode::HOVER: return "HOVER";
            case TrajectoryGenerator::Mode::WALKING: return "WALKING";
            case TrajectoryGenerator::Mode::CROSSING: return "CROSSING";
            default: return "UNKNOWN";
        }
    }
    
    int getLegIdFromName(const std::string& name) const {
        if (name.find("lf_") != std::string::npos ||
            name.find("j1") != std::string::npos || name.find("leg1") != std::string::npos) {
            return 0;
        } else if (name.find("lh_") != std::string::npos ||
                   name.find("j2") != std::string::npos || name.find("leg2") != std::string::npos) {
            return 1;
        } else if (name.find("rh_") != std::string::npos ||
                   name.find("j3") != std::string::npos || name.find("leg3") != std::string::npos) {
            return 2;
        } else if (name.find("rf_") != std::string::npos ||
                   name.find("j4") != std::string::npos || name.find("leg4") != std::string::npos) {
            return 3;
        }
        return -1;
    }

    double mass_;
    int horizon_;
    double dt_;
    double control_freq_;
    double stance_length_;
    double stance_width_;
    double nominal_body_height_;
    Eigen::Vector3d com_offset_;
    CrossingStateMachine::WindowObstacle crossing_window_;
    double crossing_activation_distance_;
    double crossing_approach_speed_;
    bool vertical_support_enabled_;
    double vertical_support_target_height_;
    double vertical_support_kp_;
    double vertical_support_kd_;
    double vertical_support_min_total_force_multiplier_;
    double vertical_support_max_leg_force_;
    double vertical_support_height_error_limit_;
    bool hover_force_sanitize_enabled_ = true;
    double hover_force_max_leg_fz_ = 55.0;
    double hover_force_min_leg_fz_ = 18.0;
    bool attitude_support_enabled_;
    double attitude_support_roll_target_;
    double attitude_support_pitch_target_;
    double attitude_support_roll_kp_;
    double attitude_support_roll_kd_;
    double attitude_support_pitch_kp_;
    double attitude_support_pitch_kd_;
    double attitude_support_max_leg_delta_;
    bool crossing_forward_assist_enabled_;
    double crossing_forward_assist_force_per_leg_;
    bool crossing_forward_assist_pre_approach_enabled_ = false;
    bool crossing_force_full_support_ = false;
    bool crossing_freeze_rail_targets_ = false;
    bool bfs_rail_ramp_enabled_ = true;
    double bfs_rail_ramp_rate_ = 0.015;
    double bfs_rail_ramp_slow_scale_ = 0.25;
    double bfs_attitude_gate_roll_ = 0.30;
    double bfs_attitude_gate_pitch_ = 0.25;
    double bfs_attitude_gate_tilt_ = 0.40;
    double bfs_attitude_gate_up_z_ = 0.85;
    double bfs_attitude_gate_angular_rate_ = 1.20;
    double bfs_min_body_z_for_ramp_ = 0.080;
    double bfs_hard_fail_body_z_ = 0.055;
    
    // 控制器
    std::unique_ptr<MPCController> mpc_controller_;
    std::unique_ptr<TrajectoryGenerator> trajectory_generator_;
    std::unique_ptr<ContactDetector> contact_detector_;
    std::unique_ptr<HybridGaitGenerator> gait_generator_;
    
    // ROS接口
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_sub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr enable_crossing_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr foot_force_pub_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr crossing_state_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    // 状态
    std::array<Eigen::Vector3d, 4> current_joint_angles_{};
    Eigen::VectorXd current_srbd_state_;
    Eigen::Vector4d current_sliding_positions_;
    Eigen::Vector4d current_sliding_velocities_ = Eigen::Vector4d::Zero();
    Eigen::Vector4d last_attitude_support_delta_ = Eigen::Vector4d::Zero();
    Eigen::Vector3d velocity_cmd_ = Eigen::Vector3d::Zero();
    Eigen::MatrixXd base_foot_positions_ = Eigen::MatrixXd::Zero(4, 3);
    Eigen::Quaterniond current_body_q_wb_{1.0, 0.0, 0.0, 0.0};
    bool odom_received_ = false;
    bool joint_received_ = false;
    std::array<bool, 4> leg_joint_received_{false, false, false, false};
    bool measured_leg_configs_valid_ = false;
    bool current_body_q_valid_ = false;
    int control_count_ = 0;
    double last_roll_error_ = 0.0;
    double last_pitch_error_ = 0.0;
    double last_level_roll_like_ = 0.0;
    double last_level_pitch_like_ = 0.0;
    double last_level_tilt_ = 0.0;
    double last_body_up_z_ = 1.0;
    bool last_bfs_rail_freeze_ = false;
    double last_bfs_rail_ramp_scale_ = 1.0;
    
    // 模式
    TrajectoryGenerator::Mode current_mode_;
    bool crossing_enabled_ = false;
    bool pending_crossing_request_ = false;
    
    // 步态
    double gait_phase_ = 0.0;
    double gait_period_ = 0.8;  // Trot周期0.8秒
};

} // namespace dog2_mpc

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<dog2_mpc::MPCNodeComplete>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
