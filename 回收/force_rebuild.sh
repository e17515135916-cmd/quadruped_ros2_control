#!/bin/bash
# 强制重新编译 dog2_description

echo "=========================================="
echo "强制重新编译 dog2_description"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash

echo "1. 删除旧的编译文件..."
rm -rf build/dog2_description install/dog2_description log/dog2_description
echo "✅ 已删除"
echo ""

echo "2. 重新编译..."
colcon build --packages-select dog2_description --symlink-install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 编译成功！"
    echo ""
    
    # 验证
    echo "3. 验证 URDF..."
    if grep -q "lf_haa_joint" install/dog2_description/share/dog2_description/urdf/dog2.urdf.xacro; then
        count=$(grep -c "lf_haa_joint" install/dog2_description/share/dog2_description/urdf/dog2.urdf.xacro)
        echo "✅ 找到 lf_haa_joint ($count 次)"
    else
        echo "❌ 未找到 lf_haa_joint"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "下一步"
    echo "=========================================="
    echo ""
    echo "1. Source 环境:"
    echo "   source install/setup.bash"
    echo ""
    echo "2. 停止当前 Gazebo (Ctrl+C)"
    echo ""
    echo "3. 重新启动:"
    echo "   ./quick_start_keyboard_control.sh"
    echo ""
    echo "4. 等待 10 秒后验证:"
    echo "   ros2 control list_hardware_interfaces"
else
    echo ""
    echo "❌ 编译失败"
    exit 1
fi
