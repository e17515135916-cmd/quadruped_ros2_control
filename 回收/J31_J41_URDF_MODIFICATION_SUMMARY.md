# J31和J41初始位置修改总结

## 修改内容

已修改URDF和启动脚本，使j31和j41（后腿髋关节）在启动时自动设置为180度（3.142弧度）。

## 修改的文件

### 1. `src/dog2_description/urdf/dog2.urdf.xacro`
- 在腿部宏定义中添加了 `hip_initial_position` 参数
- 为后续可能的扩展做准备

### 2. `view_robot_in_rviz.sh`
- 修改启动脚本，在RViz启动后自动运行初始位置设置
- 等待5秒让RViz完全启动
- 自动调用 `set_j31_j41_initial_position.py` 设置j31和j41为180度

### 3. `src/dog2_description/config/initial_joint_states.yaml`（新建）
- 创建了初始关节状态配置文件
- 记录了所有关节的初始位置
- 可用于未来的launch文件配置

## 使用方法

### 启动RViz并自动设置初始位置

```bash
cd ~/aperfect/carbot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
./view_robot_in_rviz.sh
```

脚本会自动：
1. 启动RViz
2. 等待5秒
3. 设置j31和j41为180度
4. 显示完成信息

### 手动设置初始位置（如果需要）

如果RViz已经在运行，可以手动运行：

```bash
python3 set_j31_j41_initial_position.py
```

## 预期效果

启动后，机器人应该显示：
- **j11**（前左腿髋关节）：0度，向下
- **j41**（前右腿髋关节）：0度，向下
- **j21**（后左腿髋关节）：0度，向下
- **j31**（后右腿髋关节）：180度，向下

所有四条腿都应该向下延伸，呈现"狗式"站立姿态。

## 技术说明

### 为什么j31和j41需要180度？

后腿（腿3和腿4）在URDF中有以下配置：
- `origin_rpy="1.5708 0 -3.1416"`（基座连接旋转180度）
- `hip_joint_rpy="3.1416 0 0"`（髋关节X轴旋转180度）

这些旋转导致后腿的坐标系翻转。当髋关节角度为0时，后腿向上弯曲。设置为180度后，后腿向下弯曲，与前腿方向一致。

### 关节限位

- **j11, j21**（前腿髋关节）：`-2.618` 到 `2.618` rad（±150度）
- **j31, j41**（后腿髋关节）：`-3.1416` 到 `3.1416` rad（±180度，360度旋转）

后腿髋关节有360度旋转能力，可以从0度旋转到180度。

## 下一步

完成Task 6.3：
- 验证零角度时的腿部方向
- 截图记录
- 确认所有四条腿都向下延伸

## 相关文件

- `set_j31_j41_initial_position.py` - 初始位置设置脚本
- `view_robot_in_rviz.sh` - 修改后的启动脚本
- `src/dog2_description/urdf/dog2.urdf.xacro` - URDF配置
- `src/dog2_description/config/initial_joint_states.yaml` - 初始状态配置
- `J31_J41_180DEG_TEST.md` - 测试文档
