#!/bin/bash

# 交互式调整j21位置脚本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  J21位置调整工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

URDF_FILE="src/dog2_description/urdf/dog2.urdf.xacro"

# 显示当前配置
echo "当前Leg 2配置:"
sed -n '210p' "$URDF_FILE"
echo ""

echo "当前使用的hip_xyz默认值: -0.016 0.0199 0.055"
echo ""

echo "可选的修复方案:"
echo ""
echo "1. 为Leg 2添加自定义hip_xyz参数"
echo "2. 调整Leg 2的prismatic joint位置(xyz)"
echo "3. 查看Leg 1配置作为参考"
echo "4. 退出"
echo ""

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "请输入新的hip_xyz值 (格式: x y z)"
        echo "当前默认值: -0.016 0.0199 0.055"
        echo "示例: 0.016 0.0199 0.055"
        read -p "新值: " new_hip_xyz
        
        if [ -n "$new_hip_xyz" ]; then
            # 备份当前文件
            cp "$URDF_FILE" "${URDF_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
            echo "✓ 已备份当前文件"
            
            # 修改Leg 2配置
            sed -i '210s|thigh_xyz="${leg12_thigh_xyz}" shin_xyz="${leg12_shin_xyz}"/>|thigh_xyz="${leg12_thigh_xyz}" shin_xyz="${leg12_shin_xyz}"\n             hip_xyz="'"$new_hip_xyz"'"/>|' "$URDF_FILE"
            
            echo "✓ 已更新Leg 2配置"
            echo ""
            echo "新配置:"
            sed -n '210,211p' "$URDF_FILE"
            echo ""
            
            read -p "是否立即编译并测试？(y/n): " test_now
            if [ "$test_now" = "y" ]; then
                echo ""
                echo "正在编译..."
                colcon build --packages-select dog2_description --symlink-install
                
                if [ $? -eq 0 ]; then
                    echo "✓ 编译成功"
                    echo ""
                    echo "启动RViz查看效果..."
                    killall -9 robot_state_publisher joint_state_publisher rviz2 2>/dev/null
                    sleep 1
                    source install/setup.bash
                    ros2 launch dog2_description view_dog2.launch.py &
                else
                    echo "❌ 编译失败"
                fi
            fi
        fi
        ;;
    
    2)
        echo ""
        echo "请输入新的prismatic joint位置 (格式: x y z)"
        echo "当前值: 1.3491 -0.80953 0.2649"
        echo "Leg 1参考: 1.1026 -0.80953 0.2649"
        read -p "新值: " new_xyz
        
        if [ -n "$new_xyz" ]; then
            # 备份当前文件
            cp "$URDF_FILE" "${URDF_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
            echo "✓ 已备份当前文件"
            
            # 修改Leg 2的xyz
            sed -i "210s|xyz=\"1.3491 -0.80953 0.2649\"|xyz=\"$new_xyz\"|" "$URDF_FILE"
            
            echo "✓ 已更新Leg 2配置"
            echo ""
            echo "新配置:"
            sed -n '210p' "$URDF_FILE"
            echo ""
            
            read -p "是否立即编译并测试？(y/n): " test_now
            if [ "$test_now" = "y" ]; then
                echo ""
                echo "正在编译..."
                colcon build --packages-select dog2_description --symlink-install
                
                if [ $? -eq 0 ]; then
                    echo "✓ 编译成功"
                    echo ""
                    echo "启动RViz查看效果..."
                    killall -9 robot_state_publisher joint_state_publisher rviz2 2>/dev/null
                    sleep 1
                    source install/setup.bash
                    ros2 launch dog2_description view_dog2.launch.py &
                else
                    echo "❌ 编译失败"
                fi
            fi
        fi
        ;;
    
    3)
        echo ""
        echo "Leg 1配置（参考）:"
        sed -n '207,208p' "$URDF_FILE"
        echo ""
        echo "Leg 2配置（当前）:"
        sed -n '210p' "$URDF_FILE"
        echo ""
        ;;
    
    4)
        echo "退出"
        exit 0
        ;;
    
    *)
        echo "无效选择"
        exit 1
        ;;
esac
