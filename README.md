# quadruped_ros2_control

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-22314E?logo=ros)](https://docs.ros.org/en/humble/index.html)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)](https://ubuntu.com/)
[![Simulation](https://img.shields.io/badge/Simulation-Gazebo%20%2F%20Ignition-2D7D9A)](https://gazebosim.org/)

Dog2 quadruped robot control workspace for **ROS 2**, including robot description, CHAMP-based locomotion, MPC/WBC research modules, visualization, and supporting dynamics/kinematics packages.

Dog2 四足机器人 ROS 2 控制工作区，覆盖：机器人模型、基础步态控制、MPC/WBC 研究模块、可视化与动力学/运动学工具链。

---

## Table of Contents | 目录

- [Overview | 项目概览](#overview--项目概览)
- [Repository Layout | 仓库结构](#repository-layout--仓库结构)
- [Requirements | 环境要求](#requirements--环境要求)
- [Quick Start | 快速开始](#quick-start--快速开始)
- [Launch Matrix | 常用启动矩阵](#launch-matrix--常用启动矩阵)
- [Developer Workflow | 开发流程建议](#developer-workflow--开发流程建议)
- [Troubleshooting | 常见问题](#troubleshooting--常见问题)
- [Acknowledgements | 致谢](#acknowledgements--致谢)

---

## Overview | 项目概览

This repository is suitable for:

- ROS 2 quadruped simulation bring-up
- Locomotion controller integration (CHAMP / MPC / WBC)
- Control algorithm debugging with RViz/Gazebo
- Teaching/research demos for legged robotics

本仓库适用于：

- 四足机器人 ROS 2 仿真与控制链路搭建
- CHAMP / MPC / WBC 控制器组合验证
- 使用 RViz/Gazebo 的可视化调参与问题定位
- 课程实验与科研原型开发

---

## Repository Layout | 仓库结构

```text
quadruped_ros2_control/
├── dog2_description/       # Robot URDF/Xacro, meshes, Gazebo launch files
├── dog2_champ_config/      # CHAMP config, gait params, keyboard/demo scripts
├── dog2_mpc/               # MPC controller, constraints, state machines, tests
├── dog2_wbc/               # Whole-body controller nodes (simple/complete)
├── dog2_kinematics/        # Leg inverse kinematics
├── dog2_dynamics/          # Dynamics model & tests
├── dog2_visualization/     # RViz visualization utilities and launch files
├── dog2_state_estimation/  # State estimation package skeleton
├── dog2_interfaces/        # Custom ROS interfaces
└── champ/                  # Upstream CHAMP-related packages
```

---

## Requirements | 环境要求

Recommended baseline:

- **Ubuntu 22.04**
- **ROS 2 Humble**
- Gazebo Classic / Ignition Fortress (depending on selected launch file)

Install base tools:

```bash
sudo apt update
sudo apt install -y python3-rosdep python3-colcon-common-extensions
```

Initialize rosdep (first-time only):

```bash
sudo rosdep init
rosdep update
```

---

## Quick Start | 快速开始

### 1) Clone

```bash
git clone https://github.com/e17515135916-cmd/quadruped_ros2_control.git
cd quadruped_ros2_control
```

### 2) Install dependencies

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths . --ignore-src -r -y
```

### 3) Build

```bash
colcon build --symlink-install
source install/setup.bash
```

### 4) Bring up simulation (CHAMP path)

```bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
```

### 5) Control from keyboard (new terminal)

```bash
cd <path-to>/quadruped_ros2_control
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 dog2_champ_config/scripts/dog2_keyboard_control.py
```

---

## Launch Matrix | 常用启动矩阵

> Use these as entry points; inspect each launch file for arguments.

### CHAMP-oriented

```bash
ros2 launch dog2_champ_config dog2_champ_gazebo.launch.py
ros2 launch dog2_champ_config dog2_champ_fortress.launch.py
ros2 launch dog2_champ_config champ.launch.py
```

### Description / Gazebo-oriented

```bash
ros2 launch dog2_description gazebo_dog2.launch.py
ros2 launch dog2_description gazebo_headless.launch.py
ros2 launch dog2_description view_dog2.launch.py
```

### MPC-oriented

```bash
ros2 launch dog2_mpc mpc_node.launch.py
ros2 launch dog2_mpc mpc_wbc_simulation.launch.py
ros2 launch dog2_mpc complete_simulation.launch.py
```

### Visualization

```bash
ros2 launch dog2_visualization visualization.launch.py
ros2 launch dog2_visualization visualization_no_gazebo.launch.py
```

---

## Developer Workflow | 开发流程建议

1. **Start simple**: ensure model + baseline control works before enabling MPC/WBC.
2. **Observe key signals**: `/joint_states`, `/odom`, foot-force/contact markers.
3. **Iterate parameters incrementally**: gait, constraints, controller gains.
4. **Keep launch configs reproducible**: save command history and tuned YAMLs.

Useful commands:

```bash
ros2 topic list
ros2 node list
ros2 topic echo /joint_states
ros2 topic echo /odom
colcon test
colcon test-result --verbose
```

---

## Troubleshooting | 常见问题

### Build fails due to missing dependencies

- Re-run:

  ```bash
  source /opt/ros/humble/setup.bash
  rosdep install --from-paths . --ignore-src -r -y
  ```

### Robot does not move in simulation

- Confirm control nodes are alive: `ros2 node list`
- Confirm velocity command is published: `ros2 topic echo /cmd_vel`
- Confirm joint feedback exists: `ros2 topic echo /joint_states`

### RViz has no useful output

- Check `Fixed Frame` configuration.
- Check marker/odometry topics are being published.

---

## Acknowledgements | 致谢

- [CHAMP](https://github.com/chvmp/champ) and contributors.
- ROS 2 and Gazebo open-source communities.

