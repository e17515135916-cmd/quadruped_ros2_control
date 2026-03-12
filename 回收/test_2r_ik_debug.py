#!/usr/bin/env python3
"""调试 2R 平面逆运动学"""

import numpy as np

# 测试数据
plane_x = 0.4995
plane_y = 0.0
l1 = 0.2000
l2 = 0.2995

print(f"目标平面坐标: x={plane_x:.6f}, y={plane_y:.6f}")
print(f"大腿长度: {l1:.6f}")
print(f"小腿长度: {l2:.6f}")
print(f"l1 + l2 = {l1 + l2:.6f}")

distance_sq = plane_x**2 + plane_y**2
distance = np.sqrt(distance_sq)
print(f"\n距离: {distance:.6f}")
print(f"距离平方: {distance_sq:.6f}")

print(f"\n检查工作空间:")
print(f"distance > l1 + l2: {distance} > {l1 + l2} = {distance > l1 + l2}")
print(f"distance < abs(l1 - l2): {distance} < {abs(l1 - l2)} = {distance < abs(l1 - l2)}")

if distance > l1 + l2 or distance < abs(l1 - l2):
    print("结果: 超出工作空间")
else:
    print("结果: 在工作空间内")
    
    # 计算 KFE
    cos_kfe = (l1**2 + l2**2 - distance_sq) / (2.0 * l1 * l2)
    print(f"\ncos(kfe) = {cos_kfe:.6f}")
    print(f"cos(kfe) 裁剪后 = {np.clip(cos_kfe, -1.0, 1.0):.6f}")
    
    kfe = -np.arccos(np.clip(cos_kfe, -1.0, 1.0))
    print(f"KFE = {kfe:.6f} rad ({np.degrees(kfe):.2f} deg)")
    
    # 计算 HFE
    alpha = np.arctan2(plane_y, plane_x)
    print(f"\nalpha = atan2({plane_y}, {plane_x}) = {alpha:.6f} rad ({np.degrees(alpha):.2f} deg)")
    
    beta_numerator = l1**2 + distance_sq - l2**2
    beta_denominator = 2.0 * l1 * distance
    print(f"beta 分子 = {beta_numerator:.6f}")
    print(f"beta 分母 = {beta_denominator:.6f}")
    print(f"beta cos = {beta_numerator / beta_denominator:.6f}")
    
    if abs(beta_numerator / beta_denominator) > 1.0:
        print("警告: beta cos 超出范围!")
    
    beta = np.arccos(np.clip(beta_numerator / beta_denominator, -1.0, 1.0))
    print(f"beta = {beta:.6f} rad ({np.degrees(beta):.2f} deg)")
    
    hfe = alpha - beta
    print(f"\nHFE = alpha - beta = {hfe:.6f} rad ({np.degrees(hfe):.2f} deg)")
    
    # 验证
    thigh_x = l1 * np.cos(hfe)
    thigh_y = l1 * np.sin(hfe)
    shin_x = l2 * np.cos(hfe + kfe)
    shin_y = l2 * np.sin(hfe + kfe)
    result_x = thigh_x + shin_x
    result_y = thigh_y + shin_y
    
    print(f"\n验证:")
    print(f"计算的平面坐标: x={result_x:.6f}, y={result_y:.6f}")
    print(f"误差: {np.sqrt((result_x - plane_x)**2 + (result_y - plane_y)**2) * 1000:.2f} mm")
