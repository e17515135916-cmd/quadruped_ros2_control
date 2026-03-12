#!/bin/bash
# 测试 URDF 生成

echo "=========================================="
echo "测试 URDF 生成"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 生成 URDF..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_test.urdf 2>&1

if [ $? -eq 0 ]; then
    echo "✅ URDF 生成成功"
else
    echo "❌ URDF 生成失败"
    exit 1
fi

echo ""
echo "2. 检查 ros2_control 标签..."
if grep -q "<ros2_control" /tmp/dog2_test.urdf; then
    echo "✅ 找到 ros2_control 标签"
    
    # 统计关节数
    joint_count=$(sed -n '/<ros2_control/,/<\/ros2_control>/p' /tmp/dog2_test.urdf | grep -c '<joint name=')
    echo "   ros2_control 中的关节数: $joint_count"
    
    if [ $joint_count -eq 16 ]; then
        echo "   ✅ 关节数正确 (16 个)"
    else
        echo "   ⚠️  关节数不正确，应该是 16 个"
    fi
else
    echo "❌ 未找到 ros2_control 标签"
    exit 1
fi

echo ""
echo "3. 检查 CHAMP 关节..."
champ_joints=("lf_haa_joint" "lf_hfe_joint" "lf_kfe_joint" "rf_haa_joint" "rf_hfe_joint" "rf_kfe_joint")
all_found=true

for joint in "${champ_joints[@]}"; do
    if grep -q "\"$joint\"" /tmp/dog2_test.urdf; then
        echo "  ✅ $joint"
    else
        echo "  ❌ $joint (未找到)"
        all_found=false
    fi
done

echo ""
echo "4. 检查 Gazebo 插件配置..."
if grep -q "GazeboSimROS2ControlPlugin" /tmp/dog2_test.urdf; then
    echo "✅ 找到 Gazebo 插件"
    
    # 检查参数
    param_line=$(grep -A 1 "GazeboSimROS2ControlPlugin" /tmp/dog2_test.urdf | grep "parameters")
    echo "   参数配置: $param_line"
    
    if echo "$param_line" | grep -q "ros2_controllers.yaml"; then
        echo "   ✅ 参数路径正确"
    else
        echo "   ❌ 参数路径不正确"
    fi
else
    echo "❌ 未找到 Gazebo 插件"
fi

echo ""
echo "=========================================="
echo "总结"
echo "=========================================="
echo ""

if [ "$all_found" = true ] && [ $joint_count -eq 16 ]; then
    echo "✅ URDF 生成正确，包含所有必要的配置"
    echo ""
    echo "问题可能在于："
    echo "1. robot_state_publisher 过滤掉了 ros2_control 标签"
    echo "2. Gazebo 没有正确加载 URDF"
    echo ""
    echo "建议："
    echo "- 检查 Gazebo 启动日志中的错误信息"
    echo "- 确认 gz_ros2_control 插件是否正常加载"
else
    echo "❌ URDF 生成有问题"
fi
