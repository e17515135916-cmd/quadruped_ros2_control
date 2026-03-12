#!/usr/bin/env python3
"""调试 HAA 计算"""

import numpy as np
import sys
sys.path.insert(0, 'src/dog2_kinematics')

from dog2_kinematics.leg_ik_4dof import create_dog2_leg_geometry, LegIK4DOF

# 创建腿部几何参数
geometry = create_dog2_leg_geometry(1)
solver = LegIK4DOF(geometry)

# 测试 FK：haa=0
prismatic = 0.0
haa = 0.0
hfe = 0.0
kfe = 0.0

print("=" * 60)
print("正运动学分析（haa=0）")
print("=" * 60)

# 手动计算 FK
prismatic_pos = geometry.base_to_prismatic_offset.copy()
prismatic_pos[0] += prismatic
print(f"Prismatic 位置: {prismatic_pos}")

haa_pos = prismatic_pos + geometry.prismatic_to_haa_offset
print(f"HAA 位置: {haa_pos}")

# HFE 位置（考虑 HAA 旋转）
hfe_offset_rotated = np.array([
    geometry.haa_to_hfe_offset[0],
    geometry.haa_to_hfe_offset[1] * np.cos(haa) - 
    geometry.haa_to_hfe_offset[2] * np.sin(haa),
    geometry.haa_to_hfe_offset[1] * np.sin(haa) + 
    geometry.haa_to_hfe_offset[2] * np.cos(haa)
])
print(f"HFE 偏移（旋转后）: {hfe_offset_rotated}")

hfe_pos = haa_pos + hfe_offset_rotated
print(f"HFE 位置: {hfe_pos}")

# 在 HFE 平面内的位置
thigh_length = geometry.thigh_length
shin_length = geometry.shin_length
plane_x = thigh_length * np.cos(hfe) + shin_length * np.cos(hfe + kfe)
plane_y = thigh_length * np.sin(hfe) + shin_length * np.sin(hfe + kfe)
print(f"平面坐标: plane_x={plane_x:.4f}, plane_y={plane_y:.4f}")

# 转换回基座坐标系
foot_pos = np.array([
    hfe_pos[0] + plane_x,
    hfe_pos[1] + plane_y * np.cos(haa),
    hfe_pos[2] + plane_y * np.sin(haa)
])
print(f"足端位置: {foot_pos}")

print("\n" + "=" * 60)
print("逆运动学分析")
print("=" * 60)

# 现在用 IK 求解这个位置
haa_to_foot = foot_pos - haa_pos
print(f"HAA 到足端向量: {haa_to_foot}")
print(f"Y 分量: {haa_to_foot[1]:.4f}")
print(f"Z 分量: {haa_to_foot[2]:.4f}")

haa_calculated = np.arctan2(haa_to_foot[2], haa_to_foot[1])
print(f"计算的 HAA 角度: {haa_calculated:.4f} rad ({np.degrees(haa_calculated):.2f} deg)")
print(f"原始 HAA 角度: {haa:.4f} rad ({np.degrees(haa):.2f} deg)")

# 检查 HFE 位置计算
hfe_offset_rotated_ik = np.array([
    geometry.haa_to_hfe_offset[0],
    geometry.haa_to_hfe_offset[1] * np.cos(haa_calculated) - 
    geometry.haa_to_hfe_offset[2] * np.sin(haa_calculated),
    geometry.haa_to_hfe_offset[1] * np.sin(haa_calculated) + 
    geometry.haa_to_hfe_offset[2] * np.cos(haa_calculated)
])
hfe_pos_ik = haa_pos + hfe_offset_rotated_ik
print(f"\nHFE 位置（IK 计算）: {hfe_pos_ik}")
print(f"HFE 位置（FK）: {hfe_pos}")
print(f"HFE 位置误差: {np.linalg.norm(hfe_pos_ik - hfe_pos) * 1000:.2f} mm")

# 检查平面投影
hfe_to_foot = foot_pos - hfe_pos_ik
plane_x_ik = hfe_to_foot[0]
plane_y_ik = (hfe_to_foot[1] * np.cos(haa_calculated) + 
              hfe_to_foot[2] * np.sin(haa_calculated))
print(f"\n平面坐标（IK）: plane_x={plane_x_ik:.4f}, plane_y={plane_y_ik:.4f}")
print(f"平面坐标（FK）: plane_x={plane_x:.4f}, plane_y={plane_y:.4f}")
