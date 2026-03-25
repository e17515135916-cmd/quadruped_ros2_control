# DEVELOPMENT_LOG

## 2026-03-18 10:47 今日工作概述
完成 Gazebo Fortress + ros2_control 启动链路的验证与修复，确保控制器成功激活并进入 50 Hz 主循环；针对“蜘蛛式外展步态”持续出现的 IK Failure 进行了系统性诊断，确认问题来源于目标落足点在 Y 方向超出可达工作空间，并将步态外展参数下调以逼近可行解。

### 💻 工程实现与参数调整
- **Gazebo / ros2_control 适配**
  - 将 URDF 中 ros2_control 插件切换为 `gz_ros2_control`，确保 Fortress 可正确加载控制器。
  - 纠正 `base_offset_joint` 的 Z 偏移，避免机器人整体下沉导致腿部穿地。
- **步态生成器（GaitGenerator）**
  - 旧版参数基线保持：`body_height=0.16`、`stride_length=0.02`。
  - 外展偏移调整：`y_offset = ±0.07`，使目标 Y 坐标从 0.2025 收敛到 0.1325，降低侧向外展引起的工作空间越界风险。
- **启动流程与控制器**
  - `spider_gazebo_complete.launch.py` 启动链路确认正常：`joint_state_broadcaster`、`joint_trajectory_controller`、`rail_position_controller` 皆激活。
  - 检查并规避重复启动 `spider_robot_controller` 导致的同名节点冲突。

### 🐛 Bug深度剖析与解决
- **错误现象**：控制器进入运行态后，四条腿连续报 `IK Failure`，提示 “Target out of workspace”。
- **运动学根因**：
  - 以旧版几何基座参数（`base_position.y = ±0.0625`）为基准，落足点目标在 Y 方向叠加外展偏移后达到 **0.1325 m**。该目标点在当前 3-DoF 解析 IK 下的可达区域外，导致余弦定理计算的三角不等式失效（等价于进入“工作空间死区/连杆无法闭合”区域）。
  - 当目标点超出可达范围时，IK 直接返回 None，主控制器被迫退回“站立姿态”，产生持续失败循环。
- **解决措施**：
  - 逐步降低 `y_offset`，将落足目标推回到可达空间；同时保持 `body_height` 不变，以避免引入新的垂向干涉或奇异位姿。
  - 通过日志确认 IK 目标点数值与几何模型一致，排除“旧版本未生效”的假象。

### 🚀 课题意义与下一步
本次修复聚焦于“跨越飞机油箱窗型障碍物”任务的基础支撑姿态稳定性：
- 通过收敛外展偏移，保障腿部目标点处于可达空间，从源头上减少 IK 失败，提高低姿态下的可控性。
- 低重心 + 宽支撑面是穿越窗框、抑制侧翻的核心物理条件；当前的参数收敛为后续 **直线导轨重心转移策略** 与 **MPC/WBC 约束优化** 提供了稳定可行的基线。

**下一步计划**：
1. 进一步核对 URDF 中腿基座几何与 `leg_parameters.py` 是否存在微小偏差，避免局部坐标系不一致造成的“假超界”。
2. 基于已稳定的 IK 解域，引入导轨位移作为优化变量，将 4-DoF 冗余度转化为跨越窗框时的重心迁移能力。
3. 与 MPC/WBC 控制层对接，验证低姿态下的稳态行走与侧向抗倾覆性能。

---

## 2026-03-19 10:47 今日工作概述
完成“腿序映射 + 参数同步 + URDF 统一平移”链路的梳理与合并，确保仿真模型、步态参数与控制器命名在新的腿编号顺序下保持一致；整理出待排查的残留文件范围，明确后续验证路径。

### 💻 工程实现与参数调整
- **URDF 统一重定位（Path A）**
  - 在 `dog2.urdf.xacro` 中引入 `urdf_shift_x/y/z` 统一平移量。
  - 平移应用于：`base_offset_joint`、`base_link` 的 inertial/visual/collision，以及 `j${leg_num}` 的关节 `origin`。
  - 修复 xacro 数学表达：将 `xyz` 字符串拆为 `xyz_x/xyz_y/xyz_z` 数值参数，避免下标计算报错。
- **腿编号与命名映射重排**
  - 统一腿编号顺序：`j1=LF`、`j2=LH`、`j3=RH`、`j4=RF`。
  - 同步 `joint_names.py`：
    - `LEG_PREFIX_MAP`: 1→lf, 2→lh, 3→rh, 4→rf
    - `PREFIX_TO_LEG_MAP`: lf→1, lh→2, rh→3, rf→4
- **步态参数同步**
  - `gait_params.yaml` / `gait_params_ros.yaml`：
    - `leg_sequence = [leg1, leg2, leg3, leg4]`
    - `phase_offsets` 依序设为 `0/90/180/270`
    - `leg_base_positions` 与 `leg_base_rotations` 按新腿序重排（LF→LH→RH→RF）
- **几何参数对齐**
  - `leg_parameters.py` 中 `leg_num/leg_id` 与 `base_position/base_rotation` 已按新编号顺序对齐。

### 🐛 Bug深度剖析与解决
- **问题本质**：腿编号重排后，URDF、步态参数和控制器映射若存在“旧顺序残留”，会导致目标点与关节命名错位，表现为 IK 无解、关节驱动错腿或力学异常。
- **根因分析**：
  - 多源配置（URDF、YAML、Python 配置）同时使用腿序，任何一处残留旧顺序都会造成坐标系与命名映射错配。
  - Xacro 中 `xyz` 使用字符串形式参与运算导致数学表达式出错，属于编译期静态失败。
- **解决手段**：
  - 统一引入 URDF 平移参数并修正 xacro 表达式，消除几何偏置与构建错误。
  - 将腿编号映射作为“单一真源”同步到 `joint_names.py` 与配置文件中，防止多处失配。

### 🚀 课题意义与下一步
新的腿序与几何一致性是实现“穿越窗框形障碍物”的基础前置条件：
- 只有当 URDF、控制器与步态顺序一致时，才能保证在低姿态外展状态下正确落足与重心分配，从而提升跨越窄窗框时的抗侧翻能力。
- 统一平移参数为后续引入导轨位移优化（重心转移）提供了稳定的坐标基准，支撑 MPC/WBC 的轨迹与约束建模。

**下一步计划**：
1. 对全工程执行“残留顺序扫描”（lf/rf/lh/rh 关键词），排查 MPC/WBC 与控制器配置中的旧顺序残留。
2. 重点核查 ros2_control 控制器参数与关节顺序是否与新腿序匹配。
3. 启动仿真验证新腿序下的站立姿态与 IK 可达域。

---

## 2026-03-19 16:05 urdf_shift 边界收敛与自动校验

针对“全局 urdf_shift 多层补偿导致双重偏移风险”的问题，落实为“唯一补偿层 + 自动校验”的工程约束：
- **唯一补偿层**：`urdf_shift` 仅允许出现在 `base_offset_joint`，其余 origin 均使用 base_link-local 常量。
- **URDF 边界自检脚本**：新增 `check_urdf_shift_boundary.py`，通过 xacro 展开后验证：
  - `base_link` visual/inertial 原点保持固定
  - 四条腿根 `*_rail_joint` 原点落在期望范围
- **避免双重补偿**：在 `dog2.urdf.xacro` 中明确写入注释边界，禁止 TF/控制/外参层再做补偿。

> 该修复确保 CAD 历史偏移只在一个层级出现，避免后续维护人员误在控制层重复修正。

## 2026-03-19 14:32 终局一致性重构（dog2 Spider Topology）

在本轮迭代中，我们把问题从“局部参数调不对”提升到了“系统语义与物理真实是否同构”的层面：
**保持物理拓扑不变，只在算法与描述层做可验证的映射重构**。最终确立并固化以下单一真源：
- 机头朝向：`-X`
- 逆时针腿序：`1=LF, 2=LH, 3=RH, 4=RF`
- 控制与模型命名必须与上述物理事实严格一致

### Architecture Refactoring

- **URDF 与 CAD 偏移彻底解耦**
  - 识别并隔离 CAD 导出携带的全局平移：`urdf_shift_x/y/z`。
  - 在 `dog2.urdf.xacro` 的实例化层采用 **one-time compensation**（一次性补偿）策略，避免把 CAD 偏移泄漏到控制层。
  - 关键原则落地：URDF 负责把“几何壳体”落在正确物理位置；控制层/算法层仅消费物理一致的坐标，不再背负 CAD 历史包袱。

- **HAL 语义化命名重构（从编号到解剖学语义）**
  - 从 CAD 风格无语义编号（如 `j1/j11/...`）迁移到生物力学语义接口：
    - `rail`（导轨）
    - `coxa`（基节）
    - `femur`（腿节）
    - `tibia`（胫节）
  - 同步重构 `dog2.urdf.xacro` 宏定义与 `ros2_controllers.yaml` 接口命名，实现：
    - **硬件实例 ID** 与 **算法逻辑 ID** 解耦
    - 上层控制器不再依赖 CAD 的偶然命名细节

- **拓扑一致性闭环（Model ↔ Control ↔ Gait）**
  - 统一腿序映射：`leg1=lf`, `leg2=lh`, `leg3=rh`, `leg4=rf`。
  - 与 `joint_names.py`、`leg_parameters.py`、`gait_params*.yaml` 做同源对齐，避免跨文件“半重构”导致错腿驱动。

### Bug Fixes

- **实例化层前后腿参数调用歧义修复**
  - 明确 CAD 网格关系是“左右镜像主导”，而非“前后镜像可直接复用”。
  - 修复腿实例化中 `prefix` 与 `leg_num` 的张冠李戴问题，消除 `LF/LH/RH/RF` 的错绑风险。

- **Xacro 解析崩溃修复（XML 1.0 注释陷阱）**
  - 根因：注释块内出现连续减号 `--`，触发 `XML parsing error: invalid token`。
  - 修复：重写分隔注释符号（使用 `=` / `*` 等安全字符），并建立注释语法红线，防止再次引入静态解析失败。

### Tech Debt Cleared

- 清除“CAD 导出坐标即真值”的隐性技术债，建立“CAD 仅提供网格，系统坐标由机器人软件栈定义”的工程边界。
- 清除“编号即语义”的命名技术债，统一为可读、可审计、可追踪的语义化关节体系。
- 清除“多源配置各自为政”的一致性债务：将腿序映射固化为跨 URDF / YAML / Python 的共享契约。

### Next Steps

1. **自动化一致性测试**
   - 增加启动前拓扑自检脚本：校验 URDF、控制器 joints、步态 `leg_sequence`、`leg_base_positions` 的符号与顺序一致性。
2. **TF 与外参防呆机制**
   - 在传感器外参与 TF 广播链路中加入“偏移来源标记”，硬性禁止二次补偿（Double Offset）。
3. **面向越障任务的控制层验证**
   - 在 Gazebo Fortress 中执行低姿态越障回归：验证 rail 重心迁移 + crawl gait 在窄窗框工况下的稳定裕度。
4. **MPC/WBC 接口前置整理**
   - 以 `rail/coxa/femur/tibia` 语义接口为统一输入，降低后续约束建模与调参复杂度。

> 在非标构型机器人中，最昂贵的 bug 往往不是“算法算错”，而是“语义错绑”。
> 本轮工作的价值在于：把物理真实与算法逻辑做了工程化解耦，并建立了可持续验证的映射闭环。

---

## 2026-03-19 继续：URDF 偏移边界防呆接入构建测试

本轮将“唯一补偿层”从文档约束进一步升级为**默认启用的可执行测试**，并补充脚本参数化能力，降低浮点误报风险。

### 💻 工程实现
- **脚本参数增强（防误报）**
  - `check_urdf_shift_boundary.py` 新增：
    - `--tolerance`（兼容别名 `--tol`）用于设置容差。
    - `--strict` 启用严格模式（容差固定为 `1e-6`）。
  - 输出信息增加模式与容差打印，失败信息携带 `tol`，便于快速定位。

- **CMake 默认开启 + 可显式关闭**
  - 在 `dog2_description/CMakeLists.txt` 增加开关：
    - `DOG2_ENABLE_URDF_SHIFT_BOUNDARY_CHECK`（默认 `ON`）。
  - 在 `BUILD_TESTING` 且开关开启时，注册 `ctest`：
    - `dog2_urdf_shift_boundary_check`
    - 调用脚本并默认使用 `--strict`。
  - 对缺失 `python3` / `xacro` 场景给出 warning 并跳过，避免阻塞极简环境。

- **安装集成**
  - 将 `scripts/check_urdf_shift_boundary.py` 纳入 `install(PROGRAMS ...)`，确保安装后环境也可直接运行。

### ✅ 验证结果
- 本地执行脚本通过：
  - `[PASS] URDF shift boundary checks passed`。
- 新增检查满足“默认安全、按需关闭”的工程实践目标。

### 🚀 后续建议
1. 若仓库后续引入正式 CI（如 GitHub Actions / GitLab CI），可直接在 `colcon test` 流程中复用该 `ctest`，形成“本地 + CI”双保险。
2. 若 CAD 再导出导致基准变化，优先更新期望常量并保留严格模式，确保偏移边界语义不回退。

---

## 2026-03-19 继续：关节被动耗散与URDF风格一致性加固

本轮在“偏移边界已收敛”的基础上，继续处理仿真稳定性与模型可维护性：
通过补齐关节 `dynamics`、参数化接触模型、统一材质命名和角度常量，降低高频抖动与配置漂移风险。

### 💻 工程实现
- **关节被动耗散补齐（全可动关节）**
  - 在 `dog2.urdf.xacro` 中为所有可动关节统一加入 `<dynamics damping/friction>`：
    - `rail (prismatic)`：`damping=0.25`、`friction=0.05`
    - `coxa (revolute)`：`damping=0.12`、`friction=0.02`
    - `femur/tibia (revolute)`：`damping=0.15`、`friction=0.02`
  - 参数全部抽为 xacro property，便于后续批量联调与版本对比。

- **接触模型参数化与保守基线下调**
  - 将足端（当前以 `tibia_link` 代理）接触参数抽为统一属性：
    - `foot_contact_mu1/mu2=1.0`
    - `foot_contact_kp=2.0e5`（由 `1.0e6` 下调）
    - `foot_contact_kd=50.0`（由 `100.0` 下调）
    - `minDepth=0.0005`、`maxVel=0.05`
  - 增加注释说明：后续若引入独立 foot link，再迁移接触定义。

- **URDF 可读性与一致性清理**
  - 修复多处 `material name=""` 空命名，替换为具名材质：
    - `mat_base_gray`、`mat_blue`、`mat_white`。
  - 统一角度常量来源，避免 `1.5708 / 3.1416 / 3.14159265` 混用：
    - 增加 `pi`、`half_pi` 属性
    - `rpy` 与 `hip_rpy` 统一改为引用常量。

### ✅ 验证结果
- 严格模式边界检查通过：
  - `python3 src/dog2_description/scripts/check_urdf_shift_boundary.py --strict`
  - 输出：`[PASS] URDF shift boundary checks passed (mode=strict, tol=1e-06).`

### 🧭 调参原则（已固化）
1. `joint damping` 与控制器 `D` 存在等效叠加，联调时避免双侧同时大幅上调。
2. 若低速跟踪出现“爬行/死区”，优先小幅下调 `friction` 再观察。
3. 分层联调顺序保持：`rail -> coxa -> femur/tibia -> 全身步态`。

---

## 2026-03-19 继续：控制器命名/关节语义一致性修复与启动链路收敛

本轮围绕“控制器激活超时 + 上层节点断连重试”进行了针对性收敛，核心是统一 **URDF / ros2_control / motion_control** 三层命名与时钟语义，清理导致握手失败与运行时崩溃的配置偏差。

### 💻 工程实现
- **xacro 常量冲突修复**
  - 将 `dog2.urdf.xacro` 中自定义 `pi` 重命名为 `PI_CONST`，并同步替换引用，避免与 xacro 内置全局符号冲突警告（`redefining global symbol: pi`）。

- **ROS 包清单规范化**
  - `dog2_demos/package.xml` 中 `test_dependency` 全量替换为 format=3 合法标签 `test_depend`，消除 colcon 解析告警。

- **控制器关节命名与 URDF 对齐**
  - `dog2_description/config/ros2_controllers.yaml`：
    - 12个旋转关节从 `*_haa/*_hfe/*_kfe` 统一改为 `*_coxa/*_femur/*_tibia`。
    - 导轨关节从 `j1~j4` 统一改为 `lf/lh/rh/rf_rail_joint`。
  - `dog2_motion_control/dog2_motion_control/joint_names.py`：
    - `REVOLUTE_JOINT_TYPES` 改为 `['coxa','femur','tibia']`。
    - 相关辅助函数与说明同步更新为新语义命名。

- **关节限位键值同步修复（KeyError 根因）**
  - `dog2_motion_control/dog2_motion_control/leg_parameters.py` 中 `joint_limits` 键从 `haa/hfe/kfe` 同步迁移为 `coxa/femur/tibia`，修复 `KeyError: 'coxa'`。

- **仿真时钟与生成姿态策略收敛**
  - `spider_gazebo_complete.launch.py`：
    - `spider_controller_node` 参数 `use_sim_time` 从 `False` 改为 `True`，避免仿真时钟与系统时钟混用导致状态判定抖动。
    - spawner `-c` 目标恢复为 `/controller_manager`（与 Humble + gz_ros2_control 默认行为一致）。
  - `dog2.urdf.xacro`：移除 `world_to_base_joint` 固连（避免与 spawn pose 职责重叠），保留由 launch 统一管理初始高度。

### 🐛 问题链路复盘
- **初始现象**：`Switch controller timed out`、`Not existing command interfaces`、上层控制器持续重连与紧急姿态。
- **分层根因**：
  1. 控制器 joints 与 URDF joints 命名体系不一致（历史命名残留）。
  2. motion_control 内部关节类型和限位字典键未完成同源迁移，触发运行时 `KeyError`。
  3. 启动阶段 controller_manager 目标名与插件实际行为不一致，导致 spawner 等待错误服务。
  4. `use_sim_time=False` 放大了仿真联调中的连接状态误判风险。

### ✅ 当前状态与结论
- 命名链路（URDF ↔ controllers.yaml ↔ Python 控制层）已完成同源统一。
- 运行时字典键崩溃（`KeyError: 'coxa'`）已消除。
- 启动链路已回归 ROS 2 Humble + gz_ros2_control 的默认 manager 约定。
- 后续如仍出现控制器激活超时，优先从仿真步进/启动负载角度排查，而非继续回退命名层。

### 🚀 下一步计划
1. 以最小命令集回归验证控制器状态机（`list_controllers`、`joint_states`、轨迹话题发布）。
2. 在控制器全部可激活后，再开展落地高度与接触参数二次调优（避免混叠问题源）。
3. 将“命名一致性 + 时钟一致性 + manager 目标一致性”沉淀为启动前自动检查项。

---

## 2026-03-19 22:02 继续：仿真时钟启动竞态修复与调试键名一致性收口

本轮完成了“控制器已激活但上层仍误判时钟未推进”的竞态修复，并修正调试信息发布路径中的历史键名残留，消除 `KeyError: 'haa'` 崩溃点。

### 💻 工程实现
- **调试关节键名统一（直接崩溃点修复）**
  - 文件：`src/dog2_motion_control/dog2_motion_control/spider_robot_controller.py`
  - `_publish_debug_info()` 中关节读取键从旧命名：
    - `haa / hfe / kfe`
  - 统一迁移为当前语义命名：
    - `coxa / femur / tibia`
  - 结果：消除启动后调试发布分支触发的 `KeyError: 'haa'`。

- **起立状态机时钟竞态防护**
  - 文件：`src/dog2_motion_control/dog2_motion_control/spider_robot_controller.py`
  - 调整 `start()` 与 `_execute_standup_trajectory()`：
    1. 当 `/clock` 尚未就绪（`now.nanoseconds == 0`）时，不再“跳过起立并直接进入 READY”。
    2. 改为保持 `STANDING_UP` 并等待时钟同步，避免状态机提前越级。
    3. 增加一次性等待日志标志 `_clock_wait_logged`，避免日志刷屏。
    4. 时钟就绪后再初始化 `standup_start_time`，按既定 minimum-jerk 轨迹执行起立。

- **Gazebo 自动运行确认**
  - 文件：`src/dog2_motion_control/launch/spider_gazebo_complete.launch.py`
  - 已确认 GUI / headless 两条分支均携带 `-r`，默认自动推进仿真时钟。

### ✅ 结果与结论
- 控制器链路维持可激活状态（`joint_state_broadcaster / joint_trajectory_controller / rail_position_controller`）。
- 上层节点不再因启动瞬间时钟未同步而误跳过起立流程。
- 调试路径键名与 URDF/控制器命名体系保持一致，运行时字典访问稳定。

### 🧪 建议复现命令
```bash
cd ~/aperfect/carbot_ws
rm -rf build/dog2_motion_control install/dog2_motion_control
colcon build --packages-select dog2_motion_control --symlink-install
source install/setup.bash
ros2 launch dog2_motion_control spider_gazebo_complete.launch.py
```

### 🚀 后续计划
1. 记录一次完整启动日志，确认“等待时钟同步 -> 起立完成 -> READY_FOR_MPC”三段状态转移连续可复现。
2. 在 debug 模式下增加轻量状态摘要（状态机阶段、dt、phase）用于联调可视化。
3. 将 `/clock` 就绪检查抽成可复用启动健康检查函数，供后续控制节点复用。
