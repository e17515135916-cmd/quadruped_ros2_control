#!/usr/bin/env python3
"""调试 HAA 运动学问题"""

import numpy as np
import sys
sys.path.insert(0, 'src/dog2_kinematics')

from dog2_kinematics.leg_ik_4dof import create_dog2_leg_geometry, LegIK4DOF

# 创建腿部几何参数
geometry = create_dog2_leg_geometry(1)
solver = LegIK4DOF(geometry)

# 测试简单的情况：haa=0, hfe=0, kfe=0
print("=" * 60)
print("测试 1: 所有关节角度为 0")
print("=" * 60)
prismatic = 0.0
haa = 0.0
hfe = 0.0
kfe = 0.0

foot_pos_fk = solver.forward_kinematics(prismatic, haa, hfe, kfe)
print(f"FK 结果: {foot_pos_fk}")

# 现在用 IK 求解
solution = solver.solve(foot_pos_fk, prismatic)
print(f"IK 解: prismatic={solution.prismatic:.4f}, haa={solution.haa:.4f}, hfe={solution.hfe:.4f}, kfe={solution.kfe:.4f}")
print(f"IK 有效: {solution.valid}")
if not solution.valid:
    print(f"错误信息: {solution.error_msg}")

# 用 IK 的结果再做 FK
foot_pos_fk2 = solver.forward_kinematics(solution.prismatic, solution.haa, solution.hfe, solution.kfe)
print(f"FK 结果（用 IK 的角度）: {foot_pos_fk2}")
print(f"误差: {np.linalg.norm(foot_pos_fk - foot_pos_fk2) * 1000:.2f} mm")

print("\n" + "=" * 60)
print("测试 2: haa=0.1, hfe=0, kfe=0")
print("=" * 60)
haa = 0.1
foot_pos_fk = solver.forward_kinematics(prismatic, haa, hfe, kfe)
print(f"FK 结果: {foot_pos_fk}")

solution = solver.solve(foot_pos_fk, prismatic)
print(f"IK 解: prismatic={solution.prismatic:.4f}, haa={solution.haa:.4f}, hfe={solution.hfe:.4f}, kfe={solution.kfe:.4f}")
print(f"IK 有效: {solution.valid}")

foot_pos_fk2 = solver.forward_kinematics(solution.prismatic, solution.haa, solution.hfe, solution.kfe)
print(f"FK 结果（用 IK 的角度）: {foot_pos_fk2}")
print(f"误差: {np.linalg.norm(foot_pos_fk - foot_pos_fk2) * 1000:.2f} mm")

print("\n" + "=" * 60)
print("测试 3: haa=0, hfe=1.0, kfe=-1.0")
print("=" * 60)
haa = 0.0
hfe = 1.0
kfe = -1.0
foot_pos_fk = solver.forward_kinematics(prismatic, haa, hfe, kfe)
print(f"FK 结果: {foot_pos_fk}")

solution = solver.solve(foot_pos_fk, prismatic)
print(f"IK 解: prismatic={solution.prismatic:.4f}, haa={solution.haa:.4f}, hfe={solution.hfe:.4f}, kfe={solution.kfe:.4f}")
print(f"IK 有效: {solution.valid}")

foot_pos_fk2 = solver.forward_kinematics(solution.prismatic, solution.haa, solution.hfe, solution.kfe)
print(f"FK 结果（用 IK 的角度）: {foot_pos_fk2}")
print(f"误差: {np.linalg.norm(foot_pos_fk - foot_pos_fk2) * 1000:.2f} mm")
