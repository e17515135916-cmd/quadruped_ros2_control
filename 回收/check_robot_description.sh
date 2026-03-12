#!/bin/bash
# 检查 robot_description 话题

echo "=========================================="
echo "检查 robot_description"
echo "=========================================="
echo ""

# Source 环境
source /opt/ros/humble/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

echo "1. 检查 robot_description 话题是否存在..."
if ros2 topic list | grep -q "/robot_description"; then
    echo "✅ robot_description 话题存在"
else
    echo "❌ robot_description 话题不存在"
    exit 1
fi
echo ""

echo "2. 获取 robot_description 内容..."
ros2 topic echo /robot_description --once > /tmp/robot_desc_from_topic.txt 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 成功获取"
    
    # 检查关节
    echo ""
    echo "3. 检查 CHAMP 关节..."
    for joint in lf_haa_joint lf_hfe_joint lf_kfe_joint rf_haa_joint rf_hfe_joint rf_kfe_joint; do
        if grep -q "\"$joint\"" /tmp/robot_desc_from_topic.txt; then
            echo "  ✅ $joint"
        else
            echo "  ❌ $joint (未找到)"
        fi
    done
    
    echo ""
    echo "4. 检查 ros2_control 部分..."
    if grep -q "<ros2_control" /tmp/robot_desc_from_topic.txt; then
        echo "✅ 找到 ros2_control 标签"
        
        # 统计关节数
        joint_count=$(grep -o '<joint name=' /tmp/robot_desc_from_topic.txt | wc -l)
        ros2_control_joint_count=$(sed -n '/<ros2_control/,/<\/ros2_control>/p' /tmp/robot_desc_from_topic.txt | grep -c '<joint name=')
        
        echo "  总关节数: $joint_count"
        echo "  ros2_control 中的关节数: $ros2_control_joint_count"
    else
        echo "❌ 未找到 ros2_control 标签"
    fi
else
    echo "❌ 无法获取 robot_description"
    echo "   系统可能未启动"
fi
