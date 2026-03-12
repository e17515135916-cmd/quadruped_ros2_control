#!/bin/bash
# 下载宇树Go2机器人的ROS2模型作为参考

echo "=========================================="
echo "  下载宇树Go2 ROS2模型"
echo "=========================================="
echo ""

# 创建临时目录
TEMP_DIR="/tmp/unitree_go2_reference"
mkdir -p $TEMP_DIR

echo "步骤1: 克隆宇树Go2 ROS2仓库..."
cd $TEMP_DIR

# 宇树官方ROS2仓库
git clone https://github.com/unitreerobotics/unitree_ros2.git

echo ""
echo "步骤2: 查找Go2模型文件..."
find unitree_ros2 -name "*go2*" -o -name "*urdf*" -o -name "*xacro*" | grep -E "\.(urdf|xacro)$"

echo ""
echo "=========================================="
echo "参考文件位置:"
echo "=========================================="
echo "  URDF/Xacro: $TEMP_DIR/unitree_ros2/"
echo ""
echo "你可以参考以下内容:"
echo "  • 碰撞模型配置"
echo "  • Origin偏移设置"
echo "  • Gazebo参数配置"
echo "  • 接触参数设置"
echo ""
echo "查看文件:"
echo "  cd $TEMP_DIR/unitree_ros2"
echo "  find . -name '*.urdf' -o -name '*.xacro'"
