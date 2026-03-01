# 🤖 Dog2 四足机器人 ROS 2 控制系统

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-22314E?logo=ros)](https://docs.ros.org/en/humble/index.html)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)](https://ubuntu.com/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Fortress-2D7D9A)](https://gazebosim.org/)
[![Tests](https://img.shields.io/badge/Tests-97.5%25%20Pass-brightgreen)](src/dog2_motion_control/FINAL_CHECKPOINT_REPORT.md)

Dog2 四足机器人 ROS 2 控制工作区，包含完整的蜘蛛机器人基础运动控制系统。

**Dog2 Quadruped Robot ROS 2 Control Workspace** - Complete spider robot basic motion control system with crawl gait implementation.

---

## ✨ 项目特点 | Features

- ✅ **完整的爬行步态实现** - 静态稳定的四足爬行步态（每次一条腿摆动）
- ✅ **50Hz 实时控制循环** - 高频控制保证运动平滑性
- ✅ **Gazebo Fortress 仿真** - 完整的物理仿真环境
- ✅ **16通道关节控制** - 4条腿 × (1导轨 + 3旋转关节)
- ✅ **运动学求解器** - 支持IK/FK的完整运动学链
- ✅ **错误处理机制** - 导轨滑动检测、关节卡死检测、紧急安全姿态
- ✅ **97.5% 测试覆盖** - 116/119 单元测试通过
- ✅ **完整文档** - 需求、设计、实现全流程文档

---

## 📋 目录 | Table of Contents

- [快速开始](#-快速开始--quick-start)
- [系统架构](#-系统架构--system-architecture)
- [仓库结构](#-仓库结构--repository-layout)
- [环境要求](#-环境要求--requirements)
- [测试结果](#-测试结果--test-results)
- [文档](#-文档--documentation)
- [故障排除](#-故障排除--troubleshooting)
- [致谢](#-致谢--acknowledgements)

---

## 🚀 快速开始 | Quick Start

### 一键启动 | One-Command Launch

```bash
cd ~/aperfect/carbot_ws
bash start_fortress.sh
```

这个脚本会自动完成：
1. 重新编译 dog2_motion_control 包
2. Source ROS 2 环境
3. 检查 Gazebo Fortress
4. 启动完整的仿真系统

**This script automatically:**
1. Rebuilds dog2_motion_control package
2. Sources ROS 2 environment
3. Checks Gazebo Fortress
4. Launches complete simulation system

### 等待系统启动 | Wait for System Startup

请耐心等待约 **10-15秒**：

- **0-3秒**: Gazebo 窗口打开
- **3-5秒**: 机器人模型 spawn
- **5-8秒**: 控制器加载
- **10秒**: spider_robot_controller 启动

### 测试机器人运动 | Test Robot Motion

在新终端中发送速度命令：

```bash
# 前进 | Move forward
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.05, y: 0.0, z: 0.0}}" --once

# 停止 | Stop
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}}" --once
```

### 预期结果 | Expected Results

✅ 机器人站立在地面上  
✅ 发送速度命令后开始爬行  
✅ 每次只有一条腿摆动  
✅ 其余三条腿保持支撑  
✅ 腿部顺序：leg1 → leg3 → leg2 → leg4  

---

## 🏗️ 系统架构 | System Architecture

```
dog2_fortress_with_control.launch.py (dog2_description包)
    ├── Gazebo Fortress
    ├── Robot State Publisher
    ├── Spawn Robot
    └── ros2_control Controllers
         ├── joint_state_broadcaster
         ├── joint_trajectory_controller (12个旋转关节)
         └── rail_position_controller (4个导轨关节)

spider_with_fortress.launch.py (dog2_motion_control包)
    ├── 包含上述启动文件
    └── spider_robot_controller (10秒后启动)
         ├── Gait Generator (步态生成器)
         ├── Kinematics Solver (运动学求解器)
         ├── Trajectory Planner (轨迹规划器)
         └── Joint Controller (关节控制器)
```

### 核心组件 | Core Components

1. **Gait Generator** - 生成爬行步态的相位和脚部轨迹
2. **Kinematics Solver** - IK/FK求解，支持4条腿的坐标系转换
3. **Trajectory Planner** - 轨迹平滑和插值
4. **Joint Controller** - 16通道关节命令发送和状态监控

---

## 📁 仓库结构 | Repository Layout

```text
quadruped_ros2_control/
├── dog2_description/          # 机器人URDF/Xacro模型、网格文件
│   ├── urdf/                  # URDF/Xacro文件
│   ├── meshes/                # STL网格文件
│   └── launch/                # Gazebo启动文件
│
├── dog2_motion_control/       # ⭐ 蜘蛛机器人运动控制系统（核心）
│   ├── dog2_motion_control/   # Python包
│   │   ├── spider_robot_controller.py  # 主控制器
│   │   ├── gait_generator.py           # 步态生成器
│   │   ├── kinematics_solver.py        # 运动学求解器
│   │   ├── joint_controller.py         # 关节控制器
│   │   ├── trajectory_planner.py       # 轨迹规划器
│   │   └── config_loader.py            # 配置加载器
│   ├── test/                  # 单元测试和集成测试
│   ├── launch/                # 启动文件
│   ├── config/                # 配置文件
│   └── docs/                  # 详细文档
│
├── dog2_kinematics/           # 运动学工具
├── dog2_dynamics/             # 动力学模型
├── dog2_visualization/        # RViz可视化
├── dog2_state_estimation/     # 状态估计
├── dog2_interfaces/           # 自定义ROS接口
├── dog2_gait_planner/         # 步态规划
├── dog2_mpc/                  # MPC控制器
└── dog2_wbc/                  # 全身控制器
```

---

## 💻 环境要求 | Requirements

### 必需环境 | Required

- **Ubuntu 22.04**
- **ROS 2 Humble**
- **Gazebo Fortress** (不是 Gazebo Classic)
- **Python 3.10+**

### 安装依赖 | Install Dependencies

```bash
# 安装ROS 2 Humble
sudo apt update
sudo apt install -y ros-humble-desktop

# 安装Gazebo Fortress
sudo apt install -y ros-humble-ros-gz

# 安装构建工具
sudo apt install -y python3-rosdep python3-colcon-common-extensions

# 初始化rosdep（首次）
sudo rosdep init
rosdep update

# 安装项目依赖
cd ~/aperfect/carbot_ws/src
rosdep install --from-paths . --ignore-src -r -y
```

### 构建项目 | Build Project

```bash
cd ~/aperfect/carbot_ws
colcon build --symlink-install
source install/setup.bash
```

---

## ✅ 测试结果 | Test Results

### 单元测试 | Unit Tests

- **通过率**: 97.5% (116/119 tests)
- **需求满足**: 100% (8/8 requirements)
- **正确性属性**: 100% (22/22 properties)
- **系统完整性**: 100% (15/15 items)

### 运行测试 | Run Tests

```bash
cd ~/aperfect/carbot_ws
source install/setup.bash

# 运行所有测试
colcon test --packages-select dog2_motion_control

# 查看测试结果
colcon test-result --verbose
```

详细测试报告：[FINAL_CHECKPOINT_REPORT.md](src/dog2_motion_control/FINAL_CHECKPOINT_REPORT.md)

---

## 📚 文档 | Documentation

### 核心文档 | Core Documentation

- **[START_HERE.md](START_HERE.md)** - 快速启动指南
- **[需求文档](src/.kiro/specs/spider-robot-basic-motion/requirements.md)** - 完整需求规格
- **[设计文档](src/.kiro/specs/spider-robot-basic-motion/design.md)** - 系统设计和架构
- **[任务列表](src/.kiro/specs/spider-robot-basic-motion/tasks.md)** - 实现任务清单

### 详细文档 | Detailed Documentation

- **[FINAL_SUMMARY.md](src/dog2_motion_control/FINAL_SUMMARY.md)** - 项目总结
- **[QUICK_START.md](src/dog2_motion_control/QUICK_START.md)** - 详细快速指南
- **[GAZEBO_FORTRESS_TROUBLESHOOTING.md](src/dog2_motion_control/GAZEBO_FORTRESS_TROUBLESHOOTING.md)** - 故障排除指南
- **[LAUNCH_FILES_GUIDE.md](src/dog2_motion_control/LAUNCH_FILES_GUIDE.md)** - 启动文件说明

---

## 🔧 故障排除 | Troubleshooting

### Q1: 机器人腿部耷拉

**问题**: 机器人spawn后腿部下垂，没有站立姿态

**原因**: 控制器启动时没有发送初始站立姿态命令

**解决**: 正在开发中，将在下一个版本修复

### Q2: 找不到启动文件

**解决**: 
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_motion_control --symlink-install
source install/setup.bash
```

### Q3: 控制器加载失败

**检查**: 
```bash
ros2 control list_controllers
ros2 topic list | grep joint
```

**解决**: 
1. 关闭所有终端
2. 重新运行 `bash start_fortress.sh`
3. 等待更长时间（15秒）

### Q4: Gazebo窗口不显示

**检查**: 
```bash
gz sim --version
```

**解决**: 确保安装了 Gazebo Fortress，不是 Gazebo Classic

更多问题请查看：[GAZEBO_FORTRESS_TROUBLESHOOTING.md](src/dog2_motion_control/GAZEBO_FORTRESS_TROUBLESHOOTING.md)

---

## 🎯 开发路线图 | Roadmap

- [x] 基础爬行步态实现
- [x] Gazebo Fortress 集成
- [x] 16通道关节控制
- [x] 运动学求解器
- [x] 错误处理机制
- [ ] 初始站立姿态
- [ ] 动态步态切换
- [ ] 地形适应
- [ ] 实机部署

---

## 🤝 贡献 | Contributing

欢迎提交 Issue 和 Pull Request！

**Welcome to submit Issues and Pull Requests!**

---

## 📄 许可证 | License

本项目采用 MIT 许可证。

**This project is licensed under the MIT License.**

---

## 🙏 致谢 | Acknowledgements

- ROS 2 和 Gazebo 开源社区
- 所有贡献者和测试者

**Thanks to:**
- ROS 2 and Gazebo open-source communities
- All contributors and testers

---

## 📞 联系方式 | Contact

- **GitHub**: [e17515135916-cmd/quadruped_ros2_control](https://github.com/e17515135916-cmd/quadruped_ros2_control)
- **Issues**: [提交问题](https://github.com/e17515135916-cmd/quadruped_ros2_control/issues)

---

**最后更新 | Last Updated**: 2026-03-01  
**状态 | Status**: ✅ 系统就绪 | System Ready

