#!/usr/bin/env python3
"""
改进的URDF到Blender导入脚本
正确处理变换矩阵，显示完整装配体
"""

import bpy
import xml.etree.ElementTree as ET
import os
import sys
from mathutils import Vector, Euler, Matrix
import math

def clear_scene():
    """清空场景"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def rpy_to_matrix(roll, pitch, yaw):
    """将RPY欧拉角转换为旋转矩阵"""
    # 按照ROS/URDF的惯例：先绕X轴(roll)，再绕Y轴(pitch)，最后绕Z轴(yaw)
    R_x = Matrix.Rotation(roll, 4, 'X')
    R_y = Matrix.Rotation(pitch, 4, 'Y')
    R_z = Matrix.Rotation(yaw, 4, 'Z')
    return R_z @ R_y @ R_x

def parse_origin_matrix(origin_elem):
    """解析origin标签并返回4x4变换矩阵"""
    if origin_elem is None:
        return Matrix.Identity(4)
    
    xyz = origin_elem.get('xyz', '0 0 0').split()
    rpy = origin_elem.get('rpy', '0 0 0').split()
    
    # 创建平移矩阵
    translation = Matrix.Translation(Vector([float(x) for x in xyz]))
    
    # 创建旋转矩阵
    rotation = rpy_to_matrix(float(rpy[0]), float(rpy[1]), float(rpy[2]))
    
    # 组合变换矩阵
    return translation @ rotation

def import_urdf(urdf_path):
    """导入URDF文件"""
    print(f"正在解析URDF: {urdf_path}")
    
    # 解析URDF
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    
    # 获取URDF所在目录
    urdf_dir = os.path.dirname(urdf_path)
    
    # 存储link对象和它们的世界变换矩阵
    links = {}
    link_transforms = {}
    joints_info = []
    
    # 第一步：解析所有link并导入mesh（不设置位置）
    print("\n=== 导入所有部件 ===")
    for link in root.findall('link'):
        link_name = link.get('name')
        print(f"处理link: {link_name}")
        
        # 查找visual mesh
        visual = link.find('visual')
        if visual is None:
            # 对于没有visual的link（如球形脚），创建空对象
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            obj = bpy.context.active_object
            obj.name = link_name
            links[link_name] = obj
            print(f"  ⚠️  没有visual元素，创建空对象")
            continue
            
        geometry = visual.find('geometry')
        if geometry is None:
            print(f"  ⚠️  没有geometry元素")
            continue
        
        # 检查是否是sphere（球形脚）
        sphere = geometry.find('sphere')
        if sphere is not None:
            radius = float(sphere.get('radius', '0.02'))
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius)
            obj = bpy.context.active_object
            obj.name = link_name
            links[link_name] = obj
            print(f"  ✅ 创建球体: {link_name} (半径={radius})")
            continue
            
        mesh = geometry.find('mesh')
        if mesh is None:
            print(f"  ⚠️  没有mesh元素")
            continue
            
        # 获取mesh文件路径
        mesh_filename = mesh.get('filename')
        if mesh_filename.startswith('package://'):
            # 转换ROS package路径
            mesh_filename = mesh_filename.replace('package://dog2_description/', '')
            mesh_path = os.path.join(urdf_dir, '..', mesh_filename)
        else:
            mesh_path = os.path.join(urdf_dir, mesh_filename)
        
        mesh_path = os.path.abspath(mesh_path)
        
        if not os.path.exists(mesh_path):
            print(f"  ❌ 文件不存在: {mesh_path}")
            continue
        
        # 导入STL
        try:
            bpy.ops.import_mesh.stl(filepath=mesh_path)
            
            # 获取刚导入的对象
            obj = bpy.context.selected_objects[0]
            obj.name = link_name
            
            # 应用visual的origin（mesh相对于link的偏移）
            origin = visual.find('origin')
            if origin is not None:
                visual_transform = parse_origin_matrix(origin)
                obj.matrix_local = visual_transform
            
            links[link_name] = obj
            
            print(f"  ✅ 成功: {link_name}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    # 第二步：解析joints信息
    print("\n=== 解析关节关系 ===")
    for joint in root.findall('joint'):
        joint_name = joint.get('name')
        joint_type = joint.get('type')
        
        parent_link = joint.find('parent').get('link')
        child_link = joint.find('child').get('link')
        
        # 获取joint origin（child相对于parent的变换）
        origin = joint.find('origin')
        transform = parse_origin_matrix(origin)
        
        joints_info.append({
            'name': joint_name,
            'type': joint_type,
            'parent': parent_link,
            'child': child_link,
            'transform': transform
        })
        
        print(f"  关节: {joint_name} ({parent_link} -> {child_link})")
    
    # 第三步：计算每个link的世界变换矩阵
    print("\n=== 计算世界坐标变换 ===")
    
    # base_link的世界变换是单位矩阵
    if 'base_link' in links:
        link_transforms['base_link'] = Matrix.Identity(4)
    
    # 递归计算所有link的世界变换
    def compute_transform(link_name, parent_transform):
        if link_name in link_transforms:
            return  # 已经计算过了
        
        link_transforms[link_name] = parent_transform
        
        # 找到所有以这个link为parent的joint
        for joint_info in joints_info:
            if joint_info['parent'] == link_name:
                child_name = joint_info['child']
                child_transform = parent_transform @ joint_info['transform']
                compute_transform(child_name, child_transform)
    
    # 从base_link开始递归计算
    if 'base_link' in links:
        compute_transform('base_link', Matrix.Identity(4))
    
    # 第四步：应用世界变换到所有对象
    print("\n=== 应用变换到对象 ===")
    for link_name, obj in links.items():
        if link_name in link_transforms:
            obj.matrix_world = link_transforms[link_name]
            print(f"  ✅ {link_name}: 已设置世界坐标")
        else:
            print(f"  ⚠️  {link_name}: 未找到变换矩阵")
    
    # 第五步：建立父子关系（可选，用于层级显示）
    print("\n=== 建立层级关系 ===")
    for joint_info in joints_info:
        parent_name = joint_info['parent']
        child_name = joint_info['child']
        
        if parent_name not in links or child_name not in links:
            print(f"  ⚠️  跳过 {joint_info['name']}: 缺少link")
            continue
        
        parent_obj = links[parent_name]
        child_obj = links[child_name]
        
        # 设置父子关系，但保持当前的世界变换
        child_obj.parent = parent_obj
        child_obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()
        
        print(f"  ✅ {joint_info['name']}: {parent_name} -> {child_name}")
    
    print(f"\n✅ 导入完成！共导入 {len(links)} 个部件，{len(joints_info)} 个关节")

def main():
    """主函数"""
    # 获取URDF路径
    if len(sys.argv) > 4:  # Blender传递参数的方式
        urdf_path = sys.argv[4]
    else:
        # 默认路径
        urdf_path = os.path.expanduser("~/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf")
    
    print("=== URDF导入脚本 ===")
    print(f"URDF路径: {urdf_path}")
    
    if not os.path.exists(urdf_path):
        print(f"❌ 文件不存在: {urdf_path}")
        return
    
    # 清空场景
    clear_scene()
    
    # 导入URDF
    import_urdf(urdf_path)
    
    # 调整视图
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override)
                    break

if __name__ == "__main__":
    main()
