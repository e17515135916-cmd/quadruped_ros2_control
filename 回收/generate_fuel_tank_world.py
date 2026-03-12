#!/usr/bin/env python3
"""
飞机油箱环境 Gazebo 世界文件生成器

生成包含桁条网格和穿越孔的油箱内部仿真环境。

用法：
  python3 generate_fuel_tank_world.py [--output PATH] [OPTIONS]

示例：
  # 使用默认参数生成
  python3 generate_fuel_tank_world.py
  
  # 自定义参数
  python3 generate_fuel_tank_world.py --stringer-spacing 0.2 --hole-width 0.3
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import argparse


@dataclass
class FuelTankConfig:
    """油箱环境配置参数
    
    Attributes:
        tank_length: 油箱长度 (X方向), 默认 2.0m
        tank_width: 油箱宽度 (Y方向), 默认 1.5m
        stringer_height: 桁条高度, 默认 0.03m
        stringer_width: 桁条宽度, 默认 0.02m
        stringer_spacing_x: X方向桁条间距, 默认 0.15m
        stringer_spacing_y: Y方向桁条间距, 默认 0.15m
        hole_width: 穿越孔宽度, 默认 0.25m
        hole_height: 穿越孔高度, 默认 0.20m
        panel_thickness: 面板厚度, 默认 0.02m
        panel_height: 面板总高度, 默认 0.30m
        num_panels: 面板数量, 默认 2
        robot_start_x: 机器人起始X位置, 默认 -0.5m
        robot_start_z: 机器人起始高度, 默认 0.15m
    """
    
    # 整体尺寸
    tank_length: float = 2.0
    tank_width: float = 1.5
    
    # 桁条参数
    stringer_height: float = 0.03
    stringer_width: float = 0.02
    stringer_spacing_x: float = 0.15
    stringer_spacing_y: float = 0.15
    
    # 穿越孔参数
    hole_width: float = 0.5
    hole_height: float = 0.4
    panel_thickness: float = 0.02
    panel_height: float = 0.8
    num_panels: int = 2
    panel_spacing: float = 0.5  # 面板之间的间距
    
    # 机器人起始位置
    robot_start_x: float = -0.5
    robot_start_z: float = 0.15
    
    def validate(self) -> None:
        """验证配置参数的有效性
        
        Raises:
            ValueError: 当参数无效时抛出
        """
        # 验证正数参数
        positive_params = [
            ('tank_length', self.tank_length),
            ('tank_width', self.tank_width),
            ('stringer_height', self.stringer_height),
            ('stringer_width', self.stringer_width),
            ('stringer_spacing_x', self.stringer_spacing_x),
            ('stringer_spacing_y', self.stringer_spacing_y),
            ('hole_width', self.hole_width),
            ('hole_height', self.hole_height),
            ('panel_thickness', self.panel_thickness),
            ('panel_height', self.panel_height),
            ('robot_start_z', self.robot_start_z),
        ]
        
        for name, value in positive_params:
            if value <= 0:
                raise ValueError(f"参数 '{name}' 必须为正数，当前值: {value}")
        
        # 验证整数参数
        if self.num_panels < 1:
            raise ValueError(f"面板数量必须至少为1，当前值: {self.num_panels}")
        
        # 验证桁条间距大于桁条宽度
        if self.stringer_spacing_x <= self.stringer_width:
            raise ValueError(
                f"X方向桁条间距 ({self.stringer_spacing_x}) 必须大于桁条宽度 ({self.stringer_width})"
            )
        if self.stringer_spacing_y <= self.stringer_width:
            raise ValueError(
                f"Y方向桁条间距 ({self.stringer_spacing_y}) 必须大于桁条宽度 ({self.stringer_width})"
            )
        
        # 验证穿越孔尺寸
        if self.hole_width >= self.tank_width:
            raise ValueError(
                f"穿越孔宽度 ({self.hole_width}) 必须小于油箱宽度 ({self.tank_width})"
            )
        if self.hole_height >= self.panel_height:
            raise ValueError(
                f"穿越孔高度 ({self.hole_height}) 必须小于面板高度 ({self.panel_height})"
            )
    
    def get_num_stringers_x(self) -> int:
        """计算X方向桁条数量"""
        return max(1, int(self.tank_length / self.stringer_spacing_x))
    
    def get_num_stringers_y(self) -> int:
        """计算Y方向桁条数量"""
        return max(1, int(self.tank_width / self.stringer_spacing_y))



class FuelTankWorldGenerator:
    """油箱环境世界文件生成器"""
    
    def __init__(self, config: FuelTankConfig):
        """初始化生成器
        
        Args:
            config: 油箱环境配置参数
        """
        config.validate()
        self.config = config
    
    def generate_base_plate(self) -> str:
        """生成底板SDF模型
        
        Returns:
            底板模型的SDF XML字符串
        """
        c = self.config
        return f'''
    <model name='fuel_tank_floor'>
      <static>true</static>
      <pose>0 0 -0.005 0 0 0</pose>
      <link name='floor_link'>
        <collision name='floor_collision'>
          <geometry>
            <box>
              <size>{c.tank_length + 1.0} {c.tank_width + 0.5} 0.01</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.8</mu>
                <mu2>0.8</mu2>
              </ode>
            </friction>
            <contact>
              <ode/>
            </contact>
          </surface>
        </collision>
        <visual name='floor_visual'>
          <geometry>
            <box>
              <size>{c.tank_length + 1.0} {c.tank_width + 0.5} 0.01</size>
            </box>
          </geometry>
          <material>
            <ambient>0.6 0.6 0.7 1</ambient>
            <diffuse>0.6 0.6 0.7 1</diffuse>
            <specular>0.3 0.3 0.3 1</specular>
          </material>
        </visual>
      </link>
    </model>'''
    
    def generate_single_stringer(self, name: str, x: float, y: float, 
                                  length: float, is_horizontal: bool) -> str:
        """生成单个桁条SDF模型
        
        Args:
            name: 桁条模型名称
            x: X位置
            y: Y位置
            length: 桁条长度
            is_horizontal: 是否为横向桁条
            
        Returns:
            桁条模型的SDF XML字符串
        """
        c = self.config
        z = c.stringer_height / 2
        
        if is_horizontal:
            # 横向桁条 (沿Y方向)
            size_x = c.stringer_width
            size_y = length
            rotation = 0
        else:
            # 纵向桁条 (沿X方向)
            size_x = length
            size_y = c.stringer_width
            rotation = 0
        
        return f'''
    <model name='{name}'>
      <static>true</static>
      <pose>{x} {y} {z} 0 0 {rotation}</pose>
      <link name='link'>
        <collision name='collision'>
          <geometry>
            <box>
              <size>{size_x} {size_y} {c.stringer_height}</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.6</mu>
                <mu2>0.6</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name='visual'>
          <geometry>
            <box>
              <size>{size_x} {size_y} {c.stringer_height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.35 1</ambient>
            <diffuse>0.4 0.4 0.45 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
          </material>
        </visual>
      </link>
    </model>'''
    
    def generate_stringers(self) -> Tuple[List[str], int]:
        """生成桁条网格SDF模型列表
        
        Returns:
            (桁条模型SDF字符串列表, 桁条总数)
        """
        c = self.config
        stringers = []
        count = 0
        
        # 计算桁条区域的起始位置
        start_x = 0.0
        start_y = -c.tank_width / 2
        
        num_x = c.get_num_stringers_x()
        num_y = c.get_num_stringers_y()
        
        # 生成横向桁条 (沿Y方向延伸)
        for i in range(num_x + 1):
            x = start_x + i * c.stringer_spacing_x
            y = 0  # 居中
            name = f'stringer_h_{i}'
            stringer = self.generate_single_stringer(
                name, x, y, c.tank_width, is_horizontal=True
            )
            stringers.append(stringer)
            count += 1
        
        # 生成纵向桁条 (沿X方向延伸)
        for j in range(num_y + 1):
            y = start_y + j * c.stringer_spacing_y
            x = start_x + (num_x * c.stringer_spacing_x) / 2  # 居中
            name = f'stringer_v_{j}'
            stringer = self.generate_single_stringer(
                name, x, y, num_x * c.stringer_spacing_x, is_horizontal=False
            )
            stringers.append(stringer)
            count += 1
        
        return stringers, count

    def generate_access_panel(self, panel_index: int, x_position: float) -> str:
        """生成带穿越孔的窗型面板SDF模型（悬空）
        
        面板结构（侧视图）：
        ┌─────────────────────────────────────┐
        │          上部面板                    │  <- 顶部
        ├─────────┬───────────┬───────────────┤
        │ 左侧柱  │  穿越孔   │    右侧柱      │  <- 孔洞（悬空）
        │         │ (空洞)    │               │
        ├─────────┴───────────┴───────────────┤
        │          下部面板                    │  <- 底部（离地）
        └─────────────────────────────────────┘
        
        Args:
            panel_index: 面板索引
            x_position: 面板X位置
            
        Returns:
            面板模型的SDF XML字符串
        """
        c = self.config
        
        # 孔洞底部离地高度（机器人需要从孔洞穿过）
        hole_bottom_height = 0.20  # 20cm离地，机器人base_link可以从孔洞穿过
        
        # 计算各部分尺寸
        side_width = (c.tank_width - c.hole_width) / 2
        
        # 下部面板高度（从地面到孔洞底部）
        bottom_panel_height = hole_bottom_height
        
        # 上部面板高度（从孔洞顶部到面板顶部）
        top_panel_height = c.panel_height - hole_bottom_height - c.hole_height
        
        # 面板中心Y位置
        center_y = 0
        
        # 左侧柱位置（从地面到面板顶部）
        left_x = x_position
        left_y = center_y - c.hole_width / 2 - side_width / 2
        left_z = c.panel_height / 2
        
        # 右侧柱位置
        right_y = center_y + c.hole_width / 2 + side_width / 2
        right_z = c.panel_height / 2
        
        # 下部面板位置（孔洞下方）
        bottom_z = bottom_panel_height / 2
        
        # 上部面板位置（孔洞上方）
        top_z = hole_bottom_height + c.hole_height + top_panel_height / 2
        
        return f'''
    <model name='access_panel_{panel_index}'>
      <static>true</static>
      <link name='left_pillar'>
        <pose>{left_x} {left_y} {left_z} 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {side_width} {c.panel_height}</size>
            </box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {side_width} {c.panel_height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.55 1</ambient>
            <diffuse>0.6 0.6 0.65 1</diffuse>
          </material>
        </visual>
      </link>
      <link name='right_pillar'>
        <pose>{left_x} {right_y} {right_z} 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {side_width} {c.panel_height}</size>
            </box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {side_width} {c.panel_height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.55 1</ambient>
            <diffuse>0.6 0.6 0.65 1</diffuse>
          </material>
        </visual>
      </link>
      <link name='bottom_panel'>
        <pose>{left_x} {center_y} {bottom_z} 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {c.hole_width} {bottom_panel_height}</size>
            </box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {c.hole_width} {bottom_panel_height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.55 1</ambient>
            <diffuse>0.6 0.6 0.65 1</diffuse>
          </material>
        </visual>
      </link>
      <link name='top_panel'>
        <pose>{left_x} {center_y} {top_z} 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {c.hole_width} {top_panel_height}</size>
            </box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box>
              <size>{c.panel_thickness} {c.hole_width} {top_panel_height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.55 1</ambient>
            <diffuse>0.6 0.6 0.65 1</diffuse>
          </material>
        </visual>
      </link>
    </model>'''
    
    def generate_access_panels(self) -> Tuple[List[str], int]:
        """生成所有穿越孔面板
        
        Returns:
            (面板模型SDF字符串列表, 面板总数)
        """
        c = self.config
        panels = []
        
        # 面板放置在桁条区域之后
        stringer_end_x = c.get_num_stringers_x() * c.stringer_spacing_x
        
        for i in range(c.num_panels):
            x_pos = stringer_end_x + 0.3 + i * c.panel_spacing
            panel = self.generate_access_panel(i, x_pos)
            panels.append(panel)
        
        return panels, c.num_panels

    def generate_world_header(self) -> str:
        """生成世界文件头部
        
        Returns:
            SDF世界文件头部XML字符串
        """
        return '''<?xml version='1.0'?>
<sdf version='1.6'>
  <world name='fuel_tank'>'''
    
    def generate_lights(self) -> str:
        """生成光源配置
        
        Returns:
            光源SDF XML字符串
        """
        return '''
    <light name='sun' type='directional'>
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    
    <light name='spot_light' type='spot'>
      <pose>1 0 2 0 0 0</pose>
      <diffuse>0.8 0.8 0.9 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.5</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>0 0 -1</direction>
      <spot>
        <inner_angle>0.6</inner_angle>
        <outer_angle>1.0</outer_angle>
        <falloff>1.0</falloff>
      </spot>
    </light>'''
    
    def generate_physics(self) -> str:
        """生成物理引擎配置
        
        Returns:
            物理引擎SDF XML字符串
        """
        return '''
    <gravity>0 0 -9.8</gravity>
    <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
    <atmosphere type='adiabatic'/>
    
    <physics name='default_physics' default='0' type='ode'>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>1</shadows>
    </scene>'''
    
    def generate_ground_plane(self) -> str:
        """生成地面模型
        
        Returns:
            地面模型SDF XML字符串
        """
        return '''
    <model name='ground_plane'>
      <static>true</static>
      <link name='link'>
        <collision name='collision'>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>100</mu>
                <mu2>50</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>'''
    
    def generate_gui(self) -> str:
        """生成GUI和相机配置
        
        Returns:
            GUI配置SDF XML字符串
        """
        c = self.config
        # 相机位置：在油箱侧面，俯视整个场景
        cam_x = c.tank_length / 2
        cam_y = -c.tank_width - 1.5
        cam_z = 1.5
        
        return f'''
    <gui fullscreen='0'>
      <camera name='user_camera'>
        <pose>{cam_x} {cam_y} {cam_z} 0 0.4 1.57</pose>
        <view_controller>orbit</view_controller>
        <projection_type>perspective</projection_type>
      </camera>
    </gui>'''
    
    def generate_world_footer(self) -> str:
        """生成世界文件尾部
        
        Returns:
            SDF世界文件尾部XML字符串
        """
        return '''
  </world>
</sdf>'''

    def generate(self) -> str:
        """生成完整的SDF世界文件内容
        
        Returns:
            完整的SDF世界文件XML字符串
        """
        parts = []
        
        # 头部
        parts.append(self.generate_world_header())
        
        # 光源
        parts.append(self.generate_lights())
        
        # 物理引擎
        parts.append(self.generate_physics())
        
        # 地面
        parts.append(self.generate_ground_plane())
        
        # 油箱底板
        parts.append(self.generate_base_plate())
        
        # 桁条网格
        stringers, _ = self.generate_stringers()
        parts.extend(stringers)
        
        # 穿越孔面板
        panels, _ = self.generate_access_panels()
        parts.extend(panels)
        
        # GUI
        parts.append(self.generate_gui())
        
        # 尾部
        parts.append(self.generate_world_footer())
        
        return '\n'.join(parts)
    
    def save(self, output_path: str) -> None:
        """保存世界文件到指定路径
        
        Args:
            output_path: 输出文件路径
        """
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成并保存
        content = self.generate()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 世界文件已保存到: {output_path}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='生成飞机油箱环境 Gazebo 世界文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 使用默认参数生成
  python3 generate_fuel_tank_world.py
  
  # 自定义参数
  python3 generate_fuel_tank_world.py --stringer-spacing 0.2 --hole-width 0.3
  
  # 指定输出路径
  python3 generate_fuel_tank_world.py --output /path/to/fuel_tank.world
'''
    )
    
    parser.add_argument('--output', '-o', type=str,
                        default='src/champ/champ_gazebo/worlds/fuel_tank.world',
                        help='输出文件路径')
    
    # 油箱尺寸
    parser.add_argument('--tank-length', type=float, default=2.0,
                        help='油箱长度 (X方向), 默认 2.0m')
    parser.add_argument('--tank-width', type=float, default=1.5,
                        help='油箱宽度 (Y方向), 默认 1.5m')
    
    # 桁条参数
    parser.add_argument('--stringer-height', type=float, default=0.03,
                        help='桁条高度, 默认 0.03m')
    parser.add_argument('--stringer-width', type=float, default=0.02,
                        help='桁条宽度, 默认 0.02m')
    parser.add_argument('--stringer-spacing', type=float, default=0.15,
                        help='桁条间距 (X和Y方向), 默认 0.15m')
    
    # 穿越孔参数
    parser.add_argument('--hole-width', type=float, default=0.5,
                        help='穿越孔宽度, 默认 0.5m')
    parser.add_argument('--hole-height', type=float, default=0.4,
                        help='穿越孔高度, 默认 0.4m')
    parser.add_argument('--panel-height', type=float, default=0.8,
                        help='面板总高度, 默认 0.8m')
    parser.add_argument('--num-panels', type=int, default=2,
                        help='面板数量, 默认 2')
    
    args = parser.parse_args()
    
    # 创建配置
    config = FuelTankConfig(
        tank_length=args.tank_length,
        tank_width=args.tank_width,
        stringer_height=args.stringer_height,
        stringer_width=args.stringer_width,
        stringer_spacing_x=args.stringer_spacing,
        stringer_spacing_y=args.stringer_spacing,
        hole_width=args.hole_width,
        hole_height=args.hole_height,
        panel_height=args.panel_height,
        num_panels=args.num_panels,
    )
    
    print("=" * 50)
    print("  飞机油箱环境生成器")
    print("=" * 50)
    print(f"\n配置参数:")
    print(f"  油箱尺寸: {config.tank_length}m x {config.tank_width}m")
    print(f"  桁条: 高度={config.stringer_height}m, 间距={config.stringer_spacing_x}m")
    print(f"  穿越孔: {config.hole_width}m x {config.hole_height}m")
    print(f"  面板数量: {config.num_panels}")
    print()
    
    try:
        # 验证配置
        config.validate()
        
        # 生成世界文件
        generator = FuelTankWorldGenerator(config)
        generator.save(args.output)
        
        print(f"\n桁条数量: {config.get_num_stringers_x() + 1} (横向) + {config.get_num_stringers_y() + 1} (纵向)")
        print(f"面板数量: {config.num_panels}")
        print("\n使用方法:")
        print(f"  ros2 launch dog2_champ_config dog2_fuel_tank.launch.py")
        print("  或")
        print(f"  ros2 launch champ_gazebo gazebo.launch.py world:={args.output}")
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return 1
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
