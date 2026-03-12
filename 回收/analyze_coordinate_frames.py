#!/usr/bin/env python3
"""
分析 HAA 关节的坐标系变换
找出为什么 HAA 仍然在同一平面旋转
"""

import numpy as np
import subprocess
import xml.etree.ElementTree as ET

def rpy_to_rotation_matrix(roll, pitch, yaw):
    """将 RPY (roll, pitch, yaw) 转换为旋转矩阵"""
    # Roll (绕 x 轴)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    # Pitch (绕 y 轴)
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    # Yaw (绕 z 轴)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # 组合旋转: R = Rz * Ry * Rx
    return Rz @ Ry @ Rx

def analyze_joint_axis(joint_name, parent_rpy, joint_rpy, axis):
    """分析关节轴在世界坐标系中的方向"""
    print(f"\n{'='*60}")
    print(f"分析 {joint_name}")
    print(f"{'='*60}")
    
    # 父连杆的旋转
    print(f"\n1. 父连杆 (prismatic joint) RPY: {parent_rpy}")
    R_parent = rpy_to_rotation_matrix(*parent_rpy)
    print(f"   旋转矩阵:\n{R_parent}")
    
    # 关节的旋转
    print(f"\n2. 关节 origin RPY: {joint_rpy}")
    R_joint = rpy_to_rotation_matrix(*joint_rpy)
    print(f"   旋转矩阵:\n{R_joint}")
    
    # 组合旋转
    R_total = R_parent @ R_joint
    print(f"\n3. 组合旋转矩阵 (父连杆 * 关节):\n{R_total}")
    
    # 关节轴在局部坐标系中
    axis_local = np.array(axis)
    print(f"\n4. 关节轴 (局部坐标系): {axis_local}")
    
    # 关节轴在世界坐标系中
    axis_world = R_total @ axis_local
    print(f"\n5. 关节轴 (世界坐标系): {axis_world}")
    print(f"   归一化: {axis_world / np.linalg.norm(axis_world)}")
    
    return axis_world

def main():
    print("="*60)
    print("HAA 关节坐标系变换分析")
    print("="*60)
    
    # Leg 1 (lf) 的配置
    print("\n\n" + "="*60)
    print("Leg 1 (前左腿) 配置")
    print("="*60)
    
    # Prismatic joint: origin rpy="1.5708 0 0"
    prismatic_rpy = [1.5708, 0, 0]  # 90° 绕 x 轴
    
    # HAA joint: origin rpy="-1.5708 0 0", axis xyz="0 0 1"
    haa_rpy = [-1.5708, 0, 0]  # -90° 绕 x 轴
    haa_axis = [0, 0, 1]  # z 轴
    
    haa_axis_world = analyze_joint_axis(
        "lf_haa_joint",
        prismatic_rpy,
        haa_rpy,
        haa_axis
    )
    
    # HFE joint: origin rpy="0 1.5708 0", axis xyz="-1 0 0"
    print("\n\n" + "="*60)
    print("分析 lf_hfe_joint (相对于 HAA)")
    print("="*60)
    
    hfe_rpy = [0, 1.5708, 0]  # 90° 绕 y 轴
    hfe_axis = [-1, 0, 0]  # -x 轴
    
    # HFE 的父连杆是 hip_link，它已经经过了 prismatic 和 HAA 的旋转
    R_to_hip = rpy_to_rotation_matrix(*prismatic_rpy) @ rpy_to_rotation_matrix(*haa_rpy)
    R_hfe = rpy_to_rotation_matrix(*hfe_rpy)
    R_total_hfe = R_to_hip @ R_hfe
    
    hfe_axis_local = np.array(hfe_axis)
    hfe_axis_world = R_total_hfe @ hfe_axis_local
    
    print(f"HFE 关节轴 (世界坐标系): {hfe_axis_world}")
    print(f"归一化: {hfe_axis_world / np.linalg.norm(hfe_axis_world)}")
    
    # 检查 HAA 和 HFE 的轴是否垂直
    print("\n\n" + "="*60)
    print("关节轴关系分析")
    print("="*60)
    
    haa_normalized = haa_axis_world / np.linalg.norm(haa_axis_world)
    hfe_normalized = hfe_axis_world / np.linalg.norm(hfe_axis_world)
    
    dot_product = np.dot(haa_normalized, hfe_normalized)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
    
    print(f"\nHAA 轴 (归一化): {haa_normalized}")
    print(f"HFE 轴 (归一化): {hfe_normalized}")
    print(f"点积: {dot_product:.6f}")
    print(f"夹角: {np.degrees(angle):.2f}°")
    
    if abs(dot_product) < 0.1:
        print("\n✅ HAA 和 HFE 的轴接近垂直 (符合 CHAMP 标准)")
    else:
        print("\n❌ HAA 和 HFE 的轴不垂直 (不符合 CHAMP 标准)")
        print("   HAA 应该垂直于 HFE/KFE 平面")
    
    # 分析世界坐标系中的方向
    print("\n\n" + "="*60)
    print("世界坐标系方向分析")
    print("="*60)
    
    print(f"\nHAA 轴在世界坐标系中的方向:")
    print(f"  X 分量: {haa_normalized[0]:.4f}")
    print(f"  Y 分量: {haa_normalized[1]:.4f}")
    print(f"  Z 分量: {haa_normalized[2]:.4f}")
    
    if abs(haa_normalized[2]) > 0.9:
        print("  → 主要沿 Z 轴 (垂直方向) ✅")
    elif abs(haa_normalized[0]) > 0.9:
        print("  → 主要沿 X 轴 (前后方向) ❌")
    elif abs(haa_normalized[1]) > 0.9:
        print("  → 主要沿 Y 轴 (左右方向) ❌")
    else:
        print("  → 混合方向")
    
    print(f"\nHFE 轴在世界坐标系中的方向:")
    print(f"  X 分量: {hfe_normalized[0]:.4f}")
    print(f"  Y 分量: {hfe_normalized[1]:.4f}")
    print(f"  Z 分量: {hfe_normalized[2]:.4f}")
    
    if abs(hfe_normalized[0]) > 0.9:
        print("  → 主要沿 X 轴 (前后方向) ✅")
    elif abs(hfe_normalized[1]) > 0.9:
        print("  → 主要沿 Y 轴 (左右方向) ❌")
    elif abs(hfe_normalized[2]) > 0.9:
        print("  → 主要沿 Z 轴 (垂直方向) ❌")
    else:
        print("  → 混合方向")
    
    print("\n" + "="*60)
    print("结论")
    print("="*60)
    print("\nCHAMP 标准要求:")
    print("  - HAA 轴应该沿 Z 轴 (垂直方向)")
    print("  - HFE 轴应该沿 X 轴 (前后方向)")
    print("  - HAA 和 HFE 应该垂直")
    print("\n当前配置:")
    print(f"  - HAA 轴: {haa_normalized}")
    print(f"  - HFE 轴: {hfe_normalized}")
    print(f"  - 夹角: {np.degrees(angle):.2f}°")

if __name__ == "__main__":
    main()
