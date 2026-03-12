#!/usr/bin/env python3
"""
Dog2 四自由度逆运动学测试脚本

测试内容：
1. 正运动学验证
2. 逆运动学求解
3. 往返测试（FK -> IK -> FK）
4. 工作空间测试
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/dog2_kinematics'))

from dog2_kinematics.leg_ik_4dof import LegIK4DOF, create_dog2_leg_geometry, IKSolution
import numpy as np


def test_forward_kinematics():
    """测试正运动学"""
    print("=" * 60)
    print("测试 1: 正运动学")
    print("=" * 60)
    
    # 创建腿 1 的几何参数
    geometry = create_dog2_leg_geometry(1)
    ik_solver = LegIK4DOF(geometry)
    
    # 测试站立姿态
    prismatic = 0.0
    haa = 0.0
    hfe = 0.4
    kfe = -1.0
    
    foot_pos = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
    
    print(f"\n输入关节角度:")
    print(f"  移动关节: {prismatic:.4f} m")
    print(f"  HAA (侧摆): {haa:.4f} rad ({np.degrees(haa):.2f}°)")
    print(f"  HFE (俯仰): {hfe:.4f} rad ({np.degrees(hfe):.2f}°)")
    print(f"  KFE (膝关节): {kfe:.4f} rad ({np.degrees(kfe):.2f}°)")
    print(f"\n足端位置 (基座坐标系):")
    print(f"  X: {foot_pos[0]:.4f} m")
    print(f"  Y: {foot_pos[1]:.4f} m")
    print(f"  Z: {foot_pos[2]:.4f} m")
    
    return foot_pos


def test_inverse_kinematics(target_foot_pos, prismatic_pos=0.0):
    """测试逆运动学"""
    print("\n" + "=" * 60)
    print("测试 2: 逆运动学")
    print("=" * 60)
    
    # 创建腿 1 的几何参数
    geometry = create_dog2_leg_geometry(1)
    ik_solver = LegIK4DOF(geometry)
    
    print(f"\n目标足端位置:")
    print(f"  X: {target_foot_pos[0]:.4f} m")
    print(f"  Y: {target_foot_pos[1]:.4f} m")
    print(f"  Z: {target_foot_pos[2]:.4f} m")
    print(f"\n给定移动关节位置: {prismatic_pos:.4f} m")
    
    # 求解逆运动学
    solution = ik_solver.solve(target_foot_pos, prismatic_pos)
    
    if solution.valid:
        print(f"\n✅ 逆运动学求解成功!")
        print(f"\n求解的关节角度:")
        print(f"  移动关节: {solution.prismatic:.4f} m")
        print(f"  HAA (侧摆): {solution.haa:.4f} rad ({np.degrees(solution.haa):.2f}°)")
        print(f"  HFE (俯仰): {solution.hfe:.4f} rad ({np.degrees(solution.hfe):.2f}°)")
        print(f"  KFE (膝关节): {solution.kfe:.4f} rad ({np.degrees(solution.kfe):.2f}°)")
    else:
        print(f"\n❌ 逆运动学求解失败!")
        print(f"错误信息: {solution.error_msg}")
    
    return solution


def test_round_trip():
    """测试往返（FK -> IK -> FK）"""
    print("\n" + "=" * 60)
    print("测试 3: 往返测试 (FK -> IK -> FK)")
    print("=" * 60)
    
    # 创建腿 1 的几何参数
    geometry = create_dog2_leg_geometry(1)
    ik_solver = LegIK4DOF(geometry)
    
    # 原始关节角度
    prismatic_orig = 0.0
    haa_orig = 0.1
    hfe_orig = 0.5
    kfe_orig = -1.2
    
    print(f"\n原始关节角度:")
    print(f"  移动关节: {prismatic_orig:.4f} m")
    print(f"  HAA: {haa_orig:.4f} rad ({np.degrees(haa_orig):.2f}°)")
    print(f"  HFE: {hfe_orig:.4f} rad ({np.degrees(hfe_orig):.2f}°)")
    print(f"  KFE: {kfe_orig:.4f} rad ({np.degrees(kfe_orig):.2f}°)")
    
    # 正运动学
    foot_pos = ik_solver.forward_kinematics(prismatic_orig, haa_orig, hfe_orig, kfe_orig)
    print(f"\n正运动学 -> 足端位置:")
    print(f"  X: {foot_pos[0]:.4f} m")
    print(f"  Y: {foot_pos[1]:.4f} m")
    print(f"  Z: {foot_pos[2]:.4f} m")
    
    # 逆运动学
    solution = ik_solver.solve(foot_pos, prismatic_orig)
    
    if not solution.valid:
        print(f"\n❌ 逆运动学求解失败: {solution.error_msg}")
        return
    
    print(f"\n逆运动学 -> 关节角度:")
    print(f"  移动关节: {solution.prismatic:.4f} m")
    print(f"  HAA: {solution.haa:.4f} rad ({np.degrees(solution.haa):.2f}°)")
    print(f"  HFE: {solution.hfe:.4f} rad ({np.degrees(solution.hfe):.2f}°)")
    print(f"  KFE: {solution.kfe:.4f} rad ({np.degrees(solution.kfe):.2f}°)")
    
    # 再次正运动学
    foot_pos_verify = ik_solver.forward_kinematics(
        solution.prismatic, solution.haa, solution.hfe, solution.kfe
    )
    print(f"\n正运动学（验证）-> 足端位置:")
    print(f"  X: {foot_pos_verify[0]:.4f} m")
    print(f"  Y: {foot_pos_verify[1]:.4f} m")
    print(f"  Z: {foot_pos_verify[2]:.4f} m")
    
    # 计算误差
    error = np.linalg.norm(foot_pos - foot_pos_verify)
    print(f"\n位置误差: {error:.6f} m")
    
    if error < 1e-4:
        print("✅ 往返测试通过!")
    else:
        print("❌ 往返测试失败，误差过大!")


def test_optimization():
    """测试自动优化移动关节位置"""
    print("\n" + "=" * 60)
    print("测试 4: 自动优化移动关节位置")
    print("=" * 60)
    
    # 创建腿 1 的几何参数
    geometry = create_dog2_leg_geometry(1)
    ik_solver = LegIK4DOF(geometry)
    
    # 目标足端位置（可能需要非零的移动关节位置）
    target_foot_pos = np.array([1.2, -0.9, 0.0])
    
    print(f"\n目标足端位置:")
    print(f"  X: {target_foot_pos[0]:.4f} m")
    print(f"  Y: {target_foot_pos[1]:.4f} m")
    print(f"  Z: {target_foot_pos[2]:.4f} m")
    
    # 使用自动优化
    solution = ik_solver.solve_with_optimization(target_foot_pos, prismatic_preference=0.0)
    
    if solution.valid:
        print(f"\n✅ 自动优化求解成功!")
        print(f"\n优化后的关节角度:")
        print(f"  移动关节: {solution.prismatic:.4f} m")
        print(f"  HAA (侧摆): {solution.haa:.4f} rad ({np.degrees(solution.haa):.2f}°)")
        print(f"  HFE (俯仰): {solution.hfe:.4f} rad ({np.degrees(solution.hfe):.2f}°)")
        print(f"  KFE (膝关节): {solution.kfe:.4f} rad ({np.degrees(solution.kfe):.2f}°)")
        
        # 验证
        foot_pos_verify = ik_solver.forward_kinematics(
            solution.prismatic, solution.haa, solution.hfe, solution.kfe
        )
        error = np.linalg.norm(target_foot_pos - foot_pos_verify)
        print(f"\n位置误差: {error:.6f} m")
    else:
        print(f"\n❌ 自动优化求解失败!")
        print(f"错误信息: {solution.error_msg}")


def test_all_legs():
    """测试所有四条腿"""
    print("\n" + "=" * 60)
    print("测试 5: 所有四条腿的逆运动学")
    print("=" * 60)
    
    leg_names = ["前左", "前右", "后左", "后右"]
    
    for leg_num in range(1, 5):
        print(f"\n--- 腿 {leg_num} ({leg_names[leg_num-1]}) ---")
        
        geometry = create_dog2_leg_geometry(leg_num)
        ik_solver = LegIK4DOF(geometry)
        
        # 站立姿态的关节角度
        prismatic = 0.0
        haa = 0.0
        hfe = 0.4
        kfe = -1.0
        
        # 正运动学
        foot_pos = ik_solver.forward_kinematics(prismatic, haa, hfe, kfe)
        print(f"站立姿态足端位置: [{foot_pos[0]:.3f}, {foot_pos[1]:.3f}, {foot_pos[2]:.3f}]")
        
        # 逆运动学
        solution = ik_solver.solve(foot_pos, prismatic)
        
        if solution.valid:
            print(f"✅ 逆运动学求解成功")
            print(f"   关节角度: prismatic={solution.prismatic:.3f}, "
                  f"haa={solution.haa:.3f}, hfe={solution.hfe:.3f}, kfe={solution.kfe:.3f}")
        else:
            print(f"❌ 逆运动学求解失败: {solution.error_msg}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Dog2 四自由度逆运动学测试")
    print("=" * 60)
    print("\n关节链结构（每条腿）：")
    print("1. j${leg_num}   - 移动关节（prismatic）- 直线导轨")
    print("2. j${leg_num}1  - 旋转关节（revolute） - 髋关节侧摆（HAA）")
    print("3. j${leg_num}11 - 旋转关节（revolute） - 髋关节俯仰（HFE）")
    print("4. j${leg_num}111- 旋转关节（revolute） - 膝关节（KFE）")
    print("\n求解策略：参数化直线导轨位置，求解剩余 3 个旋转关节")
    
    # 测试 1: 正运动学
    foot_pos = test_forward_kinematics()
    
    # 测试 2: 逆运动学
    test_inverse_kinematics(foot_pos, prismatic_pos=0.0)
    
    # 测试 3: 往返测试
    test_round_trip()
    
    # 测试 4: 自动优化
    test_optimization()
    
    # 测试 5: 所有四条腿
    test_all_legs()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
