# Dog2 Motion Control - 项目结构

## 目录结构

```
dog2_motion_control/
├── dog2_motion_control/              # Python包源代码
│   ├── __init__.py                   # 包初始化
│   ├── spider_robot_controller.py    # 主控制器
│   ├── kinematics_solver.py          # 运动学求解器
│   ├── gait_generator.py             # 步态生成器
│   ├── trajectory_planner.py         # 轨迹规划器
│   └── joint_controller.py           # 关节控制器
│
├── test/                             # 测试目录
│   ├── __init__.py
│   └── test_basic.py                 # 基础测试
│
├── config/                           # 配置文件
│   └── gait_params.yaml              # 步态参数配置
│
├── launch/                           # 启动文件
│   └── spider_controller.launch.py  # 控制器启动文件
│
├── resource/                         # ROS 2资源文件
│   └── dog2_motion_control
│
├── package.xml                       # ROS 2包描述文件
├── setup.py                          # Python包安装配置
├── setup.cfg                         # 安装配置
├── pytest.ini                        # pytest配置
├── requirements.txt                  # Python依赖
├── README.md                         # 项目说明
└── PROJECT_STRUCTURE.md              # 本文件
```

## 核心模块说明

### 1. spider_robot_controller.py
主控制器，协调所有子系统：
- 初始化ROS 2节点
- 创建控制循环（50Hz）
- 协调步态生成、运动学求解、轨迹规划和关节控制

### 2. kinematics_solver.py
运动学求解器：
- 逆运动学求解（IK）：脚部位置 → 关节角度
- 正运动学求解（FK）：关节角度 → 脚部位置
- 支持4条腿的坐标系转换

### 3. gait_generator.py
步态生成器：
- 生成爬行步态（crawl gait）
- 计算腿部相位和脚部轨迹
- 确保静态稳定性（至少3腿着地）

### 4. trajectory_planner.py
轨迹规划器：
- 摆动相轨迹规划（抛物线）
- 支撑相轨迹规划（线性）
- 确保速度连续性

### 5. joint_controller.py
关节控制器：
- 发送16通道关节命令（4导轨 + 12旋转关节）
- 订阅关节状态
- 监控导轨位置
- 关节限位检查

## 数据模型

### GaitConfig
步态配置参数：
- stride_length: 步长（米）
- stride_height: 步高（米）
- cycle_time: 步态周期（秒）
- duty_factor: 支撑相占比
- body_height: 身体高度（米）
- gait_type: 步态类型

## ROS 2接口

### 发布话题
- `/joint_trajectory_controller/joint_trajectory` (trajectory_msgs/JointTrajectory)
  - 16通道关节命令

### 订阅话题
- `/joint_states` (sensor_msgs/JointState)
  - 关节状态反馈
- `/cmd_vel` (geometry_msgs/Twist)
  - 速度命令（未来实现）

## 测试框架

### 单元测试
使用pytest框架：
```bash
pytest test/
```

### 属性测试
使用hypothesis库进行基于属性的测试：
- 每个属性测试至少100次迭代
- 验证21个正确性属性

## 构建和安装

### 构建包
```bash
colcon build --packages-select dog2_motion_control
```

### 安装依赖
```bash
pip3 install -r requirements.txt
```

### 运行测试
```bash
pytest
```

## 配置文件

### gait_params.yaml
包含以下配置：
- 步态参数（步长、步高、周期等）
- 关节限位（导轨和旋转关节）
- 控制参数（频率、最大速度等）

## 开发指南

1. **添加新功能**：在对应的模块中添加方法
2. **编写测试**：在test/目录下创建测试文件
3. **更新配置**：修改config/gait_params.yaml
4. **构建验证**：运行colcon build和pytest

## 依赖项

### ROS 2依赖
- rclpy
- std_msgs
- sensor_msgs
- trajectory_msgs
- geometry_msgs
- builtin_interfaces

### Python依赖
- numpy >= 1.20.0
- scipy >= 1.7.0
- hypothesis >= 6.0.0
- pytest >= 7.0.0

## 下一步开发

参考任务列表：`.kiro/specs/spider-robot-basic-motion/tasks.md`

当前完成：
- ✅ 任务1：项目结构和基础设施搭建

待实现：
- 任务2：运动学求解器
- 任务3：步态生成器
- 任务4：轨迹规划器
- 任务5：关节控制器
- 任务6：主控制器集成
- ...
