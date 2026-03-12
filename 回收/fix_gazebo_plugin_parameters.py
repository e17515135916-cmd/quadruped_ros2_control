#!/usr/bin/env python3
"""
修复 Gazebo ros2_control 插件参数路径

问题：URDF 中使用了 $(find ...) 语法，这在 Gazebo Fortress 中不起作用
解决：移除 <parameters> 标签，让插件从 ros2_control 标签中自动读取配置

Date: 2026-02-07
"""

import re

def fix_gazebo_plugin_parameters(xacro_file):
    """修复 Gazebo 插件参数配置"""
    
    with open(xacro_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 Gazebo 插件配置
    # 旧配置使用 <parameters> 标签
    # 新配置移除该标签，让插件自动从 ros2_control 读取
    
    old_plugin = r'''  <gazebo>
    <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
      <parameters>\$\(find dog2_description\)/config/ros2_controllers\.yaml</parameters>
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
    </plugin>
  </gazebo>'''
    
    new_plugin = '''  <gazebo>
    <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
    </plugin>
  </gazebo>'''
    
    if old_plugin in content:
        content = content.replace(old_plugin, new_plugin)
        print("✅ 已移除 <parameters> 标签")
    else:
        print("⚠️  未找到需要修复的插件配置")
        print("   检查是否已经修复过")
    
    # 写回文件
    with open(xacro_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新: {xacro_file}")

if __name__ == '__main__':
    xacro_file = 'src/dog2_description/urdf/dog2.urdf.xacro'
    fix_gazebo_plugin_parameters(xacro_file)
    print("\n修复完成！")
    print("\n下一步：")
    print("1. 重新编译: colcon build --packages-select dog2_description --symlink-install")
    print("2. 重启 Gazebo 系统")
