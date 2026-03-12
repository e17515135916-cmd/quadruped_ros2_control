#!/bin/bash
# 测试 HAA 关节的外展/内收功能

echo "=========================================="
echo "HAA 关节外展/内收测试"
echo "=========================================="
echo ""
echo "步骤 1: 启动 RViz"
echo "步骤 2: 运行测试脚本"
echo ""
echo "请在另一个终端运行以下命令启动 RViz:"
echo "  ./start_champ_rviz_test.sh"
echo ""
echo "然后按 Enter 继续..."
read

echo ""
echo "启动测试脚本..."
source install/setup.bash
python3 test_haa_abduction.py
