#!/bin/bash
# 测试j31和j41设置为180度（3.142弧度）的效果

echo "=== 测试j31和j41初始位置为180度 ==="
echo ""
echo "步骤："
echo "1. 启动RViz（在另一个终端）"
echo "2. 运行此脚本设置j31和j41为3.142弧度"
echo "3. 观察后腿是否向下弯曲"
echo ""
echo "按Enter继续..."
read

# 确保环境已source
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "正在设置j31和j41为3.142弧度..."
python3 set_j31_j41_initial_position.py

echo ""
echo "完成！请在RViz中查看效果："
echo "- j31（腿3的髋关节）应该向下弯曲"
echo "- j41（腿4的髋关节）应该向下弯曲"
echo "- 如果效果正确，我们需要将这个角度设为默认初始位置"
