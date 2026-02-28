#include "dog2_mpc/mpc_controller.hpp"
#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <Eigen/Dense>

namespace dog2_mpc {

class MPCNode : public rclcpp::Node {
public:
    MPCNode() : Node("mpc_node") {
        // 声明参数
        this->declare_parameter("mass", 11.8);  // 优化后的质量
        this->declare_parameter("horizon", 20);
        this->declare_parameter("dt", 0.05);
        this->declare_parameter("control_frequency", 20.0);
        this->declare_parameter("enable_sliding_constraints", true);
        this->declare_parameter("enable_boundary_constraints", true);
        
        // 获取参数
        double mass = this->get_parameter("mass").as_double();
        int horizon = this->get_parameter("horizon").as_int();
        double dt = this->get_parameter("dt").as_double();
        double control_freq = this->get_parameter("control_frequency").as_double();
        
        // 惯性张量（优化后的值）
        Eigen::Matrix3d inertia;
        inertia << 0.0153, 0.00011, 0.0,
                   0.00011, 0.052, 0.0,
                   0.0, 0.0, 0.044;
        
        // 配置MPC参数
        MPCController::Parameters params;
        params.horizon = horizon;
        params.dt = dt;
        params.enable_sliding_constraints = 
            this->get_parameter("enable_sliding_constraints").as_bool();
        params.enable_boundary_constraints = 
            this->get_parameter("enable_boundary_constraints").as_bool();
        
        // 状态权重
        params.Q.diagonal() << 100, 100, 100,  // 位置
                              10, 10, 10,       // 姿态
                              10, 10, 10,       // 线速度
                              1, 1, 1;          // 角速度
        
        // 控制权重
        params.R = Eigen::MatrixXd::Identity(12, 12) * 0.01;
        
        // 控制输入约束（接触力）
        params.u_min = Eigen::VectorXd::Constant(12, -100.0);  // -100N
        params.u_max = Eigen::VectorXd::Constant(12, 100.0);   // +100N
        
        // 创建MPC控制器
        mpc_controller_ = std::make_unique<MPCController>(mass, inertia, params);
        
        // 初始化参考轨迹（悬停）
        std::vector<Eigen::VectorXd> x_ref(horizon, Eigen::VectorXd::Zero(12));
        for (auto& x : x_ref) {
            x(2) = 0.3;  // 期望高度 30cm
        }
        mpc_controller_->setReference(x_ref);
        
        // 初始化足端位置（相对质心）
        Eigen::MatrixXd foot_positions(4, 3);
        foot_positions << 0.2, 0.15, -0.3,   // 前左
                         0.2, -0.15, -0.3,   // 前右
                         -0.2, 0.15, -0.3,   // 后左
                         -0.2, -0.15, -0.3;  // 后右
        mpc_controller_->setBaseFootPositions(foot_positions);
        
        // 订阅机器人状态
        odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/dog2/odom", 10,
            std::bind(&MPCNode::odomCallback, this, std::placeholders::_1));
        
        // 发布控制指令
        wrench_pub_ = this->create_publisher<geometry_msgs::msg::WrenchStamped>(
            "/dog2/mpc/wrench", 10);
        
        // 创建定时器
        auto timer_period = std::chrono::duration<double>(1.0 / control_freq);
        timer_ = this->create_wall_timer(
            timer_period,
            std::bind(&MPCNode::controlLoop, this));
        
        RCLCPP_INFO(this->get_logger(), "MPC Node initialized");
        RCLCPP_INFO(this->get_logger(), "  Mass: %.2f kg", mass);
        RCLCPP_INFO(this->get_logger(), "  Horizon: %d", horizon);
        RCLCPP_INFO(this->get_logger(), "  dt: %.3f s", dt);
        RCLCPP_INFO(this->get_logger(), "  Control frequency: %.1f Hz", control_freq);
    }

private:
    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        // 提取状态
        Eigen::VectorXd state(12);
        
        // 位置
        state(0) = msg->pose.pose.position.x;
        state(1) = msg->pose.pose.position.y;
        state(2) = msg->pose.pose.position.z;
        
        // 姿态（四元数转欧拉角）
        double qx = msg->pose.pose.orientation.x;
        double qy = msg->pose.pose.orientation.y;
        double qz = msg->pose.pose.orientation.z;
        double qw = msg->pose.pose.orientation.w;
        
        // Roll (x-axis rotation)
        double sinr_cosp = 2.0 * (qw * qx + qy * qz);
        double cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy);
        state(3) = std::atan2(sinr_cosp, cosr_cosp);
        
        // Pitch (y-axis rotation)
        double sinp = 2.0 * (qw * qy - qz * qx);
        if (std::abs(sinp) >= 1)
            state(4) = std::copysign(M_PI / 2, sinp);
        else
            state(4) = std::asin(sinp);
        
        // Yaw (z-axis rotation)
        double siny_cosp = 2.0 * (qw * qz + qx * qy);
        double cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz);
        state(5) = std::atan2(siny_cosp, cosy_cosp);
        
        // 线速度
        state(6) = msg->twist.twist.linear.x;
        state(7) = msg->twist.twist.linear.y;
        state(8) = msg->twist.twist.linear.z;
        
        // 角速度
        state(9) = msg->twist.twist.angular.x;
        state(10) = msg->twist.twist.angular.y;
        state(11) = msg->twist.twist.angular.z;
        
        current_state_ = state;
        state_received_ = true;
    }
    
    void controlLoop() {
        if (!state_received_) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                               "Waiting for state...");
            return;
        }
        
        // 求解MPC
        Eigen::VectorXd u_optimal;
        bool success = mpc_controller_->solve(current_state_, u_optimal);
        
        if (!success) {
            RCLCPP_ERROR(this->get_logger(), "MPC solve failed");
            return;
        }
        
        // 发布控制指令
        auto wrench_msg = geometry_msgs::msg::WrenchStamped();
        wrench_msg.header.stamp = this->now();
        wrench_msg.header.frame_id = "base_link";
        
        // 合力（前4个足端的力求和）
        double fx = u_optimal(0) + u_optimal(3) + u_optimal(6) + u_optimal(9);
        double fy = u_optimal(1) + u_optimal(4) + u_optimal(7) + u_optimal(10);
        double fz = u_optimal(2) + u_optimal(5) + u_optimal(8) + u_optimal(11);
        
        wrench_msg.wrench.force.x = fx;
        wrench_msg.wrench.force.y = fy;
        wrench_msg.wrench.force.z = fz;
        
        wrench_pub_->publish(wrench_msg);
        
        // 打印统计信息
        RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                           "MPC solve time: %.2f ms, status: %d",
                           mpc_controller_->getSolveTime(),
                           mpc_controller_->getSolveStatus());
    }
    
    std::unique_ptr<MPCController> mpc_controller_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::Publisher<geometry_msgs::msg::WrenchStamped>::SharedPtr wrench_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    Eigen::VectorXd current_state_;
    bool state_received_ = false;
};

} // namespace dog2_mpc

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<dog2_mpc::MPCNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
