#!/bin/bash

# ROS 2 控制系统架构图生成脚本
# 需要安装: npm install -g @mermaid-js/mermaid-cli

echo "正在生成 ROS 2 控制系统架构图..."

# 检查是否安装了 mmdc (mermaid-cli)
if ! command -v mmdc &> /dev/null
then
    echo "错误: 未找到 mermaid-cli"
    echo "请运行以下命令安装:"
    echo "  npm install -g @mermaid-js/mermaid-cli"
    echo ""
    echo "或者使用 Docker:"
    echo "  docker pull minlag/mermaid-cli"
    exit 1
fi

# 提取 Mermaid 代码到临时文件
sed -n '/```mermaid/,/```/p' ROS2_CONTROL_DATA_FLOW_DIAGRAM.md | sed '1d;$d' > /tmp/ros2_diagram.mmd

# 生成 PNG 图片 (高分辨率)
mmdc -i /tmp/ros2_diagram.mmd -o ros2_control_architecture.png -w 3000 -H 2400 -b transparent

# 生成 SVG 矢量图 (用于 PPT 缩放)
mmdc -i /tmp/ros2_diagram.mmd -o ros2_control_architecture.svg -b transparent

if [ -f "ros2_control_architecture.png" ]; then
    echo "✓ 成功生成 PNG 图片: ros2_control_architecture.png"
fi

if [ -f "ros2_control_architecture.svg" ]; then
    echo "✓ 成功生成 SVG 矢量图: ros2_control_architecture.svg"
fi

echo ""
echo "图片已生成，可以直接插入到 PPT 中！"
