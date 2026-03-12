#pragma once

#include <Eigen/Dense>
#include <iostream>
#include <iomanip>
#include <string>

namespace dog2_mpc {
namespace test {

/**
 * @brief 测试配置结构
 * 
 * 统一测试配置参数，确保所有测试使用一致的物理参数
 */
struct TestConfig {
    double mass = 11.8;      // kg - 机器人质量
    double gravity = 9.81;   // m/s² - 重力加速度
    double dt = 0.1;         // s - 时间步长
    int horizon = 6;         // MPC时域长度
    
    // 权重矩阵 (16×16 for extended state)
    Eigen::MatrixXd Q = Eigen::MatrixXd::Identity(16, 16);
    Eigen::MatrixXd R = Eigen::MatrixXd::Identity(12, 12);
    
    /**
     * @brief 期望的悬停重力补偿力
     * @return 总重力补偿力 (N)
     */
    double expected_hover_force() const {
        return mass * gravity;  // 115.758 N
    }
    
    /**
     * @brief 期望的单腿垂直力
     * @return 单腿垂直力 (N)
     */
    double expected_leg_force() const {
        return expected_hover_force() / 4.0;  // 28.9395 N per leg
    }
    
    /**
     * @brief 初始化默认权重矩阵
     */
    void initializeWeights() {
        Q.diagonal() << 100, 100, 200,    // 位置权重 (z更高)
                        50, 50, 50,        // 姿态权重
                        10, 10, 10,        // 线速度权重
                        5, 5, 5,           // 角速度权重
                        20, 20, 20, 20;    // 滑动副权重
        
        R = Eigen::MatrixXd::Identity(12, 12) * 0.01;  // 控制权重
    }
};

/**
 * @brief 创建16维扩展状态向量
 * 
 * 辅助函数，简化16维状态向量的创建
 * 
 * @param position 位置 [x, y, z] (m)
 * @param orientation 姿态 [roll, pitch, yaw] (rad)
 * @param linear_velocity 线速度 [vx, vy, vz] (m/s)
 * @param angular_velocity 角速度 [wx, wy, wz] (rad/s)
 * @param sliding_positions 滑动副位置 [j1, j2, j3, j4] (m)
 * @return 16维状态向量
 */
inline Eigen::VectorXd create16DState(
    const Eigen::Vector3d& position,
    const Eigen::Vector3d& orientation,
    const Eigen::Vector3d& linear_velocity,
    const Eigen::Vector3d& angular_velocity,
    const Eigen::Vector4d& sliding_positions = Eigen::Vector4d::Zero()
) {
    Eigen::VectorXd x(16);
    x << position, orientation, linear_velocity, angular_velocity, sliding_positions;
    return x;
}

/**
 * @brief 重力补偿验证器
 * 
 * 验证MPC输出的足端力是否正确补偿重力
 */
struct GravityCompensationValidator {
    double mass;       // kg
    double gravity;    // m/s²
    double tolerance;  // 容差 (N)
    
    /**
     * @brief 构造函数
     * @param m 机器人质量 (kg)
     * @param g 重力加速度 (m/s²)
     * @param tol 验证容差 (N)
     */
    GravityCompensationValidator(double m = 11.8, double g = 9.81, double tol = 10.0)
        : mass(m), gravity(g), tolerance(tol) {}
    
    /**
     * @brief 验证控制输入的重力补偿
     * @param u_optimal MPC输出的控制输入 (12维)
     * @return true if 重力补偿正确, false otherwise
     */
    bool validate(const Eigen::VectorXd& u_optimal) {
        if (u_optimal.size() != 12) {
            std::cerr << "❌ 错误: 控制输入维度不正确 (期望12, 实际" 
                      << u_optimal.size() << ")" << std::endl;
            return false;
        }
        
        // 计算总垂直力
        double fz_total = 0.0;
        for (int i = 0; i < 4; ++i) {
            fz_total += u_optimal(i * 3 + 2);  // z分量
        }
        
        // 期望的重力补偿力
        double expected_force = mass * gravity;
        
        // 净垂直力（应该接近0）
        double net_force = fz_total - expected_force;
        
        // 输出诊断信息
        std::cout << "重力补偿验证:" << std::endl;
        std::cout << "  机器人重量: " << expected_force << " N" << std::endl;
        std::cout << "  总垂直力: " << fz_total << " N" << std::endl;
        std::cout << "  净垂直力: " << net_force << " N" << std::endl;
        std::cout << "  容差: ±" << tolerance << " N" << std::endl;
        
        bool valid = std::abs(net_force) < tolerance;
        std::cout << (valid ? "✅ 重力补偿正确" : "❌ 重力补偿错误") << std::endl;
        
        return valid;
    }
    
    /**
     * @brief 验证单腿垂直力
     * @param fz 单腿垂直力 (N)
     * @param leg_id 腿编号 (1-4)
     * @return true if 单腿力合理, false otherwise
     */
    bool validateLegForce(double fz, int leg_id) {
        double expected = mass * gravity / 4.0;  // 28.9395 N
        double error = std::abs(fz - expected);
        
        bool valid = error < tolerance / 4.0;  // 单腿容差为总容差的1/4
        
        if (!valid) {
            std::cout << "⚠️  腿" << leg_id << " 垂直力异常: " 
                      << fz << " N (期望: " << expected << " N)" << std::endl;
        }
        
        return valid;
    }
};

/**
 * @brief 测试输出格式化器
 * 
 * 统一测试输出格式，提供清晰的测试报告
 */
class TestReporter {
public:
    /**
     * @brief 打印测试头部
     * @param test_name 测试名称
     */
    void printHeader(const std::string& test_name) {
        std::cout << "\n" << std::string(60, '=') << std::endl;
        std::cout << "  " << test_name << std::endl;
        std::cout << std::string(60, '=') << std::endl;
    }
    
    /**
     * @brief 打印测试章节
     * @param section_name 章节名称
     */
    void printSection(const std::string& section_name) {
        std::cout << "\n--- " << section_name << " ---" << std::endl;
    }
    
    /**
     * @brief 打印成功消息
     * @param message 消息内容
     */
    void printSuccess(const std::string& message) {
        std::cout << "✅ " << message << std::endl;
    }
    
    /**
     * @brief 打印失败消息
     * @param message 消息内容
     */
    void printFailure(const std::string& message) {
        std::cout << "❌ " << message << std::endl;
    }
    
    /**
     * @brief 打印警告消息
     * @param message 消息内容
     */
    void printWarning(const std::string& message) {
        std::cout << "⚠️  " << message << std::endl;
    }
    
    /**
     * @brief 打印信息消息
     * @param message 消息内容
     */
    void printInfo(const std::string& message) {
        std::cout << "ℹ️  " << message << std::endl;
    }
    
    /**
     * @brief 打印测试总结
     * @param all_passed 是否全部通过
     * @param total_tests 总测试数
     * @param passed_tests 通过测试数
     */
    void printSummary(bool all_passed, int total_tests, int passed_tests) {
        std::cout << "\n" << std::string(60, '=') << std::endl;
        std::cout << "测试总结: " << passed_tests << "/" << total_tests << " 通过" << std::endl;
        if (all_passed) {
            std::cout << "✅ 所有测试通过！" << std::endl;
        } else {
            std::cout << "❌ 部分测试失败 (" << (total_tests - passed_tests) << " 个)" << std::endl;
        }
        std::cout << std::string(60, '=') << std::endl;
    }
    
    /**
     * @brief 打印键值对
     * @param key 键
     * @param value 值
     */
    template<typename T>
    void printKeyValue(const std::string& key, const T& value) {
        std::cout << "  " << key << ": " << value << std::endl;
    }
    
    /**
     * @brief 打印向量
     * @param name 向量名称
     * @param vec 向量
     * @param precision 精度
     */
    void printVector(const std::string& name, const Eigen::VectorXd& vec, int precision = 3) {
        std::cout << name << ": [";
        for (int i = 0; i < vec.size(); ++i) {
            std::cout << std::fixed << std::setprecision(precision) << vec(i);
            if (i < vec.size() - 1) std::cout << ", ";
        }
        std::cout << "]" << std::endl;
    }
};

/**
 * @brief 维度验证器
 * 
 * 验证状态向量和矩阵的维度是否正确
 */
struct DimensionValidator {
    /**
     * @brief 验证状态向量维度
     * @param x 状态向量
     * @param expected_dim 期望维度
     * @param name 向量名称
     * @return true if 维度正确, false otherwise
     */
    static bool validateState(const Eigen::VectorXd& x, int expected_dim, const std::string& name = "状态向量") {
        if (x.size() != expected_dim) {
            std::cerr << "❌ 错误: " << name << "维度不匹配" << std::endl;
            std::cerr << "   期望维度: " << expected_dim << std::endl;
            std::cerr << "   实际维度: " << x.size() << std::endl;
            return false;
        }
        return true;
    }
    
    /**
     * @brief 验证矩阵维度
     * @param M 矩阵
     * @param expected_rows 期望行数
     * @param expected_cols 期望列数
     * @param name 矩阵名称
     * @return true if 维度正确, false otherwise
     */
    static bool validateMatrix(const Eigen::MatrixXd& M, int expected_rows, int expected_cols, const std::string& name = "矩阵") {
        if (M.rows() != expected_rows || M.cols() != expected_cols) {
            std::cerr << "❌ 错误: " << name << "维度不匹配" << std::endl;
            std::cerr << "   期望维度: " << expected_rows << "×" << expected_cols << std::endl;
            std::cerr << "   实际维度: " << M.rows() << "×" << M.cols() << std::endl;
            return false;
        }
        return true;
    }
    
    /**
     * @brief 检查数值是否有效（无NaN或Inf）
     * @param x 向量
     * @param name 向量名称
     * @return true if 数值有效, false otherwise
     */
    static bool validateFinite(const Eigen::VectorXd& x, const std::string& name = "向量") {
        if (!x.allFinite()) {
            std::cerr << "❌ 错误: " << name << "包含NaN或Inf" << std::endl;
            std::cerr << "   值: " << x.transpose() << std::endl;
            return false;
        }
        return true;
    }
};

} // namespace test
} // namespace dog2_mpc
