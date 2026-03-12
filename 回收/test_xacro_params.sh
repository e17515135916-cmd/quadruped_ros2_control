#!/bin/bash
# 测试 xacro 参数传递

echo "测试 xacro 参数传递"
echo "===================="
echo ""

echo "检查 Leg 1 实例化中的 hip_joint_rpy 参数:"
grep -A 10 "Leg 1: Front Left" src/dog2_description/urdf/dog2.urdf.xacro | grep hip_joint_rpy

echo ""
echo "编译后的 HAA 关节 origin:"
xacro src/dog2_description/urdf/dog2.urdf.xacro 2>/dev/null | grep -A 3 'joint name="lf_haa_joint"' | grep origin

echo ""
echo "检查 leg macro 中的 hip_joint_rpy 默认值:"
grep "hip_joint_rpy:=" src/dog2_description/urdf/dog2.urdf.xacro

echo ""
echo "检查 HAA 关节定义中如何使用 hip_joint_rpy:"
grep -A 2 'joint name="\${prefix}_haa_joint"' src/dog2_description/urdf/dog2.urdf.xacro | grep origin
