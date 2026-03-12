# quadruped_ros2_control

Dog2 四足机器人（蜘蛛形态）ROS 2 控制工程，目标是在 **ROS 2 Humble + Gazebo Fortress** 上完成从建模、步态、逆运动学到 MPC/WBC 的仿真控制闭环。

> 说明：本项目主要在 Linux 环境开发。你现在在备用 Windows 电脑补文档完全没问题——推荐通过 **WSL2 Ubuntu** 运行代码与仿真。

---

## 1. 项目功能概览

- ✅ 四足机器人 URDF/Xacro 建模与仿真启动（`dog2_description`）
- ✅ 基础运动控制与步态执行（`dog2_motion_control`）
- ✅ 运动学与动力学计算（`dog2_kinematics` / `dog2_dynamics`）
- ✅ 模型预测控制 MPC（`dog2_mpc`）
- ✅ 全身控制 WBC（`dog2_wbc`）
- ✅ 可视化与调试工具（`dog2_visualization`）
- ✅ 自定义消息接口（`dog2_interfaces`）

---

## 2. 仓库结构

```text
quadruped_ros2_control/
├── src/
│   ├── dog2_description/      # 机器人模型、Gazebo/rviz 启动、控制器配置
│   ├── dog2_motion_control/   # 主控制逻辑、步态、控制节点
│   ├── dog2_kinematics/       # 运动学求解（含 4-DOF 腿 IK）
│   ├── dog2_dynamics/         # 动力学计算模块
│   ├── dog2_mpc/              # 模型预测控制与约束处理
│   ├── dog2_wbc/              # 全身控制
│   ├── dog2_visualization/    # 可视化节点和工具
│   ├── dog2_interfaces/       # ROS 2 接口定义
│   └── ...
├── START_HERE.md              # 快速上手文档
├── PROJECT_ARCHITECTURE.md    # 架构说明
└── README.md
```

---

## 3. 环境要求

### Linux（推荐）

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress
- colcon / rosdep

### Windows（备用开发）

如果你在 Windows 上：

1. 安装 **WSL2 + Ubuntu 22.04**
2. 在 WSL 内安装 ROS 2 Humble
3. 在 WSL 内执行本仓库全部构建和运行命令

> 不建议直接在原生 Windows Python/终端里跑 ROS 2 Gazebo 工作流，兼容性和依赖管理成本较高。

---

## 4. 快速开始

### 4.1 获取代码

```bash
git clone https://github.com/e17515135916-cmd/quadruped_ros2_control.git
cd quadruped_ros2_control
```

### 4.2 安装依赖（在 ROS 2 工作空间）

```bash
# 假设仓库位于 ~/ws_dog2/src/quadruped_ros2_control
cd ~/ws_dog2
rosdep install --from-paths src --ignore-src -r -y
```

### 4.3 编译

```bash
cd ~/ws_dog2
colcon build --symlink-install
source install/setup.bash
```

### 4.4 启动仿真（示例）

根据你当前维护的 launch 文件选择其一，例如：

```bash
ros2 launch dog2_description gazebo_dog2.launch.py
```

或使用项目已有的一键脚本（如果你本地已配置）：

```bash
bash start_fortress.sh
```

---

## 5. 运行后检查

新开终端（记得 `source install/setup.bash`）后可用：

```bash
ros2 node list
ros2 topic list
ros2 control list_controllers
```

发送简单速度指令：

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.05, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --once
```

---

## 6. 常见问题（简版）

### Q1：Windows 上能不能只改代码不跑仿真？
可以。你可以在 Windows 编辑器里改代码，然后在 Linux/WSL 中编译运行。

### Q2：`ros2: command not found`？
说明 ROS 2 环境没 source：

```bash
source /opt/ros/humble/setup.bash
source ~/ws_dog2/install/setup.bash
```

### Q3：Gazebo 启动了但机器人不动？
优先检查：

1. 控制器是否已加载
2. `/cmd_vel` 是否有数据
3. 机器人状态节点是否正常

---

## 7. 相关文档

- [START_HERE.md](START_HERE.md)
- [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
- [SYSTEM_ARCHITECTURE_DIAGRAM.md](SYSTEM_ARCHITECTURE_DIAGRAM.md)
- [ROS2_CONTROL_DATA_FLOW_DIAGRAM.md](ROS2_CONTROL_DATA_FLOW_DIAGRAM.md)

---

## 8. 维护建议

- 每次修改 launch / 控制器参数后，及时更新 README 和对应模块文档。
- 保持“代码可跑 + 文档可复现”作为提交标准。
- 若后续计划开源，建议补充 License、贡献指南和版本日志。

---

**作者**：路志强  
**README 补写时间**：2026-03-12  
**建议开发平台**：Linux / WSL2 Ubuntu
