#!/bin/bash
# 验证 Gazebo ROS 2 Control 配置是否正确

echo "=========================================="
echo "验证 Gazebo ROS 2 Control 配置"
echo "=========================================="
echo ""

# 检查控制器配置文件是否存在
echo "1. 检查控制器配置文件..."
if [ -f "src/dog2_description/config/ros2_controllers.yaml" ]; then
    echo "   ✓ 控制器配置文件存在"
else
    echo "   ✗ 控制器配置文件不存在"
    exit 1
fi

# 检查 dog2.urdf.xacro 是否包含配置路径
echo ""
echo "2. 检查 dog2.urdf.xacro 配置..."
if grep -q "ros2_controllers.yaml" src/dog2_description/urdf/dog2.urdf.xacro; then
    echo "   ✓ dog2.urdf.xacro 包含控制器配置路径"
else
    echo "   ✗ dog2.urdf.xacro 缺少控制器配置路径"
    exit 1
fi

# 检查 dog2.urdf 是否包含配置路径
echo ""
echo "3. 检查 dog2.urdf 配置..."
if grep -q "ros2_controllers.yaml" src/dog2_description/urdf/dog2.urdf; then
    echo "   ✓ dog2.urdf 包含控制器配置路径"
else
    echo "   ✗ dog2.urdf 缺少控制器配置路径"
    exit 1
fi

# 检查配置文件内容
echo ""
echo "4. 检查控制器配置内容..."
if grep -q "joint_state_broadcaster" src/dog2_description/config/ros2_controllers.yaml && \
   grep -q "joint_group_effort_controller" src/dog2_description/config/ros2_controllers.yaml; then
    echo "   ✓ 控制器配置包含必要的控制器"
else
    echo "   ✗ 控制器配置不完整"
    exit 1
fi

# 检查所有关节是否在配置中
echo ""
echo "5. 检查关节配置..."
JOINTS=("j1" "j11" "j111" "j2" "j21" "j211" "j3" "j31" "j311" "j4" "j41" "j411")
MISSING_JOINTS=0

for joint in "${JOINTS[@]}"; do
    if ! grep -q "\- $joint" src/dog2_description/config/ros2_controllers.yaml; then
        echo "   ✗ 缺少关节: $joint"
        MISSING_JOINTS=$((MISSING_JOINTS + 1))
    fi
done

if [ $MISSING_JOINTS -eq 0 ]; then
    echo "   ✓ 所有 12 个关节都已配置"
else
    echo "   ✗ 缺少 $MISSING_JOINTS 个关节配置"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 所有检查通过！"
echo "=========================================="
echo ""
echo "Gazebo ROS 2 Control 配置已正确设置。"
echo "现在启动 Gazebo 时，机器人关节将能够正常控制。"
echo ""
