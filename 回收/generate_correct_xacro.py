#!/usr/bin/env python3
"""
根据正确的URDF文件生成xacro文件（只包含4个link，不包含足端）
"""

xacro_content = '''<?xml version="1.0"?>
<!--
  Dog2 Robot Description (Xacro Source)
  
  Recreated from correct URDF file
  Date: 2026-01-28
  
  INERTIA CORRECTIONS:
  - Leg 1 & 2: Positive X (front legs)
  - Leg 3 & 4: Negative X (rear legs, mirrored geometry)
  
  JOINT LIMITS:
  - Hip joints: ±150° (±2.618 rad)
  - Knee joints: ±160° (±2.8 rad)
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog2">

  <!-- ============================================ -->
  <!-- SECTION 1: PROPERTY DEFINITIONS              -->
  <!-- ============================================ -->
  
  <!-- Hip joint limits -->
  <xacro:property name="hip_lower_limit" value="-2.618"/>
  <xacro:property name="hip_upper_limit" value="2.618"/>
  <xacro:property name="hip_effort" value="50"/>
  <xacro:property name="hip_velocity" value="20"/>

  <!-- Knee joint limits -->
  <xacro:property name="knee_lower_limit" value="-2.8"/>
  <xacro:property name="knee_upper_limit" value="2.8"/>
  <xacro:property name="knee_effort" value="50"/>
  <xacro:property name="knee_velocity" value="20"/>

  <!-- Inertia properties -->
  <xacro:property name="leg12_thigh_inertia_xyz" value="0.026 -0.0760041259902766 0.0649874821212071"/>
  <xacro:property name="leg12_shin_inertia_xyz" value="0.0254901816398352 -0.143524743603395 -0.0694046953395906"/>
  
  <xacro:property name="leg3_thigh_inertia_xyz" value="-0.0259999999999999 -0.0760041259902766 0.0649874821212069"/>
  <xacro:property name="leg3_shin_inertia_xyz" value="-0.0265098183601649 -0.143524743603395 -0.0694046953395908"/>
  
  <xacro:property name="leg4_thigh_inertia_xyz" value="-0.026 -0.0760041259902766 0.0649874821212069"/>
  <xacro:property name="leg4_shin_inertia_xyz" value="-0.0265089672547710 -0.1429895138560395 -0.0691152554666486"/>

  <!-- ============================================ -->
  <!-- WORLD AND BASE LINKS                         -->
  <!-- ============================================ -->
  
  <link name="world"/>
  
  <joint name="world_joint" type="fixed">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <link name="base_link">
    <inertial>
      <origin xyz="1.2272 -0.7470 0.2649" rpy="1.5708 0 0" />
      <mass value="6.0" />
      <inertia
        ixx="0.0153"
        ixy="0.00011"
        ixz="0"
        iyy="0.052"
        iyz="0"
        izz="0.044" />
    </inertial>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <mesh filename="package://dog2_description/meshes/base_link.STL" />
      </geometry>
      <material name="">
        <color rgba="0.752941176470588 0.752941176470588 0.752941176470588 1" />
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <mesh filename="package://dog2_description/meshes/base_link.STL" />
      </geometry>
    </collision>
  </link>

  <!-- ============================================ -->
  <!-- SECTION 2: LEG MACRO DEFINITION              -->
  <!-- ============================================ -->
  
  <xacro:macro name="leg" params="leg_num origin_xyz origin_rpy
                                 thigh_inertia_xyz shin_inertia_xyz
                                 hip_joint_rpy:='0 0 1.5708'
                                 hip_joint_xyz:='-0.016 0.0199 0.055'
                                 knee_joint_xyz:='-0.0233 -0.055 0.0274'
                                 thigh_visual_rpy:='0 0 0'
                                 thigh_collision_rpy:='0 0 0'">

  <!-- Prismatic link (l${leg_num}) -->
  <link name="l${leg_num}">
    <inertial>
      <origin rpy="0 0 0" xyz="-0.0159999123716776 0.000737036465389251 0.0261570925915838"/>
      <mass value="0.3"/>
      <inertia ixx="0.000107100908138004" ixy="0" ixz="0" iyy="8.38648309010005E-05" iyz="0" izz="7.86994452918461E-05"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}.STL"/>
      </geometry>
      <material name="">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}.STL"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Prismatic joint (j${leg_num}) -->
  <joint name="j${leg_num}" type="prismatic">
    <origin rpy="${origin_rpy}" xyz="${origin_xyz}"/>
    <parent link="base_link"/>
    <child link="l${leg_num}"/>
    <axis xyz="-1 0 0"/>
    <xacro:if value="${leg_num == 1}">
      <limit effort="100" lower="-0.111" upper="0.0" velocity="5"/>
    </xacro:if>
    <xacro:if value="${leg_num == 2}">
      <limit effort="100" lower="-0.0" upper="0.111" velocity="5"/>
    </xacro:if>
    <xacro:if value="${leg_num == 3}">
      <limit effort="100" lower="-0.111" upper="0.0" velocity="5"/>
    </xacro:if>
    <xacro:if value="${leg_num == 4}">
      <limit effort="100" lower="-0.0" upper="0.111" velocity="5"/>
    </xacro:if>
  </joint>
  
  <!-- Hip link (l${leg_num}1) -->
  <link name="l${leg_num}1">
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
        <color rgba="0.266666666666667 0.529411764705882 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}1.STL"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Hip joint (j${leg_num}1) -->
  <joint name="j${leg_num}1" type="revolute">
    <origin rpy="${hip_joint_rpy}" xyz="${hip_joint_xyz}"/>
    <parent link="l${leg_num}"/>
    <child link="l${leg_num}1"/>
    <axis xyz="-1 0 0"/>
    <limit effort="${hip_effort}" lower="${hip_lower_limit}" upper="${hip_upper_limit}" velocity="${hip_velocity}"/>
  </joint>
  
  <!-- Thigh link (l${leg_num}11) -->
  <link name="l${leg_num}11">
    <inertial>
      <origin rpy="0 0 0" xyz="${thigh_inertia_xyz}"/>
      <mass value="0.4"/>
      <inertia ixx="0.000666" ixy="0" ixz="0" iyy="0.000356" iyz="0.000266" izz="0.000534"/>
    </inertial>
    <visual>
      <origin rpy="${thigh_visual_rpy}" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}11.STL"/>
      </geometry>
      <material name="">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="${thigh_collision_rpy}" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}11.STL"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Hip flexion/extension joint (HFE) (j${leg_num}11) -->
  <joint name="j${leg_num}11" type="revolute">
    <origin rpy="1.5708 1.5708 0" xyz="${knee_joint_xyz}"/>
    <parent link="l${leg_num}1"/>
    <child link="l${leg_num}11"/>
    <axis xyz="-1 0 0"/>
    <limit effort="${knee_effort}" lower="${knee_lower_limit}" upper="${knee_upper_limit}" velocity="${knee_velocity}"/>
  </joint>
  
  <!-- Shin link (l${leg_num}111) -->
  <link name="l${leg_num}111">
    <inertial>
      <origin rpy="0 0 0" xyz="${shin_inertia_xyz}"/>
      <mass value="0.5"/>
      <inertia ixx="0.004517" ixy="0.00000870" ixz="0.00000420" iyy="0.000975" iyz="-0.00176971" izz="0.003666"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}111.STL"/>
      </geometry>
      <material name="">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}111.STL"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Knee joint (KFE) (j${leg_num}111) -->
  <joint name="j${leg_num}111" type="revolute">
    <origin rpy="0 0 0" xyz="0 -0.15201 0.12997"/>
    <parent link="l${leg_num}11"/>
    <child link="l${leg_num}111"/>
    <axis xyz="-1 0 0"/>
    <limit effort="50" lower="-2.8" upper="2.8" velocity="20"/>
  </joint>
  
  <!-- Shin link (l${leg_num}1111) -->
  <link name="l${leg_num}1111">
    <inertial>
      <origin rpy="0 0 0" xyz="${shin_inertia_xyz}"/>
      <mass value="0.5"/>
      <inertia ixx="0.004517" ixy="0.00000870" ixz="0.00000420" iyy="0.000975" iyz="-0.00176971" izz="0.003666"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}1111.STL"/>
      </geometry>
      <material name="">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="package://dog2_description/meshes/l${leg_num}1111.STL"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Knee joint (j${leg_num}1111) -->
  <joint name="j${leg_num}1111" type="revolute">
    <origin rpy="0 0 0" xyz="0 -0.15201 0.12997"/>
    <parent link="l${leg_num}111"/>
    <child link="l${leg_num}1111"/>
    <axis xyz="-1 0 0"/>
    <limit effort="50" lower="-2.8" upper="0.0" velocity="20"/>
  </joint>
  
  <!-- Gazebo friction configuration for shin link -->
  <gazebo reference="l${leg_num}1111">
    <mu1>1.0</mu1>
    <mu2>1.0</mu2>
    <kp>1000000.0</kp>
    <kd>100.0</kd>
    <minDepth>0.001</minDepth>
    <maxVel>0.1</maxVel>
    <material>Gazebo/Grey</material>
  </gazebo>

  </xacro:macro>

  <!-- ============================================ -->
  <!-- SECTION 3: LEG INSTANTIATIONS                -->
  <!-- ============================================ -->

  <!-- Leg 1: Front Left -->
  <xacro:leg leg_num="1" 
             origin_xyz="1.1026 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"/>

  <!-- Leg 2: Front Right -->
  <xacro:leg leg_num="2" 
             origin_xyz="1.3491 -0.80953 0.2649" 
             origin_rpy="1.5708 0 0" 
             thigh_inertia_xyz="${leg12_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg12_shin_inertia_xyz}"/>

  <!-- Leg 3: Rear Left -->
  <xacro:leg leg_num="3" 
             origin_xyz="1.3491 -0.68953 0.2649" 
             origin_rpy="1.5708 0 -3.1416" 
             thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg3_shin_inertia_xyz}"
             hip_joint_rpy="3.1416 0 1.5708"
             knee_joint_xyz="-0.0233 -0.055 -0.0254"/>

  <!-- Leg 4: Rear Right -->
  <xacro:leg leg_num="4" 
             origin_xyz="1.1071 -0.68953 0.2649" 
             origin_rpy="1.5708 0 -3.1416" 
             thigh_inertia_xyz="${leg4_thigh_inertia_xyz}"
             shin_inertia_xyz="${leg4_shin_inertia_xyz}"
             hip_joint_rpy="3.1416 0 1.5708"
             hip_joint_xyz="0.0116 0.0199 0.055"
             knee_joint_xyz="-0.0233 -0.055 -0.0254"
             thigh_visual_rpy="0 3.1416 0"
             thigh_collision_rpy="0 3.1416 0"/>

  <!-- ============================================ -->
  <!-- SECTION 4: ROS 2 CONTROL & GAZEBO            -->
  <!-- ============================================ -->
  
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>
    
    <!-- Leg 1 Joints -->
    <joint name="j1">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j11">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j111">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j1111">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    
    <!-- Leg 2 Joints -->
    <joint name="j2">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j21">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j211">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j2111">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    
    <!-- Leg 3 Joints -->
    <joint name="j3">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j31">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j311">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j3111">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    
    <!-- Leg 4 Joints -->
    <joint name="j4">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j41">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j411">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
    <joint name="j4111">
      <command_interface name="effort"/>
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
  </ros2_control>
  
  <!-- Gazebo ROS 2 Control Plugin -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
    </plugin>
  </gazebo>

</robot>
'''

# 写入xacro文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(xacro_content)

print("✓ xacro文件已重新生成（基于正确的URDF）")
print("  - 每条腿有5个link（包含shin的两个部分）")
print("  - l${leg_num}: 导轨")
print("  - l${leg_num}1: 髋关节")
print("  - l${leg_num}11: 大腿")
print("  - l${leg_num}111: 小腿上部")
print("  - l${leg_num}1111: 小腿下部（shin）")
print("  - 腿部位置已修复")
