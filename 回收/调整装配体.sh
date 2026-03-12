#!/bin/bash
# 交互式调整Dog2机器人装配体关系

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  Dog2机器人装配体调整工具"
echo "========================================="
echo ""
echo "💡 装配关系存储在URDF文件中，不在mesh文件里！"
echo ""
echo "工作流程："
echo "1. 在RViz中查看当前装配体"
echo "2. 编辑URDF文件调整装配关系"
echo "3. 重新编译并查看效果"
echo "4. 重复直到满意"
echo ""
echo "========================================="
echo ""

echo "选择操作："
echo ""
echo "1. 启动RViz查看当前装配体"
echo "2. 编辑URDF文件（nano编辑器）"
echo "3. 编辑URDF文件（VS Code）"
echo "4. 重新编译URDF"
echo "5. 查看装配体调整指南"
echo "6. 查看当前关节配置"
echo ""

read -p "请选择 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "正在启动RViz..."
        echo ""
        echo "💡 RViz操作提示："
        echo "  - 启用TF显示：Add → TF"
        echo "  - 查看坐标系：可以看到每个link的位置"
        echo "  - 旋转视图：鼠标左键拖动"
        echo "  - 缩放：鼠标滚轮"
        echo ""
        source install/setup.bash
        ros2 launch dog2_description view_dog2.launch.py
        ;;
    2)
        echo ""
        echo "正在用nano打开URDF文件..."
        echo ""
        echo "💡 编辑提示："
        echo "  - 查找关节：Ctrl+W 输入 'j11' 等"
        echo "  - 修改origin标签中的xyz和rpy参数"
        echo "  - 保存：Ctrl+O，回车"
        echo "  - 退出：Ctrl+X"
        echo ""
        echo "关键参数："
        echo "  xyz=\"X Y Z\" - 位置偏移（米）"
        echo "  rpy=\"Roll Pitch Yaw\" - 旋转角度（弧度）"
        echo ""
        read -p "按回车继续..."
        nano src/dog2_description/urdf/dog2.urdf.xacro
        ;;
    3)
        echo ""
        echo "正在用VS Code打开URDF文件..."
        code src/dog2_description/urdf/dog2.urdf.xacro
        ;;
    4)
        echo ""
        echo "正在重新编译..."
        echo ""
        
        # 备份
        timestamp=$(date +%Y%m%d_%H%M%S)
        cp src/dog2_description/urdf/dog2.urdf.xacro \
           src/dog2_description/urdf/dog2.urdf.xacro.backup_$timestamp
        echo "✅ 已备份URDF文件：dog2.urdf.xacro.backup_$timestamp"
        echo ""
        
        # 编译
        colcon build --packages-select dog2_description
        
        if [ $? -eq 0 ]; then
            source install/setup.bash
            echo ""
            echo "========================================="
            echo "  ✅ 编译成功！"
            echo "========================================="
            echo ""
            read -p "是否立即在RViz中查看？(y/n): " view
            
            if [ "$view" = "y" ]; then
                ros2 launch dog2_description view_dog2.launch.py
            else
                echo ""
                echo "手动查看命令："
                echo "  ros2 launch dog2_description view_dog2.launch.py"
            fi
        else
            echo ""
            echo "❌ 编译失败，请检查URDF语法"
        fi
        ;;
    5)
        echo ""
        if [ -f "修改装配体关系指南.md" ]; then
            cat 修改装配体关系指南.md | less
        else
            echo "指南文件不存在"
        fi
        ;;
    6)
        echo ""
        echo "========================================="
        echo "  当前关节配置"
        echo "========================================="
        echo ""
        echo "髋关节配置（已改为XYY）："
        echo ""
        grep -A 5 "Hip joint" src/dog2_description/urdf/dog2.urdf.xacro | head -20
        echo ""
        echo "详细信息请查看URDF文件"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  快速参考"
echo "========================================="
echo ""
echo "角度转换："
echo "  90° = 1.5708 rad"
echo "  180° = 3.1416 rad"
echo "  270° = 4.7124 rad"
echo ""
echo "坐标轴："
echo "  X轴（红色）：前后"
echo "  Y轴（绿色）：左右"
echo "  Z轴（蓝色）：上下"
echo ""
echo "URDF文件位置："
echo "  src/dog2_description/urdf/dog2.urdf.xacro"
echo ""
