#!/usr/bin/env python3
"""
验证xacro生成的URDF与原始URDF的惯性值是否匹配
"""

import xml.etree.ElementTree as ET
import sys

def extract_inertia_values(urdf_file):
    """从URDF文件中提取所有链接的惯性值"""
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    inertia_values = {}
    
    for link in root.findall('link'):
        link_name = link.get('name')
        inertial = link.find('inertial')
        if inertial is not None:
            origin = inertial.find('origin')
            if origin is not None:
                xyz = origin.get('xyz')
                if xyz:
                    inertia_values[link_name] = xyz
    
    return inertia_values

def main():
    print("验证xacro生成的URDF与原始URDF的惯性值匹配")
    print("=" * 60)
    
    # 文件路径
    original_urdf = "src/dog2_description/urdf/dog2.urdf"
    xacro_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    # 生成xacro的URDF
    import subprocess
    result = subprocess.run(['xacro', xacro_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误：xacro处理失败: {result.stderr}")
        return 1
    
    # 保存生成的URDF
    generated_urdf = "src/dog2_description/urdf/dog2_generated_from_xacro.urdf"
    with open(generated_urdf, 'w') as f:
        f.write(result.stdout)
    
    # 提取惯性值
    try:
        original_inertia = extract_inertia_values(original_urdf)
        generated_inertia = extract_inertia_values(generated_urdf)
    except Exception as e:
        print(f"错误：解析URDF文件失败: {e}")
        return 1
    
    print(f"原始URDF惯性值 ({len(original_inertia)} 个链接):")
    for link, xyz in sorted(original_inertia.items()):
        print(f"  {link}: {xyz}")
    
    print(f"\n生成URDF惯性值 ({len(generated_inertia)} 个链接):")
    for link, xyz in sorted(generated_inertia.items()):
        print(f"  {link}: {xyz}")
    
    print("\n比较结果:")
    print("=" * 60)
    
    # 重点检查的链接
    key_links = ['l111', 'l1111', 'l211', 'l2111', 'l311', 'l3111', 'l411', 'l4111']
    
    all_match = True
    for link in key_links:
        if link in original_inertia and link in generated_inertia:
            orig = original_inertia[link]
            gen = generated_inertia[link]
            match = orig == gen
            status = "✅ 匹配" if match else "❌ 不匹配"
            print(f"{link:8}: {status}")
            if not match:
                print(f"         原始: {orig}")
                print(f"         生成: {gen}")
                all_match = False
        else:
            print(f"{link:8}: ❌ 缺失")
            all_match = False
    
    print("\n" + "=" * 60)
    if all_match:
        print("✅ 所有关键链接的惯性值都匹配！")
        return 0
    else:
        print("❌ 存在不匹配的惯性值！")
        return 1

if __name__ == '__main__':
    sys.exit(main())