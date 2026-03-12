# PROJECT_ARCHITECTURE

> 目的：让新的 AI 助手在一次会话内快速理解该项目的技术栈、目录结构、运行方式与开发规范，避免重复探索。

## 1. 项目概览

- 项目名称：Dog2 四足机器人 ROS 2 控制工作区
- 类型：ROS 2 机器人控制系统（非传统前后端 Web 项目）
- 主要目标：在 Gazebo Fortress 中实现四足（蜘蛛形态）机器人基础运动控制、步态规划、运动学/动力学控制与可视化
- 核心运行方式：
  - ROS 2 Launch 启动系统组件
  - Topic 发布/订阅进行模块通信
  - 控制器以固定频率（典型 50Hz）执行控制循环

---

## 2. 技术栈概览

### 2.1 平台与中间件

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress
- ros2_control（关节控制与执行接口）

### 2.2 语言与包类型

- Python（`rclpy`）
  - 典型用于高层控制逻辑、步态控制、编排
  - 包类型：`ament_python`
- C++（`rclcpp`）
  - 典型用于 MPC/WBC/动力学等性能敏感模块
  - 包类型：`ament_cmake`

### 2.3 构建与依赖管理

- 构建工具：`colcon`
- 依赖安装：`rosdep`
- 常用命令：

```bash
cd ~/aperfect/carbot_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## 3. 架构总览（逻辑分层）

1. **仿真/模型层**（`dog2_description`）
   - URDF/Xacro、Gazebo 启动、控制器配置
2. **高层运动控制层**（`dog2_motion_control`）
   - 步态生成、轨迹规划、IK/FK 调用、16 通道指令下发
3. **优化控制层**（`dog2_mpc` / `dog2_wbc`）
   - MPC、WBC 等中高阶控制
4. **支撑能力层**
   - `dog2_dynamics`（动力学）
   - `dog2_state_estimation`（状态估计）
   - `dog2_interfaces`（接口定义）
   - `dog2_visualization`（可视化）

通信主线：节点间通过 ROS Topic/Service/Action 协作，非 HTTP API 主导。

---

## 4. 目录说明（当前工作区）

> 以 `carbot_ws/src` 为主源码区。

### 4.1 主要包

- `dog2_motion_control/`：核心运动控制（Python）
  - 关键模块：
    - `spider_robot_controller.py`（主控制器）
    - `gait_generator.py`（步态）
    - `trajectory_planner.py`（轨迹）
    - `kinematics_solver.py`（运动学）
    - `joint_controller.py`（关节命令接口）
- `dog2_description/`：机器人模型与仿真描述
- `dog2_mpc/`：模型预测控制（C++）
- `dog2_wbc/`：全身控制（C++）
- `dog2_dynamics/`：动力学模型
- `dog2_visualization/`：可视化与 RViz 相关
- `dog2_interfaces/`：消息/接口相关
- `dog2_gait_planner/`：步态规划
- `dog2_state_estimation/`：状态估计
- `dog2_demos/`：演示脚本

### 4.2 目录卫生建议（强制）

- `build/`, `install/`, `log/` 属于构建产物，**不要混入源码版本管理**。
- 历史备份（`*.bak`, `*.backup`, `archive_*`）应集中管理，避免误改。
- 临时脚本、调试日志统一放到 `tools/` 或 `tmp/`，并加入 `.gitignore`。

---

## 5. 启动与执行链路

典型执行链：

1. Launch 启动 Gazebo + robot_state_publisher + ros2_control 控制器
2. 启动主控制节点（如 `spider_robot_controller`）
3. 控制循环执行：
   - 读取命令输入（如 `/cmd_vel`）
   - 更新步态相位
   - 计算足端目标
   - IK 转换到关节空间
   - 发布到关节轨迹控制器

> 本项目“路由”是 ROS Launch 与 Topic 链路，不是 Web Router。

---

## 6. 数据交互规范（替代“接口规范”）

### 6.1 通信方式

- 首选 ROS Topic（实时流）
- 需要请求-响应时使用 Service
- 长任务/可取消任务使用 Action

### 6.2 命名约定

- Topic 名称语义清晰、统一前缀
- 单位统一：
  - 角度用弧度（rad）
  - 位移用米（m）
  - 速度用 m/s 或 rad/s

### 6.3 错误与安全

- 关键控制链必须有异常降级路径：
  - 连接丢失检测
  - IK 失败回退
  - 导轨滑移监控
  - 紧急安全姿态

---

## 7. 核心开发规范

## 7.1 新增“功能模块”（替代“新增页面”）

新增功能优先按“包内模块”而非散落脚本实现。

推荐步骤：

1. 在对应包内新增模块文件（如 `new_planner.py`）
2. 在主控制器中注入并调用（构造 + update 链路）
3. 在 `launch/` 暴露运行入口
4. 增加单元测试（`test/`）
5. 更新包文档与配置样例

## 7.2 新增 ROS 节点

1. 明确节点职责（单一职责）
2. 定义输入/输出 Topic（消息类型、频率、单位）
3. 处理异常与超时
4. 提供 launch 启动配置
5. 提供最小可运行示例

## 7.3 新增“接口”（Topic/Service/Action）

1. 先确认是否可复用现有消息类型
2. 需要自定义时在 `dog2_interfaces` 统一定义
3. 更新调用方与订阅方同步迁移
4. 增加兼容期日志，避免静默破坏

## 7.4 配置管理

- 运行参数优先放 YAML（如 gait 参数）
- 参数加载后在周期边界应用，避免控制抖动
- 禁止把环境相关路径硬编码进算法逻辑

## 7.5 日志与调试

- 统一使用 ROS logger
- Debug 信息可通过专用 topic 输出
- 禁止在高频循环中无节制打印

---

## 8. 测试策略

### 8.1 测试层次

- 单元测试：算法函数、运动学、边界条件
- 集成测试：控制链路联调（步态->IK->关节命令）
- 仿真回归：Gazebo 场景下稳定性与异常行为

### 8.2 每次改动最少验证

```bash
colcon build --symlink-install
colcon test --packages-select dog2_motion_control
colcon test-result --verbose
```

关键改动（控制、安全）必须补充故障注入测试。

---

## 9. 已识别技术债（优先级）

### P0（优先处理）

- 清理 `src` 下构建产物（`build/install/log`）混入
- 收拢历史备份与临时文件，减少误修改风险

### P1

- 统一日志风格（print 与 logger 混用问题）
- 强化连接恢复策略（不仅检测恢复）

### P2

- 按职责进一步拆分高耦合控制器文件
- 完善异常分支覆盖率（紧急模式、连续 IK 失败）

---

## 10. AI 协作提示（给后续会话）

当新的 AI 接手本仓库时，建议按以下顺序工作：

1. 先读本文件 + `src/README.md`
2. 再读目标包的 `package.xml` 与 `launch/`
3. 修改前确认是否触及安全链路（导轨锁定、急停、IK 回退）
4. 优先小步改动并立即跑最小测试
5. 不在未确认情况下批量删除模型/备份文件

---

## 11. 快速入口清单

- 工作区：`~/aperfect/carbot_ws`
- 主源码：`~/aperfect/carbot_ws/src`
- 核心包：`src/dog2_motion_control`
- 关键入口：
  - `dog2_motion_control/dog2_motion_control/spider_robot_controller.py`
  - `dog2_motion_control/launch/*.launch.py`
  - `dog2_description/launch/*.launch.py`

---

## 12. 文档维护规则

- 本文档属于“全局架构索引”，每次发生以下变更必须更新：
  - 新增/删除核心包
  - 控制链路变化
  - 启动方式变化
  - 安全策略变化
- 建议在每次里程碑版本后做一次结构审计。
