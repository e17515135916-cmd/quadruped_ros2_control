# Dog2 Visualization

完整的 Dog2 四足机器人可视化系统。

## 功能特性

- ✅ **RViz2 3D 可视化**：实时显示机器人模型和关节状态
- ✅ **足端力可视化**：箭头标记显示力的大小和方向，颜色编码
- ✅ **轨迹可视化**：历史轨迹（蓝色）和规划轨迹（绿色）
- ✅ **接触状态标记**：绿色球体（接触）/ 红色球体（离地）
- ✅ **滑动副监控**：位置显示和警告级别（绿/黄/红）
- ✅ **性能监控面板**：实时显示 MPC 求解时间、控制频率等
- ✅ **越障可视化**：8 个阶段的可视化，窗框标记，腿部高亮
- ✅ **增强的 Gazebo 环境**：网格地面、距离标记、障碍物
- ✅ **实时数据图表**：PlotJuggler 配置

## 快速开始

### 安装

```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_visualization
source install/setup.bash
```

### 启动可视化（行走模式）

```bash
ros2 launch dog2_visualization visualization.launch.py mode:=walking
```

### 启动可视化（越障模式）

```bash
ros2 launch dog2_visualization visualization.launch.py mode:=crossing
```

## 配置文件

### RViz2 配置
- `config/rviz/dog2_walking.rviz` - 行走模式配置
- `config/rviz/dog2_crossing.rviz` - 越障模式配置
- `config/rviz/dog2_debug.rviz` - 调试模式配置

### Gazebo 世界文件
- `worlds/dog2_flat.world` - 平地环境
- `worlds/dog2_crossing.world` - 带窗框的越障环境
- `worlds/dog2_terrain.world` - 复杂地形环境

### PlotJuggler 配置
- `config/plotjuggler/dog2_performance.xml` - 性能数据曲线配置

## 节点说明

### visualization_node
主可视化节点，负责：
- 足端力箭头
- 轨迹线
- 接触状态球体
- 滑动副状态
- 性能监控文本

### crossing_visualization_node
越障专用可视化节点，负责：
- 越障阶段文本
- 窗框标记
- 腿部高亮
- 混合构型状态

## 话题订阅

- `/dog2/odom` - 机器人位姿和速度
- `/joint_states` - 关节状态
- `/dog2/mpc/foot_forces` - 足端力
- `/dog2/crossing/state` - 越障阶段（越障模式）

## 话题发布

- `/dog2/visualization/foot_forces` - 足端力箭头 Marker
- `/dog2/visualization/trajectory` - 轨迹线 Marker
- `/dog2/visualization/contact_markers` - 接触状态球体
- `/dog2/visualization/sliding_status` - 滑动副状态
- `/dog2/visualization/performance_text` - 性能文本面板
- `/dog2/visualization/crossing_stage` - 越障阶段文本
- `/dog2/visualization/window_marker` - 窗框标记

## 开发

### 运行测试

```bash
colcon test --packages-select dog2_visualization
colcon test-result --verbose
```

### 代码结构

```
dog2_visualization/
├── dog2_visualization/
│   ├── __init__.py
│   ├── visualization_node.py          # 主可视化节点
│   ├── crossing_visualization_node.py # 越障可视化节点
│   ├── foot_force_visualizer.py       # 足端力可视化器
│   ├── trajectory_visualizer.py       # 轨迹可视化器
│   ├── contact_marker_visualizer.py   # 接触标记可视化器
│   ├── sliding_joint_visualizer.py    # 滑动副可视化器
│   └── performance_monitor.py         # 性能监控器
├── config/
│   ├── rviz/                          # RViz2 配置文件
│   └── plotjuggler/                   # PlotJuggler 配置文件
├── worlds/                            # Gazebo 世界文件
├── launch/
│   └── visualization.launch.py        # 主启动文件
└── test/                              # 测试文件
```

## 许可证

MIT License
