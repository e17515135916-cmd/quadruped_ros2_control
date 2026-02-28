#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/bool.hpp>
#include <Eigen/Dense>
#include <cmath>

/**
 * @brief 简单的状态模拟器
 * 
 * 模拟机器人状态，用于测试MPC+WBC控制器
 * 不需要Gazebo
 * 支持越障动画
 */
class StateSimulator : public rclcpp::Node {
public:
    enum class Mode {
        WALKING,
        CROSSING_APPROACH,
        CROSSING_FRONT_LIFT,
        CROSSING_BODY_MOVE,
        CROSSING_REAR_LIFT,
        CROSSING_COMPLETE
    };
    
    StateSimulator() : Node("state_simulator") {
        // 发布器
        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/dog2/odom", 10);
        joint_pub_ = this->create_publisher<sensor_msgs::msg::JointState>("/joint_states", 10);
        
        // 订阅速度命令
        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&StateSimulator::cmdVelCallback, this, std::placeholders::_1));
        
        // 订阅越障使能
        enable_crossing_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "/enable_crossing", 10,
            std::bind(&StateSimulator::enableCrossingCallback, this, std::placeholders::_1));
        
        // 定时器：50Hz发布状态
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20),
            std::bind(&StateSimulator::publishState, this));
        
        // 初始化状态
        position_ << 0.0, 0.0, 0.3;  // 30cm高度
        velocity_ << 0.0, 0.0, 0.0;
        orientation_ << 0.0, 0.0, 0.0;  // roll, pitch, yaw
        angular_velocity_ << 0.0, 0.0, 0.0;
        
        sliding_positions_ << 0.0, 0.0, 0.0, 0.0;
        joint_positions_.resize(12, 0.0);
        
        current_mode_ = Mode::WALKING;
        crossing_phase_ = 0.0;
        
        RCLCPP_INFO(this->get_logger(), "State Simulator initialized");
        RCLCPP_INFO(this->get_logger(), "  Publishing at 50Hz");
        RCLCPP_INFO(this->get_logger(), "  Initial height: 0.3m");
        RCLCPP_INFO(this->get_logger(), "  Crossing support: ENABLED");
    }

private:
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        cmd_vel_x_ = msg->linear.x;
        cmd_vel_yaw_ = msg->angular.z;
        
        RCLCPP_INFO(this->get_logger(), "Received cmd_vel: vx=%.2f, wz=%.2f", 
                   cmd_vel_x_, cmd_vel_yaw_);
    }
    
    void enableCrossingCallback(const std_msgs::msg::Bool::SharedPtr msg) {
        if (msg->data && current_mode_ == Mode::WALKING) {
            current_mode_ = Mode::CROSSING_APPROACH;
            crossing_phase_ = 0.0;
            crossing_start_x_ = position_(0);
            RCLCPP_INFO(this->get_logger(), "🚀 Crossing mode ENABLED! Starting animation...");
        }
    }
    
    void updateCrossingAnimation(double dt) {
        crossing_phase_ += dt;
        
        switch (current_mode_) {
            case Mode::CROSSING_APPROACH:
                // 接近障碍物（1秒）
                if (crossing_phase_ > 1.0) {
                    current_mode_ = Mode::CROSSING_FRONT_LIFT;
                    crossing_phase_ = 0.0;
                    RCLCPP_INFO(this->get_logger(), "  Phase 1: Front legs lifting...");
                }
                break;
                
            case Mode::CROSSING_FRONT_LIFT:
                // 前腿抬起并伸长（1秒）
                {
                    double progress = std::min(crossing_phase_, 1.0);
                    sliding_positions_(0) = progress * 0.08;  // 前左腿伸长8cm
                    sliding_positions_(1) = progress * 0.08;  // 前右腿伸长8cm
                    position_(2) = 0.3 + progress * 0.1;      // 身体抬高10cm
                    
                    if (crossing_phase_ > 1.0) {
                        current_mode_ = Mode::CROSSING_BODY_MOVE;
                        crossing_phase_ = 0.0;
                        RCLCPP_INFO(this->get_logger(), "  Phase 2: Body moving forward...");
                    }
                }
                break;
                
            case Mode::CROSSING_BODY_MOVE:
                // 身体前移（1.5秒）
                {
                    double progress = std::min(crossing_phase_ / 1.5, 1.0);
                    position_(0) = crossing_start_x_ + progress * 0.6;  // 前移60cm
                    
                    if (crossing_phase_ > 1.5) {
                        current_mode_ = Mode::CROSSING_REAR_LIFT;
                        crossing_phase_ = 0.0;
                        RCLCPP_INFO(this->get_logger(), "  Phase 3: Rear legs lifting...");
                    }
                }
                break;
                
            case Mode::CROSSING_REAR_LIFT:
                // 后腿抬起并伸长（1秒）
                {
                    double progress = std::min(crossing_phase_, 1.0);
                    sliding_positions_(2) = progress * 0.08;  // 后右腿伸长8cm
                    sliding_positions_(3) = progress * 0.08;  // 后左腿伸长8cm
                    
                    if (crossing_phase_ > 1.0) {
                        current_mode_ = Mode::CROSSING_COMPLETE;
                        crossing_phase_ = 0.0;
                        RCLCPP_INFO(this->get_logger(), "  Phase 4: Landing...");
                    }
                }
                break;
                
            case Mode::CROSSING_COMPLETE:
                // 降落并恢复（1秒）
                {
                    double progress = std::min(crossing_phase_, 1.0);
                    double inv_progress = 1.0 - progress;
                    
                    // 腿部收回
                    sliding_positions_(0) = inv_progress * 0.08;
                    sliding_positions_(1) = inv_progress * 0.08;
                    sliding_positions_(2) = inv_progress * 0.08;
                    sliding_positions_(3) = inv_progress * 0.08;
                    
                    // 身体降低
                    position_(2) = 0.4 - progress * 0.1;
                    
                    if (crossing_phase_ > 1.0) {
                        current_mode_ = Mode::WALKING;
                        sliding_positions_.setZero();
                        position_(2) = 0.3;
                        RCLCPP_INFO(this->get_logger(), "✅ Crossing COMPLETE! Resuming normal walking.");
                    }
                }
                break;
                
            default:
                break;
        }
    }
    
    void publishState() {
        auto now = this->get_clock()->now();
        
        // 简单的运动学积分
        double dt = 0.02;  // 50Hz
        
        // 如果在越障模式，更新越障动画
        if (current_mode_ != Mode::WALKING) {
            updateCrossingAnimation(dt);
        } else {
            // 正常行走模式
            // 更新yaw
            orientation_(2) += cmd_vel_yaw_ * dt;
            
            // 更新位置（世界坐标系）
            position_(0) += cmd_vel_x_ * std::cos(orientation_(2)) * dt;
            position_(1) += cmd_vel_x_ * std::sin(orientation_(2)) * dt;
            
            // 更新速度
            velocity_(0) = cmd_vel_x_ * std::cos(orientation_(2));
            velocity_(1) = cmd_vel_x_ * std::sin(orientation_(2));
            angular_velocity_(2) = cmd_vel_yaw_;
        }
        
        // 发布Odometry
        auto odom_msg = nav_msgs::msg::Odometry();
        odom_msg.header.stamp = now;
        odom_msg.header.frame_id = "odom";
        odom_msg.child_frame_id = "base_link";
        
        odom_msg.pose.pose.position.x = position_(0);
        odom_msg.pose.pose.position.y = position_(1);
        odom_msg.pose.pose.position.z = position_(2);
        
        // 欧拉角转四元数
        double roll = orientation_(0);
        double pitch = orientation_(1);
        double yaw = orientation_(2);
        
        double cy = std::cos(yaw * 0.5);
        double sy = std::sin(yaw * 0.5);
        double cp = std::cos(pitch * 0.5);
        double sp = std::sin(pitch * 0.5);
        double cr = std::cos(roll * 0.5);
        double sr = std::sin(roll * 0.5);
        
        odom_msg.pose.pose.orientation.w = cr * cp * cy + sr * sp * sy;
        odom_msg.pose.pose.orientation.x = sr * cp * cy - cr * sp * sy;
        odom_msg.pose.pose.orientation.y = cr * sp * cy + sr * cp * sy;
        odom_msg.pose.pose.orientation.z = cr * cp * sy - sr * sp * cy;
        
        odom_msg.twist.twist.linear.x = velocity_(0);
        odom_msg.twist.twist.linear.y = velocity_(1);
        odom_msg.twist.twist.linear.z = velocity_(2);
        odom_msg.twist.twist.angular.x = angular_velocity_(0);
        odom_msg.twist.twist.angular.y = angular_velocity_(1);
        odom_msg.twist.twist.angular.z = angular_velocity_(2);
        
        odom_pub_->publish(odom_msg);
        
        // 发布JointState
        auto joint_msg = sensor_msgs::msg::JointState();
        joint_msg.header.stamp = now;
        
        // 所有关节名称（16个关节，和 dog2.urdf.xacro 保持一致）
        joint_msg.name = {
            // 滑动副（4个）
            "j1", "j2", "j3", "j4",
            // 前左腿旋转关节（3个）
            "lf_haa_joint", "lf_hfe_joint", "lf_kfe_joint",
            // 前右腿旋转关节（3个）
            "rf_haa_joint", "rf_hfe_joint", "rf_kfe_joint",
            // 后左腿旋转关节（3个）
            "lh_haa_joint", "lh_hfe_joint", "lh_kfe_joint",
            // 后右腿旋转关节（3个）
            "rh_haa_joint", "rh_hfe_joint", "rh_kfe_joint"
        };
        
        // 关节位置（16个）
        joint_msg.position = {
            // 滑动副位置
            sliding_positions_(0), sliding_positions_(1),
            sliding_positions_(2), sliding_positions_(3),
            // 前左腿旋转关节（简单的正弦波模拟行走）
            std::sin(count_ * 0.1) * 0.3,
            std::sin(count_ * 0.1 + 1.0) * 0.2,
            std::sin(count_ * 0.1 + 2.0) * 0.1,
            // 前右腿旋转关节（相位相反）
            std::sin(count_ * 0.1 + 3.14) * 0.3,
            std::sin(count_ * 0.1 + 4.14) * 0.2,
            std::sin(count_ * 0.1 + 5.14) * 0.1,
            // 后左腿旋转关节（与前左腿同相）
            std::sin(count_ * 0.1) * 0.3,
            std::sin(count_ * 0.1 + 1.0) * 0.2,
            std::sin(count_ * 0.1 + 2.0) * 0.1,
            // 后右腿旋转关节（与前右腿同相）
            std::sin(count_ * 0.1 + 3.14) * 0.3,
            std::sin(count_ * 0.1 + 4.14) * 0.2,
            std::sin(count_ * 0.1 + 5.14) * 0.1
        };
        
        joint_pub_->publish(joint_msg);
        
        // 统计
        if (++count_ % 50 == 0) {
            RCLCPP_INFO(this->get_logger(),
                       "State: pos=[%.2f, %.2f, %.2f], yaw=%.2f, vel=[%.2f, %.2f]",
                       position_(0), position_(1), position_(2),
                       orientation_(2),
                       velocity_(0), velocity_(1));
        }
    }
    
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_pub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr enable_crossing_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    Eigen::Vector3d position_;
    Eigen::Vector3d velocity_;
    Eigen::Vector3d orientation_;
    Eigen::Vector3d angular_velocity_;
    Eigen::Vector4d sliding_positions_;
    std::vector<double> joint_positions_;
    
    double cmd_vel_x_ = 0.0;
    double cmd_vel_yaw_ = 0.0;
    int count_ = 0;
    
    // 越障相关
    Mode current_mode_;
    double crossing_phase_;
    double crossing_start_x_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<StateSimulator>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
