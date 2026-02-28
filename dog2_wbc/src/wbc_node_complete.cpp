#include "dog2_wbc/wbc_controller.hpp"
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <Eigen/Dense>

namespace dog2_wbc {

/**
 * @brief 完整的WBC节点
 * 
 * 功能：
 * 1. 精确的雅可比计算
 * 2. 混合构型支持
 * 3. 滑动副力计算
 */
class WBCNodeComplete : public rclcpp::Node {
public:
    WBCNodeComplete() : Node("wbc_node_complete") {
        initializeParameters();
        initializeController();
        initializePublishersSubscribers();
        
        RCLCPP_INFO(this->get_logger(), "Complete WBC Node initialized");
        RCLCPP_INFO(this->get_logger(), "  Using accurate Jacobian calculation");
        RCLCPP_INFO(this->get_logger(), "  Supporting hybrid configuration");
    }

private:
    void initializeParameters() {
        // 声明参数
        this->declare_parameter("l1", 0.2);
        this->declare_parameter("l2", 0.2);
        this->declare_parameter("max_torque", 50.0);
        this->declare_parameter("max_sliding_force", 100.0);
        
        // 获取参数
        WBCController::Parameters params;
        params.l1 = this->get_parameter("l1").as_double();
        params.l2 = this->get_parameter("l2").as_double();
        params.max_torque = this->get_parameter("max_torque").as_double();
        params.max_sliding_force = this->get_parameter("max_sliding_force").as_double();
        
        wbc_params_ = params;
    }
    
    void initializeController() {
        wbc_controller_ = std::make_unique<WBCController>(wbc_params_);
        
        // 初始化腿状态（默认全部肘式）
        for (int i = 0; i < 4; ++i) {
            leg_states_[i].config = WBCController::LegConfiguration::ELBOW;
            leg_states_[i].in_contact = true;
            leg_states_[i].joint_angles.setZero();
            leg_states_[i].sliding_position = 0.0;
        }
    }
    
    void initializePublishersSubscribers() {
        // 订阅MPC输出的足端力
        foot_force_sub_ = this->create_subscription<std_msgs::msg::Float64MultiArray>(
            "/dog2/mpc/foot_forces", 10,
            std::bind(&WBCNodeComplete::footForceCallback, this, std::placeholders::_1));
        
        // 订阅关节状态
        joint_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10,
            std::bind(&WBCNodeComplete::jointCallback, this, std::placeholders::_1));
        
        // 发布关节力矩命令（12个旋转关节）
        torque_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/joint_group_effort_controller/commands", 10);
        
        // 发布滑动副力命令（4个滑动副）
        sliding_force_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/sliding_joint_effort_controller/commands", 10);
    }
    
    void footForceCallback(const std_msgs::msg::Float64MultiArray::SharedPtr msg) {
        if (msg->data.size() != 12) {
            RCLCPP_ERROR(this->get_logger(), "Expected 12 foot forces, got %zu", 
                        msg->data.size());
            return;
        }
        
        if (!joint_received_) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                               "Waiting for joint states...");
            return;
        }
        
        // 提取足端力
        Eigen::VectorXd foot_forces(12);
        for (int i = 0; i < 12; ++i) {
            foot_forces(i) = msg->data[i];
        }
        
        // 计算关节力矩（使用精确雅可比）
        Eigen::VectorXd torques = wbc_controller_->computeTorques(
            foot_forces, leg_states_);
        
        // 发布旋转关节力矩
        auto torque_msg = std_msgs::msg::Float64MultiArray();
        torque_msg.data.resize(12);
        for (int i = 0; i < 12; ++i) {
            torque_msg.data[i] = torques(i);
        }
        torque_pub_->publish(torque_msg);
        
        // 发布滑动副力
        auto sliding_msg = std_msgs::msg::Float64MultiArray();
        sliding_msg.data.resize(4);
        for (int i = 0; i < 4; ++i) {
            sliding_msg.data[i] = torques(12 + i);
        }
        sliding_force_pub_->publish(sliding_msg);
        
        // 统计
        if (++control_count_ % 20 == 0) {
            auto stats = wbc_controller_->getLastSolveStats();
            double total_fz = foot_forces(2) + foot_forces(5) + 
                            foot_forces(8) + foot_forces(11);
            
            RCLCPP_INFO(this->get_logger(),
                       "WBC: t=%.2fms, fz=%.1fN, τ_norm=%.2f, configs=[%s,%s,%s,%s]",
                       stats.solve_time_ms,
                       total_fz,
                       stats.torque_norm,
                       getConfigString(0).c_str(),
                       getConfigString(1).c_str(),
                       getConfigString(2).c_str(),
                       getConfigString(3).c_str());
        }
    }
    
    void jointCallback(const sensor_msgs::msg::JointState::SharedPtr msg) {
        // 更新腿状态
        // 假设关节顺序：j1_hip_roll, j1_hip_pitch, j1_knee, j2_..., j3_..., j4_...
        // 滑动副：j1, j2, j3, j4
        
        for (size_t i = 0; i < msg->name.size(); ++i) {
            const std::string& name = msg->name[i];
            double pos = msg->position[i];
            
            // 解析关节名称
            if (name.find("hip_roll") != std::string::npos) {
                int leg = getLegIdFromName(name);
                if (leg >= 0) leg_states_[leg].joint_angles(0) = pos;
            } else if (name.find("hip_pitch") != std::string::npos) {
                int leg = getLegIdFromName(name);
                if (leg >= 0) leg_states_[leg].joint_angles(1) = pos;
            } else if (name.find("knee") != std::string::npos) {
                int leg = getLegIdFromName(name);
                if (leg >= 0) leg_states_[leg].joint_angles(2) = pos;
            } else if (name == "j1") {
                leg_states_[0].sliding_position = pos;
            } else if (name == "j2") {
                leg_states_[1].sliding_position = pos;
            } else if (name == "j3") {
                leg_states_[2].sliding_position = pos;
            } else if (name == "j4") {
                leg_states_[3].sliding_position = pos;
            }
        }
        
        joint_received_ = true;
    }
    
    int getLegIdFromName(const std::string& name) {
        if (name.find("j1") != std::string::npos || name.find("leg1") != std::string::npos) {
            return 0;
        } else if (name.find("j2") != std::string::npos || name.find("leg2") != std::string::npos) {
            return 1;
        } else if (name.find("j3") != std::string::npos || name.find("leg3") != std::string::npos) {
            return 2;
        } else if (name.find("j4") != std::string::npos || name.find("leg4") != std::string::npos) {
            return 3;
        }
        return -1;
    }
    
    std::string getConfigString(int leg) const {
        return (leg_states_[leg].config == WBCController::LegConfiguration::ELBOW) 
            ? "E" : "K";
    }
    
    std::unique_ptr<WBCController> wbc_controller_;
    WBCController::Parameters wbc_params_;
    std::array<WBCController::LegState, 4> leg_states_;
    
    rclcpp::Subscription<std_msgs::msg::Float64MultiArray>::SharedPtr foot_force_sub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr torque_pub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr sliding_force_pub_;
    
    bool joint_received_ = false;
    int control_count_ = 0;
};

} // namespace dog2_wbc

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<dog2_wbc::WBCNodeComplete>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
