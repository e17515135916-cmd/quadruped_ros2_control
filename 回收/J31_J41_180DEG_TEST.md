# J31和J41初始位置180度测试

## 问题描述

当前后腿（j21和j31）向上弯曲，而不是像前腿（j11和j41）那样向下弯曲。

**原因分析：**
- 后腿有 `hip_rpy="3.1416 0 0"`（180度X轴旋转）
- 这导致后腿的坐标系翻转
- 当髋关节角度为0时，后腿向上弯曲

## 测试方案

测试将j31和j41的初始位置设为3.142弧度（180度），看是否能让后腿向下弯曲。

## 测试步骤

### 1. 启动RViz（终端1）

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
./view_robot_in_rviz.sh
```

### 2. 运行初始位置设置脚本（终端2）

```bash
cd ~/aperfect/carbot_ws
./test_j31_j41_180deg.sh
```

或者直接运行：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 set_j31_j41_initial_position.py
```

### 3. 观察效果

在RViz中观察：
- **j31**（腿3的髋关节）是否向下弯曲
- **j41**（腿4的髋关节）是否向下弯曲
- 所有四条腿是否都向下延伸

## 预期结果

如果测试成功：
- 所有四条腿都应该向下延伸
- j31和j41在3.142弧度位置时应该与j11和j21在0弧度位置时的方向一致

## 下一步

如果测试成功，需要：

1. **方案A：修改URDF默认初始位置**
   - 在URDF中为j31和j41设置初始位置为3.142
   - 使用 `<origin>` 标签的初始角度

2. **方案B：创建launch配置**
   - 在launch文件中设置初始关节状态
   - 使用 `initial_joint_states` 参数

3. **方案C：修改joint_state_publisher配置**
   - 在配置文件中设置默认关节位置

## 当前配置

### 腿部配置对比

| 腿 | 编号 | hip_rpy | 当前问题 |
|---|------|---------|---------|
| 前左 | j11 | 默认(0 0 0) | ✓ 向下 |
| 前右 | j41 | 默认(0 0 0) | ✓ 向下 |
| 后左 | j21 | 3.1416 0 0 | ✗ 向上 |
| 后右 | j31 | 3.1416 0 0 | ✗ 向上 |

### 关节限位

- j11, j41: `lower="-2.618"` `upper="2.618"` (±150度)
- j21, j31: `lower="-3.1416"` `upper="3.1416"` (±180度，360度旋转)

## 相关文件

- `set_j31_j41_initial_position.py` - 设置初始位置的脚本
- `test_j31_j41_180deg.sh` - 测试启动脚本
- `src/dog2_description/urdf/dog2.urdf.xacro` - URDF配置文件
