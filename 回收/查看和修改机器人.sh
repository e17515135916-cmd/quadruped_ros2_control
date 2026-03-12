#!/bin/bash
# 查看和修改Dog2机器人装配体的辅助脚本

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  Dog2机器人装配体修改助手"
echo "========================================="
echo ""
echo "这个脚本会帮助你："
echo "1. 在RViz中查看正确的机器人装配体"
echo "2. 打开URDF文件进行编辑"
echo "3. 重新编译并查看修改结果"
echo ""

# 检查是否source了环境
if [ -z "$ROS_DISTRO" ]; then
    echo "正在设置ROS环境..."
    source install/setup.bash
fi

echo "========================================="
echo "  选择操作："
echo "========================================="
echo ""
echo "1) 在RViz中查看机器人"
echo "2) 编辑URDF文件"
echo "3) 重新编译URDF"
echo "4) 编译后在RViz中查看"
echo "5) 完整流程（编辑→编译→查看）"
echo "6) 备份URDF文件"
echo "7) 恢复URDF备份"
echo "8) 角度转换工具"
echo "9) 退出"
echo ""
read -p "请选择 (1-9): " choice

case $choice in
    1)
        echo ""
        echo "正在启动RViz..."
        echo "提示："
        echo "- 鼠标左键拖动：旋转视图"
        echo "- 鼠标中键拖动：平移视图"
        echo "- 鼠标滚轮：缩放"
        echo "- 勾选左侧的'TF'可以看到坐标系"
        echo ""
        ros2 launch dog2_description view_dog2.launch.py
        ;;
    2)
        echo ""
        echo "正在打开URDF文件..."
        echo "文件位置: src/dog2_description/urdf/dog2.urdf.xacro"
        echo ""
        echo "修改提示："
        echo "- 搜索joint名称（如 j11, j111）"
        echo "- 修改 origin 的 xyz（位置，单位：米）"
        echo "- 修改 origin 的 rpy（旋转，单位：弧度）"
        echo "- 保存后运行选项3重新编译"
        echo ""
        gedit src/dog2_description/urdf/dog2.urdf.xacro
        ;;
    3)
        echo ""
        echo "正在重新编译URDF..."
        colcon build --packages-select dog2_description
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 编译成功！"
            echo "运行选项1在RViz中查看修改结果"
            source install/setup.bash
        else
            echo ""
            echo "❌ 编译失败，请检查URDF文件语法"
        fi
        ;;
    4)
        echo ""
        echo "正在重新编译并启动RViz..."
        colcon build --packages-select dog2_description
        if [ $? -eq 0 ]; then
            source install/setup.bash
            echo ""
            echo "✅ 编译成功！正在启动RViz..."
            ros2 launch dog2_description view_dog2.launch.py
        else
            echo ""
            echo "❌ 编译失败，请检查URDF文件语法"
        fi
        ;;
    5)
        echo ""
        echo "=== 完整修改流程 ==="
        echo ""
        echo "步骤1: 打开URDF文件进行编辑"
        echo "（编辑完成后保存并关闭编辑器）"
        echo ""
        read -p "按Enter继续..."
        gedit src/dog2_description/urdf/dog2.urdf.xacro
        
        echo ""
        echo "步骤2: 重新编译URDF"
        colcon build --packages-select dog2_description
        
        if [ $? -eq 0 ]; then
            source install/setup.bash
            echo ""
            echo "✅ 编译成功！"
            echo ""
            echo "步骤3: 在RViz中查看修改结果"
            read -p "按Enter启动RViz..."
            ros2 launch dog2_description view_dog2.launch.py
        else
            echo ""
            echo "❌ 编译失败，请检查URDF文件语法"
        fi
        ;;
    6)
        echo ""
        echo "正在备份URDF文件..."
        BACKUP_FILE="src/dog2_description/urdf/dog2.urdf.xacro.backup_$(date +%Y%m%d_%H%M%S)"
        cp src/dog2_description/urdf/dog2.urdf.xacro "$BACKUP_FILE"
        echo "✅ 备份完成: $BACKUP_FILE"
        ;;
    7)
        echo ""
        echo "可用的备份文件："
        ls -lh src/dog2_description/urdf/dog2.urdf.xacro.backup* 2>/dev/null
        echo ""
        read -p "输入要恢复的备份文件名（或按Enter取消）: " backup_file
        if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
            cp "$backup_file" src/dog2_description/urdf/dog2.urdf.xacro
            echo "✅ 已恢复备份"
            echo "运行选项3重新编译"
        else
            echo "取消恢复"
        fi
        ;;
    8)
        echo ""
        echo "=== 角度转换工具 ==="
        echo ""
        echo "1) 度 → 弧度"
        echo "2) 弧度 → 度"
        echo ""
        read -p "选择 (1-2): " conv_choice
        
        if [ "$conv_choice" = "1" ]; then
            read -p "输入角度（度）: " degrees
            python3 -c "import math; print(f'{$degrees}° = {math.radians($degrees):.4f} 弧度')"
        elif [ "$conv_choice" = "2" ]; then
            read -p "输入角度（弧度）: " radians
            python3 -c "import math; print(f'{$radians} 弧度 = {math.degrees($radians):.2f}°')"
        fi
        echo ""
        read -p "按Enter继续..."
        ;;
    9)
        echo "再见！"
        exit 0
        ;;
    *)
        echo "无效选择"
        ;;
esac
