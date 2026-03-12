#!/usr/bin/env python3
"""
正确检测Dog2关节类型
"""
import pinocchio as pin
import numpy as np

urdf_path = "src/dog2_description/urdf/dog2.urdf"
model = pin.buildModelFromUrdf(urdf_path)

print("=" * 70)
print("Dog2 URDF 分析")
print("=" * 70)
print(f"机器人名称: {model.name}")
print(f"自由度数(nq): {model.nq}")
print(f"速度维度(nv): {model.nv}")
print(f"关节数量: {model.njoints}")
print()

# 详细分析每个关节
print("=" * 70)
print("详细关节信息：")
print("=" * 70)

prismatic_joints = []
revolute_joints = []
continuous_joints = []
fixed_joints = []

for i in range(1, model.njoints):  # 从1开始，跳过universe
    joint_name = model.names[i]
    joint_model = model.joints[i]
    
    # 获取关节类型
    joint_type_str = str(type(joint_model))
    
    # 判断关节类型
    if 'JointModelPX' in joint_type_str or 'JointModelPrismatic' in joint_type_str:
        joint_type = "Prismatic (滑动副)"
        prismatic_joints.append(joint_name)
    elif 'JointModelRZ' in joint_type_str or 'JointModelRY' in joint_type_str or 'JointModelRX' in joint_type_str:
        joint_type = "Revolute (旋转副)"
        revolute_joints.append(joint_name)
    elif 'Freeflyer' in joint_type_str:
        joint_type = "Freeflyer (浮动基座)"
    elif 'Composite' in joint_type_str:
        joint_type = "Composite (复合)"
    else:
        joint_type = f"Other ({joint_type_str})"
    
    # 获取自由度
    nq = model.joints[i].nq
    nv = model.joints[i].nv
    
    print(f"{i:2d}. {joint_name:12s} | {joint_type:25s} | nq={nq}, nv={nv}")

# 统计
print()
print("=" * 70)
print("关节类型统计：")
print("=" * 70)
print(f"滑动副 (Prismatic): {len(prismatic_joints)}")
if prismatic_joints:
    print(f"  → {', '.join(prismatic_joints[:8])}")
    if len(prismatic_joints) > 8:
        print(f"  → {', '.join(prismatic_joints[8:])}")

print(f"\n旋转副 (Revolute): {len(revolute_joints)}")
if revolute_joints:
    print(f"  → {', '.join(revolute_joints[:8])}")
    if len(revolute_joints) > 8:
        print(f"  → {', '.join(revolute_joints[8:])}")

print()
print("=" * 70)
print("关键发现：")
print("=" * 70)

# 检查是否有浮动基座
if model.nq - model.nv > 0:
    print(f"✓ 有浮动基座（nq={model.nq}, nv={model.nv}, 差值={model.nq-model.nv}）")
    print("  → 浮动基座使用四元数表示姿态（nq=7, nv=6）")
else:
    print(f"✓ 固定基座")

print()

# 验证Dog2的特殊结构
if len(prismatic_joints) == 4:
    print("✓ 检测到4个滑动副髋关节（Dog2的特殊设计！）")
    print("  这些滑动关节允许腿部伸缩")
elif len(prismatic_joints) == 0:
    print("⚠️  未检测到滑动副")
    print("  可能原因：")
    print("  1. URDF中滑动关节被定义为其他类型")
    print("  2. Pinocchio将其识别为复合关节")
    print("  3. 需要查看URDF源文件确认")

print()
print("=" * 70)

# 测试正向运动学
print("\n测试正向运动学...")
q = pin.neutral(model)
pin.forwardKinematics(model, model.createData(), q)
print("✓ 正向运动学计算成功！")

# 测试质心计算
data = model.createData()
com = pin.centerOfMass(model, data, q)
print(f"✓ 质心位置: [{com[0]:.3f}, {com[1]:.3f}, {com[2]:.3f}]")

print()
print("=" * 70)
print("✓ Pinocchio可以完美处理Dog2模型！")
print("=" * 70)

