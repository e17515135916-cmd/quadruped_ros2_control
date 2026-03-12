# Dog4 Description - CHAMP 兼容配置

## 概述

这是 Dog2 机器人的 CHAMP 框架兼容版本，命名为 **dog4_description**。

## 主要特性

### ✅ CHAMP 标准关节配置

**关节轴向（1个Y轴 + 2个X轴）：**
- **HAA** (Hip Abduction/Adduction): **Y轴 (0 1 0)** - 髋关节外展/内收
- **HFE** (Hip Flexion/Extension): **X轴 (-1 0 0)** - 髋关节前后摆动  
- **KFE** (Knee Flexion/Extension): **X轴 (-1 0 0)** - 膝关节屈伸

**关节命名：**
- 前左腿 (lf): `lf_haa_joint`, `lf_hfe_joint`, `lf_kfe_joint`
- 前右腿 (rf): `rf_haa_joint`, `rf_hfe_joint`, `rf_kfe_joint`
- 后左腿 (lh): `lh_haa_joint`, `lh_hfe_joint`, `lh_kfe_joint`
- 后右腿 (rh): `rh_haa_joint`, `rh_hfe_joint`, `rh_kfe_joint`

**连杆命名：**
- `{prefix}_hip_link`
- `{prefix}_upper_leg_link`
- `{prefix}_lower_leg_link`
- `{prefix}_foot_link`

### ✅ 保留滑动副设计

Dog2 的独特 4-DOF 腿部设计：
- 滑动副关节: `j1`, `j2`, `j3`, `j4`
- 滑动副连杆: `l1`, `l2`, `l3`, `l4`

### ✅ ROS 2 Control 配置

- 16 个关节全部配置 (4 滑动副 + 12 旋转副)
- 每个关节都有 position, velocity, effort 接口

## 快速开始

### 1. 恢复到工作空间

```bash
# 复制到你的 ROS 2 工作空间
cp -r dog2_description /path/to/your_ws/src/

# 编译
cd /path/to/your_ws
colcon build --packages-select dog2_description
source install/setup.bash
```

### 2. 在 RViz2 中测试

```bash
# 使用提供的脚本
./quick_test_rviz.sh
```

在 RViz2 中：
1. 点击 **Add** → 选择 **RobotModel**
2. 设置 **Fixed Frame** 为 `base_link`
3. 使用 **joint_state_publisher_gui** 窗口控制关节

### 3. 验证关节轴向

```bash
# 生成 URDF
xacro dog2_description/urdf/dog2.urdf.xacro > /tmp/test.urdf

# 运行验证脚本
python3 verify_champ_axis_config.py
```

预期输出：
```
✅ HAA 关节 (Y轴): 全部正确
✅ HFE 关节 (X轴): 全部正确
✅ KFE 关节 (X轴): 全部正确
🎉 所有关节轴向配置符合 CHAMP 标准！
```

## 文件结构

```
dog4_description/
├── dog2_description/              # ROS 2 包
│   ├── urdf/
│   │   └── dog2.urdf.xacro       # CHAMP 兼容 URDF
│   ├── meshes/                    # 3D 模型文件
│   │   ├── *.STL                  # 视觉 mesh
│   │   └── collision/             # 碰撞 mesh
│   ├── config/
│   │   └── ros2_controllers.yaml # 控制器配置
│   ├── package.xml
│   └── CMakeLists.txt
├── specs/                         # 规范文档
│   └── champ-compliant-joint-configuration/
│       ├── requirements.md        # 需求文档
│       ├── design.md              # 设计文档
│       └── tasks.md               # 任务列表
├── quick_test_rviz.sh            # RViz2 测试脚本
├── verify_champ_axis_config.py   # 轴向验证脚本
├── CHAMP_COMPLIANCE_SUMMARY.md   # 完成总结
├── BACKUP_INFO.md                # 备份信息
└── README.md                     # 本文件
```

## 技术规格

### 关节限位

| 关节类型 | 下限 | 上限 | 单位 |
|---------|------|------|------|
| HAA | -0.785 | 0.785 | rad (±45°) |
| HFE | -2.618 | 2.618 | rad (±150°) |
| KFE | -2.8 | 0.0 | rad (-160° to 0°) |
| 滑动副 | -0.111 | 0.111 | m |

### 控制参数

| 参数 | 旋转副 | 滑动副 |
|------|--------|--------|
| Effort | 50 Nm | 100 N |
| Velocity | 20 rad/s | 5 m/s |

## 与 CHAMP 框架集成

这个配置可以直接与 [CHAMP 四足机器人控制框架](https://github.com/chvmp/champ) 集成：

1. **关节命名兼容**: 使用标准的 HAA/HFE/KFE 命名
2. **关节轴向兼容**: 1个Y轴 + 2个X轴配置
3. **额外功能**: 保留了滑动副设计（需要在 CHAMP 配置中额外处理）

### 集成步骤

```bash
# 1. 安装 CHAMP
cd ~/your_ws/src
git clone https://github.com/chvmp/champ.git

# 2. 复制 dog4 配置
cp -r dog2_description ~/your_ws/src/

# 3. 创建 CHAMP 配置文件
# 参考 CHAMP 文档创建机器人配置

# 4. 编译
cd ~/your_ws
colcon build
```

## 验证清单

- [x] 所有关节轴向符合 CHAMP 标准
- [x] 关节命名符合 CHAMP 标准
- [x] 连杆命名符合 CHAMP 标准
- [x] URDF 编译无错误
- [x] check_urdf 验证通过
- [x] RViz2 可视化正常
- [x] 滑动副功能保留
- [x] ROS 2 Control 配置完整

## 相关文档

- **需求文档**: `specs/champ-compliant-joint-configuration/requirements.md`
- **设计文档**: `specs/champ-compliant-joint-configuration/design.md`
- **任务列表**: `specs/champ-compliant-joint-configuration/tasks.md`
- **完成总结**: `CHAMP_COMPLIANCE_SUMMARY.md`
- **备份信息**: `BACKUP_INFO.md`

## 版本历史

### v1.0 (2026-02-07)
- ✅ 初始 CHAMP 兼容配置
- ✅ 重命名所有关节和连杆
- ✅ 修正 HAA 关节轴向为 Y 轴
- ✅ 更新 ROS 2 Control 配置
- ✅ 验证所有关节轴向
- ✅ 创建测试和验证脚本

## 支持

如有问题，请参考：
1. CHAMP 框架文档: https://github.com/chvmp/champ
2. ROS 2 URDF 教程: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/URDF-Main.html
3. 本备份中的 specs 文档

## 许可证

与原 Dog2 项目相同。
