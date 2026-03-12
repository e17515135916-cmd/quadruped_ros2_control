#!/usr/bin/env python3
"""
为每条腿设置不同的足端偏移
- 左侧腿(1,3): x偏移为负（靠左）
- 右侧腿(2,4): x偏移为正（靠右）
- 所有腿: y更负（靠下），z=0（在小腿末端）
"""

# 读取URDF文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# 当前所有腿使用统一的偏移
# 我们需要修改leg宏，使其接受foot_offset_xyz参数

# 首先，在leg宏的参数列表中添加foot_offset_xyz参数
old_macro_params = '''<xacro:macro name="leg" params="leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz foot_inertia_xyz
                                 hip_joint_rpy:='0 0 1.5708'
                                 hip_joint_xyz:='-0.016 0.0199 0.055'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'">'''

new_macro_params = '''<xacro:macro name="leg" params="leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz shin_inertia_xyz foot_inertia_xyz
                                 hip_joint_rpy:='0 0 1.5708'
                                 hip_joint_xyz:='-0.016 0.0199 0.055'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'
                                 foot_offset_xyz:='0 -0.33 -0.10'">'''

content = content.replace(old_macro_params, new_macro_params)

# 然后，修改足端关节定义，使用参数化的偏移
old_foot_joint = '''  <!-- Fixed joint connecting shin to foot (j${leg_num}1111) -->
  <joint name="j${leg_num}1111" type="fixed">
    <origin rpy="0 0 0" xyz="0 -0.33 -0.10"/>'''

new_foot_joint = '''  <!-- Fixed joint connecting shin to foot (j${leg_num}1111) -->
  <joint name="j${leg_num}1111" type="fixed">
    <origin rpy="0 0 0" xyz="${foot_offset_xyz}"/>'''

content = content.replace(old_foot_joint, new_foot_joint)

# 写回
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("✓ 第1步完成: 添加foot_offset_xyz参数到leg宏")
print("\n现在需要手动为每条腿设置不同的偏移值:")
print("  Leg 1 (前左): foot_offset_xyz='-0.02 -0.35 0'")
print("  Leg 2 (前右): foot_offset_xyz='0.02 -0.35 0'")
print("  Leg 3 (后左): foot_offset_xyz='-0.02 -0.35 0'")
print("  Leg 4 (后右): foot_offset_xyz='0.02 -0.35 0'")
