#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <Eigen/Dense>

namespace dog2_wbc {

/**
 * @brief 简化的WBC节点 - 用于MPC闭环仿真
 * 
 * 功能：
 * 1. 接收MPC输出的足端力（12维）
 * 2. 简化的力矩分配（假设足端雅可比已知）
 * 3. 发布关节力矩命令
 * 
 * 注意：这是简化版本，用于快速验证MPC闭环
 */
class WBCNodeSimple : public rclcpp::Node {
public:
    WBCNodeSimple() : Node("wbc_node_simple") {
        // 订阅MPC输出的足端力
        foot_force_sub_ = this->create_subscription<std_msgs::msg::Float64MultiArray>(
            "/dog2/mpc/foot_forces", 10,
            std::bind(&WBCNodeSimple::footForceCallback, this, std::placeholders::_1));
        
        // 订阅关节状态（用于雅可比计算）
        joint_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10,
            std::bind(&WBCNodeSimple::jointCallback, this, std::placeholders::_1));
        
        // 发布关节力矩命令
        torque_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/joint_group_effort_controller/commands", 10);
        
        RCLCPP_INFO(this->get_logger(), "Simple WBC Node initialized");
        RCLCPP_INFO(this->get_logger(), "  Subscribing to: /dog2/mpc/foot_forces");
        RCLCPP_INFO(this->get_logger(), "  Publishing to: /joint_group_effort_controller/commands");
    }

private:
    void footForceCallback(const std_msgs::msg::Float64MultiArray::SharedPtr msg) {
        if (msg->data.size() != 12) {
            RCLCPP_ERROR(this->get_logger(), "Expected 12 foot forces, got %zu", msg->data.size());
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
        
        // 简化的力矩分配
        // 假设：τ = J^T * f
        // 这里使用简化的雅可比（常数，基于标称姿态）
        Eigen::VectorXd joint_torques = computeJointTorques(foot_forces);
        
        // 发布关节力矩
        auto torque_msg = std_msgs::msg::Float64MultiArray();
        torque_msg.data.resize(joint_torques.size());
        for (int i = 0; i < joint_torques.size(); ++i) {
            torque_msg.data[i] = joint_torques(i);
        }
        torque_pub_->publish(torque_msg);
        
        // 统计
        if (++control_count_ % 20 == 0) {
            double total_fz = foot_forces(2) + foot_forces(5) + foot_forces(8) + foot_forces(11);
            RCLCPP_INFO(this->get_logger(),
                       "WBC: total_fz=%.1fN, torque_norm=%.2f",
                       total_fz, joint_torques.norm());
        }
    }
    
    void jointCallback(const sensor_msgs::msg::JointState::SharedPtr msg) {
        // 存储当前关节状态（用于雅可比计算）
        current_joint_positions_.clear();
        current_joint_positions_ = msg->position;
        joint_received_ = true;
    }
    
    Eigen::VectorXd computeJointTorques(const Eigen::VectorXd& foot_forces) {
        // 简化的力矩分配
        // Dog2有：4个滑动副 + 12个旋转关节 = 16个关节
        // 这里只计算12个旋转关节的力矩
        
        Eigen::VectorXd joint_torques = Eigen::VectorXd::Zero(12);
        
        // 对每条腿（3个关节）
        for (int leg = 0; leg < 4; ++leg) {
            Eigen::Vector3d f_leg = foot_forces.segment<3>(leg * 3);
            
            // 简化的雅可比转置（基于标称腿长）
            // 这是一个粗略的近似，实际应该根据当前关节角度计算
            double l1 = 0.2;  // 大腿长度
            double l2 = 0.2;  // 小腿长度
            
            // 简化映射：τ ≈ J^T * f
            // 髋关节（roll）
            joint_torques(leg * 3 + 0) = -f_leg(1) * (l1 + l2);
            
            // 髋关节（pitch）
            joint_torques(leg * 3 + 1) = f_leg(2) * l1 + f_leg(0) * (l1 + l2);
            
            // 膝关节
            joint_torques(leg * 3 + 2) = f_leg(2) * l2 + f_leg(0) * l2;
        }
        
        // 力矩限制
        double max_torque = 50.0;  // Nm
        for (int i = 0; i < joint_torques.size(); ++i) {
            if (joint_torques(i) > max_torque) joint_torques(i) = max_torque;
            if (joint_torques(i) < -max_torque) joint_torques(i) = -max_torque;
        }
        
        return joint_torques;
    }
    
    rclcpp::Subscription<std_msgs::msg::Float64MultiArray>::SharedPtr foot_force_sub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr torque_pub_;
    
    std::vector<double> current_joint_positions_;
    bool joint_received_ = false;
    int control_count_ = 0;
};

} // namespace dog2_wbc

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<dog2_wbc::WBCNodeSimple>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
