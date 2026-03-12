#!/usr/bin/env python3
"""
Final fix: Update Leg 3 and 4 configurations to match Leg 1 and 2
"""

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Fix Leg 3
content = content.replace(
    '''  <!-- Leg 3: Rear Left (with inertia corrections for mirrored geometry) -->
  <xacro:leg leg_num="3" 
             origin_xyz="1.3491 -0.68953 0.2649" 
             origin_rpy="1.5708 0 -3.1416" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg3_shin_inertia_xyz}"
             hip_joint_rpy="3.1416 0 1.5708"
             knee_joint_xyz="-0.0233 -0.055 -0.0254"
             foot_xyz="-0.0286 -0.289478 -0.14"/>''',
    '''  <!-- Leg 3: Rear Left (with inertia corrections for mirrored geometry) -->
  <xacro:leg leg_num="3" 
             origin_xyz="1.3491 -0.68953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg3_shin_inertia_xyz}"
             hip_joint_rpy="0 0 0"
             hip_joint_xyz="0.016 0.0199 0.080"
             knee_joint_xyz="-0.0233 -0.055 0.0274"
             thigh_joint_rpy="1.5708 1.5708 0"
             hip_axis="1 0 0"
             foot_xyz="-0.0286 -0.289478 -0.14"/>'''
)

# Fix Leg 4
content = content.replace(
    '''  <!-- Leg 4: Rear Right (with inertia corrections for mirrored geometry) -->
  <xacro:leg leg_num="4" 
             origin_xyz="1.1071 -0.68953 0.2649" 
             origin_rpy="1.5708 0 -3.1416" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg4_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg4_shin_inertia_xyz}"
             hip_joint_rpy="3.1416 0 1.5708"
             hip_joint_xyz="0.0116 0.0199 0.055"
             knee_joint_xyz="-0.0233 -0.055 -0.0254"
             thigh_visual_rpy="0 0 0"
             thigh_collision_rpy="0 0 0"
             foot_xyz="0.0286 -0.289478 -0.14"/>''',
    '''  <!-- Leg 4: Rear Right (with inertia corrections for mirrored geometry) -->
  <xacro:leg leg_num="4" 
             origin_xyz="1.1071 -0.68953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg4_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg4_shin_inertia_xyz}"
             hip_joint_rpy="0 0 0"
             hip_joint_xyz="-0.016 0.0199 0.080"
             knee_joint_xyz="-0.0233 -0.055 0.0274"
             thigh_visual_rpy="0 0 0"
             thigh_collision_rpy="0 0 0"
             thigh_joint_rpy="1.5708 1.5708 0"
             hip_axis="1 0 0"
             foot_xyz="0.0286 -0.289478 -0.14"/>'''
)

with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("✓ Fixed Leg 3 and Leg 4 configurations")
print("  - origin_rpy: 1.5708 0 -3.1416 → 1.5708 0 0")
print("  - hip_joint_rpy: 3.1416 0 1.5708 → 0 0 0")
print("  - knee_joint_xyz Z: -0.0254 → 0.0274")
print("  - Added hip_axis: 1 0 0")
print("  - Added thigh_joint_rpy: 1.5708 1.5708 0")
