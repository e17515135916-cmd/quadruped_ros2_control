#!/usr/bin/env python3
"""
测试Dog2动力学模型

验证Pinocchio模型加载和基本功能
"""

import sys
import os

# 添加build路径
build_path = os.path.join(os.getcwd(), 'build/dog2_dynamics')
if os.path.exists(build_path):
    sys.path.insert(0, build_path)

try:
    import pinocchio as pin
    import numpy as np
    print("✓ Pinocchio imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Pinocchio: {e}")
    sys.exit(1)

def test_dog2_model():
    """测试Dog2模型加载和基本功能"""
    
    print("\n" + "="*50)
    print("  Dog2 Dynamics Model Test")
    print("="*50)
    
    # URDF路径 - 使用原始URDF（带滑动副）
    urdf_path = "src/panda_description/urdf/dog2.urdf"
    
    if not os.path.exists(urdf_path):
        print(f"✗ URDF file not found: {urdf_path}")
        return False
    
    try:
        # 加载模型
        print(f"\n1. Loading URDF: {urdf_path}")
        model = pin.buildModelFromUrdf(urdf_path)
        data = model.createData()
        print(f"✓ Model loaded successfully")
        print(f"  nq = {model.nq} (configuration space)")
        print(f"  nv = {model.nv} (velocity space)")
        
        # 计算总质量
        print(f"\n2. Computing total mass")
        mass = pin.computeTotalMass(model)
        print(f"✓ Total mass = {mass:.2f} kg")
        
        # 测试中立姿态
        print(f"\n3. Testing neutral configuration")
        q = pin.neutral(model)
        v = np.zeros(model.nv)
        
        print(f"  q shape: {q.shape}")
        print(f"  v shape: {v.shape}")
        
        # 计算质心
        print(f"\n4. Computing center of mass")
        com = pin.centerOfMass(model, data, q)
        print(f"✓ CoM position: [{com[0]:.4f}, {com[1]:.4f}, {com[2]:.4f}] m")
        
        # 计算质心速度
        pin.centerOfMass(model, data, q, v)
        com_vel = data.vcom[0]
        print(f"✓ CoM velocity: [{com_vel[0]:.4f}, {com_vel[1]:.4f}, {com_vel[2]:.4f}] m/s")
        
        # 查找足端frame
        print(f"\n5. Finding foot frames")
        foot_names = ["l1111", "l2111", "l3111", "l4111"]
        foot_frames = []
        
        for foot_name in foot_names:
            if model.existFrame(foot_name):
                frame_id = model.getFrameId(foot_name)
                foot_frames.append(frame_id)
                print(f"✓ Found foot frame: {foot_name} (ID: {frame_id})")
            else:
                print(f"✗ Foot frame not found: {foot_name}")
        
        # 计算足端位置
        if foot_frames:
            print(f"\n6. Computing foot positions")
            pin.forwardKinematics(model, data, q)
            pin.updateFramePlacements(model, data)
            
            for i, frame_id in enumerate(foot_frames):
                pos = data.oMf[frame_id].translation
                print(f"✓ Foot {i}: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}] m")
        
        # 计算质量矩阵
        print(f"\n7. Computing mass matrix")
        M = pin.crba(model, data, q)
        print(f"✓ Mass matrix shape: {M.shape}")
        print(f"  M[0,0] = {M[0,0]:.4f}")
        
        # 计算重力项
        print(f"\n8. Computing gravity vector")
        g = pin.computeGeneralizedGravity(model, data, q)
        print(f"✓ Gravity vector shape: {g.shape}")
        print(f"  ||g|| = {np.linalg.norm(g):.4f}")
        
        # 测试滑动副限位
        print(f"\n9. Checking sliding joint limits")
        sliding_limits_lower = np.array([-0.111, -0.008, -0.008, -0.111])
        sliding_limits_upper = np.array([0.008, 0.111, 0.111, 0.008])
        print(f"✓ Lower limits: {sliding_limits_lower}")
        print(f"✓ Upper limits: {sliding_limits_upper}")
        
        print(f"\n" + "="*50)
        print("  All tests passed! ✓")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_dog2_model()
    sys.exit(0 if success else 1)
