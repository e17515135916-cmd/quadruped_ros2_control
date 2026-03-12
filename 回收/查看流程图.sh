#!/bin/bash
# 查看Dog2控制架构流程图

cd ~/aperfect/carbot_ws

echo "========================================="
echo "  查看Dog2控制架构流程图"
echo "========================================="
echo ""
echo "选择查看方式："
echo ""
echo "1. 在VS Code中查看（推荐）"
echo "2. 在浏览器中查看（在线工具）"
echo "3. 导出为PNG图片"
echo "4. 查看文本版本"
echo ""

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "正在用VS Code打开..."
        echo ""
        echo "💡 提示："
        echo "1. 确保安装了 'Markdown Preview Mermaid Support' 插件"
        echo "2. 按 Ctrl+Shift+V 打开预览"
        echo "3. 流程图会自动渲染"
        echo ""
        code DOG2_CONTROL_ARCHITECTURE.md
        ;;
    2)
        echo ""
        echo "正在打开在线Mermaid编辑器..."
        echo ""
        echo "💡 使用方法："
        echo "1. 浏览器会打开 Mermaid Live Editor"
        echo "2. 复制文件中的mermaid代码块"
        echo "3. 粘贴到左侧编辑器"
        echo "4. 右侧会显示流程图"
        echo ""
        xdg-open "https://mermaid.live/" 2>/dev/null || \
        firefox "https://mermaid.live/" 2>/dev/null || \
        google-chrome "https://mermaid.live/" 2>/dev/null || \
        echo "请手动打开浏览器访问: https://mermaid.live/"
        
        echo ""
        echo "Mermaid代码已准备好，按回车复制到剪贴板..."
        read
        
        # 提取mermaid代码
        sed -n '/```mermaid/,/```/p' DOG2_CONTROL_ARCHITECTURE.md | \
        grep -v '```' | xclip -selection clipboard 2>/dev/null || \
        echo "请手动复制文件中的mermaid代码块"
        ;;
    3)
        echo ""
        echo "导出为PNG图片..."
        echo ""
        
        # 检查是否安装了mermaid-cli
        if ! command -v mmdc &> /dev/null; then
            echo "❌ 未安装 mermaid-cli"
            echo ""
            echo "安装方法："
            echo "  sudo npm install -g @mermaid-js/mermaid-cli"
            echo ""
            read -p "是否现在安装？(y/n): " install
            
            if [ "$install" = "y" ]; then
                sudo npm install -g @mermaid-js/mermaid-cli
                if [ $? -eq 0 ]; then
                    echo "✅ 安装成功"
                else
                    echo "❌ 安装失败"
                    exit 1
                fi
            else
                exit 0
            fi
        fi
        
        # 提取mermaid代码到临时文件
        sed -n '/```mermaid/,/```/p' DOG2_CONTROL_ARCHITECTURE.md | \
        grep -v '```' > /tmp/dog2_architecture.mmd
        
        # 转换为PNG
        mmdc -i /tmp/dog2_architecture.mmd -o DOG2_CONTROL_ARCHITECTURE.png
        
        if [ $? -eq 0 ]; then
            echo "✅ 导出成功！"
            echo ""
            echo "图片位置：DOG2_CONTROL_ARCHITECTURE.png"
            echo ""
            read -p "是否现在打开图片？(y/n): " open
            
            if [ "$open" = "y" ]; then
                xdg-open DOG2_CONTROL_ARCHITECTURE.png 2>/dev/null || \
                eog DOG2_CONTROL_ARCHITECTURE.png 2>/dev/null || \
                echo "请手动打开: DOG2_CONTROL_ARCHITECTURE.png"
            fi
        else
            echo "❌ 导出失败"
        fi
        ;;
    4)
        echo ""
        echo "========================================="
        echo "  Dog2控制架构（文本版）"
        echo "========================================="
        echo ""
        cat DOG2_CONTROL_ARCHITECTURE.md | less
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  文件位置"
echo "========================================="
echo ""
echo "Markdown文档："
echo "  ~/aperfect/carbot_ws/DOG2_CONTROL_ARCHITECTURE.md"
echo ""
echo "在线查看："
echo "  https://mermaid.live/"
echo ""
