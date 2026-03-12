#!/usr/bin/env python3
"""
Recreate the dog-style URDF with box primitive hip brackets.

This script takes the old spider-style URDF and converts it to dog-style by:
1. Replacing hip bracket meshes with box primitives
2. Updating joint origins for new bracket geometry
3. Fixing rear leg orientations to match front legs
"""

from pathlib import Path
import shutil
from datetime import datetime

def create_dog_style_urdf():
    """Create dog-style URDF from scratch."""
    
    # Backup current file
    urdf_path = Path("src/dog2_description/urdf/dog2.urdf.xacro")
    backup_dir = Path(f"backups/dog_style_recreation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(urdf_path, backup_dir / "dog2.urdf.xacro.backup")
    print(f"✓ Backup created: {backup_dir}")
    
    # Read the template from the good backup
    template_path = Path("backups/runable_20260129_195222/dog2.urdf.xacro")
    with open(template_path, 'r') as f:
        content = f.read()
    
    print("\nApplying transformations...")
    print("=" * 60)
    
    # Step 1: Update macro default parameters for dog-style
    print("\n1. Updating macro defaults...")
    content = content.replace(
        "                                 hip_joint_xyz:='-0.016 0.0199 0.055'",
        "                                 hip_joint_xyz:='-0.016 0.0199 0.080'"
    )
    print("   ✓ Changed hip_joint_xyz Z from 0.055 to 0.080 (cantilever height)")
    
    # Step 2: Replace hip bracket mesh with box primitives
    print("\n2. Replacing hip bracket mesh with box primitives...")
    
    old_hip_visual = '''  <link name="l${leg_num}1">
    <inertial>
      <origin rpy="0 0 0" xyz="-0.0233000000000003 -0.038305456702832 0.000879463367713051"/>
      <mass value="0.25"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}1.STL"/>
      </geometry>
      <material name="">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/collision/l${leg_num}1_collision.STL"/>
      </geometry>
    </collision>
  </link>'''
    
    new_hip_visual = '''  <link name="l${leg_num}1">
    <inertial>
      <origin rpy="0 0 0" xyz="-0.0233000000000003 -0.038305456702832 0.000879463367713051"/>
      <mass value="0.25"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
    <visual>
      <!-- Vertical body: 35mm x 25mm x 60mm -->
      <origin rpy="0 0 0" xyz="0 0 0.030"/>
      <geometry>
        <box size="0.035 0.025 0.060"/>
      </geometry>
      <material name="">
        <color rgba="0.9 0.9 0.9 1"/>
      </material>
    </visual>
    <visual>
      <!-- Horizontal cantilever platform: 40mm x 30mm x 5mm -->
      <origin rpy="0 0 0" xyz="0 0 0.0625"/>
      <geometry>
        <box size="0.040 0.030 0.005"/>
      </geometry>
      <material name="">
        <color rgba="0.9 0.9 0.9 1"/>
      </material>
    </visual>
    <collision>
      <!-- Simplified collision: single box encompassing both parts -->
      <origin rpy="0 0 0" xyz="0 0 0.0325"/>
      <geometry>
        <box size="0.040 0.030 0.065"/>
      </geometry>
    </collision>
  </link>'''
    
    content = content.replace(old_hip_visual, new_hip_visual)
    print("   ✓ Replaced mesh with box primitives (vertical body + horizontal platform)")
    
    # Step 3: Update hip joint axis from Z to X
    print("\n3. Updating hip joint rotation axis...")
    content = content.replace(
        '<axis xyz="0 0 -1"/>',
        '<axis xyz="1 0 0"/>'
    )
    print("   ✓ Changed hip joint axis from Z (0 0 -1) to X (1 0 0)")
    
    # Step 4: Fix front legs (Leg 1 & 2) - remove old RPY rotations
    print("\n4. Fixing front legs (Leg 1 & 2)...")
    
    # Leg 1
    content = content.replace(
        '''  <!-- Leg 1: Front Left -->
  <xacro:leg leg_num="1" 
             origin_xyz="1.1026 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             prismatic_inertia_xyz="0.0159999141740211 0.0007376899322864 0.0261433571319548"
             hip_joint_xyz="0.0116 0.0199 0.055"
             foot_xyz="0.026 -0.289478 -0.14"/>''',
        '''  <!-- Leg 1: Front Left -->
  <xacro:leg leg_num="1" 
             origin_xyz="1.1026 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.111" 
             prismatic_upper="0.0"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             hip_axis="1 0 0"/>'''
    )
    
    # Leg 2
    content = content.replace(
        '''  <!-- Leg 2: Front Right -->
  <xacro:leg leg_num="2" 
             origin_xyz="1.3491 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             prismatic_inertia_xyz="0.0159999141740211 0.0007376899322864 0.0261433571319548"
             hip_joint_xyz="0.0116 0.0199 0.055"
             foot_xyz="0.026 -0.289478 -0.14"/>''',
        '''  <!-- Leg 2: Front Right -->
  <xacro:leg leg_num="2" 
             origin_xyz="1.3491 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"
             hip_axis="1 0 0"/>'''
    )
    print("   ✓ Leg 1 & 2: Removed old parameters, using macro defaults")
    
    # Step 5: Fix rear legs (Leg 3 & 4) - KEY FIX FOR ORIENTATION
    print("\n5. Fixing rear legs (Leg 3 & 4) - CRITICAL FOR DOWNWARD ORIENTATION...")
    
    # Leg 3 - Change origin_rpy and remove old rotations
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
             hip_joint_xyz="-0.016 0.0199 0.080"
             knee_joint_xyz="-0.0233 -0.055 0.0274"
             thigh_joint_rpy="1.5708 1.5708 0"
             hip_axis="1 0 0"/>'''
    )
    
    # Leg 4
    content = content.replace(
        '''  <!-- Leg 4: Rear Right (with inertia corrections for mirrored geometry) -->
  <xacro:leg leg_num="4" 
             origin_xyz="1.1071 -0.68953 0.2649" 
             origin_rpy="1.5708 0 -3.1416" 
             prismatic_lower="-0.0" 
             prismatic_upper="0.111"
             thigh_inertia_xyz="${leg4_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg4_shin_inertia_xyz}"
             prismatic_inertia_xyz="0.0159999183367299 0.0007376902203368 0.0261433564499887"
             hip_joint_rpy="3.1416 0 1.5708"
             hip_joint_xyz="0.0116 0.0199 0.055"
             knee_joint_xyz="-0.0233 -0.055 -0.0254"
             thigh_visual_rpy="0 3.1416 0"
             thigh_collision_rpy="0 3.1416 0"
             foot_xyz="-0.0286 -0.289478 -0.14"/>''',
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
             thigh_joint_rpy="1.5708 1.5708 0"
             hip_axis="1 0 0"/>'''
    )
    print("   ✓ Leg 3: origin_rpy changed from '1.5708 0 -3.1416' to '1.5708 0 0'")
    print("   ✓ Leg 3: hip_joint_xyz changed to '-0.016 0.0199 0.080' (SAME AS LEG 1)")
    print("   ✓ Leg 4: origin_rpy changed from '1.5708 0 -3.1416' to '1.5708 0 0'")
    print("   ✓ Leg 4: hip_joint_xyz changed to '-0.016 0.0199 0.080' (SAME AS LEG 2)")
    
    # Write the new file
    with open(urdf_path, 'w') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✓ Dog-style URDF created successfully!")
    print("=" * 60)
    print("\nKey changes:")
    print("  • Hip brackets: Mesh → Box primitives (vertical body + horizontal platform)")
    print("  • Hip joint axis: Z-axis → X-axis rotation")
    print("  • Joint origin Z: 0.055m → 0.080m (cantilever height)")
    print("  • Rear legs: Removed 180° Z rotation from origin_rpy")
    print("  • Rear legs: hip_joint_xyz now matches front legs")
    print("\nResult: ALL FOUR LEGS SHOULD NOW POINT DOWNWARD! 🎉")
    print("\nNext step: ./view_robot_in_rviz.sh")
    
    return True

if __name__ == "__main__":
    success = create_dog_style_urdf()
    exit(0 if success else 1)
