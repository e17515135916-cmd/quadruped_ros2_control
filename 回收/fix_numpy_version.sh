#!/bin/bash
# 修复NumPy版本冲突

echo "=========================================="
echo "修复NumPy版本冲突"
echo "=========================================="

# 1. 卸载NumPy 2.x
echo "正在卸载NumPy 2.x..."
pip3 uninstall -y numpy

# 2. 安装NumPy 1.x（兼容版本）
echo "正在安装NumPy 1.24.x（兼容版本）..."
pip3 install --user "numpy<2.0,>=1.21"

# 3. 验证版本
echo ""
echo "=========================================="
echo "验证NumPy版本："
python3 -c "import numpy; print(f'NumPy版本: {numpy.__version__}')"

echo ""
echo "✓ 修复完成！"
echo "现在运行: python3 verify_installation.py"
echo "=========================================="

