#!/bin/bash
# 诊断 Gazebo 加载的 URDF 是否包含 ros2_control

echo "=========================================="
echo "诊断 Gazebo URDF 加载"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 生成完整 URDF（包含 ros2_control）..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_full.urdf 2>&1

if [ $? -eq 0 ]; then
    echo "✅ URDF 生成成功"
else
    echo "❌ URDF 生成失败"
    exit 1
fi

echo ""
echo "2. 检查 ros2_control 标签..."
if grep -q "<ros2_control" /tmp/dog2_full.urdf; then
    echo "✅ 找到 ros2_control 标签"
    
    # 统计关节数
    ros2_control_joint_count=$(sed -n '/<ros2_control/,/<\/ros2_control>/p' /tmp/dog2_full.urdf | grep -c '<joint name=')
    echo "   ros2_control 中的关节数: $ros2_control_joint_count"
else
    echo "❌ 未找到 ros2_control 标签"
fi

echo ""
echo "3. 检查 CHAMP 关节..."
for joint in lf_haa_joint lf_hfe_joint lf_kfe_joint; do
    if grep -q "name=\"$joint\"" /tmp/dog2_full.urdf; then
        echo "  ✅ $joint"
    else
        echo "  ❌ $joint (未找到)"
    fi
done

echo ""
echo "4. 检查 Gazebo 插件配置..."
if grep -q "gz_ros2_control::GazeboSimROS2ControlPlugin" /tmp/dog2_full.urdf; then
    echo "✅ 找到 Gazebo ros2_control 插件"
    
    # 检查是否有 parameters 标签
    if sed -n '/<plugin.*gz_ros2_control/,/<\/plugin>/p' /tmp/dog2_full.urdf | grep -q "<parameters>"; then
        echo "⚠️  警告：插件配置包含 <parameters> 标签"
        echo "   这可能导致 Gazebo Fortress 无法正确加载"
    else
        echo "✅ 插件配置正确（无 <parameters> 标签）"
    fi
else
    echo "❌ 未找到 Gazebo ros2_control 插件"
fi

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "完整 URDF 已保存到: /tmp/dog2_full.urdf"
echo "可以使用以下命令查看:"
echo "  cat /tmp/dog2_full.urdf | grep -A 5 'ros2_control'"
