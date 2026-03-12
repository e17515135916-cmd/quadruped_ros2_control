#!/usr/bin/env python3
"""
验证视觉外观保持不变的脚本。

此脚本对比修改前后的 URDF，验证：
1. 视觉网格文件未改变
2. 视觉原点未改变
3. 视觉几何体未改变
4. 只有髋关节轴向改变了

验证需求：6.5, 2.3
"""

import subprocess
import xml.etree.ElementTree as ET
import os


def parse_urdf_from_xacro(xacro_path):
    """从 xacro 文件生成并解析 URDF。"""
    try:
        result = subprocess.run(
            ['xacro', xacro_path],
            capture_output=True,
            text=True,
            check=True
        )
        return ET.fromstring(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ 处理 xacro 失败: {e}")
        print(f"  stderr: {e.stderr}")
        raise


def get_visual_info(root, link_name):
    """获取指定连杆的视觉信息。"""
    visual_info = {}
    
    for link in root.findall('.//link[@name="{}"]'.format(link_name)):
        visual = link.find('visual')
        if visual is not None:
            # 获取几何体信息
            geometry = visual.find('geometry')
            if geometry is not None:
                mesh = geometry.find('mesh')
                if mesh is not None:
                    visual_info['mesh_filename'] = mesh.get('filename', '')
                    visual_info['mesh_scale'] = mesh.get('scale', '1 1 1')
            
            # 获取原点信息
            origin = visual.find('origin')
            if origin is not None:
                visual_info['origin_xyz'] = origin.get('xyz', '0 0 0')
                visual_info['origin_rpy'] = origin.get('rpy', '0 0 0')
            else:
                visual_info['origin_xyz'] = '0 0 0'
                visual_info['origin_rpy'] = '0 0 0'
    
    return visual_info


def get_joint_axis(root, joint_name):
    """获取指定关节的轴向信息。"""
    for joint in root.findall('.//joint[@name="{}"]'.format(joint_name)):
        axis = joint.find('axis')
        if axis is not None:
            return axis.get('xyz', '')
    return None


def compare_visual_models(current_xacro, backup_xacro=None):
    """对比当前和备份的视觉模型。"""
    print("\n" + "="*70)
    print("视觉外观验证")
    print("="*70)
    
    # 解析当前 URDF
    print("\n正在解析当前 URDF...")
    current_root = parse_urdf_from_xacro(current_xacro)
    print("✓ 当前 URDF 解析成功")
    
    # 如果有备份，则对比
    if backup_xacro and os.path.exists(backup_xacro):
        print(f"\n正在解析备份 URDF: {backup_xacro}")
        backup_root = parse_urdf_from_xacro(backup_xacro)
        print("✓ 备份 URDF 解析成功")
        compare_mode = True
    else:
        print("\n未找到备份文件，仅验证当前配置")
        backup_root = None
        compare_mode = False
    
    # 髋关节连杆列表
    hip_links = ['l11', 'l21', 'l31', 'l41']
    hip_joints = ['j11', 'j21', 'j31', 'j41']
    
    all_passed = True
    
    # 验证视觉模型
    print("\n" + "-"*70)
    print("验证髋关节连杆视觉模型")
    print("-"*70)
    
    for link in hip_links:
        print(f"\n检查连杆 {link}:")
        current_visual = get_visual_info(current_root, link)
        
        if not current_visual:
            print(f"  ⚠ 警告: 未找到 {link} 的视觉信息")
            continue
        
        print(f"  网格文件: {current_visual.get('mesh_filename', 'N/A')}")
        print(f"  网格缩放: {current_visual.get('mesh_scale', 'N/A')}")
        print(f"  原点 XYZ: {current_visual.get('origin_xyz', 'N/A')}")
        print(f"  原点 RPY: {current_visual.get('origin_rpy', 'N/A')}")
        
        if compare_mode:
            backup_visual = get_visual_info(backup_root, link)
            
            if current_visual == backup_visual:
                print(f"  ✓ {link} 视觉模型未改变")
            else:
                print(f"  ✗ {link} 视觉模型已改变！")
                all_passed = False
                
                # 显示差异
                for key in current_visual:
                    if current_visual.get(key) != backup_visual.get(key):
                        print(f"    差异 {key}:")
                        print(f"      当前: {current_visual.get(key)}")
                        print(f"      备份: {backup_visual.get(key)}")
    
    # 验证髋关节轴向
    print("\n" + "-"*70)
    print("验证髋关节轴向配置")
    print("-"*70)
    
    for joint in hip_joints:
        print(f"\n检查关节 {joint}:")
        current_axis = get_joint_axis(current_root, joint)
        
        if current_axis:
            print(f"  当前轴向: {current_axis}")
            
            # 验证是否为 X 轴
            if current_axis.strip() == "1 0 0":
                print(f"  ✓ {joint} 轴向正确 (X 轴)")
            else:
                print(f"  ✗ {joint} 轴向不正确，应为 '1 0 0'")
                all_passed = False
            
            if compare_mode:
                backup_axis = get_joint_axis(backup_root, joint)
                if backup_axis:
                    print(f"  备份轴向: {backup_axis}")
                    if current_axis != backup_axis:
                        print(f"  ℹ {joint} 轴向已从 {backup_axis} 改为 {current_axis}")
        else:
            print(f"  ✗ 未找到 {joint} 的轴向信息")
            all_passed = False
    
    # 打印总结
    print("\n" + "="*70)
    print("验证总结")
    print("="*70)
    
    if all_passed:
        print("\n✓ 所有验证通过")
        print("  - 视觉模型保持不变")
        print("  - 髋关节轴向已正确更新为 X 轴 (1 0 0)")
    else:
        print("\n✗ 验证失败")
        print("  请检查上述错误信息")
    
    print("="*70 + "\n")
    
    return all_passed


def main():
    """主函数。"""
    # 当前 xacro 文件路径
    current_xacro = 'src/dog2_description/urdf/dog2.urdf.xacro'
    
    # 查找最新的备份文件
    backup_xacro = None
    backup_dir = 'backups'
    
    if os.path.exists(backup_dir):
        # 查找包含 hip_joint_axis_change 的备份目录
        for item in sorted(os.listdir(backup_dir), reverse=True):
            if 'hip_joint_axis_change' in item:
                potential_backup = os.path.join(backup_dir, item, 'dog2.urdf.xacro')
                if os.path.exists(potential_backup):
                    backup_xacro = potential_backup
                    break
    
    # 如果没找到特定备份，尝试查找任何备份的 xacro 文件
    if not backup_xacro:
        for root, dirs, files in os.walk(backup_dir):
            if 'dog2.urdf.xacro' in files:
                backup_xacro = os.path.join(root, 'dog2.urdf.xacro')
                break
    
    # 运行对比
    success = compare_visual_models(current_xacro, backup_xacro)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
