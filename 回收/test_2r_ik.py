#!/usr/bin/env python3
"""测试 2R 平面逆运动学"""

import numpy as np
import sys
sys.path.insert(0, 'src/dog2_kinematics')

from dog2_kinematics.leg_ik_4dof import create_dog2_leg_geometry, LegIK4DOF

# 创建腿部几何参数
geometry = create_dog2_leg_geometry(1)
solver = LegIK4DOF(geometry)

# 测试 2R IK
plane_x = 0.4995
plane_y = 0.0
l1 = geometry.thigh_length
l2 = geometry.shin_length

print(f"目标平面坐标: x={plane_x:.4f}, y={plane_y:.4f}")
print(f"大腿长度: {l1:.4f}")
print(f"小腿长度: {l2:.4f}")

success, hfe, kfe = solver._solve_2r_plane_ik(plane_x, plane_y, l1, l2)
print(f"\n2R IK 结果:")
print(f"成功: {success}")
print(f"HFE: {hfe:.4f} rad ({np.degrees(hfe):.2f} deg)")
print(f"KFE: {kfe:.4f} rad ({np.degrees(kfe):.2f} deg)")

# 验证：用这些角度计算平面坐标
thigh_x = l1 * np.cos(hfe)
thigh_y = l1 * np.sin(hfe)
shin_x = l2 * np.cos(hfe + kfe)
shin_y = l2 * np.sin(hfe + kfe)
result_x = thigh_x + shin_x
result_y = thigh_y + shin_y

print(f"\n验证:")
print(f"计算的平面坐标: x={result_x:.4f}, y={result_y:.4f}")
print(f"误差: {np.sqrt((result_x - plane_x)**2 + (result_y - plane_y)**2) * 1000:.2f} mm")

# 测试原始情况：hfe=0, kfe=0
print("\n" + "=" * 60)
print("测试原始情况：hfe=0, kfe=0")
print("=" * 60)
hfe_orig = 0.0
kfe_orig = 0.0
thigh_x = l1 * np.cos(hfe_orig)
thigh_y = l1 * np.sin(hfe_orig)
shin_x = l2 * np.cos(hfe_orig + kfe_orig)
shin_y = l2 * np.sin(hfe_orig + kfe_orig)
orig_x = thigh_x + shin_x
orig_y = thigh_y + shin_y
print(f"原始平面坐标: x={orig_x:.4f}, y={orig_y:.4f}")

# 用 2R IK 求解这个位置
success, hfe_calc, kfe_calc = solver._solve_2r_plane_ik(orig_x, orig_y, l1, l2)
print(f"\n2R IK 结果:")
print(f"成功: {success}")
print(f"HFE: {hfe_calc:.4f} rad ({np.degrees(hfe_calc):.2f} deg)")
print(f"KFE: {kfe_calc:.4f} rad ({np.degrees(kfe_calc):.2f} deg)")
print(f"原始 HFE: {hfe_orig:.4f} rad")
print(f"原始 KFE: {kfe_orig:.4f} rad")
