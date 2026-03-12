#!/bin/bash
# 修复 joint_state_publisher_gui 显示旧关节名称的问题

echo "======================================================================"
echo "修复 Joint State Publisher GUI 显示问题"
echo "======================================================================"
echo ""

# 1. 重新构建工作空间
echo "步骤 1: 重新构建 dog2_description 包..."
colcon build --packages-select dog2_description

if [ $? -ne 0 ]; then
    echo "错误: 构建失败"
    exit 1
fi

echo "✓ 构建成功"
echo ""

# 2. 重新 source 环境
echo "步骤 2: 重新加载环境..."
source install/setup.bash
echo "✓ 环境已重新加载"
echo ""

# 3. 验证 URDF 中的关节名称
echo "步骤 3: 验证 URDF 关节名称..."
echo ""
echo "应该看到以下关节名称："
echo "  - j1, j2, j3, j4 (滑动副)"
echo "  - lf_haa_joint, lf_hfe_joint, lf_kfe_joint (前左腿)"
echo "  - rf_haa_joint, rf_hfe_joint, rf_kfe_joint (前右腿)"
echo "  - lh_haa_joint, lh_hfe_joint, lh_kfe_joint (后左腿)"
echo "  - rh_haa_joint, rh_hfe_joint, rh_kfe_joint (后右腿)"
echo ""

xacro src/dog2_description/urdf/dog2.urdf.xacro 2>/dev/null | grep -E 'joint name=' | grep -v 'fixed' | head -16

echo ""
echo "======================================================================"
echo "修复完成！"
echo "======================================================================"
echo ""
echo "现在请重新启动 RViz："
echo "  ./start_champ_rviz_test.sh"
echo ""
echo "或者："
echo "  ros2 launch launch_champ_rviz_test.py"
echo ""
