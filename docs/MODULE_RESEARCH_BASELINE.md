# Dog2 模块研究基线

本文档用于后续逐模块推进 Dog2 越障控制栈。目标是先把模块边界、接口契约和验证门槛固定下来，再进入代码修改，避免后续改动反复破坏已经稳定的部分。

## 总原则

1. 先确认结构真值源，再改算法。
2. 每次只推进一个模块，跨模块修改必须有明确接口理由。
3. 每个模块完成后留下固定验证命令。
4. 后续模块修改必须先跑前序模块的快速回归。
5. 不把临时动作脚本当作最终控制链路，越障动作应进入现有 `MPC + WBC + effort_controller` 链路。

## 真实运行链路

窗型越障 research stack 的主链路：

```text
dog2_bringup/launch/window_crossing_test.launch.py
  -> crossing_trial.launch.py
    -> system.launch.py
      -> sim_base.launch.py
        -> effort_research_sim.launch.py
          -> Gazebo + robot_state_publisher + joint_state_broadcaster + effort_controller
      -> control_stack.launch.py
        -> dog2_state_estimation/sim_state_estimator_node.py
        -> dog2_gait_planner/gait_scheduler_node.py
        -> dog2_mpc/mpc_node_complete
        -> dog2_wbc/wbc_node_complete
        -> dog2_bringup/wbc_effort_mux
```

核心 topic 链路：

```text
/joint_states
/dog2/state_estimation/odom
/dog2/state_estimation/robot_state
/dog2/gait/contact_phase
/enable_crossing
  -> mpc_node_complete
  -> /dog2/mpc/crossing_state
  -> /dog2/mpc/foot_forces
  -> wbc_node_complete
  -> /dog2/wbc/joint_effort_command
  -> /dog2/wbc/rail_effort_command
  -> wbc_effort_mux
  -> /effort_controller/commands
```

## 模块 0：结构真值源

范围：

- `src/dog2_description/urdf/dog2.urdf.xacro`
- `src/dog2_motion_control/dog2_motion_control/joint_names.py`
- `src/dog2_motion_control/dog2_motion_control/urdf_joint_limits.py`
- `src/dog2_motion_control/config/effort_controllers.yaml`

当前结论：

- 单腿是 `1P + 3R`：`rail + coxa + femur + tibia`。
- 16 通道顺序固定为每腿 `rail, coxa, femur, tibia`，腿顺序 `lf, lh, rh, rf`。
- URDF 语义注释规定：
  - `rail_joint` 正方向为机身 `+X`。
  - `coxa_joint` 是 hip yaw。
  - `femur_joint` 和 `tibia_joint` 是 pitch。
- rail 限位不是统一符号：
  - `lf_rail_joint`: `[0.0, 0.111]`
  - `lh_rail_joint`: `[-0.111, 0.0]`
  - `rh_rail_joint`: `[0.0, 0.111]`
  - `rf_rail_joint`: `[-0.111, 0.0]`

不可破坏约束：

- 不改 URDF/xacro/mesh，除非明确授权。
- 不恢复旧的 `j1/j2/j3/j4` 作为主语义。
- 不写四腿统一 rail 常数，例如 `[0.08, 0.08, 0.08, 0.08]`。
- `effort_controller` 的 16 通道顺序必须和 `joint_names.py` 一致。

快速验证：

```bash
python3 src/dog2_description/scripts/check_urdf_shift_boundary.py --strict
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest src/dog2_motion_control/test/test_joint_names.py src/dog2_motion_control/test/test_effort_controller_config.py src/dog2_motion_control/test/test_urdf_joint_limits_sync.py
```

## 模块 1：仿真与 bringup

范围：

- `src/dog2_bringup/launch/system.launch.py`
- `src/dog2_bringup/launch/sim_base.launch.py`
- `src/dog2_bringup/launch/effort_research_sim.launch.py`
- `src/dog2_bringup/worlds/*.sdf`
- `src/dog2_motion_control/launch/spider_gazebo_mpc.launch.py`
- `src/dog2_description/config/ros2_controllers.yaml`
- `src/dog2_motion_control/config/effort_controllers.yaml`

职责：

- 启动 Gazebo、robot description、ros2_control 和基础 controller。
- 区分 position 模式、effort 模式、research effort 模式。
- 保证 `/joint_states`、`/odom`、`/effort_controller/commands` 可用。

不可破坏约束：

- 平地 smoke 不应依赖窗型障碍。
- `controller_mode:=effort research_stack:=true` 必须使用 `effort_controller`。
- crossing world 的 topic 名称必须和 launch 中的 `gz_world_name`、odom bridge 参数一致。

快速验证：

```bash
colcon build --packages-select dog2_description dog2_motion_control dog2_bringup --symlink-install
source install/setup.bash
ros2 launch dog2_bringup smoke_test.launch.py controller_mode:=effort research_stack:=true expect_research_stack:=true ros_domain_id:=44 result_file:=/tmp/dog2_smoke_result.txt
```

## 模块 2：状态估计与步态相位

范围：

- `src/dog2_state_estimation/dog2_state_estimation/sim_state_estimator_node.py`
- `src/dog2_gait_planner/dog2_gait_planner/gait_scheduler_node.py`
- `src/dog2_interfaces/msg/*.msg`

职责：

- 把 Gazebo odom、joint states、contact 近似包装成统一 `RobotState`。
- 发布 `/dog2/state_estimation/odom` 和 `/dog2/state_estimation/robot_state`。
- 发布 `/dog2/gait/contact_phase`，供 smoke、MPC/WBC debug 和验证节点判断链路新鲜度。

不可破坏约束：

- research stack 使用 wall timer 时，不能被 `/clock` 停滞冻结。
- `RobotState.joint_state` 必须保留完整 16 通道信息。
- contact phase 不一定是真实接触，但必须稳定、新鲜、腿顺序一致。

快速验证：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest src/dog2_state_estimation/test/test_state_estimator.py src/dog2_gait_planner/test/test_gait_scheduler.py
```

## 模块 3：基础运动控制与 IK

范围：

- `src/dog2_motion_control/dog2_motion_control/kinematics_solver.py`
- `src/dog2_motion_control/dog2_motion_control/spider_robot_controller.py`
- `src/dog2_motion_control/dog2_motion_control/mpc_robot_controller.py`
- `src/dog2_motion_control/dog2_motion_control/leg_parameters.py`

职责：

- 提供位置模式基础站立、爬行、关节限制、rail lock 和 IK/FK 工具。
- 作为结构语义和实际关节命名的 Python 侧参考实现。

当前风险：

- 一些历史测试仍强调 rail lock 或 rail offset 行为，这和越障时 rail 主动运动存在模式差异。
- 修改 research stack 前，不能把基础位置控制路径打坏。

不可破坏约束：

- 位置模式站立/基础行走仍应可启动。
- 16 通道命令结构保持一致。
- IK 与 URDF 语义同步，不引入隐藏 base compensation。

快速验证：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest src/dog2_motion_control/test/test_joint_names.py src/dog2_motion_control/test/test_rail_limits.py src/dog2_motion_control/test/test_rail_offset.py src/dog2_motion_control/test/test_kinematics.py
```

## 模块 4：MPC 越障规划

范围：

- `src/dog2_mpc/include/dog2_mpc/*.hpp`
- `src/dog2_mpc/src/crossing_state_machine.cpp`
- `src/dog2_mpc/src/trajectory_generator.cpp`
- `src/dog2_mpc/src/mpc_controller.cpp`
- `src/dog2_mpc/src/mpc_node_complete.cpp`

职责：

- 维护 16D SRBD 状态：12D base + 4D rail。
- 管理 crossing 状态机、阶段目标、rail 目标和足端力优化。
- 输出 `/dog2/mpc/foot_forces` 与 `/dog2/mpc/crossing_state`。

当前结论：

- `crossing_state_machine.cpp` 已经部分使用真实 rail 限位符号。
- `trajectory_generator.cpp` 仍有四腿统一 `0.08` rail placeholder，不能作为最终逻辑。
- 当前 MPC 输出主要是足端力，尚未完整表达前腿/后腿的 3R 越障动作参考。

不可破坏约束：

- crossing rail target 必须按 `lf, lh, rh, rf` 分腿处理。
- `APPROACH` 不应把 rail 强行拉回不可行目标。
- `BODY_FORWARD_SHIFT`、`FRONT_LEGS_TRANSIT`、`REAR_LEGS_TRANSIT` 必须有明确支撑腿、摆动腿、rail target 和阶段切换条件。
- QP 失败时 fallback 不能让验证误判为成功。

快速验证：

```bash
colcon build --packages-select dog2_mpc --symlink-install
./build/dog2_mpc/test_crossing_basic
./build/dog2_mpc/test_16d_mpc_with_sliding
./build/dog2_mpc/test_mpc_crossing_loop
```

## 模块 5：WBC 与 effort 映射

范围：

- `src/dog2_wbc/src/wbc_controller.cpp`
- `src/dog2_wbc/src/wbc_node_complete.cpp`
- `src/dog2_bringup/dog2_bringup/wbc_effort_mux.py`

职责：

- 把 MPC 足端力通过 4DoF 单腿雅可比映射为 3R 关节力矩和 rail effort。
- 按 crossing stage 切换前腿/后腿构型标签。
- 合成 16 通道 `/effort_controller/commands`。

当前结论：

- `wbc_effort_mux.py` 的默认 `freeze_rail_effort` 是 false，但 launch 参数可以冻结 rail。
- `wbc_controller.cpp` 使用简化几何模型，`J(0,3)=1.0` 代表 rail 影响足端 x，需要和 URDF/Pinocchio 做一致性验证。
- WBC 目前没有显式关节轨迹任务，更多是足端力到 effort 的映射。

不可破坏约束：

- `/dog2/wbc/rail_effort_command` 和 `/effort_controller/commands` 中 rail 通道顺序必须一致。
- crossing 期间不能无意冻结 rail effort。
- WBC 修改后必须确认 12 旋转关节和 4 rail effort 都新鲜。

快速验证：

```bash
colcon build --packages-select dog2_wbc dog2_bringup --symlink-install
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest src/dog2_bringup/test/test_research_stack_files.py
```

## 模块 6：窗型越障场景与验收

范围：

- `src/dog2_bringup/worlds/window_frame.sdf`
- `src/dog2_bringup/launch/crossing_trial.launch.py`
- `src/dog2_bringup/launch/window_crossing_test.launch.py`
- `src/dog2_bringup/dog2_bringup/crossing_check.py`

职责：

- 提供窗型障碍 world。
- 触发 `/enable_crossing`。
- 自动判断 crossing 是否成功。

当前 PASS 标准：

- trigger 发出。
- 看到 `CROSSING:*` 状态。
- rail 位移超过阈值。
- body x 超过窗框关键位置。
- 状态估计、步态、MPC、WBC、effort command topic 保持新鲜。

不可破坏约束：

- PASS 不能只代表“不崩溃”。
- rail 动作必须来自真实 `/joint_states` 位移，而不是只看 command。
- 窗型 world 不应影响 flat-ground smoke。

快速验证：

```bash
ros2 launch dog2_bringup window_crossing_test.launch.py ros_domain_id:=47 timeout_sec:=150.0 result_file:=/tmp/dog2_window_crossing_result.txt
cat /tmp/dog2_window_crossing_result.txt
```

## 推荐推进顺序

1. 固定结构与接口基线：模块 0。
2. 固定 bringup 和 flat-ground research smoke：模块 1、2。
3. 固定 MPC 内部 crossing 阶段和 rail 目标：模块 4。
4. 固定 WBC 的 4DoF 映射和 rail effort 输出：模块 5。
5. 最后调窗型场景和端到端验收：模块 6。

每进入下一模块前，都先跑上一模块的快速验证。若失败，先回到最近一次改动模块修复，不把问题带到下游。

## 第一阶段建议

第一阶段先锁定模块 0、1、2，不改 MPC/WBC 算法：

1. 运行结构和 joint-order 测试，确认 16 通道语义基线。
2. 构建基础包，跑 flat-ground research smoke。
3. 记录当前 window crossing 的真实 PASS/FAIL 结果，作为之后改 MPC/WBC 的对照。

完成这三步后，再进入模块 4。这样后续如果 crossing 失败，我们能判断是算法改动导致，而不是结构、launch 或 topic 链路本身不稳。
