#!/usr/bin/env python3
"""测试新的 HAA 轴配置"""

import numpy as np

def rpy_to_rotation_matrix(roll, pitch, yaw):
    """将 RPY 转换为旋转矩阵"""
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    return Rz @ Ry @ Rx

print("="*60)
print("测试新的 HAA 轴配置")
print("="*60)

# Prismatic joint: rpy="1.5708 0 0"
R_prismatic = rpy_to_rotation_matrix(1.5708, 0, 0)
print("\nPrismatic joint 旋转矩阵:")
print(R_prismatic)

# HAA 轴: "0 -1 0" (-y 轴)
haa_axis_local = np.array([0, -1, 0])
print(f"\nHAA 轴 (局部坐标系): {haa_axis_local}")

# HAA 轴在世界坐标系中
haa_axis_world = R_prismatic @ haa_axis_local
print(f"HAA 轴 (世界坐标系): {haa_axis_world}")
print(f"归一化: {haa_axis_world / np.linalg.norm(haa_axis_world)}")

if abs(haa_axis_world[2]) > 0.9:
    print("\n✅ HAA 轴指向 Z 轴（垂直方向）")
else:
    print("\n❌ HAA 轴不指向 Z 轴")

# 测试 HFE
print("\n" + "="*60)
print("测试 HFE 轴")
print("="*60)

# HFE: rpy="0 1.5708 0", axis="-1 0 0"
R_hfe = rpy_to_rotation_matrix(0, 1.5708, 0)
R_total_hfe = R_prismatic @ R_hfe

hfe_axis_local = np.array([-1, 0, 0])
hfe_axis_world = R_total_hfe @ hfe_axis_local

print(f"HFE 轴 (世界坐标系): {hfe_axis_world}")
print(f"归一化: {hfe_axis_world / np.linalg.norm(hfe_axis_world)}")

# 检查垂直性
haa_norm = haa_axis_world / np.linalg.norm(haa_axis_world)
hfe_norm = hfe_axis_world / np.linalg.norm(hfe_axis_world)
dot = np.dot(haa_norm, hfe_norm)
angle = np.degrees(np.arccos(np.clip(dot, -1, 1)))

print(f"\n夹角: {angle:.2f}°")
if abs(dot) < 0.1:
    print("✅ HAA 和 HFE 垂直")
else:
    print("❌ HAA 和 HFE 不垂直")
