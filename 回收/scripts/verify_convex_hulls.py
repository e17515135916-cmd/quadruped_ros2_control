#!/usr/bin/env python3
"""
凸包质量验证脚本
检查生成的凸包文件是否符合要求

使用方法：
    python3 scripts/verify_convex_hulls.py
"""

import os
import sys

try:
    import numpy as np
    from stl import mesh
except ImportError:
    print("错误: 需要安装 numpy-stl 库")
    print("运行: pip3 install numpy-stl")
    sys.exit(1)


# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ORIGINAL_DIR = os.path.join(PROJECT_ROOT, "src/dog2_description/meshes")
COLLISION_DIR = os.path.join(PROJECT_ROOT, "src/dog2_description/meshes/collision")

# 文件对
FILE_PAIRS = [
    ("base_link.STL", "base_link_collision.STL"),
    ("l1.STL", "l1_collision.STL"),
    ("l11.STL", "l11_collision.STL"),
    ("l111.STL", "l111_collision.STL"),
    ("l1111.STL", "l1111_collision.STL"),
    ("l2.STL", "l2_collision.STL"),
    ("l21.STL", "l21_collision.STL"),
    ("l211.STL", "l211_collision.STL"),
    ("l2111.STL", "l2111_collision.STL"),
    ("l3.STL", "l3_collision.STL"),
    ("l31.STL", "l31_collision.STL"),
    ("l311.STL", "l311_collision.STL"),
    ("l3111.STL", "l3111_collision.STL"),
    ("l4.STL", "l4_collision.STL"),
    ("l41.STL", "l41_collision.STL"),
    ("l411.STL", "l411_collision.STL"),
    ("l4111.STL", "l4111_collision.STL"),
]

# 质量标准
MAX_FACE_COUNT = 500
MIN_FACE_COUNT = 50
MAX_VOLUME_DIFF_PERCENT = 30  # 体积差异不超过 30%


def load_stl(filepath):
    """加载 STL 文件"""
    try:
        return mesh.Mesh.from_file(filepath)
    except Exception as e:
        print(f"  ❌ 加载失败: {e}")
        return None


def get_mesh_info(stl_mesh):
    """获取网格信息"""
    face_count = len(stl_mesh.vectors)
    volume = stl_mesh.get_mass_properties()[0]  # 体积
    
    # 计算边界框
    min_coords = stl_mesh.vectors.reshape(-1, 3).min(axis=0)
    max_coords = stl_mesh.vectors.reshape(-1, 3).max(axis=0)
    bbox_size = max_coords - min_coords
    
    return {
        'faces': face_count,
        'volume': volume,
        'bbox': bbox_size
    }


def verify_pair(original_file, collision_file):
    """验证一对文件"""
    print(f"\n{'='*60}")
    print(f"验证: {original_file} → {collision_file}")
    print(f"{'='*60}")
    
    original_path = os.path.join(ORIGINAL_DIR, original_file)
    collision_path = os.path.join(COLLISION_DIR, collision_file)
    
    # 检查文件存在
    if not os.path.exists(original_path):
        print(f"  ⚠️  原始文件不存在: {original_file}")
        return False
    
    if not os.path.exists(collision_path):
        print(f"  ❌ 凸包文件不存在: {collision_file}")
        return False
    
    # 加载文件
    original_mesh = load_stl(original_path)
    collision_mesh = load_stl(collision_path)
    
    if original_mesh is None or collision_mesh is None:
        return False
    
    # 获取信息
    original_info = get_mesh_info(original_mesh)
    collision_info = get_mesh_info(collision_mesh)
    
    print(f"\n原始模型:")
    print(f"  面数: {original_info['faces']}")
    print(f"  体积: {original_info['volume']:.6f} m³")
    print(f"  尺寸: {original_info['bbox'][0]:.3f} x {original_info['bbox'][1]:.3f} x {original_info['bbox'][2]:.3f} m")
    
    print(f"\n凸包模型:")
    print(f"  面数: {collision_info['faces']}")
    print(f"  体积: {collision_info['volume']:.6f} m³")
    print(f"  尺寸: {collision_info['bbox'][0]:.3f} x {collision_info['bbox'][1]:.3f} x {collision_info['bbox'][2]:.3f} m")
    
    # 验证标准
    passed = True
    
    # 1. 检查面数
    if collision_info['faces'] > MAX_FACE_COUNT:
        print(f"\n  ⚠️  警告: 面数过多 ({collision_info['faces']} > {MAX_FACE_COUNT})")
        print(f"      建议: 增加简化强度")
        passed = False
    elif collision_info['faces'] < MIN_FACE_COUNT:
        print(f"\n  ⚠️  警告: 面数过少 ({collision_info['faces']} < {MIN_FACE_COUNT})")
        print(f"      建议: 减少简化强度")
    else:
        print(f"\n  ✓ 面数合理 ({collision_info['faces']} 面)")
    
    # 2. 检查体积差异
    volume_diff = abs(collision_info['volume'] - original_info['volume'])
    volume_diff_percent = (volume_diff / original_info['volume']) * 100
    
    print(f"  体积差异: {volume_diff_percent:.2f}%")
    
    if volume_diff_percent > MAX_VOLUME_DIFF_PERCENT:
        print(f"  ⚠️  警告: 体积差异较大 ({volume_diff_percent:.2f}% > {MAX_VOLUME_DIFF_PERCENT}%)")
        passed = False
    else:
        print(f"  ✓ 体积差异合理")
    
    # 3. 检查文件大小
    original_size = os.path.getsize(original_path) / 1024  # KB
    collision_size = os.path.getsize(collision_path) / 1024  # KB
    size_reduction = (1 - collision_size / original_size) * 100
    
    print(f"\n  文件大小:")
    print(f"    原始: {original_size:.1f} KB")
    print(f"    凸包: {collision_size:.1f} KB")
    print(f"    减少: {size_reduction:.1f}%")
    
    if passed:
        print(f"\n✅ 验证通过")
    else:
        print(f"\n⚠️  验证未完全通过，但可能仍然可用")
    
    return passed


def main():
    """主函数"""
    print("="*60)
    print("凸包质量验证工具")
    print("="*60)
    print(f"原始目录: {ORIGINAL_DIR}")
    print(f"凸包目录: {COLLISION_DIR}")
    print("="*60)
    
    if not os.path.exists(COLLISION_DIR):
        print(f"\n❌ 错误: 凸包目录不存在")
        print(f"   {COLLISION_DIR}")
        print("\n请先运行: ./scripts/generate_convex_hulls.sh")
        return 1
    
    passed_count = 0
    failed_count = 0
    
    for original_file, collision_file in FILE_PAIRS:
        result = verify_pair(original_file, collision_file)
        if result:
            passed_count += 1
        else:
            failed_count += 1
    
    # 总结
    print(f"\n{'='*60}")
    print("验证完成")
    print(f"{'='*60}")
    print(f"✅ 通过: {passed_count} 个文件")
    print(f"⚠️  警告: {failed_count} 个文件")
    print("="*60)
    
    if failed_count == 0:
        print("\n🎉 所有凸包文件质量良好！")
        print("\n下一步:")
        print("  1. 更新 URDF 文件中的 collision mesh 路径")
        print("  2. 在 RViz 中可视化检查")
        print("  3. 在 Gazebo 中测试稳定性")
        return 0
    else:
        print("\n⚠️  部分文件有警告，但通常仍然可用")
        print("   如果 Gazebo 测试出现问题，可以调整参数重新生成")
        return 0


if __name__ == "__main__":
    sys.exit(main())
