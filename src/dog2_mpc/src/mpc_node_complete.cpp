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
#include <Eigen/Dense>

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
    void initializeParameters() {
        // 声明参数
        this->declare_parameter("mass", 11.8);
        this->declare_parameter("horizon", 10);
        this->declare_parameter("dt", 0.05);
        this->declare_parameter("control_frequency", 20.0);
        this->declare_parameter("enable_sliding_constraints", true);
        this->declare_parameter("mode", "hover");  // hover, walking, crossing
        this->declare_parameter("slack_linear_weight", 1e5);
        this->declare_parameter("rail_tracking_error_threshold", 0.005);
        this->declare_parameter("support_polygon_margin_threshold", 0.015);
        this->declare_parameter("crossing_transition_stable_time", 0.15);
        this->declare_parameter("default_stance_length", 0.40);
        this->declare_parameter("default_stance_width", 0.30);
        this->declare_parameter("nominal_body_height", 0.28);
        this->declare_parameter("com_offset_x", 0.0);
        this->declare_parameter("com_offset_y", 0.0);
        this->declare_parameter("com_offset_z", 0.0);
        
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

        // rail soft bound exact penalty 一次项权重（支持动态调参）
        mpc_controller_->setSlackLinearWeight(
            this->get_parameter("slack_linear_weight").as_double());

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

        trajectory_generator_ = std::make_unique<TrajectoryGenerator>();
        contact_detector_ = std::make_unique<ContactDetector>();
        gait_generator_ = std::make_unique<HybridGaitGenerator>();
        crossing_state_machine_ = std::make_unique<CrossingStateMachine>();
        
        // 设置基础足端位置（蜘蛛式站姿参数化）
        const double half_length = 0.5 * stance_length_;
        const double half_width = 0.5 * stance_width_;
        Eigen::MatrixXd base_foot_positions(4, 3);
        base_foot_positions << -half_length, -half_width, -nominal_body_height_,
                                half_length, -half_width, -nominal_body_height_,
                                half_length,  half_width, -nominal_body_height_,
                               -half_length,  half_width, -nominal_body_height_;
        base_foot_positions.rowwise() += com_offset_.transpose();
        mpc_controller_->setBaseFootPositions(base_foot_positions);
        
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
        
        for (size_t i = 0; i < msg->name.size(); ++i) {
            if (msg->name[i] == "j1") sliding_positions(0) = msg->position[i];
            else if (msg->name[i] == "j2") sliding_positions(1) = msg->position[i];
            else if (msg->name[i] == "j3") sliding_positions(2) = msg->position[i];
            else if (msg->name[i] == "j4") sliding_positions(3) = msg->position[i];
        }
        
        current_sliding_positions_ = sliding_positions;
        joint_received_ = true;
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
    
    void enableCrossingCallback(const std_msgs::msg::Bool::SharedPtr msg) {
        if (msg->data && current_mode_ != TrajectoryGenerator::Mode::CROSSING) {
            current_mode_ = TrajectoryGenerator::Mode::CROSSING;
            trajectory_generator_->setMode(current_mode_);
            crossing_enabled_ = true;
            
            // 初始化越障状态机
            CrossingStateMachine::RobotState robot_state;
            robot_state.position = current_srbd_state_.segment<3>(0);
            robot_state.velocity = current_srbd_state_.segment<3>(6);
            
            CrossingStateMachine::WindowObstacle window;
            window.x_position = robot_state.position.x() + 1.0;  // 1米前方
            window.height = 0.4;
            window.width = 0.6;
            
            crossing_state_machine_->initialize(robot_state, window);
            
            RCLCPP_INFO(this->get_logger(), "Crossing mode ENABLED");
        }
    }
    
    void controlLoop() {
        if (!odom_received_ || !joint_received_) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                               "Waiting for state...");
            return;
        }

        // 动态读取 exact penalty 一次项权重
        mpc_controller_->setSlackLinearWeight(
            this->get_parameter("slack_linear_weight").as_double());
        
        // 构建16维扩展状态
        Eigen::VectorXd extended_state(16);
        extended_state.segment<12>(0) = current_srbd_state_;
        extended_state.segment<4>(12) = current_sliding_positions_;
        
        // 生成参考轨迹
        std::vector<Eigen::VectorXd> x_ref;
        
        switch (current_mode_) {
            case TrajectoryGenerator::Mode::HOVER:
                x_ref = trajectory_generator_->generateHoverTrajectory(
                    extended_state, horizon_, dt_);
                break;
                
            case TrajectoryGenerator::Mode::WALKING: {
                // 更新步态
                gait_phase_ += dt_ / gait_period_;
                if (gait_phase_ >= 1.0) gait_phase_ -= 1.0;
                
                HybridGaitGenerator::GaitState gait_state;
                // GaitState不需要phase成员，直接传递
                
                x_ref = trajectory_generator_->generateWalkingTrajectory(
                    extended_state, velocity_cmd_, gait_state, horizon_, dt_);
                break;
            }
                
            case TrajectoryGenerator::Mode::CROSSING: {
                // 更新越障状态机
                CrossingStateMachine::RobotState robot_state;
                robot_state.position = current_srbd_state_.segment<3>(0);
                robot_state.velocity = current_srbd_state_.segment<3>(6);
                
                crossing_state_machine_->update(robot_state, dt_);
                auto crossing_state = crossing_state_machine_->getCurrentState();
                
                CrossingStateMachine::WindowObstacle window;
                window.x_position = 1.0;
                window.height = 0.4;
                
                x_ref = trajectory_generator_->generateCrossingTrajectory(
                    extended_state, crossing_state, window, horizon_, dt_);
                break;
            }
        }
        
        // 设置MPC参考轨迹
        mpc_controller_->setReference(x_ref);
        
        // 求解MPC
        Eigen::VectorXd u_optimal;
        bool success = mpc_controller_->solve(extended_state, u_optimal);
        
        if (!success) {
            RCLCPP_ERROR_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                                "MPC solve failed");
            return;
        }
        
        // 足端接触检测（基于步态相位）
        std::array<double, 4> gait_phases;
        for (int i = 0; i < 4; ++i) {
            gait_phases[i] = gait_phase_ + (i % 2) * 0.5;
            if (gait_phases[i] >= 1.0) gait_phases[i] -= 1.0;
        }
        auto contact_state = contact_detector_->detectFromGait(gait_phases);
        
        // 对摆动腿的力置零
        for (int i = 0; i < 4; ++i) {
            if (!contact_state.in_contact[i]) {
                u_optimal.segment<3>(i * 3).setZero();
            }
        }
        
        // 发布足端力
        auto force_msg = std_msgs::msg::Float64MultiArray();
        force_msg.data.resize(12);
        for (int i = 0; i < 12; ++i) {
            force_msg.data[i] = u_optimal(i);
        }
        foot_force_pub_->publish(force_msg);
        
        // 统计
        if (++control_count_ % 20 == 0) {
            RCLCPP_INFO(this->get_logger(),
                       "MPC: t=%.2fms, h=%.3fm, mode=%s, contacts=[%d,%d,%d,%d]",
                       mpc_controller_->getSolveTime(),
                       current_srbd_state_(2),
                       getModeString().c_str(),
                       contact_state.in_contact[0],
                       contact_state.in_contact[1],
                       contact_state.in_contact[2],
                       contact_state.in_contact[3]);
        }
    }
    
    std::string getModeString() const {
        switch (current_mode_) {
            case TrajectoryGenerator::Mode::HOVER: return "HOVER";
            case TrajectoryGenerator::Mode::WALKING: return "WALKING";
            case TrajectoryGenerator::Mode::CROSSING: return "CROSSING";
            default: return "UNKNOWN";
        }
    }
    
    // 参数
    double mass_;
    int horizon_;
    double dt_;
    double control_freq_;
    double stance_length_;
    double stance_width_;
    double nominal_body_height_;
    Eigen::Vector3d com_offset_;
    
    // 控制器
    std::unique_ptr<MPCController> mpc_controller_;
    std::unique_ptr<TrajectoryGenerator> trajectory_generator_;
    std::unique_ptr<ContactDetector> contact_detector_;
    std::unique_ptr<HybridGaitGenerator> gait_generator_;
    std::unique_ptr<CrossingStateMachine> crossing_state_machine_;
    
    // ROS接口
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_sub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr enable_crossing_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr foot_force_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    // 状态
    Eigen::VectorXd current_srbd_state_;
    Eigen::Vector4d current_sliding_positions_;
    Eigen::Vector3d velocity_cmd_;
    bool odom_received_ = false;
    bool joint_received_ = false;
    int control_count_ = 0;
    
    // 模式
    TrajectoryGenerator::Mode current_mode_;
    bool crossing_enabled_ = false;
    
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
