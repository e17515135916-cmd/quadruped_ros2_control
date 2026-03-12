#!/usr/bin/env python3
"""Replace hip link mesh with box primitives"""

# Read the file
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# Define the old text (mesh-based)
old_text = '''  <link name="l${leg_num}1">
    <inertial>
      <origin rpy="0 0 0" xyz="-0.0233000000000003 -0.038305456702832 0.000879463367713051"/>
      <mass value="0.25"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
    <visual>
      <!-- MODIFIED: Added 90° rotation around Z-axis to match x-axis joint rotation -->
      <!-- Date: 2026-02-02 -->
      <origin rpy="0 0 1.5708" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}1.STL"/>
      </geometry>
      <material name="">
        <color rgba="0.266666666666667 0.529411764705882 1 1"/>
      </material>
    </visual>
    <collision>
      <!-- MODIFIED: Added 90° rotation around Z-axis to match visual origin -->
      <!-- This ensures collision geometry aligns with visual mesh after joint axis change -->
      <!-- Date: 2026-02-02 -->
      <origin rpy="0 0 1.5708" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/collision/l${leg_num}1_collision.STL"/>
      </geometry>
    </collision>
  </link>'''

# Define the new text (box primitives)
new_text = '''  <!-- Hip link (l${leg_num}1) -->
  <!-- MODIFIED: Replaced mesh with box primitives for simplified bracket geometry -->
  <!-- This creates a "dog-style" hip bracket with horizontal cantilever platform -->
  <!-- Date: 2026-02-07 -->
  <link name="l${leg_num}1">
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
      <!-- Positioned at top of vertical body -->
      <origin rpy="0 0 0" xyz="0 0 0.0625"/>
      <geometry>
        <box size="0.040 0.030 0.005"/>
      </geometry>
      <material name="">
        <color rgba="0.9 0.9 0.9 1"/>
      </material>
    </visual>
    <collision>
      <!-- Simplified collision: single box encompassing both vertical body and platform -->
      <origin rpy="0 0 0" xyz="0 0 0.0325"/>
      <geometry>
        <box size="0.040 0.030 0.065"/>
      </geometry>
    </collision>
  </link>'''

# Replace
if old_text in content:
    content = content.replace(old_text, new_text)
    print("Replacement successful!")
else:
    print("ERROR: Old text not found in file")
    print("Searching for partial match...")
    if 'l${leg_num}1.STL' in content:
        print("Found mesh reference - file has old content")
    exit(1)

# Write back
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("File updated successfully")
