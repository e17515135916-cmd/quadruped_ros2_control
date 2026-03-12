#!/bin/bash
# 在RViz2中查看备份的URDF文件（简化版）
# 文件: backups/before_restore_20260202_150821/dog2.urdf.xacro

echo "正在启动RViz2查看备份的URDF文件..."

# 获取当前工作目录
WORKSPACE_DIR=$(pwd)
BACKUP_XACRO="${WORKSPACE_DIR}/backups/before_restore_20260202_150821/dog2.urdf.xacro"

# 检查文件是否存在
if [ ! -f "$BACKUP_XACRO" ]; then
    echo "错误: 找不到备份文件 $BACKUP_XACRO"
    exit 1
fi

# 生成临时URDF文件
TEMP_URDF="/tmp/backup_dog2.urdf"
echo "正在将xacro转换为URDF..."
xacro "$BACKUP_XACRO" > "$TEMP_URDF"

if [ $? -ne 0 ]; then
    echo "错误: xacro转换失败"
    exit 1
fi

echo "URDF文件已生成: $TEMP_URDF"

# 启动robot_state_publisher（使用文件而不是命令行参数）
echo "正在启动robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher "$TEMP_URDF" &
RSP_PID=$!

# 等待一下让robot_state_publisher启动
sleep 2

# 启动joint_state_publisher（不带GUI）
echo "正在发布joint_states..."
ros2 run joint_state_publisher joint_state_publisher &
JSP_PID=$!

# 等待一下
sleep 1

# 启动RViz2
echo "正在启动RViz2..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "=========================================="
echo "RViz2已启动，查看备份URDF文件"
echo "=========================================="
echo "备份文件: backups/before_restore_20260202_150821/dog2.urdf.xacro"
echo ""
echo "在RViz2中："
echo "1. 点击左下角 'Add' 按钮"
echo "2. 选择 'RobotModel'"
echo "3. 设置 Fixed Frame 为 'base_link' 或 'world'"
echo "4. 可以添加 'TF' 来查看坐标系"
echo ""
echo "按 Ctrl+C 停止所有进程"
echo "=========================================="

# 等待用户中断
wait $RVIZ_PID

# 清理进程
echo "正在清理进程..."
kill $RSP_PID 2>/dev/null
kill $JSP_PID 2>/dev/null

echo "完成"
