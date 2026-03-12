#!/usr/bin/env python3
"""
测试 xacro 参数传递
检查 hip_joint_rpy 参数是否被正确传递到编译后的 URDF
"""

import subprocess
import xml.etree.ElementTree as ET

def compile_xacro():
    """编译 xacro 文件"""
    cmd = "bash -c 'source install/setup.bash && xacro src/dog2_description/urdf/dog2.urdf.xacro'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def parse_urdf(urdf_content):
    """解析 URDF 内容"""
    root = ET.fromstring(urdf_content)
    return root

def check_haa_joints(root):
    """检查所有 HAA 关节的 RPY 值"""
    print("=" * 60)
    print("检查 HAA 关节的 RPY 值")
    print("=" * 60)
    
    haa_joints = ['lf_haa_joint', 'rf_haa_joint', 'lh_haa_joint', 'rh_haa_joint']
    
    for joint_name in haa_joints:
        joint = root.find(f".//joint[@name='{joint_name}']")
        if joint is not None:
            origin = joint.find('origin')
            if origin is not None:
                rpy = origin.get('rpy', 'N/A')
                xyz = origin.get('xyz', 'N/A')
                print(f"\n{joint_name}:")
                print(f"  RPY: {rpy}")
                print(f"  XYZ: {xyz}")
            else:
                print(f"\n{joint_name}: No origin element found")
        else:
            print(f"\n{joint_name}: Joint not found")

def main():
    print("编译 xacro 文件...")
    urdf_content = compile_xacro()
    
    if not urdf_content:
        print("错误：无法编译 xacro 文件")
        return
    
    print("解析 URDF...")
    root = parse_urdf(urdf_content)
    
    check_haa_joints(root)
    
    print("\n" + "=" * 60)
    print("预期值：")
    print("  Leg 1 (lf): RPY = -1.5708 0 0")
    print("  Leg 2 (rf): RPY = -1.5708 0 0")
    print("  Leg 3 (lh): RPY = 0 0 0")
    print("  Leg 4 (rh): RPY = 0 0 0")
    print("=" * 60)

if __name__ == "__main__":
    main()
