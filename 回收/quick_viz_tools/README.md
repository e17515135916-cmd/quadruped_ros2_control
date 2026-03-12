# PPT必杀图快速生成工具 🎨

快速生成机器人项目演示所需的专业可视化图表，无需复杂配置！

## 🚀 快速开始

### 一键生成所有图表

```bash
cd quick_viz_tools
python3 generate_all.py
```

所有图表将保存到 `presentation_outputs/` 目录。

## 📊 可用图表

### 1. 工作空间对比图 (Workspace Comparison)
**证明导轨有用的关键图！**

```bash
python3 workspace_comparison.py
```

- 展示导轨扩展前后的工作空间差异
- 自动计算面积增加百分比
- 可自定义导轨扩展距离

**自定义参数：**
```bash
python3 workspace_comparison.py 0.15  # 150mm扩展
```

### 2. ROS节点通信图 (ROS Graph)
**展示系统架构的专业图！**

```bash
python3 ros_graph.py
```

- 展示闭环控制架构
- MPC + WBC 控制策略
- 前向控制流和反馈数据流

### 3. 状态机流转图 (FSM Diagram)
**展示穿越窗框策略！**

```bash
python3 fsm_diagram.py
```

- 4个关键状态
- 状态转换条件
- 机器人姿态变化示意

### 4. 数据曲线图 (Data Plot)
**展示控制效果的绝杀图！**

```bash
python3 data_plot.py
```

- 身体高度稳定性
- 导轨伸缩过程
- 速度控制效果
- IMU数据

**使用真实数据：**
```bash
python3 data_plot.py your_data.csv
```

## 📁 输出说明

所有图表默认保存到 `presentation_outputs/` 目录：

```
presentation_outputs/
├── workspace_comparison.png  # 工作空间对比图
├── ros_graph.png             # ROS通信图
├── fsm_diagram.png           # 状态机流转图
└── data_plot.png             # 数据曲线图
```

## 🎨 图表特点

- ✅ **高分辨率**: 300 DPI，适合PPT和论文
- ✅ **专业配色**: 深色科技风格
- ✅ **即开即用**: 无需配置文件
- ✅ **独立运行**: 每个脚本都可单独使用
- ✅ **演示数据**: 没有真实数据也能生成示例图

## 📦 依赖安装

```bash
pip install numpy matplotlib pandas scipy
```

## 💡 使用技巧

### 1. 批量生成不同参数的图表

```bash
# 生成不同导轨扩展距离的对比图
for ext in 0.05 0.10 0.15 0.20; do
    python3 workspace_comparison.py $ext
    mv presentation_outputs/workspace_comparison.png \
       presentation_outputs/workspace_${ext}m.png
done
```

### 2. 集成到你的数据采集流程

```python
# 在你的实验脚本中
import sys
sys.path.append('quick_viz_tools')
from data_plot import plot_data_curves

# 实验结束后自动生成图表
plot_data_curves(csv_path='experiment_data.csv', 
                output_path='results/plot.png')
```

### 3. 自定义图表样式

每个脚本都可以直接修改，所有绘图代码都很简单易懂：

```python
# 修改颜色
color = '#00bcd4'  # 改成你喜欢的颜色

# 修改字体大小
fontsize = 14

# 修改DPI
plt.savefig(output_path, dpi=300)  # 改成更高的DPI
```

## 🔧 故障排除

### 中文显示问题

如果中文显示为方块，安装中文字体：

```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei

# 或者修改脚本，使用英文标签
```

### 导入错误

确保在 `quick_viz_tools/` 目录下运行脚本：

```bash
cd quick_viz_tools
python3 generate_all.py
```

## 📝 与完整系统的关系

这些快速脚本是从完整的 `presentation_viz` 系统中提取的**精简版本**：

- ✅ **快速脚本** (quick_viz_tools/): 立即可用，无需配置
- 🔧 **完整系统** (presentation_viz/): 功能完整，支持配置文件、批量处理等

如果你需要：
- 快速出图 → 用这些脚本
- 自动化流程 → 用完整系统

## 🎯 下一步

1. **运行一键生成**: `python3 generate_all.py`
2. **查看输出**: 打开 `presentation_outputs/` 目录
3. **插入PPT**: 直接拖拽图片到PPT中
4. **调整参数**: 根据需要修改脚本参数

## 📧 问题反馈

如果遇到问题或需要新功能，请查看主项目的 `presentation_viz/` 目录。

---

**快速、简单、专业 - 让你的PPT更出彩！** 🚀
