#!/bin/bash

# 快速测试新的L1 mesh

set -e

echo "=========================================="
echo "测试新的L1 Mesh"
echo "=========================================="
echo ""

WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$WORKSPACE_DIR"

# 步骤1：替换mesh文件
echo "步骤1：替换mesh文件"
./替换新l1mesh.sh

# 步骤2：编译
echo ""
echo "步骤2：编译..."
colcon build --packages-select dog2_description

if [ $? -ne 0 ]; then
    echo "✗ 编译失败"
    exit 1
fi

echo "✓ 编译成功"

# 步骤3：source环境
echo ""
echo "步骤3：设置环境..."
source install/setup.bash

# 步骤4：启动RViz查看
echo ""
echo "步骤4：启动RViz查看..."
echo ""
echo "正在启动RViz，请检查L1部件是否正确显示..."
echo ""

ros2 launch dog2_description view_dog2.launch.py
