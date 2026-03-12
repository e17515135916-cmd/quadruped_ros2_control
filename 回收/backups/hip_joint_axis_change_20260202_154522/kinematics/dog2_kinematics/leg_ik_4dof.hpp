/**
 * @file leg_ik_4dof.hpp
 * @brief Dog2 四自由度腿部逆运动学求解器
 * 
 * 关节链结构（每条腿）：
 * 1. j${leg_num}   - 移动关节（prismatic）- 直线导轨，沿 X 轴
 * 2. j${leg_num}1  - 旋转关节（revolute） - 髋关节侧摆（HAA）
 * 3. j${leg_num}11 - 旋转关节（revolute） - 髋关节俯仰（HFE）
 * 4. j${leg_num}111- 旋转关节（revolute） - 膝关节（KFE）
 * 
 * 求解策略：
 * - 直线导轨位置作为输入参数（参数化策略）
 * - 基于给定的导轨位置，求解剩余 3 个旋转关节的解析解
 * 
 * @author Dog2 Kinematics Team
 * @date 2026-01-31
 */

#ifndef DOG2_KINEMATICS_LEG_IK_4DOF_HPP
#define DOG2_KINEMATICS_LEG_IK_4DOF_HPP

#include <Eigen/Dense>
#include <cmath>
#include <optional>

namespace dog2_kinematics {

/**
 * @brief 腿部几何参数
 */
struct LegGeometry {
    // 从基座到移动关节的偏移
    Eigen::Vector3d base_to_prismatic_offset;
    
    // 从移动关节到髋关节侧摆轴的偏移
    Eigen::Vector3d prismatic_to_haa_offset;
    
    // 从髋关节侧摆轴到髋关节俯仰轴的偏移
    Eigen::Vector3d haa_to_hfe_offset;
    
    // 大腿长度（髋关节俯仰轴到膝关节）
    double thigh_length;
    
    // 小腿长度（膝关节到足端）
    double shin_length;
    
    // 关节限位
    double prismatic_lower;
    double prismatic_upper;
    double haa_lower;
    double haa_upper;
    double hfe_lower;
    double hfe_upper;
    double kfe_lower;
    double kfe_upper;
};

/**
 * @brief 逆运动学求解结果
 */
struct IKSolution {
    double prismatic;  // 移动关节位置 [m]
    double haa;        // 髋关节侧摆角度 [rad]
    double hfe;        // 髋关节俯仰角度 [rad]
    double kfe;        // 膝关节角度 [rad]
    bool valid;        // 解是否有效
    std::string error_msg;  // 错误信息
};

/**
 * @brief Dog2 四自由度腿部逆运动学求解器
 */
class LegIK4DOF {
public:
    /**
     * @brief 构造函数
     * @param geometry 腿部几何参数
     */
    explicit LegIK4DOF(const LegGeometry& geometry);
    
    /**
     * @brief 求解逆运动学（给定移动关节位置）
     * 
     * @param foot_position_base 足端在基座坐标系中的目标位置 [x, y, z]
     * @param prismatic_position 移动关节的位置（参数化输入）[m]
     * @return IKSolution 逆运动学解
     * 
     * 求解流程：
     * 1. 使用给定的 prismatic_position 计算移动关节的位置
     * 2. 将足端位置转换到移动关节坐标系
     * 3. 求解 HAA（髋关节侧摆）
     * 4. 将问题投影到 HFE-KFE 平面
     * 5. 使用 2R 平面逆运动学求解 HFE 和 KFE
     */
    IKSolution solve(const Eigen::Vector3d& foot_position_base, 
                     double prismatic_position) const;
    
    /**
     * @brief 求解逆运动学（自动优化移动关节位置）
     * 
     * @param foot_position_base 足端在基座坐标系中的目标位置 [x, y, z]
     * @param prismatic_preference 移动关节的偏好位置（默认为中间位置）[m]
     * @return IKSolution 逆运动学解
     * 
     * 优化策略：
     * - 尝试使用 prismatic_preference
     * - 如果无解，在允许范围内搜索最优位置
     */
    IKSolution solveWithOptimization(const Eigen::Vector3d& foot_position_base,
                                     double prismatic_preference = 0.0) const;
    
    /**
     * @brief 正运动学（验证用）
     * 
     * @param prismatic 移动关节位置 [m]
     * @param haa 髋关节侧摆角度 [rad]
     * @param hfe 髋关节俯仰角度 [rad]
     * @param kfe 膝关节角度 [rad]
     * @return Eigen::Vector3d 足端在基座坐标系中的位置
     */
    Eigen::Vector3d forwardKinematics(double prismatic, double haa, 
                                      double hfe, double kfe) const;
    
    /**
     * @brief 获取腿部几何参数
     */
    const LegGeometry& getGeometry() const { return geometry_; }
    
private:
    LegGeometry geometry_;
    
    /**
     * @brief 求解 2R 平面逆运动学（HFE-KFE）
     * 
     * @param x 目标点 X 坐标（在 HFE 平面内）
     * @param y 目标点 Y 坐标（在 HFE 平面内）
     * @param l1 大腿长度
     * @param l2 小腿长度
     * @param hfe 输出：髋关节俯仰角度 [rad]
     * @param kfe 输出：膝关节角度 [rad]
     * @return bool 是否有解
     */
    bool solve2RPlaneIK(double x, double y, double l1, double l2,
                        double& hfe, double& kfe) const;
    
    /**
     * @brief 检查关节限位
     */
    bool checkJointLimits(double prismatic, double haa, 
                          double hfe, double kfe) const;
};

/**
 * @brief 创建 Dog2 腿部几何参数（基于 URDF）
 * 
 * @param leg_num 腿编号（1-4）
 * @return LegGeometry 腿部几何参数
 */
LegGeometry createDog2LegGeometry(int leg_num);

} // namespace dog2_kinematics

#endif // DOG2_KINEMATICS_LEG_IK_4DOF_HPP
