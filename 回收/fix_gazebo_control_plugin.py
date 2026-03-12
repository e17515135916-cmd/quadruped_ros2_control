#!/usr/bin/env python3
"""
修复 Gazebo ros2_control 插件配置

问题：Gazebo 只暴露了 4 个滑轨关节，没有暴露 12 个腿部关节
原因：gz_ros2_control 插件可能没有正确加载 URDF 中定义的所有关节

解决方案：
1. 确保 URDF 中的 ros2_control 标签正确
2. 确保 Gazebo 插件配置正确
3. 使用 package:// 语法而不是 $(find ...) 语法
"""

import os
import sys

def fix_urdf():
    urdf_path = 'src/dog2_description/urdf/dog2.urdf.xacro'
    
    print("=" * 60)
    print("修复 Gazebo ros2_control 插件配置")
    print("=" * 60)
    print()
    
    # 读取 URDF
    with open(urdf_path, 'r') as f:
        content = f.read()
    
    # 检查当前配置
    if 'gz_ros2_control/GazeboSimSystem' in content:
        print("✅ 使用正确的插件: gz_ros2_control/GazeboSimSystem")
    else:
        print("❌ 插件配置错误")
        return False
    
    # 检查参数路径
    if '$(find dog2_description)' in content:
        print("⚠️  发现 $(find ...) 语法，Gazebo Fortress 可能不支持")
        print("   建议使用 package:// 语法")
        
        # 替换为 package:// 语法
        old_line = '<parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>'
        new_line = '<parameters>package://dog2_description/config/ros2_controllers.yaml</parameters>'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            print(f"   修复: {old_line}")
            print(f"   改为: {new_line}")
            
            # 写回文件
            with open(urdf_path, 'w') as f:
                f.write(content)
            
            print()
            print("✅ URDF 已更新")
            return True
        else:
            print("   未找到需要替换的行")
    else:
        print("✅ 参数路径配置正确")
    
    # 检查 ros2_control 标签中的关节数量
    joint_count = content.count('<joint name="lf_')
    joint_count += content.count('<joint name="rf_')
    joint_count += content.count('<joint name="lh_')
    joint_count += content.count('<joint name="rh_')
    
    print(f"\n📊 URDF 中定义的腿部关节数量: {joint_count}")
    if joint_count == 12:
        print("✅ 关节数量正确 (12 个)")
    else:
        print(f"❌ 关节数量错误，应该是 12 个，实际是 {joint_count} 个")
    
    return True

def main():
    if fix_urdf():
        print()
        print("=" * 60)
        print("下一步操作")
        print("=" * 60)
        print()
        print("1. 重新编译:")
        print("   colcon build --packages-select dog2_description --symlink-install")
        print()
        print("2. Source 环境:")
        print("   source install/setup.bash")
        print()
        print("3. 停止当前 Gazebo (Ctrl+C)")
        print()
        print("4. 重新启动:")
        print("   ./quick_start_keyboard_control.sh")
        print()
        print("5. 检查硬件接口:")
        print("   ros2 control list_hardware_interfaces")
        print("   应该看到 12 个腿部关节接口")
    else:
        print("\n❌ 修复失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
