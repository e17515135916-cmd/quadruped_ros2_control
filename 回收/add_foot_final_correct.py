#!/usr/bin/env python3
"""
在膝关节定义之后添加足端Link和关节
"""

# 读取文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# 定义要添加的足端内容
foot_content = '''
  
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
    <xacro:if value="${leg_num == 1}">
      <origin rpy="0 0 0" xyz="-0.02 -0.35 0"/>
    </xacro:if>
    <xacro:if value="${leg_num == 2}">
      <origin rpy="0 0 0" xyz="0.02 -0.35 0"/>
    </xacro:if>
    <xacro:if value="${leg_num == 3}">
      <origin rpy="0 0 0" xyz="-0.02 -0.35 0"/>
    </xacro:if>
    <xacro:if value="${leg_num == 4}">
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
'''

# 找到膝关节定义的结束位置（</joint>之后）
# 查找包含 j${leg_num}111 的joint定义
import re

# 查找膝关节定义（注意是3个1，不是4个）
pattern = r'(<joint\s+name="j\$\{leg_num\}111".*?</joint>)'
matches = list(re.finditer(pattern, content, re.DOTALL))

if matches:
    # 在最后一个膝关节定义之后插入足端
    last_match = matches[-1]
    insert_pos = last_match.end()
    
    content = content[:insert_pos] + foot_content + content[insert_pos:]
    print(f"✓ 在位置 {insert_pos} 插入足端定义")
else:
    print("✗ 未找到膝关节定义")
    exit(1)

# 写回文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("✓ 足端已添加")
print("\n配置:")
print("  - 几何体: 球体，半径0.02m")
print("  - 位置: Leg 1,3 (左): xyz='-0.02 -0.35 0'")
print("  -       Leg 2,4 (右): xyz='0.02 -0.35 0'")
