#!/bin/bash
# 测试单个文件的凸包生成
# 用于在批量处理前验证流程

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}单文件凸包测试${NC}"
echo -e "${GREEN}========================================${NC}"

# 默认测试文件
TEST_FILE="${1:-l111.STL}"

echo -e "${YELLOW}测试文件:${NC} $TEST_FILE"
echo ""

# 检查 Blender
if ! command -v blender &> /dev/null; then
    echo "错误: 未找到 Blender"
    exit 1
fi

# 创建临时 Python 脚本
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'EOF'
import bpy
import os
import sys

# 配置
input_file = sys.argv[-1]
input_dir = "src/dog2_description/meshes"
output_dir = "src/dog2_description/meshes/collision"

input_path = os.path.join(input_dir, input_file)
output_file = input_file.replace('.STL', '_collision.STL')
output_path = os.path.join(output_dir, output_file)

print(f"\n处理: {input_file}")
print(f"输入: {input_path}")
print(f"输出: {output_path}\n")

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 导入
bpy.ops.import_mesh.stl(filepath=input_path)
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

print(f"原始面数: {len(obj.data.polygons)}")

# 凸包
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.convex_hull()
bpy.ops.object.mode_set(mode='OBJECT')

print(f"凸包面数: {len(obj.data.polygons)}")

# 简化
if len(obj.data.polygons) > 300:
    modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
    modifier.ratio = 0.35
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print(f"简化后面数: {len(obj.data.polygons)}")

# 清理
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles()
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# 导出
os.makedirs(output_dir, exist_ok=True)
bpy.ops.export_mesh.stl(
    filepath=output_path,
    use_selection=True,
    axis_forward='Y',
    axis_up='Z'
)

print(f"\n✅ 成功生成: {output_file}")
print(f"   位置: {output_path}")
EOF

# 运行 Blender
blender --background --python "$TEMP_SCRIPT" -- "$TEST_FILE"

# 清理
rm "$TEMP_SCRIPT"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "检查生成的文件:"
echo "  ls -lh src/dog2_description/meshes/collision/"
echo ""
echo "如果满意，运行完整批量处理:"
echo "  ./scripts/generate_convex_hulls.sh"
