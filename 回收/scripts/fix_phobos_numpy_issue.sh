#!/bin/bash
# 修复Phobos的numpy兼容性问题

set -e

echo "=== 修复Phobos numpy兼容性问题 ==="
echo ""

# 获取Blender的Python路径
echo "正在查找Blender Python..."
BLENDER_PYTHON=$(blender --background --python-expr "import sys; print(sys.executable)" 2>&1 | grep -o "/.*python.*" | head -1)

if [ -z "$BLENDER_PYTHON" ]; then
    echo "❌ 无法找到Blender Python"
    echo "尝试使用snap版本的路径..."
    BLENDER_PYTHON="/snap/blender/current/3.0/python/bin/python3.10"
fi

echo "Blender Python: $BLENDER_PYTHON"
echo ""

# 检查Python是否可执行
if [ ! -f "$BLENDER_PYTHON" ]; then
    echo "❌ Python路径不存在: $BLENDER_PYTHON"
    echo ""
    echo "尝试查找snap安装的Blender Python..."
    SNAP_PYTHON=$(find /snap/blender -name "python3.*" -type f 2>/dev/null | head -1)
    if [ -n "$SNAP_PYTHON" ]; then
        BLENDER_PYTHON="$SNAP_PYTHON"
        echo "✅ 找到: $BLENDER_PYTHON"
    else
        echo "❌ 无法找到Blender Python"
        exit 1
    fi
fi

echo "=== 卸载旧的依赖 ==="
$BLENDER_PYTHON -m pip uninstall -y numpy scipy trimesh 2>/dev/null || true

echo ""
echo "=== 重新安装兼容的依赖 ==="
echo "安装numpy..."
$BLENDER_PYTHON -m pip install --upgrade --force-reinstall numpy

echo ""
echo "安装scipy（这可能需要几分钟）..."
$BLENDER_PYTHON -m pip install --upgrade scipy

echo ""
echo "安装trimesh..."
$BLENDER_PYTHON -m pip install --upgrade trimesh

echo ""
echo "安装pyyaml..."
$BLENDER_PYTHON -m pip install --upgrade pyyaml

echo ""
echo "✅ 依赖安装完成"
echo ""

echo "=== 测试Phobos ==="
cat > /tmp/test_phobos_imports.py << 'EOF'
import sys
print("Python版本:", sys.version)
print("")

try:
    import numpy
    print("✅ numpy:", numpy.__version__)
except Exception as e:
    print("❌ numpy导入失败:", e)

try:
    import scipy
    print("✅ scipy:", scipy.__version__)
except Exception as e:
    print("❌ scipy导入失败:", e)

try:
    import trimesh
    print("✅ trimesh:", trimesh.__version__)
except Exception as e:
    print("❌ trimesh导入失败:", e)

try:
    import yaml
    print("✅ yaml: 已安装")
except Exception as e:
    print("❌ yaml导入失败:", e)

print("")
try:
    import phobos
    print("✅ phobos: 导入成功")
except Exception as e:
    print("❌ phobos导入失败:", e)
EOF

echo "运行测试..."
blender --background --python /tmp/test_phobos_imports.py 2>&1 | grep -E "✅|❌|Python版本|numpy|scipy|trimesh|yaml|phobos"

echo ""
echo "=== 修复完成 ==="
echo ""
echo "🎯 下一步："
echo "1. 重启Blender"
echo "2. Edit → Preferences → Add-ons"
echo "3. 搜索 'phobos' 并启用"
echo ""
echo "如果还有问题，可能需要使用系统Python而不是Blender内置Python"
