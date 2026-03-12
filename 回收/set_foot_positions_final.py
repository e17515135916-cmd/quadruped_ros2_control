#!/usr/bin/env python3
"""
为每条腿设置不同的足端位置
使用xacro条件语句
"""

import re

# 读取URDF文件
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'r') as f:
    content = f.read()

# 找到足端关节定义
old_joint = '''  <!-- Fixed joint connecting shin to foot (j${leg_num}1111) -->
  <joint name="j${leg_num}1111" type="fixed">
    <origin rpy="0 0 0" xyz="0 -0.22 0"/>
    <parent link="l${leg_num}111"/>
    <child link="l${leg_num}1111"/>
  </joint>'''

# 新的定义：为每条腿设置不同的偏移
new_joint = '''  <!-- Fixed joint connecting shin to foot (j${leg_num}1111) -->
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
  </joint>'''

content = content.replace(old_joint, new_joint)

# 写回
with open('src/dog2_description/urdf/dog2.urdf.xacro', 'w') as f:
    f.write(content)

print("✓ 足端位置已更新:")
print("  Leg 1 (前左): xyz='-0.02 -0.35 0' (靠左，向下)")
print("  Leg 2 (前右): xyz='0.02 -0.35 0' (靠右，向下)")
print("  Leg 3 (后左): xyz='-0.02 -0.35 0' (靠左，向下)")
print("  Leg 4 (后右): xyz='0.02 -0.35 0' (靠右，向下)")
