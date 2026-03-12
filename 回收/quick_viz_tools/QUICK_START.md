# 🚀 5分钟快速出图指南

## 立即开始

```bash
cd quick_viz_tools
python3 generate_all.py
```

**就这么简单！** 所有图表已保存到 `presentation_outputs/` 目录。

## ✅ 已生成的图表

1. **workspace_comparison.png** (338 KB) - 工作空间对比图
2. **ros_graph.png** (383 KB) - ROS节点通信图  
3. **fsm_diagram.png** (390 KB) - 状态机流转图
4. **data_plot.png** (759 KB) - 数据曲线图

## 📋 使用这些图表

### 直接拖入PPT
所有图表都是高分辨率(300 DPI)，直接拖入PPT即可使用。

### 图表说明

#### 1. 工作空间对比图
- **用途**: 证明导轨扩展的有效性
- **亮点**: 自动计算面积增加百分比
- **自定义**: `python3 workspace_comparison.py 0.15` (150mm扩展)

#### 2. ROS节点通信图
- **用途**: 展示系统架构
- **亮点**: 清晰的闭环控制流程
- **包含**: MPC + WBC控制策略

#### 3. 状态机流转图
- **用途**: 展示穿越窗框策略
- **亮点**: 4个状态 + 机器人姿态图标
- **包含**: 完整的状态转换逻辑

#### 4. 数据曲线图
- **用途**: 展示控制效果
- **亮点**: 4个子图展示关键数据
- **包含**: 身体高度、导轨位置、速度、IMU

## 🔧 使用真实数据

如果你有实验数据CSV文件：

```bash
python3 data_plot.py your_experiment_data.csv
```

CSV格式要求：
```csv
timestamp,body_height,rail_position,velocity_x,imu_az
0.0,0.3,0.0,0.3,9.81
0.01,0.301,0.0,0.299,9.82
...
```

## 💡 常见问题

### Q: 图表中文显示为方块？
A: 脚本已配置中文字体，如果还有问题，安装字体：
```bash
sudo apt-get install fonts-wqy-zenhei
```

### Q: 想修改图表样式？
A: 直接编辑对应的Python脚本，所有绘图代码都很简单易懂。

### Q: 需要更多图表？
A: 查看完整的 `presentation_viz/` 系统，支持更多功能。

## 🎯 下一步

1. ✅ 图表已生成
2. 📂 打开 `presentation_outputs/` 目录
3. 🖼️ 拖拽图片到PPT
4. 🎨 根据需要调整参数重新生成

**就是这么简单！祝你演示成功！** 🚀
