#!/usr/bin/env python3
"""
完整添加球形足端到DOG2 URDF
"""

import re

# 读取当前URDF
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# 定义要添加的足端Link和关节
foot_definition = '''  
  <!-- Foot link (l${leg_num}1111) - Spherical geometry -->
  <link name="l${leg_num}1111">
    <inertial>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <mass value="0.05"/>
      <inertia ixx="8e-6" ixy="0" ixz="0" iyy="8e-6" iyz="0" izz="8e-6"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <sphere radius="0.02"/>
      </geometry>
      <material name="">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <sphere radius="0.02"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Fixed joint connecting shin to foot (j${leg_num}1111) -->
  <joint name="j${leg_num}1111" type="fixed">
    <!-- 左侧腿(1,3)靠左，右侧腿(2,4)靠右，所有腿向下到小腿末端 -->
    <xacro:if value="${leg_num == 1 or leg_num == 3}">
      <origin rpy="0 0 0" xyz="-0.02 -0.35 0"/>
    </xacro:if>
    <xacro:if value="${leg_num == 2 or leg_num == 4}">
      <origin rpy="0 0 0" xyz="0.02 -0.35 0"/>
    </xacro:if>
    <parent link="l${leg_num}111"/>
    <child link="l${leg_num}1111"/>
  </joint>
  
  <!-- Gazebo friction configuration for foot link -->
  <gazebo reference="l${leg_num}1111">
    <mu1>1.5</mu1>
    <mu2>1.5</mu2>
    <kp>1000000.0</kp>
    <kd>100.0</kd>
    <minDepth>0.001</minDepth>
    <maxVel>0.1</maxVel>
    <material>Gazebo/Grey</material>
  </gazebo>

  </xacro:macro>'''

# 找到leg宏的结束位置（</xacro:macro>）
# 在leg宏定义中，应该在最后一个</joint>之后，</xacro:macro>之前添加足端

# 查找leg宏中膝关节定义的位置
pattern = r'(  <!-- Knee joint \(KFE\) \(j\$\{leg_num\}111\) -->.*?</joint>)'

# 在膝关节定义后添加足端定义
def add_foot_after_knee(match):
    return match.group(1) + foot_definition

content = re.sub(pattern, add_foot_after_knee, content, flags=re.DOTALL)

# 写回文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("✓ 球形足端已添加到URDF")
print("\n足端配置:")
print("  - 几何体: 球体，半径0.02m")
print("  - 质量: 0.05kg")
print("  - 颜色: 灰色 (0.5, 0.5, 0.5, 1)")
print("  - 位置:")
print("    * Leg 1,3 (左侧): xyz='-0.02 -0.35 0'")
print("    * Leg 2,4 (右侧): xyz='0.02 -0.35 0'")
print("  - 摩擦系数: mu1=mu2=1.5")
