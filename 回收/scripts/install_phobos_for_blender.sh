#!/bin/bash
# 自动安装Phobos插件到Blender

set -e

echo "=== Phobos插件自动安装脚本 ==="
echo ""

# 检查Blender是否已安装
if ! command -v blender &> /dev/null; then
    echo "❌ Blender未安装，正在安装..."
    sudo snap install blender --classic
    echo "✅ Blender安装完成"
else
    echo "✅ Blender已安装"
    blender --version
fi

echo ""
echo "=== 下载Phobos插件 ==="

# 创建下载目录
DOWNLOAD_DIR="$HOME/Downloads"
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# 检查是否已下载
if [ -d "phobos" ]; then
    echo "⚠️  Phobos目录已存在，正在更新..."
    cd phobos
    git pull
    cd ..
else
    echo "📥 正在下载Phobos..."
    git clone https://github.com/dfki-ric/phobos.git
fi

echo "✅ Phobos下载完成: $DOWNLOAD_DIR/phobos"
echo ""

# 获取Blender配置目录
BLENDER_VERSION=$(blender --version | grep "Blender" | awk '{print $2}' | cut -d'.' -f1-2)
BLENDER_CONFIG="$HOME/.config/blender/${BLENDER_VERSION}"
ADDONS_DIR="${BLENDER_CONFIG}/scripts/addons"

echo "=== 安装Phobos到Blender ==="
echo "Blender版本: $BLENDER_VERSION"
echo "配置目录: $BLENDER_CONFIG"

# 创建addons目录
mkdir -p "$ADDONS_DIR"

# 复制或链接phobos到addons目录
if [ -L "$ADDONS_DIR/phobos" ]; then
    echo "⚠️  Phobos链接已存在，正在更新..."
    rm "$ADDONS_DIR/phobos"
fi

if [ -d "$ADDONS_DIR/phobos" ]; then
    echo "⚠️  Phobos目录已存在，正在删除..."
    rm -rf "$ADDONS_DIR/phobos"
fi

echo "📦 正在安装Phobos..."
ln -s "$DOWNLOAD_DIR/phobos/phobos" "$ADDONS_DIR/phobos"

echo "✅ Phobos已安装到: $ADDONS_DIR/phobos"
echo ""

echo "=== 安装Python依赖 ==="
# Phobos需要一些Python库
BLENDER_PYTHON=$(blender --background --python-expr "import sys; print(sys.executable)" 2>&1 | grep -o "/.*python.*")

if [ -n "$BLENDER_PYTHON" ]; then
    echo "Blender Python路径: $BLENDER_PYTHON"
    echo "正在安装依赖..."
    
    # 安装pip（如果没有）
    $BLENDER_PYTHON -m ensurepip 2>/dev/null || true
    
    # 安装必要的库
    $BLENDER_PYTHON -m pip install --upgrade pip 2>/dev/null || true
    $BLENDER_PYTHON -m pip install numpy pyyaml 2>/dev/null || true
    
    echo "✅ Python依赖安装完成"
else
    echo "⚠️  无法找到Blender Python，请手动安装依赖"
fi

echo ""
echo "=== 启用Phobos插件 ==="
echo ""
echo "现在需要在Blender中手动启用插件："
echo ""
echo "1. 打开Blender"
echo "2. Edit → Preferences (或按 F4 → Preferences)"
echo "3. 点击左侧 'Add-ons' 标签"
echo "4. 在搜索框输入 'phobos'"
echo "5. 勾选 'Import-Export: Phobos' 前面的复选框"
echo "6. 点击左下角 'Save Preferences' 保存设置"
echo ""
echo "启用后，File → Import 菜单中会出现 'URDF (.urdf)' 选项"
echo ""

# 创建一个测试脚本
cat > "$DOWNLOAD_DIR/test_phobos.py" << 'EOF'
import bpy
import sys

# 检查phobos是否可用
try:
    import phobos
    print("✅ Phobos模块导入成功")
    print(f"Phobos版本: {phobos.__version__ if hasattr(phobos, '__version__') else '未知'}")
    print(f"Phobos路径: {phobos.__file__}")
except ImportError as e:
    print(f"❌ Phobos模块导入失败: {e}")
    sys.exit(1)

# 检查URDF导入功能
if hasattr(bpy.ops, 'import_scene') and hasattr(bpy.ops.import_scene, 'urdf'):
    print("✅ URDF导入功能可用")
else:
    print("⚠️  URDF导入功能不可用，请在Blender中启用Phobos插件")
EOF

echo "=== 测试Phobos安装 ==="
echo "正在测试..."
blender --background --python "$DOWNLOAD_DIR/test_phobos.py" 2>&1 | grep -E "✅|❌|⚠️" || echo "⚠️  测试脚本执行完成，请查看上方输出"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "📍 Phobos源码位置: $DOWNLOAD_DIR/phobos"
echo "📍 Blender插件位置: $ADDONS_DIR/phobos"
echo "📍 测试脚本位置: $DOWNLOAD_DIR/test_phobos.py"
echo ""
echo "🎯 下一步："
echo "1. 打开Blender"
echo "2. Edit → Preferences → Add-ons"
echo "3. 搜索 'phobos' 并启用"
echo "4. File → Import → URDF (.urdf)"
echo "5. 选择你的URDF文件: $(pwd)/src/dog2_description/urdf/dog2.urdf"
echo ""
echo "如果遇到问题，运行以下命令查看详细信息："
echo "  blender --background --python $DOWNLOAD_DIR/test_phobos.py"
echo ""
