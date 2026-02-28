/**
 * @file leg_ik_4dof.cpp
 * @brief Dog2 四自由度腿部逆运动学求解器实现
 */

#include "dog2_kinematics/leg_ik_4dof.hpp"
#include <iostream>
#include <limits>

namespace dog2_kinematics {

LegIK4DOF::LegIK4DOF(const LegGeometry& geometry)
    : geometry_(geometry) {}

IKSolution LegIK4DOF::solve(const Eigen::Vector3d& foot_position_base,
                             double prismatic_position) const {
    IKSolution solution;
    solution.prismatic = prismatic_position;
    solution.valid = false;
    
    // 步骤 1: 计算移动关节在基座坐标系中的位置
    // 移动关节沿 X 轴移动，从 base_to_prismatic_offset 开始
    Eigen::Vector3d prismatic_pos = geometry_.base_to_prismatic_offset;
    prismatic_pos.x() += prismatic_position;  // 沿 -X 方向移动（根据 URDF axis="-1 0 0"）
    
    // 步骤 2: 计算髋关节侧摆轴（HAA）在基座坐标系中的位置
    Eigen::Vector3d haa_pos = prismatic_pos + geometry_.prismatic_to_haa_offset;
    
    // 步骤 3: 计算从 HAA 到足端的向量
    Eigen::Vector3d haa_to_foot = foot_position_base - haa_pos;
    
    // 步骤 4: 求解 HAA（髋关节侧摆角度）
    // 注意：虽然 URDF 中 axis="1 0 0"，但由于 rpy="0 0 1.5708"（Z 轴旋转 90 度），
    // 实际上关节在父坐标系中是绕 Y 轴旋转的
    // HAA 控制腿在 X-Z 平面的侧向摆动
    double haa_distance_xz = std::sqrt(haa_to_foot.x() * haa_to_foot.x() + 
                                       haa_to_foot.z() * haa_to_foot.z());
    
    if (haa_distance_xz < 1e-6) {
        solution.error_msg = "足端位置太接近 HAA 轴";
        return solution;
    }
    
    // HAA 角度（绕 Y 轴旋转，从 X 轴到足端在 X-Z 平面的投影）
    // 对于 Y 轴旋转：正角度使 X 轴向 Z 轴旋转
    solution.haa = std::atan2(haa_to_foot.z(), haa_to_foot.x());
    
    // 步骤 5: 计算髋关节俯仰轴（HFE）在基座坐标系中的位置
    // HFE 相对于 HAA 有一个偏移
    // 对于 Y 轴旋转，旋转矩阵为：
    // Ry(θ) = [ cos(θ)  0  sin(θ)]
    //         [   0     1    0   ]
    //         [-sin(θ)  0  cos(θ)]
    Eigen::Vector3d hfe_offset_rotated;
    hfe_offset_rotated.x() = geometry_.haa_to_hfe_offset.x() * std::cos(solution.haa) + 
                             geometry_.haa_to_hfe_offset.z() * std::sin(solution.haa);
    hfe_offset_rotated.y() = geometry_.haa_to_hfe_offset.y();
    hfe_offset_rotated.z() = -geometry_.haa_to_hfe_offset.x() * std::sin(solution.haa) + 
                             geometry_.haa_to_hfe_offset.z() * std::cos(solution.haa);
    
    Eigen::Vector3d hfe_pos = haa_pos + hfe_offset_rotated;
    
    // 步骤 6: 将问题投影到 HFE-KFE 平面
    // 在这个平面内，我们有一个 2R 机械臂问题
    Eigen::Vector3d hfe_to_foot = foot_position_base - hfe_pos;
    
    // 计算在 HFE 平面内的坐标
    // 对于 Y 轴旋转，平面在旋转后的 X-Y 局部坐标系中
    double plane_x = hfe_to_foot.x() * std::cos(solution.haa) - 
                     hfe_to_foot.z() * std::sin(solution.haa);
    double plane_y = hfe_to_foot.y();
    
    // 步骤 7: 求解 2R 平面逆运动学
    if (!solve2RPlaneIK(plane_x, plane_y, 
                        geometry_.thigh_length, geometry_.shin_length,
                        solution.hfe, solution.kfe)) {
        solution.error_msg = "2R 平面逆运动学无解（目标点超出工作空间）";
        return solution;
    }
    
    // 步骤 8: 检查关节限位
    if (!checkJointLimits(solution.prismatic, solution.haa, 
                          solution.hfe, solution.kfe)) {
        solution.error_msg = "关节超出限位";
        return solution;
    }
    
    solution.valid = true;
    return solution;
}

IKSolution LegIK4DOF::solveWithOptimization(const Eigen::Vector3d& foot_position_base,
                                             double prismatic_preference) const {
    // 首先尝试使用偏好位置
    IKSolution solution = solve(foot_position_base, prismatic_preference);
    if (solution.valid) {
        return solution;
    }
    
    // 如果偏好位置无解，搜索最优位置
    const int num_samples = 20;
    double best_error = std::numeric_limits<double>::max();
    IKSolution best_solution;
    best_solution.valid = false;
    
    for (int i = 0; i < num_samples; ++i) {
        double prismatic = geometry_.prismatic_lower + 
                          (geometry_.prismatic_upper - geometry_.prismatic_lower) * 
                          i / (num_samples - 1);
        
        IKSolution candidate = solve(foot_position_base, prismatic);
        if (candidate.valid) {
            // 计算与偏好位置的距离
            double error = std::abs(prismatic - prismatic_preference);
            if (error < best_error) {
                best_error = error;
                best_solution = candidate;
            }
        }
    }
    
    if (!best_solution.valid) {
        best_solution.error_msg = "在整个移动关节范围内都无解";
    }
    
    return best_solution;
}

Eigen::Vector3d LegIK4DOF::forwardKinematics(double prismatic, double haa,
                                              double hfe, double kfe) const {
    // 移动关节位置
    Eigen::Vector3d prismatic_pos = geometry_.base_to_prismatic_offset;
    prismatic_pos.x() += prismatic;
    
    // HAA 位置
    Eigen::Vector3d haa_pos = prismatic_pos + geometry_.prismatic_to_haa_offset;
    
    // HFE 位置（考虑 HAA 绕 Y 轴旋转）
    // 对于 Y 轴旋转，旋转矩阵为：
    // Ry(θ) = [ cos(θ)  0  sin(θ)]
    //         [   0     1    0   ]
    //         [-sin(θ)  0  cos(θ)]
    Eigen::Vector3d hfe_offset_rotated;
    hfe_offset_rotated.x() = geometry_.haa_to_hfe_offset.x() * std::cos(haa) + 
                             geometry_.haa_to_hfe_offset.z() * std::sin(haa);
    hfe_offset_rotated.y() = geometry_.haa_to_hfe_offset.y();
    hfe_offset_rotated.z() = -geometry_.haa_to_hfe_offset.x() * std::sin(haa) + 
                             geometry_.haa_to_hfe_offset.z() * std::cos(haa);
    
    Eigen::Vector3d hfe_pos = haa_pos + hfe_offset_rotated;
    
    // 大腿末端位置（膝关节）
    double thigh_x = geometry_.thigh_length * std::cos(hfe);
    double thigh_y = geometry_.thigh_length * std::sin(hfe);
    
    // 小腿末端位置（足端）
    double shin_x = geometry_.shin_length * std::cos(hfe + kfe);
    double shin_y = geometry_.shin_length * std::sin(hfe + kfe);
    
    // 在 HFE 平面内的位置
    double plane_x = thigh_x + shin_x;
    double plane_y = thigh_y + shin_y;
    
    // 转换回基座坐标系（考虑 HAA 绕 Y 轴旋转）
    // plane_x 在 X-Z 平面内，需要通过 Y 轴旋转变换
    Eigen::Vector3d foot_pos;
    foot_pos.x() = hfe_pos.x() + plane_x * std::cos(haa);
    foot_pos.y() = hfe_pos.y() + plane_y;
    foot_pos.z() = hfe_pos.z() + plane_x * std::sin(haa);
    
    return foot_pos;
}

bool LegIK4DOF::solve2RPlaneIK(double x, double y, double l1, double l2,
                                double& hfe, double& kfe) const {
    // 2R 平面逆运动学（肘向下配置）
    // l1: 大腿长度, l2: 小腿长度
    // (x, y): 目标点在 HFE 平面内的坐标
    
    double distance_sq = x * x + y * y;
    double distance = std::sqrt(distance_sq);
    
    // 检查是否在工作空间内
    if (distance > l1 + l2 || distance < std::abs(l1 - l2)) {
        return false;
    }
    
    // 使用余弦定理求解膝关节角度
    double cos_kfe = (l1 * l1 + l2 * l2 - distance_sq) / (2.0 * l1 * l2);
    
    // 数值稳定性检查
    if (cos_kfe > 1.0) cos_kfe = 1.0;
    if (cos_kfe < -1.0) cos_kfe = -1.0;
    
    // 膝关节角度（肘向下配置，负角度）
    kfe = -std::acos(cos_kfe);
    
    // 求解髋关节俯仰角度
    double alpha = std::atan2(y, x);
    double beta = std::acos((l1 * l1 + distance_sq - l2 * l2) / (2.0 * l1 * distance));
    
    hfe = alpha - beta;
    
    return true;
}

bool LegIK4DOF::checkJointLimits(double prismatic, double haa,
                                  double hfe, double kfe) const {
    if (prismatic < geometry_.prismatic_lower || prismatic > geometry_.prismatic_upper) {
        return false;
    }
    if (haa < geometry_.haa_lower || haa > geometry_.haa_upper) {
        return false;
    }
    if (hfe < geometry_.hfe_lower || hfe > geometry_.hfe_upper) {
        return false;
    }
    if (kfe < geometry_.kfe_lower || kfe > geometry_.kfe_upper) {
        return false;
    }
    return true;
}

LegGeometry createDog2LegGeometry(int leg_num) {
    LegGeometry geometry;
    
    // 基于 URDF 的几何参数
    // 这些值需要根据实际 URDF 测量
    
    // 从基座到移动关节的偏移（根据 URDF origin）
    if (leg_num == 1) {
        geometry.base_to_prismatic_offset = Eigen::Vector3d(1.1026, -0.80953, 0.2649);
    } else if (leg_num == 2) {
        geometry.base_to_prismatic_offset = Eigen::Vector3d(1.1026, 0.80953, 0.2649);
    } else if (leg_num == 3) {
        geometry.base_to_prismatic_offset = Eigen::Vector3d(-1.1026, -0.80953, 0.2649);
    } else if (leg_num == 4) {
        geometry.base_to_prismatic_offset = Eigen::Vector3d(-1.1026, 0.80953, 0.2649);
    }
    
    // 从移动关节到 HAA 的偏移（根据 URDF hip_joint_xyz）
    geometry.prismatic_to_haa_offset = Eigen::Vector3d(-0.016, 0.0199, 0.055);
    
    // 从 HAA 到 HFE 的偏移（根据 URDF knee_joint_xyz）
    geometry.haa_to_hfe_offset = Eigen::Vector3d(-0.0233, -0.055, 0.0274);
    
    // 大腿长度（根据 URDF j${leg_num}111 origin）
    geometry.thigh_length = std::sqrt(0.15201 * 0.15201 + 0.12997 * 0.12997);
    
    // 小腿长度（根据 URDF j${leg_num}1111 origin）
    geometry.shin_length = 0.299478;
    
    // 关节限位（根据 URDF）
    geometry.prismatic_lower = -0.1;  // 需要根据实际 URDF 调整
    geometry.prismatic_upper = 0.1;   // 需要根据实际 URDF 调整
    geometry.haa_lower = -2.618;      // ±150°
    geometry.haa_upper = 2.618;
    geometry.hfe_lower = -2.8;        // ±160°
    geometry.hfe_upper = 2.8;
    geometry.kfe_lower = -2.8;
    geometry.kfe_upper = 0.0;         // 根据 URDF，膝关节只能向一个方向弯曲
    
    return geometry;
}

} // namespace dog2_kinematics
